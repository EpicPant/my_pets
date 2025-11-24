"""config with settings classes"""

from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field
from loguru import logger

ENV_PATH = Path(__file__).resolve().parents[2] / ".env"


class DBSettings(BaseSettings):
    """setting class for database config"""

    DB_HOST: str
    DB_PORT: int
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH,
        env_file_encoding="utf-8",
        extra="ignore",
    )

    @property
    def DB_URL(self) -> str:
        """get and validate postgres database url"""
        return f"postgresql+asyncpg://{self.DB_USER}:{self.DB_PASSWORD}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"


class AuthSettings(BaseSettings):
    """Setting class for JWT"""

    SECRET_KEY: str
    ALGORITHM: str

    model_config = SettingsConfigDict(
        env_file=ENV_PATH, env_file_encoding="utf-8", extra="ignore"
    )


auth_settings = AuthSettings()
db_settings = DBSettings()
logger.info(db_settings.DB_URL)
