from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    app_name: str = "Revora API"
    database_url: str = "sqlite:///./revora.db"
    secret_key: str = "development-only-change-me"
    access_token_expire_minutes: int = 60
    cors_origins: str = "http://localhost:5173"
    redis_url: str = "redis://localhost:6379/0"
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

    @property
    def cors_origin_list(self) -> list[str]:
        return [x.strip() for x in self.cors_origins.split(",") if x.strip()]

settings = Settings()
