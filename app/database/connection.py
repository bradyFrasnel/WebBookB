from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

# Moteur de connexion résilient (pool_pre_ping, pool_recycle et timeout adaptés à Neon Serverless PostgreSQL)
engine = create_engine(
    settings.DATABASE_URL,
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_recycle=300,
    connect_args={"connect_timeout": 10},
)

# Fabrique de sessions
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


# Classe de base des modèles
class Base(DeclarativeBase):
    pass


def get_db():
    from app.database.migrations import run_startup_migrations

    run_startup_migrations(max_retries=1, retry_delay=0.5)
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
