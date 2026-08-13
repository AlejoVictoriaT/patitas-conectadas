"""Autenticación: correo + contraseña y Google OAuth 2.0."""

from __future__ import annotations

import secrets
from urllib.parse import urlencode

import httpx
from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import RedirectResponse
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Post, User
from ..schemas import (
    LoginIn,
    PasswordChangeIn,
    ProfileUpdateIn,
    RegisterIn,
    TokenOut,
    UserOut,
)
from ..security import (
    create_access_token,
    create_state_token,
    decode_access_token,
    get_current_user,
    hash_password,
    manage_token_matches,
    verify_password,
)
from ..utils import client_ip, normalize_phone, rate_limit_ok

router = APIRouter(prefix="/api/auth", tags=["auth"])

GOOGLE_AUTH_URL = "https://accounts.google.com/o/oauth2/v2/auth"
GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v3/userinfo"


def _find_user_by_email(db: Session, email: str) -> User | None:
    return db.scalar(select(User).where(func.lower(User.email) == email.lower()))


def _token_response(user: User) -> TokenOut:
    return TokenOut(access_token=create_access_token(user.id), user=UserOut.model_validate(user))


@router.post("/register", response_model=TokenOut, status_code=status.HTTP_201_CREATED)
def register(payload: RegisterIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    if not rate_limit_ok(f"register:{client_ip(request)}", limit=5, window_seconds=600):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espera unos minutos.")

    if _find_user_by_email(db, payload.email):
        raise HTTPException(status_code=409, detail="Ya existe una cuenta con este correo.")

    user = User(
        name=payload.name.strip(),
        email=payload.email.lower(),
        password_hash=hash_password(payload.password),
        auth_provider="email",
        is_admin=payload.email.lower() in settings.admin_emails,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _token_response(user)


@router.post("/login", response_model=TokenOut)
def login(payload: LoginIn, request: Request, db: Session = Depends(get_db)) -> TokenOut:
    if not rate_limit_ok(f"login:{client_ip(request)}", limit=10, window_seconds=300):
        raise HTTPException(status_code=429, detail="Demasiados intentos. Espera unos minutos.")

    user = _find_user_by_email(db, payload.email)
    if not user or not verify_password(payload.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Correo o contraseña incorrectos.")
    if not user.is_active:
        raise HTTPException(status_code=403, detail="Esta cuenta está desactivada.")
    return _token_response(user)


@router.get("/me", response_model=UserOut)
def me(user: User = Depends(get_current_user)) -> User:
    return user


@router.patch("/me", response_model=UserOut)
def update_profile(
    payload: ProfileUpdateIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> User:
    if payload.name is not None:
        user.name = payload.name.strip()
    if payload.phone is not None:
        user.phone = normalize_phone(payload.phone)
    db.commit()
    db.refresh(user)
    return user


@router.post("/password", status_code=status.HTTP_204_NO_CONTENT, response_model=None)
def change_password(
    payload: PasswordChangeIn,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> None:
    if user.password_hash and not verify_password(payload.current_password or "", user.password_hash):
        raise HTTPException(status_code=400, detail="La contraseña actual no es correcta.")
    user.password_hash = hash_password(payload.new_password)
    user.auth_provider = "email" if user.auth_provider == "email" else user.auth_provider
    db.commit()


# ------------------------------------------------------------------ Google OAuth


@router.get("/providers")
def providers() -> dict:
    """Indica al frontend qué métodos de acceso están disponibles."""
    return {"email": True, "google": bool(settings.google_client_id and settings.google_client_secret)}


@router.get("/google/start")
def google_start(next: str = "/") -> RedirectResponse:
    if not (settings.google_client_id and settings.google_client_secret):
        raise HTTPException(status_code=503, detail="El acceso con Google no está configurado.")

    state = create_state_token({"next": next, "nonce": secrets.token_urlsafe(8)})
    params = {
        "client_id": settings.google_client_id,
        "redirect_uri": settings.google_redirect_uri,
        "response_type": "code",
        "scope": "openid email profile",
        "state": state,
        "prompt": "select_account",
        "access_type": "online",
    }
    return RedirectResponse(f"{GOOGLE_AUTH_URL}?{urlencode(params)}")


@router.get("/google/callback")
async def google_callback(
    request: Request,
    code: str | None = None,
    state: str | None = None,
    error: str | None = None,
    db: Session = Depends(get_db),
) -> RedirectResponse:
    def fail(message: str) -> RedirectResponse:
        return RedirectResponse(f"{settings.site_url}/ingresar?error={message}")

    if error or not code or not state:
        return fail("google_cancelado")

    payload = decode_access_token(state)
    if not payload:
        return fail("estado_invalido")
    next_path = payload.get("next") or "/"

    try:
        async with httpx.AsyncClient(timeout=15) as client:
            token_response = await client.post(
                GOOGLE_TOKEN_URL,
                data={
                    "code": code,
                    "client_id": settings.google_client_id,
                    "client_secret": settings.google_client_secret,
                    "redirect_uri": settings.google_redirect_uri,
                    "grant_type": "authorization_code",
                },
            )
            if token_response.status_code >= 400:
                return fail("google_token")
            access_token = token_response.json().get("access_token")
            if not access_token:
                return fail("google_token")

            profile_response = await client.get(
                GOOGLE_USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"}
            )
            if profile_response.status_code >= 400:
                return fail("google_perfil")
            profile = profile_response.json()
    except httpx.HTTPError:
        return fail("google_conexion")

    email = (profile.get("email") or "").lower()
    if not email or not profile.get("email_verified", True):
        return fail("google_sin_correo")

    user = db.scalar(select(User).where(User.google_sub == profile.get("sub"))) or _find_user_by_email(db, email)
    if user is None:
        user = User(
            name=profile.get("name") or email.split("@")[0],
            email=email,
            auth_provider="google",
            google_sub=profile.get("sub"),
            avatar_url=profile.get("picture"),
            is_admin=email in settings.admin_emails,
        )
        db.add(user)
    else:
        user.google_sub = user.google_sub or profile.get("sub")
        user.avatar_url = user.avatar_url or profile.get("picture")
    if not user.is_active:
        return fail("cuenta_desactivada")

    db.commit()
    db.refresh(user)

    jwt_token = create_access_token(user.id)
    fragment = urlencode({"token": jwt_token, "next": next_path})
    return RedirectResponse(f"{settings.site_url}/auth/callback#{fragment}")


# ---------------------------------------------- vincular publicación de invitado


@router.post("/claim/{manage_token}", response_model=dict)
def claim_guest_post(
    manage_token: str,
    user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> dict:
    """Asocia a la cuenta actual una publicación creada como invitado."""
    from ..security import hash_manage_token

    post = db.scalar(select(Post).where(Post.manage_token_hash == hash_manage_token(manage_token)))
    if not post or not manage_token_matches(manage_token, post.manage_token_hash):
        raise HTTPException(status_code=404, detail="El enlace de administración no es válido.")
    if post.user_id and post.user_id != user.id:
        raise HTTPException(status_code=409, detail="Esta publicación ya pertenece a otra cuenta.")

    post.user_id = user.id
    db.commit()
    return {"ok": True, "post_id": post.id, "slug": post.slug, "type": post.type}
