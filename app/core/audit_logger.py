import logging
from datetime import datetime, timezone

security_logger = logging.getLogger("webbook.security")
if not security_logger.handlers:
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s | SECURITY | %(levelname)s | %(message)s"
    )
    handler.setFormatter(formatter)
    security_logger.addHandler(handler)
    security_logger.setLevel(logging.INFO)


def mask_email(email: str) -> str:
    cleaned = (email or "").strip().lower()
    if "@" not in cleaned:
        return "***"
    local, domain = cleaned.split("@", 1)
    prefix = local[:2] if len(local) > 2 else local[:1]
    return f"{prefix}***@{domain}"


def log_security_event(event: str, **details: object) -> None:
    """Journalise un événement de sécurité sans jamais exposer de secret ou mot de passe."""
    safe_parts = [f"event={event}"]
    for key, val in details.items():
        if key in {"mot_de_passe", "password", "token", "secret"}:
            continue
        safe_parts.append(f"{key}={val}")
    safe_parts.append(f"ts={datetime.now(timezone.utc).isoformat()}")
    security_logger.info(" ".join(safe_parts))
