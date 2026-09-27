from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config: SettingsConfigDict = SettingsConfigDict(
        env_file=".env", extra="ignore"
    )

    DATABASE_CONNECTION: str
    SECRET_KEY: str
    TOKEN_ALGO: str
    EXPIRY_TIME: int


settings = Settings()
