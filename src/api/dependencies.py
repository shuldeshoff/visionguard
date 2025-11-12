"""
FastAPI dependencies
"""
from fastapi import Depends
from sqlalchemy.orm import Session

from src.db.database import get_db
from src.db.repository import VideoAnalysisRepository


def get_repository(db: Session = Depends(get_db)) -> VideoAnalysisRepository:
    """
    Dependency для получения repository
    
    Args:
        db: Database session
        
    Returns:
        VideoAnalysisRepository: Repository instance
    """
    return VideoAnalysisRepository(db)

