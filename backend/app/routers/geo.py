"""Catálogo de países, departamentos y ciudades para el selector con buscador."""

from __future__ import annotations

from fastapi import APIRouter, Query

from ..data.geo import ALL_CITIES, DEFAULT_COUNTRY, list_cities, list_countries, list_regions
from ..utils import slugify

router = APIRouter(prefix="/api/geo", tags=["ubicaciones"])


@router.get("/countries")
def countries() -> dict:
    return {"default": DEFAULT_COUNTRY, "items": list_countries()}


@router.get("/regions")
def regions(country: str = DEFAULT_COUNTRY) -> list[str]:
    return list_regions(country)


@router.get("/cities")
def cities(country: str = DEFAULT_COUNTRY, region: str | None = None) -> list[str]:
    return list_cities(country, region)


@router.get("/search")
def search_cities(
    q: str = Query(default="", max_length=80),
    country: str | None = None,
    limit: int = Query(default=25, ge=1, le=100),
) -> list[dict]:
    """Búsqueda de ciudades sin distinguir mayúsculas ni tildes."""
    needle = slugify(q)
    rows = [row for row in ALL_CITIES if not country or row[0] == country]

    if not needle:
        results = rows[:limit]
    else:
        starts, contains = [], []
        for row in rows:
            city_slug = slugify(row[2])
            if city_slug.startswith(needle):
                starts.append(row)
            elif needle in city_slug or needle in slugify(row[1]):
                contains.append(row)
        results = (starts + contains)[:limit]

    return [
        {"country": country_name, "region": region, "city": city, "label": f"{city}, {region}"}
        for country_name, region, city in results
    ]
