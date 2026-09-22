"""Configuração validada a partir do ambiente e do arquivo local .env."""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, SecretStr, field_validator, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.engine import make_url
from sqlalchemy.exc import ArgumentError


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    app_name: str = Field(default="CodeTrack", min_length=1)
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = Field(default=False, validation_alias="CODETRACK_DEBUG")
    database_url: SecretStr

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, value: SecretStr) -> SecretStr:
        try:
            url = make_url(value.get_secret_value())
        except (ArgumentError, ValueError):
            raise ValueError("DATABASE_URL deve ser uma URL PostgreSQL válida.") from None
        if url.drivername != "postgresql+psycopg" or not url.host or not url.database:
            raise ValueError("DATABASE_URL exige postgresql+psycopg, host e banco.")
        return value

    @model_validator(mode="after")
    def validate_production_debug(self) -> Self:
        if self.environment == "production" and self.debug:
            raise ValueError("CODETRACK_DEBUG deve ser false em production.")
        return self
