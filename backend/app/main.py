"""
AgriConnect FastAPI application entrypoint.

Run locally with:
    uvicorn app.main:app --reload
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .database import engine
from .routers import auth, orders, shops, users

app = FastAPI(
    title="AgriConnect API",
    description="Backend API for the AgriConnect delivery, farming, and shopping platform.",
    version="0.1.0",
)

# Creates agriconnect.db and all tables on startup if they don't already
# exist. Fine for local SQLite development; use Alembic migrations instead
# once this points at a real PostgreSQL database.
models.Base.metadata.create_all(bind=engine)

# Allow the Vite dev server to call the API during local development.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


app.include_router(auth.router)
app.include_router(users.router)
app.include_router(shops.router)
app.include_router(orders.router)


@app.get("/", tags=["Health"])
def read_root():
    """Basic liveness check."""
    return {"status": "ok", "service": "AgriConnect API"}
