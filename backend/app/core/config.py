"""Configuração validada a partir do ambiente e do arquivo local .env."""

from pathlib import Path
from typing import Literal, Self

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=Path(__file__).resolve().parents[2] / ".env",
        env_file_encoding="utf-8",
        hide_input_in_errors=True,
        str_strip_whitespace=True,
    )

    app_name: str = Field(default="CodeTrack", min_length=1)
    environment: Literal["development", "test", "production"] = "development"
    debug: bool = False

    @model_validator(mode="after")
    def validate_production_debug(self) -> Self:
        if self.environment == "production" and self.debug:
            raise ValueError("DEBUG deve ser false em production.")
        return self
