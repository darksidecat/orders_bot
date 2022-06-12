import json

from pydantic import BaseSettings, validator


class DB(BaseSettings):
    host: str
    port: int
    name: str
    user: str
    password: str


class Redis(BaseSettings):
    host: str
    db: int


class TgBot(BaseSettings):
    token: str
    admin_ids: list[int]
    use_redis: bool

    @validator("admin_ids", pre=True, always=True)
    def admin_ids_list(cls, v) -> list[int]:
        return json.loads(v)


class Settings(BaseSettings):
    tg_bot: TgBot
    db: DB
    redis: Redis

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        env_nested_delimiter = "__"


def load_config(env_file=".env") -> Settings:
    settings = Settings(_env_file=env_file)
    return settings
