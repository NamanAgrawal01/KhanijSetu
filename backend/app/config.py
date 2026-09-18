import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    # Railway injects DATABASE_URL automatically for its MySQL plugin
    DATABASE_URL: str = "sqlite:///./khanijsetu.db"
    SECRET_KEY: str = "khanijsetu-dev-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 480
    AI_API_KEY: str = ""
    AI_API_URL: str = ""
    TESSERACT_PATH: str = ""
    HOST: str = "0.0.0.0"
    # Railway sets PORT env var — read it from environment
    PORT: int = int(os.environ.get("PORT", 8000))
    # Add your Railway frontend URL here, comma-separated
    CORS_ORIGINS: str = "http://localhost:5173,http://localhost:3000"
    UPLOAD_DIR: str = "./uploads"
    MAX_FILE_SIZE: int = 10485760
    ENVIRONMENT: str = "development"
    ALLOWED_UPLOAD_EXTENSIONS: str = ".csv,.xlsx,.xls,.pdf,.jpg,.jpeg,.png"

    @property
    def cors_origins_list(self) -> list[str]:
        origins = [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]
        # In production, allow all Railway subdomains if not explicitly set
        if self.ENVIRONMENT == "production" and not any("railway.app" in o for o in origins):
            origins.append("https://*.railway.app")
        return origins

    @property
    def ai_available(self) -> bool:
        return bool(self.AI_API_KEY and self.AI_API_URL)

    class Config:
        env_file = ".env"

settings = Settings()
