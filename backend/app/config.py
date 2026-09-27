from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_env: str = "development"
    database_url: str = "postgresql+psycopg://lostlink:lostlink@localhost:5432/lostlink"
    jwt_secret: str = "CHANGE_ME_TO_A_LONG_RANDOM_SECRET"
    access_token_minutes: int = 1440
    cors_origins: str = "http://localhost:5173,http://127.0.0.1:5173"
    upload_dir: str = "./uploads"
    max_upload_mb: int = 10
    ai_enabled: bool = True
    ai_model_id: str = "google/siglip-base-patch16-224"
    ai_device: str = "auto"
    ai_top_k: int = 50
    match_min_score: float = 0.52
    match_auto_review_score: float = 0.78

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", case_sensitive=False)

    @property
    def cors_list(self):
        return [x.strip().rstrip("/") for x in self.cors_origins.split(",") if x.strip()]


@lru_cache
def get_settings():
    return Settings()
