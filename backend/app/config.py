# app/config.py
from pydantic_settings import BaseSettings
from pydantic import Field, Json
from typing import List


class Settings(BaseSettings):
    # --- General ---
    PROJECT_NAME: str = "Gestion Notes & Employés API"

    # --- Database ---
    DATABASE_URL: str = Field(...)

    # --- Auth & Security ---
    JWT_SECRET: str = Field(...)
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # --- CORS ---
    CORS_ORIGINS: Json[List[str]] = ["http://localhost:4200", "http://127.0.0.1:4200"]

    # Debug
    DEBUG: bool = False

    # Email settings
    MAIL_USERNAME: str
    MAIL_PASSWORD: str
    MAIL_FROM: str
    MAIL_FROM_NAME: str = "Gestion Notes"

    MAIL_SERVER: str = "smtp.gmail.com"
    MAIL_PORT: int = 465

    MAIL_STARTTLS: bool = False
    MAIL_SSL_TLS: bool = True

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()
