import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase


def _get_database_url() -> str:
    data_dir = os.environ.get("DATA_DIR", "/data")
    return f"sqlite:///{data_dir}/invoices.db"


class Base(DeclarativeBase):
    pass


def _make_engine():
    return create_engine(
        _get_database_url(),
        connect_args={"check_same_thread": False},
    )


# Module-level engine and session factory — can be reinitialised by init_db()
engine = _make_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables.  Reinitialises the engine so that DATA_DIR changes
    made after module import (e.g. in test fixtures) are picked up."""
    global engine, SessionLocal

    from app import models  # noqa: F401 — ensure models are registered

    engine = _make_engine()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    Base.metadata.create_all(engine)
