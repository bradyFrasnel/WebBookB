from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI, HTTPException, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.core.config import settings
from app.core.rate_limit import rate_limit_and_size_middleware
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

logger = logging.getLogger("webbook.api")


@asynccontextmanager
async def lifespan(_app: FastAPI):
    run_startup_migrations()
    yield


# Fermeture automatique des routes d'inspection (/docs, /redoc, /openapi.json) hors mode DEBUG
app = FastAPI(
    title=settings.APP_NAME,
    version="1.2.1",
    description="API REST du gestionnaire personnel de sites web WebBook.",
    lifespan=lifespan,
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    openapi_url="/openapi.json" if settings.DEBUG else None,
)


@app.middleware("http")
async def security_and_rate_limit_middleware(request: Request, call_next):
    response = await rate_limit_and_size_middleware(request, call_next)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    response.headers["Strict-Transport-Security"] = (
        "max-age=63072000; includeSubDomains; preload"
    )
    response.headers["Permissions-Policy"] = (
        "camera=(), microphone=(), geolocation=(), payment=()"
    )
    response.headers["Cross-Origin-Opener-Policy"] = "same-origin"
    if not settings.DEBUG:
        response.headers["Content-Security-Policy"] = (
            "default-src 'none'; frame-ancestors 'none'; base-uri 'none'"
        )
    if request.url.path.startswith("/api/auth"):
        response.headers["Cache-Control"] = "no-store, no-cache, must-revalidate"
        response.headers["Pragma"] = "no-cache"
    return response


# CORS strictement limité au domaine officiel et aux aperçus du projet WebBookF uniquement
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_origin_regex=r"^https://webbookf(-[a-z0-9-]+-bradyfrasnels-projects)?\.vercel\.app$",
    allow_credentials=True,
    allow_methods=["GET", "HEAD", "POST", "PATCH", "DELETE", "OPTIONS"],
    allow_headers=["Authorization", "Content-Type", "Accept"],
    expose_headers=["Retry-After"],
)


@app.exception_handler(OperationalError)
async def database_operational_error_handler(
    _request: Request, _exc: OperationalError
):
    """Intercepte une panne ou coupure temporaire de PostgreSQL/Neon et renvoie un 503 propre."""
    engine.dispose()
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "La base de données est temporairement indisponible ou en cours de réveil. Veuillez réessayer dans quelques secondes."
        },
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    """Empêche toute fuite de trace interne en production lorsque DEBUG=False."""
    logger.exception(
        "Erreur interne non gérée sur %s %s : %s",
        request.method,
        request.url.path,
        exc,
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={"detail": "Une erreur interne est survenue sur le serveur."},
    )


app.include_router(auth.router)
app.include_router(utilisateur.router)
app.include_router(categorie.router)
app.include_router(site.router)
app.include_router(note.router)
app.include_router(historique.router)
app.include_router(statistique.router)


@app.api_route("/", methods=["GET", "HEAD"], tags=["Santé"])
def accueil():
    return {"status": "ok", "message": f"{settings.APP_NAME} API fonctionne !"}


@app.api_route("/health", methods=["GET", "HEAD"], tags=["Santé"])
def health_check():
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "version": "1.2.1",
        "smtp_configured": bool(settings.SMTP_USER and settings.SMTP_PASSWORD),
    }


@app.api_route("/test-db", methods=["GET", "HEAD"], tags=["Santé"])
def tester_base_de_donnees():
    if not settings.DEBUG:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Ressource introuvable.",
        )
    migrations_ok = run_startup_migrations(max_retries=2, retry_delay=1.0)
    with engine.connect() as connexion:
        resultat = connexion.execute(text("SELECT 1"))
        return {
            "database": "PostgreSQL",
            "connexion": resultat.scalar_one(),
            "tables_initialisees": migrations_ok,
        }
