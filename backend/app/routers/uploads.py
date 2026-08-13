"""Subida de fotografías.

El frontend redimensiona y comprime la imagen en el navegador antes de enviarla,
para que subir desde un celular con datos móviles sea rápido.
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, File, HTTPException, Request, UploadFile

from ..config import settings
from ..models import User
from ..schemas import UploadOut
from ..security import get_current_user_optional
from ..storage import ALLOWED_CONTENT_TYPES, StorageError, upload_image
from ..utils import client_ip, rate_limit_ok

router = APIRouter(prefix="/api", tags=["fotos"])

# Firmas de archivo aceptadas (evita que se suba cualquier binario con nombre de imagen)
_MAGIC_NUMBERS = (
    b"\xff\xd8\xff",       # JPEG
    b"\x89PNG\r\n\x1a\n",  # PNG
)


def _looks_like_image(data: bytes) -> bool:
    if data.startswith(_MAGIC_NUMBERS):
        return True
    if data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return True
    if data[4:8] == b"ftyp" and data[8:12] in (b"heic", b"heix", b"hevc", b"mif1", b"msf1"):
        return True
    return False


@router.post("/uploads", response_model=UploadOut)
async def upload_photo(
    request: Request,
    file: UploadFile = File(...),
    user: User | None = Depends(get_current_user_optional),
) -> UploadOut:
    if not rate_limit_ok(f"upload:{client_ip(request)}", limit=40, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Demasiadas fotos en poco tiempo. Intenta más tarde.")

    content_type = (file.content_type or "").lower()
    if content_type not in ALLOWED_CONTENT_TYPES:
        raise HTTPException(
            status_code=400,
            detail="Formato no admitido. Usa una foto JPG, PNG o WebP.",
        )

    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="El archivo llegó vacío. Intenta de nuevo.")
    if len(data) > settings.max_upload_bytes:
        limit_mb = round(settings.max_upload_bytes / (1024 * 1024), 1)
        raise HTTPException(status_code=413, detail=f"La foto supera {limit_mb} MB. Intenta con una más liviana.")
    if not _looks_like_image(data):
        raise HTTPException(status_code=400, detail="El archivo no parece ser una imagen válida.")

    try:
        url = await upload_image(data, content_type)
    except StorageError as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return UploadOut(url=url)
