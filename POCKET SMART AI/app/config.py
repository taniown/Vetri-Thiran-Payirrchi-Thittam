from functools import lru_cache

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str = "sqlite:///./pocketsmart.db"
    secret_key: str = "pocketsmart-secret-key"
    app_name: str = "Pocket Smart AI"
    debug: bool = True
    cors_origin_list: list[str] = ["http://localhost:3000"]

    class Config:
        env_file = ".env"


@lru_cache
def get_settings() -> Settings:
    return Settings()