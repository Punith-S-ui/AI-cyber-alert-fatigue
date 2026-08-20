"""Application configuration."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    PROJECT_NAME: str = "AI Cybersecurity Alert Fatigue Reduction System"
    API_V1_PREFIX: str = "/api"

    # NOTE: In a real production deployment this MUST come from an environment
    # variable / secrets manager. A default is provided so the demo project
    # runs out-of-the-box on a first-time Windows setup.
    SECRET_KEY: str = os.environ.get("APP_SECRET_KEY", "dev-secret-key-change-me-in-production-8f92a1")
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 8  # 8 hours

    BASE_DIR: str = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    DATABASE_URL: str = f"sqlite:///{os.path.join(BASE_DIR, 'app.db')}"

    ML_MODELS_DIR: str = os.path.join(BASE_DIR, "ml_models")

    CORS_ORIGINS: list = [
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ]

    UPLOAD_MAX_ROWS: int = 20000

    class Config:
        env_file = ".env"


settings = Settings()
os.makedirs(settings.ML_MODELS_DIR, exist_ok=True)
