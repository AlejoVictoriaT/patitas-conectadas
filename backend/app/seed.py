"""Datos iniciales.

Uso:
    python -m backend.app.seed                      # crea tablas + contenido de ayuda
    python -m backend.app.seed --demo               # añade publicaciones de ejemplo
    python -m backend.app.seed --admin correo@x.com --password Secreta123
"""

from __future__ import annotations

import argparse
from datetime import timedelta
from urllib.parse import quote

from sqlalchemy import func, select

from .db import SessionLocal, init_db
from .models import (
    INITIAL_STATUS,
    TYPE_ADOPTION,
    TYPE_FOUND,
    TYPE_LOST,
    Article,
    Photo,
    Post,
    User,
    utcnow,
)
from .security import hash_password
from .utils import generate_public_id, slugify

PALETA = {
    TYPE_LOST: ("#F04438", "#FEE4E2"),
    TYPE_FOUND: ("#12B76A", "#D1FADF"),
    TYPE_ADOPTION: ("#2E90FA", "#D1E9FF"),
}


def placeholder_photo(texto: str, tipo: str) -> str:
    """SVG en línea para los datos de demostración (no requiere red ni almacenamiento)."""
    color, fondo = PALETA.get(tipo, ("#7A5AF8", "#ECE9FE"))
    svg = (
        "<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 600 600'>"
        f"<rect width='600' height='600' fill='{fondo}'/>"
        f"<circle cx='300' cy='250' r='120' fill='{color}' opacity='.25'/>"
        f"<text x='300' y='285' font-size='120' text-anchor='middle'>&#128054;</text>"
        f"<text x='300' y='430' font-size='42' font-family='sans-serif' text-anchor='middle' fill='{color}'>"
        f"{texto}</text></svg>"
    )
    return "data:image/svg+xml;utf8," + quote(svg)


ARTICULOS = [
    {
        "title": "¿Qué hacer en las primeras 24 horas si perdiste a tu mascota?",
        "category": "consejo",
        "excerpt": "Las primeras horas son decisivas. Estos pasos aumentan mucho las probabilidades de reencuentro.",
        "content": (
            "1. Recorre la zona llamando a tu mascota con voz tranquila; el miedo hace que se escondan cerca.\n\n"
            "2. Publica de inmediato con una foto clara, la ciudad y el barrio donde se perdió.\n\n"
            "3. Comparte el enlace por WhatsApp en los grupos de tu barrio, conjunto o edificio.\n\n"
            "4. Pregunta en tiendas, veterinarias, panaderías y a las personas que trabajan en la calle: "
            "suelen ver todo lo que pasa en el sector.\n\n"
            "5. Deja en la puerta de tu casa algo con tu olor o su cobija: muchos animales regresan solos.\n\n"
            "6. Revisa los albergues y las publicaciones de 'mascota encontrada' de tu ciudad todos los días."
        ),
    },
    {
        "title": "Encontraste una mascota: guía rápida para ayudarla",
        "category": "consejo",
        "excerpt": "Antes de llevarla a casa, revisa estos puntos para encontrar a su familia más rápido.",
        "content": (
            "Revisa si tiene collar, placa o algún distintivo, y toma una foto clara de frente.\n\n"
            "Lleva al animal a una veterinaria para verificar si tiene microchip; en muchos lugares es gratuito.\n\n"
            "Publica en la plataforma como 'Mascota encontrada' indicando el sector donde la viste, "
            "pero guarda un detalle que solo su familia conocería: sirve para confirmar quién es el dueño real.\n\n"
            "No entregues la mascota sin verificar fotografías previas o documentos veterinarios."
        ),
    },
    {
        "title": "Cómo tomar una buena foto para tu publicación",
        "category": "consejo",
        "excerpt": "Una foto clara multiplica las posibilidades de que alguien reconozca a la mascota.",
        "content": (
            "Usa luz natural y toma la foto a la altura del animal.\n\n"
            "Que se vea el cuerpo completo y, si es posible, una segunda foto de la cara.\n\n"
            "Incluye una foto de las señales particulares: manchas, cicatrices, collar o placa.\n\n"
            "Evita filtros: los colores reales ayudan a identificarla."
        ),
    },
    {
        "title": "Esterilización: por qué es la mejor forma de prevenir el abandono",
        "category": "esterilizacion",
        "excerpt": "Muchas alcaldías realizan jornadas gratuitas durante todo el año.",
        "content": (
            "La esterilización previene camadas no deseadas, reduce el abandono y mejora la salud del animal.\n\n"
            "Consulta la Secretaría de Salud o de Ambiente de tu municipio: las jornadas gratuitas se anuncian "
            "por barrios y suelen requerir inscripción previa.\n\n"
            "Después de la cirugía, mantén el reposo indicado y revisa la herida a diario."
        ),
    },
    {
        "title": "Vacunación antirrábica: calendario y recomendaciones",
        "category": "vacunacion",
        "excerpt": "La vacuna antirrábica es gratuita en las jornadas oficiales de la mayoría de municipios.",
        "content": (
            "Perros y gatos deben recibir la vacuna antirrábica desde los tres meses de edad y luego cada año.\n\n"
            "Lleva el carné de vacunación a cada jornada.\n\n"
            "Si tu mascota está enferma o preñada, consulta con un veterinario antes de vacunarla."
        ),
    },
    {
        "title": "Ser hogar de paso: cómo funciona y qué se necesita",
        "category": "hogar_de_paso",
        "excerpt": "Un hogar temporal salva vidas mientras la mascota encuentra una familia definitiva.",
        "content": (
            "Un hogar de paso recibe temporalmente a un animal rescatado mientras se recupera o encuentra adopción.\n\n"
            "Normalmente la fundación cubre gastos veterinarios y el hogar aporta cuidado, alimentación y paseos.\n\n"
            "Necesitas un espacio seguro, tiempo para el acompañamiento y acuerdo de todas las personas de la casa."
        ),
    },
    {
        "title": "Adoptar con responsabilidad: preguntas antes de decidir",
        "category": "bienestar_animal",
        "excerpt": "Adoptar es un compromiso de 10 a 20 años. Estas preguntas ayudan a tomar una buena decisión.",
        "content": (
            "¿Cuánto tiempo pasa sola la casa durante el día?\n\n"
            "¿El presupuesto mensual alcanza para alimento, vacunas y una urgencia veterinaria?\n\n"
            "¿El tamaño y la energía del animal encajan con tu vivienda y tu rutina?\n\n"
            "¿Toda la familia está de acuerdo?\n\n"
            "Si la respuesta a alguna es dudosa, ser hogar de paso o padrino puede ser una gran alternativa."
        ),
    },
    {
        "title": "Directorio de albergues y fundaciones",
        "category": "fundacion",
        "excerpt": "Organizaciones que reciben reportes de animales en situación de calle.",
        "content": (
            "Este directorio se irá ampliando por ciudad. Si administras una fundación, un albergue o un "
            "hogar de paso y quieres aparecer aquí, escríbenos desde la sección de contacto.\n\n"
            "Antes de llevar un animal a un albergue, confirma disponibilidad: la mayoría trabaja al límite "
            "de su capacidad y necesita coordinación previa."
        ),
    },
]

DEMO_POSTS = [
    {
        "type": TYPE_LOST,
        "species": "perro",
        "pet_name": "Max",
        "breed": "Criollo",
        "sex": "macho",
        "color": "Café con blanco",
        "size": "mediano",
        "has_collar": True,
        "description": "Se perdió cerca del parque Caldas. Lleva collar azul y responde al nombre de Max. Es muy asustadizo con las motos.",
        "city": "Manizales",
        "region": "Caldas",
        "neighborhood": "Palermo",
        "days_ago": 2,
        "whatsapp": "3101234567",
    },
    {
        "type": TYPE_FOUND,
        "species": "gato",
        "pet_name": None,
        "breed": "Mestizo",
        "sex": "hembra",
        "color": "Gris atigrado",
        "size": "pequeno",
        "description": "Fue encontrada cerca de la iglesia del barrio. Es tranquila y parece estar acostumbrada a las personas. Está en un hogar temporal mientras aparece su familia.",
        "city": "Manizales",
        "region": "Caldas",
        "neighborhood": "La Enea",
        "days_ago": 1,
        "whatsapp": "3157654321",
    },
    {
        "type": TYPE_ADOPTION,
        "species": "perro",
        "pet_name": "Luna",
        "breed": "Labrador mestiza",
        "sex": "hembra",
        "color": "Negra",
        "size": "grande",
        "description": "Es cariñosa, juguetona y busca una familia responsable. Está esterilizada, desparasitada y con vacunas al día.",
        "city": "Medellín",
        "region": "Antioquia",
        "neighborhood": "Laureles",
        "days_ago": 5,
        "whatsapp": "3009876543",
    },
    {
        "type": TYPE_LOST,
        "species": "gato",
        "pet_name": "Simón",
        "breed": "Siamés",
        "sex": "macho",
        "color": "Beige con café",
        "size": "pequeno",
        "has_tag": True,
        "description": "Salió por la ventana el fin de semana. Tiene placa con número de teléfono y una mancha oscura en la pata trasera derecha.",
        "city": "Bogotá",
        "region": "Bogotá D.C.",
        "neighborhood": "Chapinero",
        "days_ago": 4,
        "whatsapp": "3204455667",
    },
    {
        "type": TYPE_ADOPTION,
        "species": "gato",
        "pet_name": "Nina",
        "breed": "Criolla",
        "sex": "hembra",
        "color": "Blanco y negro",
        "size": "pequeno",
        "description": "Rescatada de la calle hace tres meses. Ya está socializada, usa arenera y convive bien con otros gatos.",
        "city": "Cali",
        "region": "Valle del Cauca",
        "neighborhood": "San Fernando",
        "days_ago": 9,
        "whatsapp": "3183322110",
    },
    {
        "type": TYPE_FOUND,
        "species": "perro",
        "pet_name": None,
        "breed": "Pastor mestizo",
        "sex": "macho",
        "color": "Negro con fuego",
        "size": "grande",
        "description": "Apareció en la portería del conjunto, muy flaco y con hambre. Está bien cuidado mientras aparece su familia.",
        "city": "Pereira",
        "region": "Risaralda",
        "neighborhood": "Cuba",
        "days_ago": 3,
        "whatsapp": "3115566778",
    },
]


def seed_articles(db) -> int:
    creados = 0
    for data in ARTICULOS:
        slug = slugify(data["title"], max_length=120)
        if db.scalar(select(func.count()).select_from(Article).where(Article.slug == slug)):
            continue
        db.add(Article(slug=slug, **data))
        creados += 1
    db.commit()
    return creados


def seed_demo_posts(db) -> int:
    creados = 0
    for data in DEMO_POSTS:
        nombre = data.get("pet_name") or f"{data['species']}-{data['city']}"
        if db.scalar(
            select(func.count())
            .select_from(Post)
            .where(Post.pet_name == data.get("pet_name"), Post.city == data["city"], Post.type == data["type"])
        ):
            continue

        public_id = generate_public_id()
        etiqueta = data.get("pet_name") or ("Encontrado" if data["type"] == TYPE_FOUND else "En adopción")
        post = Post(
            public_id=public_id,
            slug=f"{slugify(nombre)}-{public_id}",
            type=data["type"],
            status=INITIAL_STATUS[data["type"]],
            species=data["species"],
            pet_name=data.get("pet_name"),
            breed=data.get("breed"),
            sex=data.get("sex"),
            color=data.get("color"),
            size=data.get("size"),
            has_collar=data.get("has_collar"),
            has_tag=data.get("has_tag"),
            description=data["description"],
            country="Colombia",
            region=data["region"],
            city=data["city"],
            neighborhood=data.get("neighborhood"),
            event_date=(utcnow() - timedelta(days=data["days_ago"])).date(),
            created_at=utcnow() - timedelta(days=data["days_ago"]),
            contact_name="Equipo Patitas",
            contact_whatsapp=f"57{data['whatsapp']}",
        )
        post.photos.append(Photo(url=placeholder_photo(etiqueta, data["type"]), position=0, is_primary=True))
        db.add(post)
        creados += 1
    db.commit()
    return creados


def create_admin(db, email: str, password: str, name: str = "Administrador") -> str:
    user = db.scalar(select(User).where(func.lower(User.email) == email.lower()))
    if user:
        user.is_admin = True
        if password:
            user.password_hash = hash_password(password)
        db.commit()
        return f"Usuario existente actualizado como administrador: {email}"

    db.add(
        User(
            name=name,
            email=email.lower(),
            password_hash=hash_password(password),
            auth_provider="email",
            is_admin=True,
        )
    )
    db.commit()
    return f"Administrador creado: {email}"


def main() -> None:
    parser = argparse.ArgumentParser(description="Datos iniciales de Patitas Conectadas")
    parser.add_argument("--demo", action="store_true", help="Crear publicaciones de ejemplo")
    parser.add_argument("--admin", help="Correo del administrador a crear/promover")
    parser.add_argument("--password", help="Contraseña del administrador")
    args = parser.parse_args()

    init_db()
    print("Tablas verificadas.")

    with SessionLocal() as db:
        print(f"Artículos creados: {seed_articles(db)}")
        if args.demo:
            print(f"Publicaciones de ejemplo creadas: {seed_demo_posts(db)}")
        if args.admin:
            if not args.password:
                parser.error("--admin requiere --password")
            print(create_admin(db, args.admin, args.password))


if __name__ == "__main__":
    main()
