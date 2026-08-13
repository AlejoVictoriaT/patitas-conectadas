"""Contraseñas, JWT y dependencias de autenticación.

El hash de contraseñas usa PBKDF2-HMAC-SHA256 de la librería estándar: evita
dependencias nativas (que complican el empaquetado serverless) y es seguro.
"""

from __future__ import annotations

import base64
import hashlib
import hmac
import secrets
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.orm import Session

from .config import settings
from .db import get_db
from .models import User

PBKDF2_ITERATIONS = 210_000


# ------------------------------------------------------------------ contraseñas


def hash_password(password: str) -> str:
    salt = secrets.token_bytes(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode("utf-8"), salt, PBKDF2_ITERATIONS)
    return "pbkdf2_sha256${}${}${}".format(
        PBKDF2_ITERATIONS,
        base64.b64encode(salt).decode(),
        base64.b64encode(digest).decode(),
    )


def verify_password(password: str, stored: str | None) -> bool:
    if not stored:
        return False
    try:
        algorithm, iterations, salt_b64, digest_b64 = stored.split("$")
        if algorithm != "pbkdf2_sha256":
            return False
        expected = base64.b64decode(digest_b64)
        candidate = hashlib.pbkdf2_hmac(
            "sha256", password.encode("utf-8"), base64.b64decode(salt_b64), int(iterations)
        )
    except (ValueError, TypeError):
        return False
    return hmac.compare_digest(candidate, expected)


# ------------------------------------------------------- tokens de administración

def generate_manage_token() -> str:
    """Token secreto que recibe un usuario invitado para administrar su publicación."""
    return secrets.token_urlsafe(24)


def hash_manage_token(token: str) -> str:
    return hashlib.sha256(f"{token}{settings.jwt_secret}".encode("utf-8")).hexdigest()


def manage_token_matches(token: str, stored_hash: str | None) -> bool:
    if not stored_hash:
        return False
    return hmac.compare_digest(hash_manage_token(token), stored_hash)


# -------------------------------------------------------------------------- JWT


def create_access_token(user_id: str, extra: dict | None = None) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        "sub": user_id,
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=settings.jwt_expire_minutes)).timestamp()),
    }
    if extra:
        payload.update(extra)
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm)


def decode_access_token(token: str) -> dict | None:
    try:
        return jwt.decode(token, settings.jwt_secret, algorithms=[settings.jwt_algorithm])
    except jwt.PyJWTError:
        return None


def create_state_token(payload: dict, minutes: int = 10) -> str:
    now = datetime.now(timezone.utc)
    data = {**payload, "exp": int((now + timedelta(minutes=minutes)).timestamp())}
    return jwt.encode(data, settings.jwt_secret, algorithm=settings.jwt_algorithm)


# ------------------------------------------------------------------ dependencias


def _user_from_header(authorization: str | None, db: Session) -> User | None:
    if not authorization or not authorization.lower().startswith("bearer "):
        return None
    payload = decode_access_token(authorization.split(" ", 1)[1].strip())
    if not payload:
        return None
    user = db.get(User, payload.get("sub", ""))
    if user and user.is_active:
        return user
    return None


def get_current_user_optional(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User | None:
    """Devuelve el usuario si hay sesión válida; `None` para visitantes/invitados."""
    return _user_from_header(authorization, db)


def get_current_user(
    authorization: str | None = Header(default=None),
    db: Session = Depends(get_db),
) -> User:
    user = _user_from_header(authorization, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Necesitas iniciar sesión para continuar.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_current_admin(user: User = Depends(get_current_user)) -> User:
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso restringido.")
    return user
