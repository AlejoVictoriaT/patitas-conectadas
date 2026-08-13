"""Punto de entrada de la función serverless de Vercel (runtime Python / ASGI).

Vercel reenvía todas las rutas `/api/*` (y las de crawlers) a este archivo.
La aplicación FastAPI vive en `backend/app` para poder ejecutarla también en local.
"""

import os
import sys

# La raíz del proyecto debe estar en sys.path para poder importar `backend.*`
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from backend.app.main import app  # noqa: E402

# Vercel busca una variable ASGI llamada `app` o `handler`.
handler = app
