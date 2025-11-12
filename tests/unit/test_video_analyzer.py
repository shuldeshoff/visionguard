"""
Тесты для VideoAnalyzer
"""
import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import numpy as np

from src.services.video_analyzer import VideoAnalyzer, VideoAnalysisResult
from src.utils.exceptions import InvalidVideoError, VideoProcessingError


class TestVideoAnalysisResult:
    """Тесты для VideoAnalysisResult"""
    
    def test_result_creation(self):
        """Тест создания результата"""
        result = VideoAnalysisResult(
            motion_detected=True,
            frames_analyzed=100,
            processing_time=2.5,
            total_frames=150,
            motion_percentage=45.5,
            avg_motion_intensity=0.75
        )
        
        assert result.motion_detected is True
        assert result.frames_analyzed == 100
        assert result.processing_time == 2.5
    
    def test_result_to_dict(self):
        """Тест преобразования результата в словарь"""
        result = VideoAnalysisResult(
            motion_detected=False,
            frames_analyzed=50,
            processing_time=1.234567,
            motion_percentage=5.678
        )
        
        result_dict = result.to_dict()
        
        assert isinstance(result_dict, dict)
        assert result_dict["motion_detected"] is False
        assert result_dict["frames_analyzed"] == 50
        assert result_dict["processing_time"] == 1.235  # Округление
        assert result_dict["motion_percentage"] == 5.68  # Округление


class TestVideoAnalyzer:
    """Тесты для VideoAnalyzer"""
    
    def test_analyzer_initialization(self):
        """Тест инициализации анализатора"""
        analyzer = VideoAnalyzer(
            frame_sample_rate=10,
            motion_threshold=0.05,
            processing_width=320,
            processing_height=240
        )
        
        assert analyzer.frame_sample_rate == 10
        assert analyzer.motion_threshold == 0.05
        assert analyzer.processing_width == 320
        assert analyzer.processing_height == 240
    
    def test_analyzer_default_settings(self):
        """Тест инициализации с настройками по умолчанию"""
        analyzer = VideoAnalyzer()
        
        assert analyzer.frame_sample_rate > 0
        assert 0 < analyzer.motion_threshold < 1
        assert analyzer.processing_width > 0
        assert analyzer.processing_height > 0
    
    def test_preprocess_frame(self):
        """Тест предобработки кадра"""
        analyzer = VideoAnalyzer(
            processing_width=320,
            processing_height=240
        )
        
        # Создаем тестовый кадр (цветной)
        frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        
        processed = analyzer._preprocess_frame(frame)
        
        # Проверяем размер
        assert processed.shape == (240, 320)
        # Проверяем что это grayscale (2D массив)
        assert len(processed.shape) == 2
    
    def test_detect_motion_with_motion(self):
        """Тест детекции движения когда есть движение"""
        analyzer = VideoAnalyzer(motion_threshold=0.01)
        
        # Создаем два разных кадра
        frame1 = np.zeros((240, 320), dtype=np.uint8)
        frame2 = np.zeros((240, 320), dtype=np.uint8)
        frame2[100:140, 150:190] = 255  # Белый квадрат
        
        motion_detected, intensity = analyzer._detect_motion(frame1, frame2)
        
        assert motion_detected is True
        assert intensity > 0
    
    def test_detect_motion_without_motion(self):
        """Тест детекции движения когда движения нет"""
        analyzer = VideoAnalyzer(motion_threshold=0.02)
        
        # Два одинаковых кадра
        frame1 = np.ones((240, 320), dtype=np.uint8) * 100
        frame2 = np.ones((240, 320), dtype=np.uint8) * 100
        
        motion_detected, intensity = analyzer._detect_motion(frame1, frame2)
        
        assert motion_detected is False
        assert intensity >= 0
    
    def test_analyze_invalid_video_path(self):
        """Тест анализа несуществующего видео"""
        analyzer = VideoAnalyzer()
        invalid_path = Path("/nonexistent/video.mp4")
        
        with pytest.raises(InvalidVideoError):
            analyzer.analyze(invalid_path)
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/static_video.mp4").exists(),
        reason="Test video not found. Run: python scripts/generate_test_video.py"
    )
    def test_analyze_static_video(self):
        """Тест анализа статичного видео"""
        analyzer = VideoAnalyzer()
        video_path = Path("tests/fixtures/static_video.mp4")
        
        result = analyzer.analyze(video_path)
        
        assert isinstance(result, VideoAnalysisResult)
        assert result.motion_detected is False
        assert result.frames_analyzed > 0
        assert result.processing_time > 0
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/motion_video.mp4").exists(),
        reason="Test video not found. Run: python scripts/generate_test_video.py"
    )
    def test_analyze_motion_video(self):
        """Тест анализа видео с движением"""
        analyzer = VideoAnalyzer()
        video_path = Path("tests/fixtures/motion_video.mp4")
        
        result = analyzer.analyze(video_path)
        
        assert isinstance(result, VideoAnalysisResult)
        assert result.motion_detected is True
        assert result.frames_analyzed > 0
        assert result.processing_time > 0
        assert result.motion_percentage > 10.0

