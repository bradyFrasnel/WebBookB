from contextlib import asynccontextmanager

from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text
from sqlalchemy.exc import OperationalError

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
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def add_security_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
    return response


@app.exception_handler(OperationalError)
async def database_operational_error_handler(_request: Request, _exc: OperationalError):
    """Intercepte une panne ou coupure temporaire de PostgreSQL/Neon et renvoie un 503 propre."""
    engine.dispose()
    return JSONResponse(
        status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
        content={
            "detail": "La base de données est temporairement indisponible ou en cours de réveil. Veuillez réessayer dans quelques secondes."
        },
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
        "version": "1.2.0",
        "smtp_configured": bool(settings.SMTP_USER and settings.SMTP_PASSWORD),
    }


@app.api_route("/test-db", methods=["GET", "HEAD"], tags=["Santé"])
def tester_base_de_donnees():
    migrations_ok = run_startup_migrations(max_retries=2, retry_delay=1.0)
    with engine.connect() as connexion:
        resultat = connexion.execute(text("SELECT 1"))
        return {
            "database": "PostgreSQL",
            "connexion": resultat.scalar_one(),
            "tables_initialisees": migrations_ok,
        }
