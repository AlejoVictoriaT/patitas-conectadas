"""Motor y sesión de SQLAlchemy.

En serverless no conviene mantener un pool de conexiones vivo entre invocaciones,
por eso se usa `NullPool` cuando corremos en Vercel.
"""

from collections.abc import Generator

from sqlalchemy import create_engine, event
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import NullPool

from .config import settings

engine_kwargs: dict = {"pool_pre_ping": True, "future": True}

if settings.is_sqlite:
    engine_kwargs["connect_args"] = {"check_same_thread": False}
else:
    # Neon + funciones serverless: una conexión por invocación.
    engine_kwargs["poolclass"] = NullPool
    engine_kwargs["connect_args"] = {"connect_timeout": 10}

engine = create_engine(settings.database_url, **engine_kwargs)

if settings.is_sqlite:

    @event.listens_for(engine, "connect")
    def _sqlite_pragmas(dbapi_connection, _record):  # pragma: no cover - trivial
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """Crea las tablas si no existen (suficiente para la V1, sin migraciones)."""
    from . import models  # noqa: F401  (registra los modelos en el metadata)

    models.Base.metadata.create_all(bind=engine)
