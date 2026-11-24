from datetime import datetime, timedelta, timezone
import hashlib
import hmac
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import settings

password_hash = PasswordHash.recommended()


def hash_password(mot_de_passe: str) -> str:
    return password_hash.hash(mot_de_passe)


def verify_password(mot_de_passe_clair: str, mot_de_passe_hash: str) -> bool:
    return password_hash.verify(mot_de_passe_clair, mot_de_passe_hash)


def _compute_password_fingerprint(mot_de_passe_hash: str) -> str:
    """Empreinte dérivée du hash actuel permettant d'invalider un lien dès son premier usage."""
    return hmac.new(
        settings.SECRET_KEY.encode("utf-8"),
        mot_de_passe_hash.encode("utf-8"),
        hashlib.sha256,
    ).hexdigest()[:16]


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
) -> str:
    now = datetime.now(timezone.utc)
    expire = now + (
        expires_delta
        if expires_delta is not None
        else timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    payload: dict[str, Any] = {
        "sub": subject,
        "type": "access",
        "exp": expire,
        "iat": now,
    }
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_access_token(token: str) -> dict[str, Any]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        # Empêche toute confusion de type (ex: utilisation d'un jeton password_reset comme session)
        token_type = payload.get("type")
        if token_type not in (None, "access"):
            raise ValueError("Type de jeton invalide pour l'authentification.")
        return payload
    except InvalidTokenError as exc:
        raise ValueError("Token invalide ou expiré.") from exc


def create_password_reset_token(email: str, mot_de_passe_hash: str = "") -> str:
    now = datetime.now(timezone.utc)
    expire = now + timedelta(
        minutes=settings.PASSWORD_RESET_TOKEN_EXPIRE_MINUTES
    )
    payload: dict[str, Any] = {
        "sub": email,
        "type": "password_reset",
        "exp": expire,
        "iat": now,
    }
    if mot_de_passe_hash:
        payload["pwd_fp"] = _compute_password_fingerprint(mot_de_passe_hash)
    return jwt.encode(
        payload,
        settings.SECRET_KEY,
        algorithm=settings.ALGORITHM,
    )


def decode_password_reset_token(token: str) -> tuple[str, str | None]:
    try:
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=[settings.ALGORITHM],
        )
        if payload.get("type") != "password_reset":
            raise ValueError("Type de jeton invalide.")
        email = payload.get("sub")
        if not email:
            raise ValueError("Jeton incomplet.")
        pwd_fp = payload.get("pwd_fp")
        return str(email), (str(pwd_fp) if pwd_fp else None)
    except InvalidTokenError as exc:
        raise ValueError("Lien de réinitialisation invalide ou expiré.") from exc


def is_reset_token_still_unused(
    token_pwd_fp: str | None, current_mot_de_passe_hash: str
) -> bool:
    if token_pwd_fp is None:
        return True
    expected_fp = _compute_password_fingerprint(current_mot_de_passe_hash)
    return hmac.compare_digest(token_pwd_fp, expected_fp)
