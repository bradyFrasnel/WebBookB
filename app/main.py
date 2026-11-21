from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.database.connection import engine
from app.database.migrations import run_startup_migrations
from app.routes import (
    auth,
    categorie,
    historique,
    note,
    site,
    statistique,
    utilisateur,
)


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_startup_migrations()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version="1.1.0",
    description="API REST du gestionnaire personnel de sites web WebBook.",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response

app.include_router(auth.router)
app.include_router(utilisateur.router)
app.include_router(categorie.router)
app.include_router(site.router)
app.include_router(note.router)
app.include_router(historique.router)
app.include_router(statistique.router)


@app.get("/", tags=["Santé"])
def accueil():
    return {"message": f"{settings.APP_NAME} API fonctionne !"}


@app.get("/test-db", tags=["Santé"])
def tester_base_de_donnees():
    with engine.connect() as connexion:
        resultat = connexion.execute(text("SELECT 1"))
        return {
            "database": "PostgreSQL",
            "connexion": resultat.scalar_one(),
        }
