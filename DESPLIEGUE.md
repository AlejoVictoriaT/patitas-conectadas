# 🚀 Desplegar Patitas Conectadas en Vercel

Guía completa, de principio a fin, usando el **plan gratuito** de Vercel.

Tiempo aproximado: 20–30 minutos la primera vez.

**Antes de empezar necesitas:**

- Una cuenta en [github.com](https://github.com) (gratis)
- Una cuenta en [vercel.com](https://vercel.com) (gratis, puedes entrar con GitHub)
- El proyecto funcionando en local (ya lo tienes)

---

## Paso 1 — Subir el código a GitHub

Todo el proyecto está en tu equipo pero aún no en GitHub. Desde la raíz del proyecto:

```powershell
cd C:\Users\USUARIO\Documents\patitas-conectadas
git add .
git commit -m "Plataforma de mascotas perdidas, encontradas y en adopcion"
```

Ahora crea el repositorio y súbelo. **Opción A**, si tienes la CLI de GitHub instalada:

```powershell
gh repo create patitas-conectadas --private --source=. --push
```

**Opción B**, manual: crea un repositorio vacío en github.com (sin README ni .gitignore, porque ya los tienes) y luego:

```powershell
git remote add origin https://github.com/TU-USUARIO/patitas-conectadas.git
git push -u origin main
```

> El `.gitignore` ya excluye `.venv`, `node_modules`, la base SQLite local, `backend/uploads/` y `.env`. No se sube nada sensible.

---

## Paso 2 — Importar el proyecto en Vercel

1. Entra a [vercel.com](https://vercel.com) → **Add New** → **Project**.
2. En *Import Git Repository* elige `patitas-conectadas`.
3. ⚠️ **Root Directory: déjalo en la raíz (`./`)**. No lo apuntes a `frontend`: la función Python vive en `/api` y quedaría fuera del despliegue.
4. *Framework Preset*: **Other**.
5. No toques *Build Command* ni *Output Directory* — `vercel.json` ya los define.
6. Pulsa **Deploy**.

Este primer despliegue construye bien el frontend, pero la API va a fallar porque todavía no hay base de datos. **Es lo esperado**, se arregla en los pasos siguientes.

---

## Paso 3 — Base de datos (Neon Postgres)

1. Dentro del proyecto en Vercel, ve a la pestaña **Storage**.
2. **Create Database** → elige **Neon** (Marketplace) → plan **Free**.
3. Conéctala al proyecto marcando los tres entornos: *Production*, *Preview* y *Development*.

Vercel inyecta la variable `DATABASE_URL` automáticamente. Compruébalo en **Settings → Environment Variables**.

> El backend detecta esa variable y adapta la cadena al driver `psycopg` sin que tengas que tocar nada.

---

## Paso 4 — Almacenamiento de fotos (Vercel Blob)

1. En **Storage** → **Create** → **Blob**.
2. Ponle un nombre y pulsa **Connect to project**.

Esto inyecta `BLOB_READ_WRITE_TOKEN`.

> Sin esta variable la aplicación intenta guardar las fotos en disco, y el disco de las funciones serverless se borra en cada invocación: **las fotos se perderían**. El plan gratuito da 1 GB, que alcanza para miles de fotos porque el navegador las comprime a 200–400 KB antes de subirlas.

---

## Paso 5 — Tus propias variables de entorno

Primero genera un secreto de sesión. En tu equipo:

```powershell
.\.venv\Scripts\python.exe -c "import secrets; print(secrets.token_urlsafe(48))"
```

Copia el resultado. Luego, en Vercel → **Settings → Environment Variables**, agrega estas tres para **Production** y **Preview**:

| Variable | Valor | Para qué sirve |
|---|---|---|
| `JWT_SECRET` | el texto que generaste | Firma las sesiones de los usuarios |
| `ADMIN_EMAILS` | tu correo | Te da acceso al panel administrativo al registrarte |
| `SITE_URL` | `https://tu-proyecto.vercel.app` | Enlaces para compartir y retorno de Google |

> `SITE_URL` debe ser el dominio que te asignó Vercel (lo ves en la portada del proyecto). Si no la defines se deduce sola, pero conviene fijarla.

La lista completa de variables opcionales está en `.env.example`.

---

## Paso 6 — Redesplegar

Las variables de entorno **solo se aplican en despliegues nuevos**, así que hay que forzar uno:

**Deployments** → el último de la lista → menú `···` → **Redeploy**.

Cuando termine, abre en el navegador:

```
https://tu-proyecto.vercel.app/api/health
```

Debe responder `{"ok": true, ...}`. Las tablas de la base de datos se crean solas en este primer arranque.

---

## Paso 7 — Crear tu administrador y el contenido de ayuda

La base ya tiene las tablas, pero está vacía. Vamos a sembrarla desde tu equipo.

1. Copia la cadena de conexión: **Storage** → tu base de datos → variable `DATABASE_URL`. Usa la que dice **pooled** (lleva `-pooler` en el host).
2. Ejecuta, desde la raíz del proyecto:

```powershell
cd C:\Users\USUARIO\Documents\patitas-conectadas
$env:DATABASE_URL = "postgresql://usuario:clave@ep-xxx-pooler.region.aws.neon.tech/neondb?sslmode=require"
.\.venv\Scripts\python.exe -m backend.app.seed --admin tu@correo.com --password UnaClaveSegura123
Remove-Item Env:\DATABASE_URL
```

Esto crea los 8 artículos de ayuda y tu usuario administrador.

- Agrega `--demo` al final si quieres también las 6 publicaciones de ejemplo. Sirven para enseñar la plataforma y luego las borras desde el panel.
- La última línea limpia la variable para que tu entorno local vuelva a usar SQLite.

---

## Paso 8 — Comprobar que todo funciona

Recorre esta lista en el sitio ya desplegado:

1. **`/api/health`** responde `{"ok": true}`.
2. **Publica una mascota de prueba con foto.** Recarga la página: si la foto sigue viéndose, Blob está bien conectado.
3. **Copia el enlace de esa publicación y mándatelo por WhatsApp.** Debe aparecer la vista previa con la foto, el nombre, el tipo y la ciudad.
4. **Inicia sesión** con el correo y la contraseña del Paso 7, y entra a `/admin`.
5. Prueba **buscar** filtrando por ciudad.

Si los cinco pasan, el despliegue está completo.

---

## Paso 9 (opcional) — Acceso con Google

1. Entra a [Google Cloud Console](https://console.cloud.google.com) → **APIs y servicios** → **Credenciales**.
2. **Crear credenciales** → **ID de cliente de OAuth** → tipo **Aplicación web**.
3. Configura:
   - *Orígenes autorizados de JavaScript*: `https://tu-proyecto.vercel.app`
   - *URI de redirección autorizados*: `https://tu-proyecto.vercel.app/api/auth/google/callback`
4. Copia el **ID de cliente** y el **secreto**.
5. En Vercel agrega `GOOGLE_CLIENT_ID` y `GOOGLE_CLIENT_SECRET`, y **redespliega**.

El botón «Continuar con Google» aparece solo cuando ambas variables existen. Si las quitas, el acceso por correo sigue funcionando con normalidad.

---

## Paso 10 (opcional) — Dominio propio

1. **Settings → Domains** → agrega tu dominio y sigue las instrucciones de DNS.
2. Actualiza `SITE_URL` con el nuevo dominio.
3. Si usas Google, actualiza también el URI de redirección en la consola de Google.
4. Redespliega.

---

## De aquí en adelante

- Cada `git push` a `main` despliega a producción automáticamente.
- Cada rama o pull request genera una URL de vista previa independiente.

---

## Si algo falla

| Síntoma | Causa habitual |
|---|---|
| `/api/health` devuelve 500 | `DATABASE_URL` ausente o mal copiada. Revisa **Deployments → Functions → Logs**. Usa la cadena *pooled*. |
| Las fotos se suben pero luego no se ven | Falta `BLOB_READ_WRITE_TOKEN`, o lo agregaste sin redesplegar. |
| Google responde `redirect_uri_mismatch` | El URI debe coincidir carácter por carácter, con `https://` y sin barra final. |
| Cambiaste una variable y no pasa nada | Las variables solo entran en despliegues nuevos. Redespliega. |
| El build falla en `npm ci` | `frontend/package-lock.json` desactualizado. Corre `npm install` dentro de `frontend`, haz commit del lockfile y vuelve a subir. |
| El panel `/admin` te rebota al inicio | Tu correo no está en `ADMIN_EMAILS`, o te registraste antes de agregarlo. Vuelve a correr el seed del Paso 7 con `--admin`. |

**Dónde ver los errores:** Vercel → tu proyecto → **Deployments** → el despliegue → pestaña **Functions** → **Logs**. Ahí aparece cualquier fallo del backend Python.

---

## Un ajuste para más adelante

Cuando la base de datos ya esté estable, agrega la variable `AUTO_CREATE_TABLES=0`. Ahorra unas consultas de verificación en cada arranque en frío, a cambio de tener que correr el seed a mano cuando cambien los modelos.
