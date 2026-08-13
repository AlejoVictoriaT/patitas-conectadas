"""Utilidades compartidas: slugs, teléfonos, antispam y etiquetas legibles."""

from __future__ import annotations

import re
import secrets
import time
import unicodedata

import httpx

from .config import settings
from .models import (
    STATUS_ADOPTION_ACTIVE,
    STATUS_ADOPTION_DONE,
    STATUS_CLOSED,
    STATUS_FOUND_ACTIVE,
    STATUS_FOUND_DELIVERED,
    STATUS_LOST_ACTIVE,
    STATUS_LOST_REUNITED,
    TYPE_ADOPTION,
    TYPE_FOUND,
    TYPE_LOST,
)

_ALPHABET = "abcdefghijkmnpqrstuvwxyz23456789"  # sin caracteres ambiguos


def slugify(value: str, max_length: int = 60) -> str:
    normalized = unicodedata.normalize("NFKD", value or "")
    ascii_text = normalized.encode("ascii", "ignore").decode("ascii").lower()
    ascii_text = re.sub(r"[^a-z0-9]+", "-", ascii_text).strip("-")
    return ascii_text[:max_length].strip("-")


def generate_public_id(length: int = 8) -> str:
    return "".join(secrets.choice(_ALPHABET) for _ in range(length))


def normalize_phone(value: str | None, default_country_code: str = "57") -> str | None:
    """Deja el número en formato internacional sin signos, apto para wa.me."""
    if not value:
        return None
    digits = re.sub(r"\D", "", value)
    if not digits:
        return None
    if digits.startswith("00"):
        digits = digits[2:]
    # Número colombiano de 10 dígitos sin indicativo
    if len(digits) == 10 and digits.startswith("3"):
        digits = default_country_code + digits
    return digits[:15]


def whatsapp_link(phone: str | None, message: str = "") -> str | None:
    number = normalize_phone(phone)
    if not number:
        return None
    from urllib.parse import quote

    base = f"https://wa.me/{number}"
    return f"{base}?text={quote(message)}" if message else base


# --------------------------------------------------------------- etiquetas UI

TYPE_LABELS = {
    TYPE_LOST: "Perdida",
    TYPE_FOUND: "Encontrada",
    TYPE_ADOPTION: "En adopción",
}

STATUS_LABELS = {
    STATUS_LOST_ACTIVE: "Perdida",
    STATUS_LOST_REUNITED: "Reunida con su familia",
    STATUS_FOUND_ACTIVE: "Encontrada — buscando a su familia",
    STATUS_FOUND_DELIVERED: "Entregada a su familia",
    STATUS_ADOPTION_ACTIVE: "Disponible para adopción",
    STATUS_ADOPTION_DONE: "Adoptada",
    STATUS_CLOSED: "Caso cerrado",
}

SPECIES_LABELS = {
    "perro": "Perro",
    "gato": "Gato",
    "otro": "Otro",
}


def type_label(value: str) -> str:
    return TYPE_LABELS.get(value, value)


def status_label(value: str) -> str:
    return STATUS_LABELS.get(value, value)


def species_label(value: str) -> str:
    return SPECIES_LABELS.get(value, (value or "").capitalize())


# ------------------------------------------------------------------- antispam

_rate_buckets: dict[str, list[float]] = {}


def rate_limit_ok(key: str, limit: int, window_seconds: int) -> bool:
    """Límite de peticiones en memoria.

    En serverless cada instancia tiene su propio contador, así que es una barrera
    contra abuso trivial, no una garantía. El captcha opcional cubre el resto.
    """
    now = time.time()
    hits = [t for t in _rate_buckets.get(key, []) if now - t < window_seconds]
    if len(hits) >= limit:
        _rate_buckets[key] = hits
        return False
    hits.append(now)
    _rate_buckets[key] = hits
    return True


async def verify_captcha(token: str | None, remote_ip: str | None = None) -> bool:
    """Valida un token de Cloudflare Turnstile. Sin secreto configurado, no exige captcha."""
    if not settings.turnstile_secret:
        return True
    if not token:
        return False
    try:
        async with httpx.AsyncClient(timeout=8) as client:
            response = await client.post(
                "https://challenges.cloudflare.com/turnstile/v0/siteverify",
                data={
                    "secret": settings.turnstile_secret,
                    "response": token,
                    **({"remoteip": remote_ip} if remote_ip else {}),
                },
            )
        return bool(response.json().get("success"))
    except httpx.HTTPError:
        # Ante un fallo del proveedor no bloqueamos publicaciones legítimas.
        return True


def client_ip(request) -> str:
    forwarded = request.headers.get("x-forwarded-for")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.client.host if request.client else "desconocido"
