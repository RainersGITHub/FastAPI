import pathlib

from pydantic_settings import SettingsConfigDict, BaseSettings


class Settings(BaseSettings):
    DATABASE_TYPE: str
    USERNAME: str
    PASSWORD: str
    HOST: str
    PORT: str
    DATABASE_NAME: str
    ENCODING: str
    SECRET_KEY: str
    ALGORITHM: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    model_config = SettingsConfigDict(env_file=f"{pathlib.Path(__file__).resolve().parent}/.env")


settings = Settings()
