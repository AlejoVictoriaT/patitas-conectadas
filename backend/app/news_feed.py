"""Ingesta de contenido animal por RSS.

Qué hace: lee feeds de mascotas y las secciones generales de varios medios, se
queda solo con lo que habla de perros, gatos y animales de compañía, descarta lo
angustiante, lo clasifica por tema y lo guarda.

Qué NO hace, a propósito:

* No copia el texto de la nota. Guarda titular, el resumen que el propio feed
  publica y el enlace al medio. Republicar el cuerpo completo sería apropiarse
  de trabajo ajeno; enviar tráfico a la fuente no.
* No inventa ni reescribe titulares. Lo que se muestra es lo que el medio dijo.

Por qué se filtra lo duro: esta sección la abre alguien que acaba de publicar
que perdió a su perro. Maltrato, envenenamientos o la muerte de una mascota son
temas legítimos, pero no aquí: quien llega buscando ayuda no necesita que se le
confirme su peor miedo. Lo que sí sirve es dónde hay jornada de adopción, cómo
se vacuna, qué albergue necesita manos y por qué su perro hace lo que hace.
"""

from __future__ import annotations

import asyncio
import math
import re
import unicodedata
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from typing import NamedTuple
from urllib.parse import quote_plus, urlparse

import httpx
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from .data.geo import COUNTRIES
from .models import NEWS_TOPICS, NewsItem, utcnow

# --------------------------------------------------------------------- feeds


class Fuente(NamedTuple):
    nombre: str
    url: str
    # Un agregador no es un medio: devuelve notas de muchos, y cada una trae el
    # suyo en `<source url="…">`. En esos feeds el medio y la procedencia se
    # deciden nota por nota, no por la fuente entera.
    agregador: bool = False
    # Prensa de fuera. Solo entra por los temas atemporales y solo se muestra
    # cuando el material colombiano de ese tema no alcanza.
    extranjero: bool = False


# Temas que valen igual aquí que en cualquier parte y hoy que en tres meses. Una
# jornada de adopción en Tarragona no le sirve a nadie en Pereira, pero por qué
# un gato se acuesta sobre el teclado se lee igual de bien en los dos sitios.
#
# Es la única puerta por la que entra prensa extranjera. Si algún tema local
# crece, esa prensa desaparece sola de la pantalla: ver `temas_reforzados`.
TEMAS_ATEMPORALES = ("comportamiento", "salud")

# Cuántas notas colombianas necesita un tema para sostenerse solo. Por debajo de
# esto se completa con las de fuera; por encima, dejan de mostrarse.
MINIMO_LOCAL_POR_TEMA = 8


# Consultas a Google Noticias, acotadas a Colombia.
#
# Son el motor de lo local, y existen por una razón concreta: los medios
# colombianos casi no tienen sección de mascotas. Lo que sí hay —y mucho— son
# jornadas de esterilización, vacunación antirrábica y adopción publicadas en
# la sección de ciudad, de salud o directamente por una alcaldía. Buscar por
# tema en toda la prensa las encuentra; suscribirse a secciones de mascotas, no.
CONSULTAS: tuple[str, ...] = (
    "adopcion de mascotas",
    "jornada de adopcion perros gatos",
    "jornada de vacunacion antirrabica mascotas",
    "esterilizacion de perros y gatos",
    "albergue de animales",
    "fundacion animalista",
    "centro de bienestar animal",
    "tenencia responsable de mascotas",
    "rescate de perros",
    "rescate de gatos",
    "comportamiento de los perros",
    "cuidado de mascotas veterinario",
    "perros y gatos",
    "mascotas Colombia",
)

_PLANTILLA_GOOGLE = (
    "https://news.google.com/rss/search?q={consulta}&hl=es-419&gl=CO&ceid=CO:es-419"
)

# Solo feeds verificados que responden XML. Si un medio cambia su URL, la
# ingesta lo salta y sigue con los demás: nunca falla entera por uno solo.
#
# Todos son colombianos a propósito. Antes había fuentes españolas, que traían
# mucho volumen y buen material de comportamiento, pero una jornada de adopción
# en Tacoronte no le sirve a nadie que esté buscando a su perro en Pereira.
FEEDS: list[Fuente] = [
    *[
        Fuente("Google Noticias", _PLANTILLA_GOOGLE.format(consulta=quote_plus(c)), agregador=True)
        for c in CONSULTAS
    ],
    # Medios con feed propio: aportan lo que el agregador no tiene, que es la
    # imagen de portada. Se leen enteros y el filtro se queda con lo de animales.
    Fuente("El Tiempo · Mascotas", "https://www.eltiempo.com/rss/vida_mascotas.xml"),
    Fuente("El Tiempo", "https://www.eltiempo.com/rss/vida.xml"),
    Fuente("El Tiempo", "https://www.eltiempo.com/rss/colombia.xml"),
    Fuente("El Tiempo · Bogotá", "https://www.eltiempo.com/rss/bogota.xml"),
    Fuente("El País (Cali)", "https://www.elpais.com.co/arc/outboundfeeds/rss/?outputType=xml"),
    Fuente("Publimetro", "https://www.publimetro.co/arc/outboundfeeds/rss/?outputType=xml"),
    Fuente("Semana", "https://www.semana.com/arc/outboundfeeds/rss/?outputType=xml"),
    Fuente("El Heraldo", "https://www.elheraldo.co/arc/outboundfeeds/rss/?outputType=xml"),
    Fuente("El Colombiano", "https://www.elcolombiano.com/rss/portada.xml"),
    # Refuerzo para los temas atemporales. Comportamiento y salud son justo lo
    # que la prensa colombiana casi no publica y estos medios publican a diario.
    Fuente("La Vanguardia", "https://www.lavanguardia.com/rss/mascotas.xml", extranjero=True),
    Fuente("Muy Interesante", "https://www.muyinteresante.com/feed/", extranjero=True),
]

# Medios colombianos cuyo dominio no termina en `.co`. Con la regla del dominio
# alcanza para alcaldías y gobernaciones (todas `.gov.co`); estos hay que
# nombrarlos. Sin la lista, El Tiempo y Semana quedarían fuera por llamarse
# `.com`, y con ella no entran ni Infobae ni MVS ni sipse, que son los que se
# colaban por publicar de mascotas en español.
DOMINIOS_COLOMBIANOS = frozenset({
    "eltiempo.com", "elespectador.com", "semana.com", "elcolombiano.com",
    "vanguardia.com", "lapatria.com", "pulzo.com", "minuto30.com",
    "rcnradio.com", "noticiasrcn.com", "bluradio.com", "kienyke.com",
    "elpais.com.co", "eluniversal.com.co", "elheraldo.co", "publimetro.co",
    "infobae.com/colombia",
})

# Ventana de vigencia. Muy distinta a la del feed de emergencia que había antes:
# «cómo saber si tu gato tiene dolor» sirve igual hoy que dentro de un mes, y con
# un mes y medio la sección se mantiene llena sin depender de que los medios
# publiquen algo de mascotas esta semana.
DIAS_DE_VIGENCIA = 45

# ------------------------------------------------------------- vocabulario

# Puerta de entrada. Se aplica a TODOS los feeds, también a los dedicados: son
# de mascotas, pero publican fauna silvestre —osos en Kamchatka, orcas en el
# Estrecho— y eso no es de lo que trata esta plataforma. Pedir que la nota
# nombre a un animal de compañía resuelve las dos cosas con una sola regla.
#
# Deliberadamente NO incluye «animal» a secas: dejaría pasar ganadería, fauna y
# cualquier uso figurado. Las formas compuestas de abajo sí son inequívocas.
PALABRAS_ANIMALES = (
    "mascota", "perro", "perra", "perrit", "perruno", "cachorro", "cachorra",
    "gato", "gata", "gatit", "gatuno", "michi", "minino", "lomito",
    "canino", "canina", "felino", "felina", "adiestra", "etolog", "antrozoolog",
    "galgo", "labrador", "bulldog", "chihuahua", "pastor aleman", "beagle",
    "bienestar animal", "proteccion animal", "protectora de animales",
    "animales de compania", "animal de compania", "tenencia responsable",
    "adopcion de mascotas", "refugio de animales", "albergue de animales",
    "medicina veterinaria", "clinica veterinaria", "peludo", "cuatro patas",
    "pet friendly", "pet-friendly",
)

# Exclusión. Se mira titular y resumen: basta con que aparezca en cualquiera.
#
# Las formas de «morir» están aquí a propósito, aunque eso deje fuera el
# contenido sobre duelo por una mascota, que es útil y está bien escrito. Es una
# decisión editorial, no técnica: si algún día hay una sección de acompañamiento,
# ese material entra por ahí y estas palabras salen de la lista.
PALABRAS_ANGUSTIANTES = (
    "maltrat", "crueldad", "torturad", "tortura a", "envenen", "sacrific",
    "eutanas", "matanza", "masacre", "apunal", "degoll", "descuartiz",
    "mutilad", "quemado vivo", "quemada viva", "pelea de perros",
    "peleas de perros", "zoofilia", "abuso sexual", "asesin", "balead",
    "murio", "muere", "mueren", "morir", "muerte", "muertos", "muertas",
    "fallecid", "cadaver", "sin vida", "atropell", "arrollad", "ataque mortal",
    "devorad", "agoniz", "desnutrid", "corrida de toros", "tauromaquia",
    "coleo", "trafico de fauna", "trafico ilegal",
)

# «abandonado» no está en la lista de arriba, y es a propósito: media sección de
# adopciones se cuenta con esa palabra —«fue abandonado y hoy busca familia»— y
# excluirla costaría más de lo que evita. Los casos duros de abandono caen igual
# por las otras: casi siempre traen «muere», «maltrato» o «desnutrido».

# La emergencia tiene su propia sección y sus propios teléfonos. Aquí no entra,
# ni siquiera cuando la nota es buena —«la perrita que venció a los escombros»
# lo es—, porque el punto de esta pantalla es ser el lugar donde no se habla de
# eso. Sin esta lista, los feeds generales la llenan de terremoto en un día.
PALABRAS_EMERGENCIA = (
    "terremoto", "sismo", "temblor", "replica", "epicentro", "damnificad",
    "escombros", "derrumbe", "colaps", "evacuad", "zona de desastre",
    "calamidad publica", "tragedia", "catastrofe", "inundacion", "incendio",
    "deslizamiento", "avalancha", "emergencia",
)

# Política y actualidad municipal de fuera. Se aplica SOLO a la prensa
# extranjera, y es lo que separa el consejo del cotilleo: «por qué tu gato se
# sube al teclado» sirve en Pereira, «el concejal de Tacoronte anuncia un censo
# felino» no le sirve a nadie aquí. Sin esto, el refuerzo atemporal se llenaba
# de plenos de ayuntamiento y de entrevistas a cargos públicos españoles.
PALABRAS_ACTUALIDAD_AJENA = (
    "ayuntamiento", "concejal", "consistorio", "diputacion", "generalitat",
    "comunidad de madrid", "junta de andalucia", "alcalde de", "alcaldesa de",
    "municipio de", "provincia de", "gobierno espanol", "ministerio",
    "congreso de los diputados", "ley de bienestar animal en espana",
)

# Nombres propios que contienen un animal y no hablan de uno. El Parque del
# Perro es una zona de Cali: sin esta lista, cada cierre vial del barrio entra
# al feed de mascotas.
EXPRESIONES_ENGANOSAS = (
    "parque del perro", "perro caliente", "perros calientes", "gato hidraulico",
    "dia de perros", "pelea de gatos", "ojo de gato",
)

# --- temas -----------------------------------------------------------------

PALABRAS_ADOPCION = (
    "adopcion", "adopta", "adoptar", "adoptad", "adoptante", "en adopcion",
    "hogar de paso", "hogares de paso", "familia de acogida", "acogida temporal",
    "jornada de adopcion", "feria de adopcion", "busca hogar", "buscan hogar",
    "nuevo hogar", "dar en adopcion", "padrino", "apadrina",
)

# Sin «jornada», «campaña», «brigada» ni «alcaldía»: son palabras de cualquier
# noticia municipal y arrastraban aquí notas que no hablaban de ningún refugio.
PALABRAS_REFUGIOS = (
    "albergue", "refugio", "fundacion", "protectora", "perrera", "coso municipal",
    "zoonosis", "rescat", "voluntari", "donacion", "donar", "santuario",
    "secretaria de ambiente", "centro de bienestar animal", "bienestar animal",
    "tenencia responsable", "proteccion animal", "animalista",
)

# Sin «salud» a secas, que era la palabra más golosa de todas: aparecía en una
# de cada dos notas y se llevaba el tema entero.
PALABRAS_SALUD = (
    "vacuna", "esteriliz", "castrac", "desparasit", "veterinari",
    "enfermedad", "sintoma", "senales de alerta", "diagnostic", "tratamiento",
    "garrapata", "pulga", "rabia", "moquillo", "parvovirus", "leishman",
    "cistitis", "infeccion", "cancer", "tumor", "hipertiroidismo", "toxic",
    "alimentacion", "nutricion", "dieta", "obesidad", "sobrepeso", "chequeo",
    "cirugia", "artrosis", "displasia", "microchip", "golpe de calor",
    "calor extremo", "higiene", "pelaje", "dental", "urgencia veterinaria",
)

# Solo vocabulario de conducta. La versión anterior incluía «estudio»,
# «científico», «revela», «señales», «experto» y «por qué», que no describen un
# tema sino la forma de escribir un artículo: con ellas, comportamiento se
# quedaba con seis de cada diez notas, incluidas las de cistitis y cáncer.
PALABRAS_COMPORTAMIENTO = (
    "comportamiento", "conducta", "etolog", "adiestra", "adiestrador",
    "educar", "psicolog", "cerebro", "emocion", "ansiedad", "estres", "miedo",
    "ladrido", "ladra", "muerde", "arana", "rascador", "juego", "juguete",
    "paseo", "socializ", "lenguaje corporal", "castig", "obedien", "habito",
    "rutina", "vinculo", "apego", "celos", "territorial", "marcaje",
    "ronrone", "maulla", "por que mi perro", "por que mi gato",
    "por que los perros", "por que los gatos",
)

# Estas se buscan solo en el TITULAR. Son señales fuertes de una historia
# concreta, y en el resumen aparecerían por arrastre de notas relacionadas.
PALABRAS_HISTORIAS = (
    "reencuentr", "heroe", "heroina", "milagro", "emotiv", "conmovedor",
    "viral", "celebr", "cumpleanos", "record", "premio", "homenaje",
    "sobrevivi", "salvo la vida", "regreso a casa", "volvio a casa",
    "espero", "fiel",
)

# --- geografía --------------------------------------------------------------

# Se arma desde el catálogo que ya usa el selector de ciudades, en vez de
# mantener una segunda lista a mano. Se cortan los municipios por departamento
# porque la detección es una expresión regular: con los 1.100 municipios del
# país sería enorme y sumaría falsos positivos por nombres cortos y comunes.
#
# Es una lista plana y no un mapa por departamento porque lo único que se hace
# con ella es etiquetar de dónde habla una nota. No hay filtro por departamento:
# el que existía venía del feed de la emergencia, donde tenía sentido acotar a
# las zonas golpeadas, y en una sección de adopciones y consejos no lo tiene.
MUNICIPIOS_POR_DEPARTAMENTO = 8

CIUDADES = tuple(
    dict.fromkeys(
        lugar
        for departamento, municipios in COUNTRIES["Colombia"].items()
        for lugar in (departamento, *municipios[:MUNICIPIOS_POR_DEPARTAMENTO])
    )
)


def _sin_tildes(texto: str) -> str:
    normalizado = unicodedata.normalize("NFKD", texto or "")
    return normalizado.encode("ascii", "ignore").decode("ascii").lower()


def _compilar(palabras: tuple[str, ...], *, exacto: bool = False) -> re.Pattern:
    """Compila una lista de términos en una sola expresión regular.

    Por defecto ancla solo el inicio de la palabra, para que «rescat» cubra
    «rescate», «rescatado» y «rescatistas».

    Con `exacto=True` ancla también el final, y ahí está la diferencia entre
    acertar y no: sin el límite de cierre, «Cali» coincide dentro de «calidad» y
    «Buga» dentro de «bugambilia». Se usa para nombres propios de lugar, donde
    la palabra completa es justamente lo que hay que encontrar.
    """
    alternativas = "|".join(re.escape(p) for p in palabras)
    cierre = r"\b" if exacto else ""
    return re.compile(rf"\b(?:{alternativas}){cierre}", re.IGNORECASE)


RE_ANIMALES = _compilar(PALABRAS_ANIMALES)
RE_ANGUSTIANTE = _compilar(PALABRAS_ANGUSTIANTES)
RE_EMERGENCIA = _compilar(PALABRAS_EMERGENCIA)
RE_ACTUALIDAD_AJENA = _compilar(PALABRAS_ACTUALIDAD_AJENA)
RE_ENGANOSA = _compilar(EXPRESIONES_ENGANOSAS)
RE_ADOPCION = _compilar(PALABRAS_ADOPCION)
RE_REFUGIOS = _compilar(PALABRAS_REFUGIOS)
RE_SALUD = _compilar(PALABRAS_SALUD)
RE_COMPORTAMIENTO = _compilar(PALABRAS_COMPORTAMIENTO)
RE_HISTORIAS = _compilar(PALABRAS_HISTORIAS)

_CIUDAD_RE = {ciudad: _compilar((_sin_tildes(ciudad),), exacto=True) for ciudad in CIUDADES}


def es_angustiante(texto_plano: str) -> bool:
    return bool(RE_ANGUSTIANTE.search(texto_plano) or RE_EMERGENCIA.search(texto_plano))


def clasificar_tema(titulo_plano: str, texto_plano: str) -> str:
    """Asigna uno de los temas de `NEWS_TOPICS`.

    El orden no es arbitrario. Adopción va primero porque es lo único que el
    lector puede accionar el mismo día. Las historias se miran enseguida y solo
    en el titular: «Reencuentro tras tres años en el albergue» es una historia,
    no una nota sobre albergues, y el orden inverso la clasificaría mal.

    Comportamiento va antes que salud por el formato con el que titulan los
    medios de mascotas: «Fulana, veterinaria: los perros dan vueltas antes de
    acostarse porque…» habla de conducta, pero nombra a una veterinaria en la
    primera palabra. Con salud primero, todo terminaba en salud.

    Lo que no encaja en nada cae en historias, que es el cajón honesto para una
    nota que solo cuenta algo.
    """
    if RE_ADOPCION.search(texto_plano):
        return "adopcion"
    if RE_HISTORIAS.search(titulo_plano):
        return "historias"
    if RE_REFUGIOS.search(texto_plano):
        return "refugios"
    if RE_COMPORTAMIENTO.search(texto_plano):
        return "comportamiento"
    if RE_SALUD.search(texto_plano):
        return "salud"
    return "historias"


def detectar_ciudades(texto: str) -> list[str]:
    plano = _sin_tildes(texto)
    return [ciudad for ciudad, patron in _CIUDAD_RE.items() if patron.search(plano)]


# Los blogs «minuto a minuto» publican entradas cuyo titular es solo la hora.
RE_TITULAR_FECHA = re.compile(
    r"^\s*(lunes|martes|miercoles|miércoles|jueves|viernes|sabado|sábado|domingo)?[\s,]*"
    r"\d{1,2}\s+de\s+\w+|^\s*\d{1,2}:\d{2}",
    re.IGNORECASE,
)


def es_titular_basura(titulo: str) -> bool:
    """Descarta titulares que no son noticias: horas sueltas, fechas, vacíos."""
    limpio = titulo.strip()
    if len(limpio) < 25:
        return True
    return bool(RE_TITULAR_FECHA.match(limpio))


def es_relevante(titulo_plano: str, texto_plano: str) -> bool:
    """Decide si una nota entra al feed. Tres condiciones, todas necesarias.

    1. El TITULAR nombra a un animal de compañía. Se exige en el titular y no en
       el resumen a propósito: mirando también el resumen entraban notas como
       «Familia de Medellín pide ayuda por la desaparición de una anciana», que
       mencionaba un perro de pasada. Si la nota trata de animales, lo dice en el
       titular; si solo los menciona, no es una nota de animales.
    2. No es una expresión que solo suena a animal (el Parque del Perro de Cali).
    3. No es angustiante ni habla de la emergencia. Esto sí se mira en todo el
       texto: para descartar basta con que aparezca en cualquier parte.
    """
    if not RE_ANIMALES.search(titulo_plano):
        return False
    if RE_ENGANOSA.search(texto_plano):
        return False
    return not es_angustiante(texto_plano)


# ------------------------------------------------------------------ parseo

@dataclass
class Entrada:
    external_id: str
    title: str
    summary: str | None
    url: str
    image_url: str | None
    source: str
    topic: str
    is_local: bool
    cities: str | None
    published_at: datetime


ETIQUETAS_HTML = re.compile(r"<[^>]+>")
ESPACIOS = re.compile(r"\s+")


def _limpiar(texto: str | None, maximo: int) -> str | None:
    if not texto:
        return None
    limpio = ESPACIOS.sub(" ", ETIQUETAS_HTML.sub("", texto)).strip()
    if not limpio:
        return None
    if len(limpio) <= maximo:
        return limpio
    # Se corta en la última palabra completa para no dejar sílabas sueltas.
    recorte = limpio[:maximo].rsplit(" ", 1)[0]
    return f"{recorte}…"


SOLO_ALFANUM = re.compile(r"[^a-z0-9 ]")


def clave_de_nota(titulo: str) -> str:
    """Identificador estable de una nota, derivado del titular.

    Se usa como `external_id`, que es la columna con índice único, y por eso
    deduplica en dos planos a la vez: dentro de una corrida y entre corridas.

    Hace falta porque el identificador del agregador NO es estable: la misma
    nota encontrada por «adopción de mascotas» y por «jornada de adopción perros
    gatos» llega con dos `guid` distintos, y aparecía dos veces en la pantalla.
    El titular sí es el mismo, y normalizado —sin tildes, sin signos, sin dobles
    espacios— aguanta las diferencias de puntuación entre una y otra.

    El riesgo es descartar dos notas distintas con el mismo titular exacto. Pasa
    poco, y cuando pasa suelen ser la misma noticia replicada.
    """
    plano = SOLO_ALFANUM.sub("", _sin_tildes(titulo))
    return ESPACIOS.sub(" ", plano).strip()[:380]


def _fecha(texto: str | None) -> datetime:
    if not texto:
        return utcnow()
    for parseador in (parsedate_to_datetime, datetime.fromisoformat):
        try:
            fecha = parseador(texto.strip())
            return fecha if fecha.tzinfo else fecha.replace(tzinfo=timezone.utc)
        except (TypeError, ValueError):
            continue
    return utcnow()


def _texto(item: ET.Element, *nombres: str) -> str | None:
    for nombre in nombres:
        valor = item.findtext(nombre)
        if valor and valor.strip():
            return valor.strip()
    return None


def es_dominio_colombiano(url: str | None) -> bool:
    """Decide por el dominio si un medio es colombiano.

    La regla del `.co` cubre sola casi todo lo institucional —alcaldías,
    gobernaciones, secretarías, que son quienes publican las jornadas— porque
    todas viven bajo `.gov.co`. Los medios grandes que se llaman `.com` van en
    la lista de al lado.
    """
    host = (urlparse(url or "").hostname or "").removeprefix("www.").lower()
    if not host:
        return False
    return host.endswith(".co") or host in DOMINIOS_COLOMBIANOS


def _medio_del_item(item: ET.Element) -> tuple[str | None, str | None]:
    """Devuelve (nombre del medio, url del medio) del elemento `<source>`."""
    nodo = item.find("source")
    if nodo is None:
        return None, None
    nombre = (nodo.text or "").strip() or None
    return nombre, nodo.get("url")


def _sin_sufijo_del_medio(titulo: str, medio: str | None) -> str:
    """Quita el « - El Tiempo» que Google Noticias añade a cada titular.

    El medio ya se muestra aparte en la tarjeta; dejarlo también al final del
    titular lo repite y le roba espacio al texto que sí importa.
    """
    if medio and titulo.endswith(f" - {medio}"):
        return titulo[: -(len(medio) + 3)].strip()
    return titulo


def _imagen(item: ET.Element) -> str | None:
    enclosure = item.find("enclosure")
    if enclosure is not None:
        url = enclosure.get("url")
        if url and str(enclosure.get("type", "")).startswith("image"):
            return url
    # media:content / media:thumbnail (namespace de Media RSS)
    for etiqueta in ("{http://search.yahoo.com/mrss/}content", "{http://search.yahoo.com/mrss/}thumbnail"):
        nodo = item.find(etiqueta)
        if nodo is not None and nodo.get("url"):
            return nodo.get("url")
    return None


def parsear_feed(xml: str, fuente: Fuente) -> list[Entrada]:
    """Convierte el XML de un feed en entradas ya clasificadas y filtradas."""
    try:
        raiz = ET.fromstring(xml)
    except ET.ParseError:
        return []

    canal = raiz.find("channel")
    items = canal.findall("item") if canal is not None else raiz.findall(".//item")

    limite = utcnow() - timedelta(days=DIAS_DE_VIGENCIA)
    entradas: list[Entrada] = []

    for item in items:
        titulo = _texto(item, "title")
        enlace = _texto(item, "link", "guid")
        if not titulo or not enlace:
            continue

        medio, url_medio = _medio_del_item(item)

        if fuente.agregador:
            # El agregador mezcla prensa de todo el continente. La procedencia
            # se decide por el dominio del medio, y lo que no es colombiano no
            # entra: es exactamente el material que sobraba antes. Para volver a
            # aceptarlo, basta con no descartar aquí y dejarlo a `is_local`.
            if not es_dominio_colombiano(url_medio):
                continue
            titulo = _sin_sufijo_del_medio(titulo, medio)
            nombre_fuente = medio or fuente.nombre
            # El `description` de Google Noticias es solo un enlace envuelto en
            # HTML: al limpiarlo queda el titular repetido. Mejor sin resumen.
            descripcion = None
            es_local = True
        else:
            nombre_fuente = fuente.nombre
            descripcion = _texto(
                item, "description", "{http://purl.org/rss/1.0/modules/content/}encoded"
            )
            es_local = not fuente.extranjero

        if es_titular_basura(titulo):
            continue

        # La clasificación mira titular + resumen: el titular solo se queda corto.
        titulo_plano = _sin_tildes(titulo)
        plano = _sin_tildes(f"{titulo} {descripcion or ''}")

        if not es_relevante(titulo_plano, plano):
            continue

        publicado = _fecha(_texto(item, "pubDate", "{http://purl.org/dc/elements/1.1/}date"))
        if publicado < limite:
            continue

        tema = clasificar_tema(titulo_plano, plano)

        if not es_local:
            # La prensa de fuera solo entra por lo que sirve igual en cualquier
            # sitio y en cualquier momento. Una adopción o un albergue suyo son
            # información de su ciudad, no de la nuestra.
            if tema not in TEMAS_ATEMPORALES:
                continue
            if RE_ACTUALIDAD_AJENA.search(plano):
                continue

        # Solo tiene sentido buscar ciudades colombianas en material colombiano:
        # en uno español, «Sevilla» o «Córdoba» pondrían una etiqueta falsa.
        ciudades = detectar_ciudades(f"{titulo} {descripcion or ''}") if es_local else []

        titulo_limpio = _limpiar(titulo, 290) or titulo[:290]

        entradas.append(
            Entrada(
                external_id=clave_de_nota(titulo_limpio),
                title=titulo_limpio,
                summary=_limpiar(descripcion, 480),
                url=enlace[:600],
                image_url=(_imagen(item) or "")[:600] or None,
                source=(nombre_fuente or fuente.nombre)[:80],
                topic=tema,
                is_local=es_local,
                cities=", ".join(ciudades)[:300] or None,
                published_at=publicado,
            )
        )

    return entradas


# ------------------------------------------------------------------ ingesta

async def descargar(url: str, cliente: httpx.AsyncClient) -> str | None:
    try:
        respuesta = await cliente.get(url)
        if respuesta.status_code >= 400:
            return None
        return respuesta.text
    except httpx.HTTPError:
        return None


def purgar_antiguas(db: Session) -> int:
    """Borra lo vencido y lo que quedó con un tema que ya no existe.

    Lo segundo importa una sola vez, pero importa: las notas que quedaron del
    feed anterior tienen guardado «tragedia» o «esperanza» en la columna, y sin
    esto seguirían apareciendo —sin etiqueta y fuera de tema— hasta cumplir la
    ventana de vigencia. Se ejecuta en cada sincronización, así que se limpia
    solo en el primer cron después del cambio.
    """
    limite = utcnow() - timedelta(days=DIAS_DE_VIGENCIA)
    borradas = (
        db.query(NewsItem)
        .filter(or_(NewsItem.published_at < limite, NewsItem.topic.notin_(NEWS_TOPICS)))
        .delete(synchronize_session=False)
    )

    # Filas guardadas cuando el identificador era el `guid` del medio. Si no se
    # borran, conviven con la misma nota bajo su clave nueva y la pantalla la
    # muestra dos veces durante mes y medio. Se reconocen porque su
    # `external_id` no es el que hoy les correspondería.
    #
    # Recorre la tabla entera, y puede hacerlo porque nunca pasa de unos cientos
    # de filas: la ventana de vigencia la mantiene pequeña. Después del primer
    # cron esto no borra nada más.
    for fila in db.scalars(select(NewsItem)).all():
        if fila.external_id != clave_de_nota(fila.title):
            db.delete(fila)
            borradas += 1

    db.commit()
    return int(borradas or 0)


async def sincronizar(db: Session) -> dict:
    """Descarga todos los feeds, guarda lo nuevo y borra lo vencido."""
    cabeceras = {
        # Algunos medios rechazan peticiones sin user-agent.
        "user-agent": "PatitasConectadasBot/1.0 (+https://patitas-conectadas.vercel.app)",
        "accept": "application/rss+xml, application/xml, text/xml;q=0.9, */*;q=0.8",
    }

    entradas: list[Entrada] = []
    fuentes_ok = 0
    fuentes_fallidas: list[str] = []

    # En paralelo y no en fila: con las consultas al agregador son más de veinte
    # peticiones, y una detrás de otra se pasaban del tiempo máximo de la función
    # en Vercel. El semáforo evita abrir las veintitantas de golpe.
    semaforo = asyncio.Semaphore(8)

    async def traer(fuente: Fuente, cliente: httpx.AsyncClient):
        async with semaforo:
            return fuente, await descargar(fuente.url, cliente)

    async with httpx.AsyncClient(timeout=20, headers=cabeceras, follow_redirects=True) as cliente:
        for fuente, xml in await asyncio.gather(*(traer(f, cliente) for f in FEEDS)):
            if xml is None:
                fuentes_fallidas.append(fuente.nombre)
                continue
            fuentes_ok += 1
            entradas.extend(parsear_feed(xml, fuente))

    # Un mismo hecho aparece en varias consultas y en varios feeds. Cuando llega
    # por dos caminos gana la versión con imagen: el agregador no publica
    # ninguna y el feed propio del medio sí, y la tarjeta se ve mucho mejor.
    unicas: dict[str, Entrada] = {}
    for entrada in entradas:
        previa = unicas.get(entrada.external_id)
        if previa is None or (not previa.image_url and entrada.image_url):
            unicas[entrada.external_id] = entrada

    purgadas = purgar_antiguas(db)

    if not unicas:
        return {
            "nuevas": 0,
            "revisadas": 0,
            "purgadas": purgadas,
            "fuentes_ok": fuentes_ok,
            "fuentes_fallidas": fuentes_fallidas,
        }

    existentes = set(
        db.scalars(
            select(NewsItem.external_id).where(NewsItem.external_id.in_(list(unicas)))
        ).all()
    )

    nuevas = 0
    for external_id, entrada in unicas.items():
        if external_id in existentes:
            continue
        db.add(
            NewsItem(
                external_id=entrada.external_id,
                title=entrada.title,
                summary=entrada.summary,
                url=entrada.url,
                image_url=entrada.image_url,
                source=entrada.source,
                topic=entrada.topic,
                is_local=entrada.is_local,
                cities=entrada.cities,
                published_at=entrada.published_at,
            )
        )
        nuevas += 1

    db.commit()
    return {
        "nuevas": nuevas,
        "revisadas": len(unicas),
        "purgadas": purgadas,
        "fuentes_ok": fuentes_ok,
        "fuentes_fallidas": fuentes_fallidas,
    }


# ----------------------------------------------------------------- lectura

def _mezclar_por_tema(items: list[NewsItem], limite: int) -> list[NewsItem]:
    """Arma la primera página alternando temas, en vez de apilar el más frecuente.

    Sin esto la portada sería casi entera de comportamiento: los feeds dedicados
    publican mucho más consejo que jornada de adopción, y el lector se llevaría
    la impresión de que aquí no hay nada más. Se reparte por turnos —una de cada
    tema hasta llenar— y dentro de cada tema va primero lo de Colombia y lo más
    reciente. Cuando un tema se queda sin notas, los demás siguen repartiendo.
    """
    def orden(item: NewsItem):
        return (not item.is_local, -item.published_at.timestamp())

    por_tema: dict[str, list[NewsItem]] = {tema: [] for tema in NEWS_TOPICS}
    for item in sorted(items, key=orden):
        por_tema.setdefault(item.topic, []).append(item)

    seleccion: list[NewsItem] = []
    while len(seleccion) < limite:
        ronda = False
        for tema in NEWS_TOPICS:
            cola = por_tema.get(tema)
            if not cola:
                continue
            seleccion.append(cola.pop(0))
            ronda = True
            if len(seleccion) >= limite:
                break
        if not ronda:
            break

    return sorted(seleccion, key=lambda i: -i.published_at.timestamp())


def temas_reforzados(db: Session) -> set[str]:
    """Temas cuyo material colombiano no alcanza y admiten refuerzo de fuera.

    Es lo que hace que la mezcla se regule sola. Comportamiento vive hoy de la
    prensa española porque aquí casi no se publica etología; el día que un medio
    colombiano empiece a hacerlo y pase de `MINIMO_LOCAL_POR_TEMA`, las notas de
    fuera dejan de aparecer sin que nadie toque nada.

    Se cuenta solo lo local a propósito: contar el total haría que el refuerzo se
    apagara por culpa del propio refuerzo, y el tema volvería a quedarse corto.
    """
    filas = db.execute(
        select(NewsItem.topic, func.count())
        .where(NewsItem.is_published.is_(True), NewsItem.is_local.is_(True))
        .group_by(NewsItem.topic)
    ).all()
    locales = dict(filas)
    return {t for t in NEWS_TOPICS if locales.get(t, 0) < MINIMO_LOCAL_POR_TEMA}


def _filtrar(topic: str | None, only_local: bool, reforzados: set[str]):
    consulta = select(NewsItem).where(NewsItem.is_published.is_(True))
    if topic:
        consulta = consulta.where(NewsItem.topic == topic)
    if only_local:
        consulta = consulta.where(NewsItem.is_local.is_(True))
    else:
        # Lo colombiano siempre; lo de fuera, solo en los temas que lo necesitan.
        consulta = consulta.where(
            or_(NewsItem.is_local.is_(True), NewsItem.topic.in_(reforzados))
        )
    return consulta


def listar(
    db: Session,
    *,
    topic: str | None = None,
    only_local: bool = False,
    page: int = 1,
    page_size: int = 6,
) -> dict:
    """Devuelve una página de noticias más el total, para poder paginar.

    La primera página se mezcla por tema para que se vea de entrada que la
    sección cubre varias cosas. A partir de la segunda se ordena por fecha sin
    más: quien pide «ver más» ya decidió seguir leyendo, y a esas alturas
    reordenar solo confundiría sobre qué es lo reciente.
    """
    consulta = _filtrar(topic, only_local, temas_reforzados(db))

    total = int(
        db.scalar(select(func.count()).select_from(consulta.subquery())) or 0
    )

    if page <= 1 and not topic:
        # Se traen de más para que la mezcla tenga de dónde escoger.
        candidatas = list(
            db.scalars(
                consulta.order_by(NewsItem.published_at.desc()).limit(max(page_size * 6, 48))
            ).all()
        )
        items = _mezclar_por_tema(candidatas, page_size)
    else:
        # Dentro de un tema, lo colombiano primero y después lo de refuerzo. Sin
        # esto, un medio extranjero que publica a diario enterraría las notas de
        # una alcaldía que publica una vez por semana.
        items = list(
            db.scalars(
                consulta.order_by(NewsItem.is_local.desc(), NewsItem.published_at.desc())
                .offset((page - 1) * page_size)
                .limit(page_size)
            ).all()
        )

    return {
        "items": items,
        "total": total,
        "page": page,
        "page_size": page_size,
        "pages": max(1, math.ceil(total / page_size)) if total else 1,
    }
