"""Noticias y recursos: albergues, jornadas, consejos y bienestar animal."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import and_, func, or_, select
from sqlalchemy.orm import Session

from ..db import get_db
from ..models import ARTICLE_CATEGORIES, Article
from ..schemas import ArticleOut

router = APIRouter(prefix="/api/articles", tags=["noticias"])

CATEGORY_LABELS = {
    "noticia": "Noticia",
    "albergue": "Albergue",
    "hogar_de_paso": "Hogar de paso",
    "fundacion": "Fundación",
    "jornada_adopcion": "Jornada de adopción",
    "esterilizacion": "Esterilización",
    "vacunacion": "Vacunación",
    "consejo": "Consejo",
    "bienestar_animal": "Bienestar animal",
}


@router.get("/categories")
def categories() -> list[dict]:
    return [{"value": c, "label": CATEGORY_LABELS.get(c, c)} for c in ARTICLE_CATEGORIES]


@router.get("", response_model=list[ArticleOut])
def list_articles(
    db: Session = Depends(get_db),
    category: str | None = None,
    city: str | None = None,
    q: str | None = None,
    limit: int = Query(default=30, ge=1, le=100),
) -> list[Article]:
    filters = [Article.is_published.is_(True)]
    if category:
        filters.append(Article.category == category)
    if city:
        # Los recursos sin ciudad se consideran de alcance nacional.
        filters.append(or_(func.lower(Article.city) == city.lower(), Article.city.is_(None)))
    if q:
        needle = f"%{q.strip()}%"
        filters.append(or_(Article.title.ilike(needle), Article.content.ilike(needle)))

    return list(
        db.scalars(
            select(Article)
            .where(and_(*filters))
            .order_by(Article.published_at.desc())
            .limit(limit)
        ).all()
    )


@router.get("/{slug}", response_model=ArticleOut)
def get_article(slug: str, db: Session = Depends(get_db)) -> Article:
    article = db.scalar(select(Article).where(Article.slug == slug, Article.is_published.is_(True)))
    if not article:
        raise HTTPException(status_code=404, detail="No encontramos este contenido.")
    return article
