"""
Pydantic модели для API запросов и ответов
"""
from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class VideoAnalysisResponse(BaseModel):
    """Ответ на запрос анализа видео"""
    
    id: int = Field(..., description="Уникальный идентификатор анализа")
    filename: str = Field(..., description="Название видеофайла")
    motion_detected: bool = Field(..., description="Обнаружено ли движение в видео")
    frames_analyzed: int = Field(..., ge=0, description="Количество проанализированных кадров")
    processing_time: float = Field(..., ge=0, description="Время обработки в секундах")
    status: str = Field(..., description="Статус обработки")
    error_message: Optional[str] = Field(None, description="Сообщение об ошибке (если есть)")
    created_at: datetime = Field(..., description="Дата и время создания")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "filename": "security_camera_001.mp4",
                "motion_detected": True,
                "frames_analyzed": 150,
                "processing_time": 2.34,
                "status": "completed",
                "error_message": None,
                "created_at": "2025-11-12T10:30:00"
            }
        }


class VideoAnalysisDetailedResponse(VideoAnalysisResponse):
    """Расширенный ответ с дополнительной информацией"""
    
    total_frames: Optional[int] = Field(None, description="Общее количество кадров в видео")
    motion_percentage: Optional[float] = Field(None, description="Процент кадров с движением")
    avg_motion_intensity: Optional[float] = Field(None, description="Средняя интенсивность движения")
    
    class Config:
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id": 1,
                "filename": "security_camera_001.mp4",
                "motion_detected": True,
                "frames_analyzed": 150,
                "processing_time": 2.34,
                "status": "completed",
                "error_message": None,
                "created_at": "2025-11-12T10:30:00",
                "total_frames": 300,
                "motion_percentage": 45.5,
                "avg_motion_intensity": 0.75
            }
        }


class AnalysisListResponse(BaseModel):
    """Ответ со списком анализов"""
    
    total: int = Field(..., description="Общее количество записей")
    items: list[VideoAnalysisResponse] = Field(..., description="Список анализов")
    
    class Config:
        json_schema_extra = {
            "example": {
                "total": 42,
                "items": [
                    {
                        "id": 1,
                        "filename": "video1.mp4",
                        "motion_detected": True,
                        "frames_analyzed": 150,
                        "processing_time": 2.34,
                        "status": "completed",
                        "created_at": "2025-11-12T10:30:00"
                    }
                ]
            }
        }


class ErrorResponse(BaseModel):
    """Ответ с ошибкой"""
    
    error: str = Field(..., description="Тип ошибки")
    message: str = Field(..., description="Описание ошибки")
    details: Optional[dict] = Field(None, description="Дополнительные детали")
    
    class Config:
        json_schema_extra = {
            "example": {
                "error": "VideoTooLargeError",
                "message": "Video file size (150.5MB) exceeds maximum allowed size (100MB)",
                "details": {
                    "size_mb": 150.5,
                    "max_size_mb": 100
                }
            }
        }


class HealthResponse(BaseModel):
    """Ответ health check"""
    
    status: str = Field(..., description="Статус сервиса")
    service: str = Field(..., description="Название сервиса")
    version: str = Field(..., description="Версия")
    database: str = Field(..., description="Статус подключения к БД")
    
    class Config:
        json_schema_extra = {
            "example": {
                "status": "healthy",
                "service": "VisionGuard",
                "version": "0.1.0",
                "database": "connected"
            }
        }

