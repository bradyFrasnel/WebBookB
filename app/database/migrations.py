import logging
import time

from sqlalchemy import text
from sqlalchemy.exc import OperationalError

from app.database.connection import Base, engine
import app.models  # noqa: F401 - charge tous les modèles dans Base.metadata

logger = logging.getLogger(__name__)

_migrations_applied = False


def run_startup_migrations(max_retries: int = 3, retry_delay: float = 2.0) -> bool:
    """Crée les tables et colonnes avec tentatives multiples (gère le réveil ou une panne temporaire de Neon)."""
    global _migrations_applied
    if _migrations_applied:
        return True

    statements = [
        "ALTER TABLE utilisateur ADD COLUMN IF NOT EXISTS nom_utilisateur VARCHAR(100);",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS note_personnelle TEXT;",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS derniere_consultation TIMESTAMPTZ;",
        "ALTER TABLE site ADD COLUMN IF NOT EXISTS nombre_consultations INTEGER NOT NULL DEFAULT 0;",
        "UPDATE site SET icone_url = NULL WHERE icone_url LIKE '%domain=127.0.0.1%' OR icone_url LIKE '%domain=localhost%';",
    ]

    for attempt in range(1, max_retries + 1):
        try:
            Base.metadata.create_all(bind=engine)
            with engine.begin() as conn:
                for sql in statements:
                    conn.execute(text(sql))
            _migrations_applied = True
            logger.info("Migrations PostgreSQL / Neon appliquées avec succès.")
            return True
        except OperationalError as exc:
            logger.warning(
                "Tentative %s/%s de connexion à PostgreSQL/Neon échouée : %s",
                attempt,
                max_retries,
                exc,
            )
            engine.dispose()
            if attempt < max_retries:
                time.sleep(retry_delay)
        except Exception as exc:
            logger.error("Erreur lors des migrations au démarrage : %s", exc)
            break

    logger.warning(
        "L'API démarre en mode dégradé (base de données temporairement injoignable). "
        "Les tables seront initialisées dès le rétablissement de la connexion."
    )
    return False
