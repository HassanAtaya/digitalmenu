from pydantic_settings import BaseSettings
from pydantic import Field


class Settings(BaseSettings):
    app_name: str = "Digital Menu API"
    api_v1_prefix: str = "/api"
    secret_key: str = Field(default="CHANGE_ME_SECRET", validation_alias="SECRET_KEY")
    access_token_expire_minutes: int = 60 * 24

    postgres_host: str = Field(default="localhost", validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(default=5432, validation_alias="POSTGRES_PORT")
    postgres_db: str = Field(default="digital_menu", validation_alias="POSTGRES_DB")
    postgres_user: str = Field(default="postgres", validation_alias="POSTGRES_USER")
    postgres_password: str = Field(default="postgres", validation_alias="POSTGRES_PASSWORD")

    media_dir: str = Field(default="media", validation_alias="MEDIA_DIR")

    class Config:
        env_file = ".env"
        case_sensitive = False


settings = Settings()  # type: ignore


