from pathlib import Path
from typing import List, Union
from pydantic import AnyHttpUrl, validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    PROJECT_NAME: str = "QuantLab Quantitative Research Platform"
    VERSION: str = "1.0.0"
    API_V1_STR: str = "/api/v1"
    
    ENVIRONMENT: str = "development"
    LOG_LEVEL: str = "INFO"
    SECRET_KEY: str = "quantlab-insecure-dev-key-change-in-production-1234567890"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 1440  # 24 hours
    
    # Dual-tier storage configuration
    DATABASE_URL: str = "sqlite:///./quantlab.db"
    PARQUET_STORAGE_PATH: str = "./data/parquet"
    SAMPLE_DATA_PATH: str = "./data/sample"
    
    # CORS whitelisting
    BACKEND_CORS_ORIGINS: List[str] = [
        "http://localhost:3000",
        "http://127.0.0.1:3000",
        "http://localhost:8000",
        "http://127.0.0.1:8000",
    ]
    
    # Worker execution limits
    MAX_PARALLEL_BACKTESTS: int = 4
    JOB_TIMEOUT_SECONDS: int = 600
    
    # Optional external provider credentials
    ALPHA_VANTAGE_API_KEY: str = ""
    TIINGO_API_KEY: str = ""
    OPENAI_API_KEY: str = ""
    ANTHROPIC_API_KEY: str = ""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore"
    )

    def init_storage_directories(self) -> None:
        """Ensure local data directories exist."""
        Path(self.PARQUET_STORAGE_PATH).mkdir(parents=True, exist_ok=True)
        Path(self.SAMPLE_DATA_PATH).mkdir(parents=True, exist_ok=True)


settings = Settings()
settings.init_storage_directories()
