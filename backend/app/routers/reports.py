"""Reporte de publicaciones por parte de cualquier visitante."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import REPORT_REASONS, Post, Report
from ..schemas import ReportIn
from ..utils import client_ip, rate_limit_ok, verify_captcha

router = APIRouter(prefix="/api", tags=["reportes"])

# A partir de este número de reportes la publicación se oculta automáticamente
AUTO_HIDE_THRESHOLD = 3


@router.get("/report-reasons")
def report_reasons() -> list[dict]:
    labels = {
        "informacion_falsa": "La información es falsa o engañosa",
        "contenido_inapropiado": "Contenido inapropiado",
        "duplicada": "Publicación duplicada",
        "venta_de_animales": "Venta de animales",
        "spam": "Spam o publicidad",
        "maltrato": "Posible maltrato animal",
        "otro": "Otro motivo",
    }
    return [{"value": reason, "label": labels[reason]} for reason in REPORT_REASONS]


@router.post("/posts/{identifier}/report", status_code=status.HTTP_201_CREATED)
async def report_post(
    identifier: str,
    payload: ReportIn,
    request: Request,
    db: Session = Depends(get_db),
) -> dict:
    ip = client_ip(request)
    if not rate_limit_ok(f"report:{ip}", limit=10, window_seconds=3600):
        raise HTTPException(status_code=429, detail="Has enviado varios reportes. Intenta más tarde.")
    if not await verify_captcha(payload.captcha_token, ip):
        raise HTTPException(status_code=400, detail="Verificación de seguridad fallida.")

    post = db.scalar(
        select(Post).where(or_(Post.slug == identifier, Post.public_id == identifier, Post.id == identifier))
    )
    if not post:
        raise HTTPException(status_code=404, detail="No encontramos esta publicación.")

    duplicated = db.scalar(
        select(func.count())
        .select_from(Report)
        .where(Report.post_id == post.id, Report.reporter_ip == ip)
    )
    if duplicated:
        return {"ok": True, "message": "Ya recibimos tu reporte. Gracias por avisarnos."}

    db.add(
        Report(
            post_id=post.id,
            reason=payload.reason,
            details=(payload.details or "").strip() or None,
            reporter_email=payload.reporter_email,
            reporter_ip=ip,
        )
    )
    post.reports_count += 1

    auto_hidden = False
    if post.reports_count >= AUTO_HIDE_THRESHOLD and post.is_active:
        post.is_active = False
        post.hidden_reason = "Oculta automáticamente por múltiples reportes; pendiente de revisión."
        auto_hidden = True

    db.commit()
    return {
        "ok": True,
        "auto_hidden": auto_hidden,
        "message": "Gracias. Nuestro equipo revisará esta publicación.",
    }
