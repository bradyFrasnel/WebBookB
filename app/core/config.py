import json
from typing import Any

from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "WebBook"
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440
    PASSWORD_RESET_TOKEN_EXPIRE_MINUTES: int = 30
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 465
    SMTP_USER: str = ""
    SMTP_PASSWORD: str = ""
    SMTP_FROM_NAME: str = "WebBook"
    SMTP_FROM_EMAIL: str = ""
    FRONTEND_URL: str = "https://webbookf.vercel.app"
    DEBUG: bool = False
    CORS_ORIGINS: str | list[str] = [
        "https://webbookf.vercel.app",
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ]

    @field_validator("SMTP_HOST", mode="before")
    @classmethod
    def normaliser_smtp_host(cls, value: Any) -> str:
        if not isinstance(value, str) or not value.strip():
            return "smtp.gmail.com"
        return value.strip().strip('"').strip("'").lower()

    @field_validator("SMTP_PORT", mode="before")
    @classmethod
    def normaliser_smtp_port(cls, value: Any) -> int:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            cleaned = value.strip().strip('"').strip("'")
            if cleaned.isdigit():
                return int(cleaned)
        return 465

    @field_validator("SMTP_PASSWORD", mode="before")
    @classmethod
    def normaliser_smtp_password(cls, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        # Supprime automatiquement les espaces et guillemets éventuels
        return "".join(value.strip().strip('"').strip("'").split())

    @field_validator("SMTP_USER", mode="before")
    @classmethod
    def normaliser_smtp_user(cls, value: Any) -> str:
        if not isinstance(value, str):
            return ""
        return value.strip().strip('"').strip("'")

    @field_validator("DATABASE_URL", mode="before")
    @classmethod
    def normaliser_database_url(cls, value: Any) -> Any:
        if not isinstance(value, str):
            return value
        # Supprime tout espace ou saut de ligne accidentel lors d'un copier-coller
        cleaned = "".join(value.split())
        if cleaned.startswith("postgres://"):
            return cleaned.replace("postgres://", "postgresql+psycopg://", 1)
        if cleaned.startswith("postgresql://"):
            return cleaned.replace("postgresql://", "postgresql+psycopg://", 1)
        return cleaned

    @field_validator("CORS_ORIGINS", mode="after")
    @classmethod
    def normaliser_cors_origins(cls, value: str | list[str]) -> list[str]:
        if isinstance(value, str):
            cleaned = value.strip()
            if cleaned.startswith("["):
                try:
                    parsed = json.loads(cleaned)
                    if isinstance(parsed, list):
                        return [
                            str(origin).strip().rstrip("/")
                            for origin in parsed
                            if str(origin).strip()
                        ]
                except json.JSONDecodeError:
                    pass
            return [
                origin.strip().rstrip("/")
                for origin in cleaned.split(",")
                if origin.strip()
            ]
        return [
            str(origin).strip().rstrip("/")
            for origin in value
            if str(origin).strip()
        ]

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
