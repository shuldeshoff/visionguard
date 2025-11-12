"""
Repository паттерн для работы с базой данных
"""
from typing import List, Optional
from sqlalchemy.orm import Session
from sqlalchemy import desc
import logging

from src.db.models import VideoAnalysis

logger = logging.getLogger(__name__)


class VideoAnalysisRepository:
    """
    Repository для работы с VideoAnalysis моделью
    
    Инкапсулирует всю логику работы с БД для видео анализа
    """
    
    def __init__(self, db: Session):
        """
        Инициализация репозитория
        
        Args:
            db: SQLAlchemy session
        """
        self.db = db
    
    def create(
        self,
        filename: str,
        motion_detected: bool,
        frames_analyzed: int,
        processing_time: float,
        status: str = "completed",
        error_message: Optional[str] = None
    ) -> VideoAnalysis:
        """
        Создание новой записи анализа видео
        
        Args:
            filename: Название видеофайла
            motion_detected: Обнаружено ли движение
            frames_analyzed: Количество кадров
            processing_time: Время обработки
            status: Статус обработки
            error_message: Сообщение об ошибке
            
        Returns:
            VideoAnalysis: Созданная запись
        """
        analysis = VideoAnalysis(
            filename=filename,
            motion_detected=motion_detected,
            frames_analyzed=frames_analyzed,
            processing_time=processing_time,
            status=status,
            error_message=error_message
        )
        
        try:
            self.db.add(analysis)
            self.db.commit()
            self.db.refresh(analysis)
            logger.info(f"Created video analysis record: id={analysis.id}, filename={filename}")
            return analysis
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating video analysis: {e}")
            raise
    
    def get_by_id(self, analysis_id: int) -> Optional[VideoAnalysis]:
        """
        Получение записи по ID
        
        Args:
            analysis_id: ID записи
            
        Returns:
            Optional[VideoAnalysis]: Запись или None
        """
        return self.db.query(VideoAnalysis).filter(VideoAnalysis.id == analysis_id).first()
    
    def get_all(
        self,
        skip: int = 0,
        limit: int = 100,
        status: Optional[str] = None
    ) -> List[VideoAnalysis]:
        """
        Получение списка всех записей с пагинацией
        
        Args:
            skip: Количество пропускаемых записей
            limit: Максимальное количество записей
            status: Фильтр по статусу (опционально)
            
        Returns:
            List[VideoAnalysis]: Список записей
        """
        query = self.db.query(VideoAnalysis)
        
        if status:
            query = query.filter(VideoAnalysis.status == status)
        
        return query.order_by(desc(VideoAnalysis.created_at)).offset(skip).limit(limit).all()
    
    def get_by_filename(self, filename: str) -> List[VideoAnalysis]:
        """
        Получение всех анализов для конкретного файла
        
        Args:
            filename: Название файла
            
        Returns:
            List[VideoAnalysis]: Список записей
        """
        return (
            self.db.query(VideoAnalysis)
            .filter(VideoAnalysis.filename == filename)
            .order_by(desc(VideoAnalysis.created_at))
            .all()
        )
    
    def update_status(
        self,
        analysis_id: int,
        status: str,
        error_message: Optional[str] = None
    ) -> Optional[VideoAnalysis]:
        """
        Обновление статуса записи
        
        Args:
            analysis_id: ID записи
            status: Новый статус
            error_message: Сообщение об ошибке (опционально)
            
        Returns:
            Optional[VideoAnalysis]: Обновленная запись или None
        """
        analysis = self.get_by_id(analysis_id)
        
        if not analysis:
            logger.warning(f"Video analysis not found: id={analysis_id}")
            return None
        
        try:
            analysis.status = status
            if error_message:
                analysis.error_message = error_message
            
            self.db.commit()
            self.db.refresh(analysis)
            logger.info(f"Updated video analysis status: id={analysis_id}, status={status}")
            return analysis
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error updating video analysis: {e}")
            raise
    
    def delete(self, analysis_id: int) -> bool:
        """
        Удаление записи
        
        Args:
            analysis_id: ID записи
            
        Returns:
            bool: True если удалено, False если не найдено
        """
        analysis = self.get_by_id(analysis_id)
        
        if not analysis:
            return False
        
        try:
            self.db.delete(analysis)
            self.db.commit()
            logger.info(f"Deleted video analysis: id={analysis_id}")
            return True
        except Exception as e:
            self.db.rollback()
            logger.error(f"Error deleting video analysis: {e}")
            raise
    
    def count_total(self) -> int:
        """
        Подсчет общего количества записей
        
        Returns:
            int: Количество записей
        """
        return self.db.query(VideoAnalysis).count()
    
    def count_by_status(self, status: str) -> int:
        """
        Подсчет записей по статусу
        
        Args:
            status: Статус для фильтрации
            
        Returns:
            int: Количество записей
        """
        return self.db.query(VideoAnalysis).filter(VideoAnalysis.status == status).count()
    
    def count_with_motion(self) -> int:
        """
        Подсчет видео с обнаруженным движением
        
        Returns:
            int: Количество видео с движением
        """
        return (
            self.db.query(VideoAnalysis)
            .filter(VideoAnalysis.motion_detected == True)
            .count()
        )

