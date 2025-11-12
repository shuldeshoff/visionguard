"""
SQLAlchemy ORM модели для базы данных
"""
from sqlalchemy import Column, Integer, String, Boolean, Float, Text, DateTime
from sqlalchemy.sql import func
from datetime import datetime

from src.db.database import Base


class VideoAnalysis(Base):
    """
    Модель для хранения результатов анализа видео
    
    Attributes:
        id: Уникальный идентификатор записи
        filename: Название видеофайла
        motion_detected: Флаг обнаружения движения
        frames_analyzed: Количество проанализированных кадров
        processing_time: Время обработки в секундах
        status: Статус обработки (pending, processing, completed, failed)
        error_message: Сообщение об ошибке (если есть)
        created_at: Дата создания записи
        updated_at: Дата последнего обновления
    """
    
    __tablename__ = "video_analyses"
    
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    filename = Column(String(255), nullable=False, index=True)
    motion_detected = Column(Boolean, nullable=False, index=True)
    frames_analyzed = Column(Integer, nullable=False)
    processing_time = Column(Float, nullable=False)
    status = Column(String(50), nullable=False, index=True, default="pending")
    error_message = Column(Text, nullable=True)
    created_at = Column(DateTime, nullable=False, default=func.now(), server_default=func.now())
    updated_at = Column(DateTime, nullable=False, default=func.now(), onupdate=func.now())
    
    def __repr__(self) -> str:
        """Строковое представление модели"""
        return (
            f"<VideoAnalysis(id={self.id}, "
            f"filename='{self.filename}', "
            f"motion_detected={self.motion_detected}, "
            f"status='{self.status}')>"
        )
    
    def to_dict(self) -> dict:
        """
        Преобразование модели в словарь
        
        Returns:
            dict: Словарь с данными модели
        """
        return {
            "id": self.id,
            "filename": self.filename,
            "motion_detected": self.motion_detected,
            "frames_analyzed": self.frames_analyzed,
            "processing_time": self.processing_time,
            "status": self.status,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }

