"""
Тесты для ORM моделей
"""
import pytest
from datetime import datetime
from src.db.models import VideoAnalysis


def test_video_analysis_model_creation():
    """Тест создания модели VideoAnalysis"""
    analysis = VideoAnalysis(
        filename="test_video.mp4",
        motion_detected=True,
        frames_analyzed=100,
        processing_time=2.5,
        status="completed"
    )
    
    assert analysis.filename == "test_video.mp4"
    assert analysis.motion_detected is True
    assert analysis.frames_analyzed == 100
    assert analysis.processing_time == 2.5
    assert analysis.status == "completed"
    assert analysis.error_message is None


def test_video_analysis_repr():
    """Тест строкового представления модели"""
    analysis = VideoAnalysis(
        id=1,
        filename="test.mp4",
        motion_detected=True,
        frames_analyzed=50,
        processing_time=1.0,
        status="completed"
    )
    
    repr_str = repr(analysis)
    assert "VideoAnalysis" in repr_str
    assert "test.mp4" in repr_str
    assert "motion_detected=True" in repr_str


def test_video_analysis_to_dict():
    """Тест преобразования модели в словарь"""
    now = datetime.now()
    analysis = VideoAnalysis(
        id=1,
        filename="test.mp4",
        motion_detected=False,
        frames_analyzed=75,
        processing_time=1.5,
        status="completed",
        created_at=now
    )
    
    result = analysis.to_dict()
    
    assert isinstance(result, dict)
    assert result["id"] == 1
    assert result["filename"] == "test.mp4"
    assert result["motion_detected"] is False
    assert result["frames_analyzed"] == 75
    assert result["processing_time"] == 1.5
    assert result["status"] == "completed"

