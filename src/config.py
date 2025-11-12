"""
Конфигурация приложения
"""
from pydantic_settings import BaseSettings
from typing import List


class Settings(BaseSettings):
    """Настройки приложения через переменные окружения"""
    
    # Database
    POSTGRES_USER: str = "visionguard"
    POSTGRES_PASSWORD: str = "password"
    POSTGRES_DB: str = "visionguard_db"
    POSTGRES_HOST: str = "db"
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        """Формирование URL подключения к БД"""
        return (
            f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}"
            f"@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
        )
    
    # Application
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000
    APP_NAME: str = "VisionGuard"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = False
    
    # Video Processing
    MAX_VIDEO_SIZE_MB: int = 100
    FRAME_SAMPLE_RATE: int = 5
    MOTION_THRESHOLD: float = 0.02
    PROCESSING_WIDTH: int = 640
    PROCESSING_HEIGHT: int = 480
    
    # File Upload
    UPLOAD_DIR: str = "/tmp/visionguard_uploads"
    
    @property
    def MAX_UPLOAD_SIZE(self) -> int:
        """Максимальный размер файла в байтах"""
        return self.MAX_VIDEO_SIZE_MB * 1024 * 1024
    
    # Logging
    LOG_LEVEL: str = "INFO"
    LOG_FORMAT: str = "json"
    
    # CORS
    ALLOW_ORIGINS: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"
        case_sensitive = True


# Singleton instance
settings = Settings()

