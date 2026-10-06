from typing import List, Optional, Union
from pydantic import field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    # Core Application Settings
    ENVIRONMENT: str = "development"
    DEBUG: bool = True
    APP_NAME: str = "FarmSathi"
    API_V1_STR: str = "/api/v1"

    # Security & Tokens
    SECRET_KEY: str = "farmsathi_dev_secret_key_super_secure_replace_in_prod_12345"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7
    ALGORITHM: str = "HS256"

    # Database
    DATABASE_URL: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/farmsathi_v2_db"
    DATABASE_SYNC_URL: str = "postgresql://postgres:postgres@localhost:5432/farmsathi_v2_db"

    # CORS
    ALLOWED_ORIGINS: Union[List[str], str] = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
        "http://localhost:3000",
    ]

    @field_validator("ALLOWED_ORIGINS", mode="before")
    @classmethod
    def assemble_cors_origins(cls, v: Union[str, List[str]]) -> List[str]:
        if isinstance(v, str) and not v.startswith("["):
            return [i.strip() for i in v.split(",") if i.strip()]
        elif isinstance(v, list):
            return v
        return ["http://localhost:5173", "http://127.0.0.1:5173"]

    # Storage
    STORAGE_DIR: str = "./storage/uploads"

    # Machine Learning Settings
    CROP_MODEL_PATH: str = "ml/models/farmsathi_crop_recommendation_rf.pkl"
    DISEASE_MODEL_PATH: str = "ml/models/farmsathi_disease_model.pth"
    DISEASE_CLASSES_PATH: str = "ml/models/disease_classes.json"
    DISEASE_EVAL_METRICS_PATH: str = "ml/models/disease_eval_metrics.json"
    DISEASE_CONFIDENCE_THRESHOLD: float = 0.70
    MAX_UPLOAD_SIZE_BYTES: int = 10 * 1024 * 1024  # 10 MB

    # External APIs & Weather Settings
    WEATHER_API_BASE_URL: str = "https://api.open-meteo.com/v1"
    WEATHER_GEOCODING_API_BASE_URL: str = "https://geocoding-api.open-meteo.com/v1"
    WEATHER_TIMEOUT_SECONDS: int = 10
    WEATHER_CACHE_TTL_MINUTES: int = 30

    # Advisory Settings
    ADVISORY_PROVIDER: str = "auto"
    GEMINI_API_KEY: Optional[str] = None
    GEMINI_MODEL: str = "gemini-2.5-flash"
    OPENAI_API_KEY: Optional[str] = None
    OPENAI_MODEL: str = "gpt-4o-mini"
    ADVISORY_TIMEOUT_SECONDS: int = 20

    model_config = SettingsConfigDict(
        env_file=(".env", "../.env"),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
