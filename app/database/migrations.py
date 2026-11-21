from sqlalchemy import text

from app.database.connection import Base, engine
import app.models  # noqa: F401 - charge tous les modèles dans Base.metadata


def run_startup_migrations() -> None:
    """Crée les nouvelles tables et ajoute les nouvelles colonnes de façon idempotente."""
    Base.metadata.create_all(bind=engine)

    statements = [
        "ALTER TABLE utilisateur ADD COLUMN IF NOT EXISTS nom_utilisateur VARCHAR(100);",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS note_personnelle TEXT;",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS derniere_consultation TIMESTAMPTZ;",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS nombre_consultations INTEGER NOT NULL DEFAULT 0;",
        "UPDATE site SET icone_url = NULL WHERE icone_url LIKE '%domain=127.0.0.1%' OR icone_url LIKE '%domain=localhost%';",
    ]

    with engine.begin() as conn:
        for sql in statements:
            conn.execute(text(sql))
