import logging
from collections.abc import Generator

from pgvector.psycopg import register_vector
from sqlalchemy import create_engine, event, text
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session, sessionmaker

from legal_doc_ai.config import get_settings

settings = get_settings()
engine = create_engine(settings.postgres_url, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)


@event.listens_for(engine, "connect")
def connect(dbapi_connection, connection_record) -> None:  # pragma: no cover
    try:
        register_vector(dbapi_connection)
    except Exception:  # noqa: BLE001 - optional adapter registration boundary
        logging.getLogger(__name__).warning("pgvector registration unavailable")


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def ensure_pgvector_extension(db: Session) -> None:
    db.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
    db.commit()


def test_db_connection() -> bool:
    try:
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        return True
    except SQLAlchemyError:
        return False


def init_db() -> None:
    from legal_doc_ai.models import Base

    with SessionLocal() as db:
        ensure_pgvector_extension(db)
    Base.metadata.create_all(bind=engine)
