# 🐾 Patitas Conectadas

Plataforma web **responsive y Mobile First** para publicar y buscar **mascotas perdidas, encontradas y en adopción**.

No es una app nativa: es una aplicación web moderna que funciona en cualquier navegador y se adapta a celular, tablet y computador. Está pensada para que **publicar una mascota desde el celular tome menos de dos minutos y sin obligar a crear una cuenta**.

- **Frontend:** Vue 3 + Vite + Vue Router + Pinia (CSS propio, sin frameworks de UI)
- **Backend:** Python + FastAPI + SQLAlchemy 2.0
- **Base de datos:** Neon Postgres (SQLite en desarrollo, sin configurar nada)
- **Fotos:** Vercel Blob (carpeta local en desarrollo)
- **Despliegue:** Vercel, dentro del plan gratuito

---

## 1. Estructura del proyecto

```
patitas-conectadas/
├── api/index.py              # Entrada de la función serverless (ASGI) en Vercel
├── backend/
│   ├── app/
│   │   ├── main.py           # Aplicación FastAPI
│   │   ├── config.py         # Variables de entorno
│   │   ├── db.py             # Motor y sesión de SQLAlchemy
│   │   ├── models.py         # Usuario, Publicación, Foto, Reporte, Noticia
│   │   ├── schemas.py        # Validación de entrada/salida
│   │   ├── security.py       # Contraseñas, JWT y enlaces de administración
│   │   ├── storage.py        # Subida de fotos (Vercel Blob / disco local)
│   │   ├── serializers.py    # Respuestas públicas (privacidad de la dirección)
│   │   ├── seed.py           # Datos iniciales
│   │   ├── data/geo.py       # Países, departamentos y ciudades
│   │   └── routers/          # auth, posts, uploads, reports, geo, news, admin, meta
│   └── uploads/              # Fotos en desarrollo (ignorada por git)
├── frontend/
│   └── src/
│       ├── views/            # Inicio, Buscar, Publicar, Detalle, Admin…
│       ├── components/       # PetCard, PhotoUploader, CitySelect, ShareButtons…
│       ├── stores/           # Pinia: sesión y estado de interfaz
│       ├── lib/              # Fechas, etiquetas, compresión de imágenes
│       └── styles/main.css   # Sistema de diseño Mobile First
├── requirements.txt          # Dependencias de la función Python
├── vercel.json               # Build, rewrites y crawlers
└── .env.example
```

---

## 2. Ejecutar en local

Necesitas **Python 3.12** y **Node 20+**.

### Backend

```bash
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -r requirements-dev.txt

# Datos iniciales: tablas + artículos de ayuda + ejemplos + administrador
.venv\Scripts\python.exe -m backend.app.seed --demo --admin tu@correo.com --password TuClave123

# API en http://127.0.0.1:8000  (documentación en /api/docs)
.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

Sin `DATABASE_URL` se usa SQLite en `backend/patitas.db`, y sin `BLOB_READ_WRITE_TOKEN` las fotos se guardan en `backend/uploads/`. No necesitas ninguna cuenta para desarrollar.

### Frontend

```bash
cd frontend
npm install
npm run dev        # http://localhost:5173 (proxy de /api hacia el puerto 8000)
```

---

## 3. Desplegar en Vercel (plan gratuito)

> 📘 **Guía paso a paso completa: [`DESPLIEGUE.md`](DESPLIEGUE.md)** — incluye GitHub, Neon, Blob, variables, seed, verificación y solución de problemas. Lo de abajo es el resumen.

### 3.1 Base de datos — Neon Postgres

1. En el panel de Vercel: **Storage → Create Database → Neon (Postgres)** y conéctala al proyecto.
2. Vercel inyecta `DATABASE_URL` automáticamente. Usa la cadena **pooled**; el backend la adapta al driver `psycopg` sin que hagas nada.
3. Las tablas se crean solas en el primer arranque (`AUTO_CREATE_TABLES=1`). Para crear el administrador y los artículos de ayuda, ejecuta el seed desde tu equipo apuntando a Neon (PowerShell, desde la raíz del proyecto):

   ```powershell
   $env:DATABASE_URL = "postgresql://usuario:clave@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require"
   .\.venv\Scripts\python.exe -m backend.app.seed --admin tu@correo.com --password TuClave123
   Remove-Item Env:\DATABASE_URL   # vuelve a SQLite para el desarrollo local
   ```

### 3.2 Fotos — Vercel Blob

1. **Storage → Create → Blob**, conéctalo al proyecto.
2. Vercel inyecta `BLOB_READ_WRITE_TOKEN`. El plan gratuito incluye 1 GB, suficiente para miles de fotos porque el navegador las comprime a ~200–400 KB antes de subirlas.

### 3.3 Variables de entorno

En **Settings → Environment Variables** (ver `.env.example` para la lista completa):

| Variable | Obligatoria | Para qué sirve |
|---|---|---|
| `JWT_SECRET` | **Sí** | Firma las sesiones. Genera uno largo y aleatorio. |
| `SITE_URL` | Recomendada | URL final del sitio (enlaces compartidos y OAuth). Si no la defines se usa el dominio de Vercel. |
| `ADMIN_EMAILS` | Recomendada | Correos que reciben rol de administrador al registrarse. |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | Opcional | Habilita «Continuar con Google». |
| `TURNSTILE_SECRET` / `TURNSTILE_SITE_KEY` | Opcional | Activa captcha al publicar y al reportar. |

### 3.4 Google OAuth

En Google Cloud Console → **Credenciales → ID de cliente OAuth → Aplicación web**:

- Orígenes autorizados: `https://tu-dominio.vercel.app`
- URI de redirección: `https://tu-dominio.vercel.app/api/auth/google/callback`

Si las variables no están definidas, el botón de Google simplemente no aparece y el acceso por correo sigue funcionando.

### 3.5 Desplegar

```bash
git push          # con el repositorio conectado a Vercel
# o
npx vercel --prod
```

`vercel.json` ya define: build del frontend, la función Python, el enrutado de `/api/*` y el reenvío de la SPA.

---

## 4. Decisiones que vale la pena conocer

### Publicar sin cuenta

Un usuario invitado publica y recibe un **enlace privado** (`/gestionar/<token>`). El token se guarda con hash en la base de datos: quien tenga la URL pública **no** puede editar la publicación. Si más adelante crea una cuenta, la publicación se vincula con un clic.

### Privacidad de la ubicación

La dirección exacta es opcional y **nunca** se devuelve en la API pública: solo la ve quien administra la publicación. En público se muestran ciudad, barrio o sector.

### Compartir en WhatsApp y redes

Una SPA no genera vista previa al compartir un enlace. Por eso `vercel.json` detecta los rastreadores (WhatsApp, Facebook, Twitter, Google…) por `User-Agent` y les entrega una página con los metadatos Open Graph correctos (foto principal, nombre, tipo y ciudad). Las personas reciben la SPA normal, sin redirecciones ni parpadeos.

### Fotos

El navegador redimensiona a 1600 px y comprime a JPEG antes de subir. La primera foto se marca como principal automáticamente y se puede cambiar con **⭐ Establecer como principal**, reordenar o eliminar (siempre queda al menos una).

### Moderación

Cualquier visitante puede reportar. A los **3 reportes** la publicación se oculta automáticamente y queda pendiente de revisión en el panel. Además hay honeypot invisible, límite de publicaciones por IP y captcha opcional.

### Noticias

Un cron diario lee feeds RSS (`backend/app/news_feed.py`) y guarda **solo titular, resumen corto y enlace**: el cuerpo de la nota es del medio que la escribió. Cada nota se clasifica en adopción, albergues, salud, comportamiento o buenas historias, y la primera página alterna temas para que no se vea un muro de lo mismo.

Las fuentes son de dos clases. Unas son feeds de medios; las otras son **consultas temáticas a Google Noticias acotadas a Colombia**, y son las que sostienen la sección. La razón: los medios colombianos casi no tienen sección de mascotas, pero publican muchísimo sobre jornadas de esterilización, vacunación antirrábica y adopción — en la sección de ciudad, en la de salud, o directamente desde una alcaldía. Buscar por tema en toda la prensa las encuentra; suscribirse a secciones de mascotas, no.

De esas consultas solo entra lo colombiano, decidido por el dominio del medio (`.co` cubre todas las alcaldías; los medios que se llaman `.com` están listados en `DOMINIOS_COLOMBIANOS`).

**Refuerzo por tema.** La prensa colombiana casi no publica etología ni comportamiento animal, así que ese tema se quedaba en cinco notas. Para eso hay fuentes extranjeras, con dos condiciones: solo entran por los temas de `TEMAS_ATEMPORALES` —comportamiento y salud, lo que vale igual aquí que en Madrid y hoy que en tres meses— y nunca por adopción, albergues o historias, que son información de la ciudad de uno. Además se descarta su actualidad municipal (`PALABRAS_ACTUALIDAD_AJENA`): el consejo sirve, el pleno del ayuntamiento de Tacoronte no.

Y solo se **muestran** cuando hacen falta: `temas_reforzados` cuenta las notas colombianas de cada tema, y las de fuera aparecen únicamente en los que no llegan a `MINIMO_LOCAL_POR_TEMA`. Dentro de un tema reforzado, lo colombiano va primero. El día que un medio local empiece a publicar comportamiento, las de fuera desaparecen solas sin tocar nada.

El `external_id` es el titular normalizado y no el `guid` del feed, porque el del agregador no es estable: la misma nota encontrada por dos consultas llega con dos identificadores distintos y salía duplicada.

El filtro descarta a propósito dos cosas: lo angustiante (maltrato, muerte, envenenamientos) y lo relacionado con la emergencia, que tiene su propia sección. Esta pantalla la abre alguien que acaba de publicar que perdió a su perro; el criterio es no confirmarle su peor miedo. Las listas de palabras están al inicio del módulo y cambiarlas cambia el tono de la sección.

### Estados

| Tipo | Estado inicial | Estados siguientes |
|---|---|---|
| 🔴 Perdida | Perdida | 🟢 Reunida con su familia · ⚫ Caso cerrado |
| 🟢 Encontrada | Encontrada — buscando a su familia | 🏠 Entregada a su familia · ⚫ Caso cerrado |
| 💙 Adopción | Disponible para adopción | 🏠 Adoptada · ⚫ Caso cerrado |

Las publicaciones cerradas no se borran: quedan con un mensaje de buenas noticias.

---

## 5. API

Documentación interactiva en `/api/docs`. Resumen:

| Método | Ruta | Descripción |
|---|---|---|
| `GET` | `/api/config` | Catálogos para los formularios |
| `POST` | `/api/auth/register` · `/api/auth/login` | Cuenta con correo |
| `GET` | `/api/auth/google/start` · `/callback` | Acceso con Google |
| `POST` | `/api/auth/claim/{token}` | Vincular publicación de invitado |
| `GET` | `/api/posts` | Búsqueda con filtros y paginación |
| `POST` | `/api/posts` | Crear publicación (invitado o registrado) |
| `GET` | `/api/posts/{slug}` | Detalle público |
| `PATCH` | `/api/posts/{id}` | Editar (sesión o `X-Manage-Token`) |
| `POST` | `/api/posts/{id}/status` | Cambiar estado |
| `POST` | `/api/posts/{id}/photos` … | Agregar, ordenar, marcar principal, eliminar |
| `GET` | `/api/manage/{token}` | Acceso del invitado a su publicación |
| `POST` | `/api/uploads` | Subir una foto |
| `POST` | `/api/posts/{id}/report` | Reportar |
| `GET` | `/api/geo/search?q=` | Buscador de ciudades |
| `GET` | `/api/articles` | Guías y recursos propios |
| `GET` | `/api/news` · `/topics` · `/regions` | Noticias de medios sobre perros y gatos |
| `*` | `/api/admin/*` | Panel administrativo |

---

## 6. Qué no incluye la V1

Por decisión de alcance no se implementan (pero la arquitectura los permite después): app nativa, reconocimiento facial de mascotas, coincidencias con IA, notificaciones, chat interno, mapas avanzados, marketplace y pagos.
