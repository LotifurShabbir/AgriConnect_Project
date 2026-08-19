"""
Database connection setup for AgriConnect.

Configures the SQLAlchemy engine, session factory, and declarative base
that all ORM models (see models.py) and API routes depend on.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

# --------------------------------------------------------------------------
# Database URL
# --------------------------------------------------------------------------
# SQLite for local development/testing — a single file, no server required.
# Swap this for a PostgreSQL URL (e.g. via the DATABASE_URL env var) in
# staging/production:
#   postgresql://<username>:<password>@<host>:<port>/<database_name>
SQLALCHEMY_DATABASE_URL = "sqlite:///./agriconnect.db"

# SQLite only allows a connection to be used by the thread that created it;
# FastAPI's dependency-injected sessions may be used across threads, so this
# check must be disabled. Not needed (and not valid) for PostgreSQL.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class that all SQLAlchemy models in models.py inherit from.
Base = declarative_base()


def get_db():
    """
    FastAPI dependency that provides a database session per-request
    and guarantees it is closed afterwards, even if an error occurs.

    Usage:
        @app.get("/items")
        def list_items(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
