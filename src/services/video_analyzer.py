"""
Анализатор видео для детекции движения
"""
import cv2
import numpy as np
from pathlib import Path
from typing import Dict, Optional
import logging
import time

from src.config import settings
from src.utils.exceptions import VideoProcessingError, InvalidVideoError

logger = logging.getLogger(__name__)


class VideoAnalysisResult:
    """
    Результат анализа видео
    """
    def __init__(
        self,
        motion_detected: bool,
        frames_analyzed: int,
        processing_time: float,
        total_frames: int = 0,
        motion_percentage: float = 0.0,
        avg_motion_intensity: float = 0.0
    ):
        self.motion_detected = motion_detected
        self.frames_analyzed = frames_analyzed
        self.processing_time = processing_time
        self.total_frames = total_frames
        self.motion_percentage = motion_percentage
        self.avg_motion_intensity = avg_motion_intensity
    
    def to_dict(self) -> Dict:
        """Преобразование в словарь"""
        return {
            "motion_detected": self.motion_detected,
            "frames_analyzed": self.frames_analyzed,
            "processing_time": round(self.processing_time, 3),
            "total_frames": self.total_frames,
            "motion_percentage": round(self.motion_percentage, 2),
            "avg_motion_intensity": round(self.avg_motion_intensity, 3)
        }


class VideoAnalyzer:
    """
    Анализатор видео для детекции движения
    
    Использует алгоритм Frame Differencing для определения движения в видео
    """
    
    def __init__(
        self,
        frame_sample_rate: Optional[int] = None,
        motion_threshold: Optional[float] = None,
        processing_width: Optional[int] = None,
        processing_height: Optional[int] = None
    ):
        """
        Инициализация анализатора
        
        Args:
            frame_sample_rate: Анализировать каждый N-й кадр (для оптимизации)
            motion_threshold: Порог для определения движения (0.0-1.0)
            processing_width: Ширина кадра для обработки
            processing_height: Высота кадра для обработки
        """
        self.frame_sample_rate = frame_sample_rate or settings.FRAME_SAMPLE_RATE
        self.motion_threshold = motion_threshold or settings.MOTION_THRESHOLD
        self.processing_width = processing_width or settings.PROCESSING_WIDTH
        self.processing_height = processing_height or settings.PROCESSING_HEIGHT
        
        logger.info(
            f"VideoAnalyzer initialized: "
            f"sample_rate={self.frame_sample_rate}, "
            f"threshold={self.motion_threshold}, "
            f"resolution={self.processing_width}x{self.processing_height}"
        )
    
    def analyze(self, video_path: Path) -> VideoAnalysisResult:
        """
        Анализ видео на наличие движения
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            VideoAnalysisResult: Результат анализа
            
        Raises:
            InvalidVideoError: Если не удается открыть видео
            VideoProcessingError: Если произошла ошибка при обработке
        """
        logger.info(f"Starting video analysis: {video_path}")
        start_time = time.time()
        
        # Открытие видео
        cap = cv2.VideoCapture(str(video_path))
        
        if not cap.isOpened():
            raise InvalidVideoError(f"Cannot open video file: {video_path}")
        
        try:
            result = self._process_video(cap)
            
            processing_time = time.time() - start_time
            result.processing_time = processing_time
            
            logger.info(
                f"Video analysis completed: motion={result.motion_detected}, "
                f"frames={result.frames_analyzed}, time={processing_time:.2f}s"
            )
            
            return result
            
        except Exception as e:
            logger.error(f"Error during video processing: {e}")
            raise VideoProcessingError(f"Failed to process video: {e}")
        
        finally:
            cap.release()
    
    def _process_video(self, cap: cv2.VideoCapture) -> VideoAnalysisResult:
        """
        Обработка видео и детекция движения
        
        Args:
            cap: OpenCV VideoCapture объект
            
        Returns:
            VideoAnalysisResult: Результат анализа
        """
        frame_count = 0
        frames_analyzed = 0
        motion_frames = 0
        prev_frame = None
        total_motion_intensity = 0.0
        
        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
        
        logger.debug(f"Total frames in video: {total_frames}")
        
        while True:
            ret, frame = cap.read()
            
            if not ret:
                break
            
            frame_count += 1
            
            # Анализируем только каждый N-й кадр для оптимизации
            if frame_count % self.frame_sample_rate != 0:
                continue
            
            frames_analyzed += 1
            
            # Обработка кадра
            processed_frame = self._preprocess_frame(frame)
            
            if prev_frame is not None:
                # Детекция движения между кадрами
                motion_detected, motion_intensity = self._detect_motion(
                    prev_frame, 
                    processed_frame
                )
                
                if motion_detected:
                    motion_frames += 1
                    total_motion_intensity += motion_intensity
            
            prev_frame = processed_frame
        
        # Вычисление результатов
        motion_percentage = (motion_frames / frames_analyzed * 100) if frames_analyzed > 0 else 0
        avg_motion_intensity = (total_motion_intensity / motion_frames) if motion_frames > 0 else 0
        
        # Определяем наличие движения: если больше 10% кадров содержат движение
        has_motion = motion_percentage > 10.0
        
        logger.debug(
            f"Analysis results: frames_analyzed={frames_analyzed}, "
            f"motion_frames={motion_frames}, motion_percentage={motion_percentage:.2f}%"
        )
        
        return VideoAnalysisResult(
            motion_detected=has_motion,
            frames_analyzed=frames_analyzed,
            processing_time=0.0,  # Will be set later
            total_frames=total_frames,
            motion_percentage=motion_percentage,
            avg_motion_intensity=avg_motion_intensity
        )
    
    def _preprocess_frame(self, frame: np.ndarray) -> np.ndarray:
        """
        Предобработка кадра для анализа
        
        Args:
            frame: Исходный кадр
            
        Returns:
            np.ndarray: Обработанный кадр
        """
        # Изменение размера для оптимизации
        resized = cv2.resize(
            frame, 
            (self.processing_width, self.processing_height)
        )
        
        # Преобразование в grayscale
        gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)
        
        # Применение Gaussian blur для уменьшения шума
        blurred = cv2.GaussianBlur(gray, (21, 21), 0)
        
        return blurred
    
    def _detect_motion(
        self, 
        prev_frame: np.ndarray, 
        curr_frame: np.ndarray
    ) -> tuple[bool, float]:
        """
        Детекция движения между двумя кадрами
        
        Args:
            prev_frame: Предыдущий кадр
            curr_frame: Текущий кадр
            
        Returns:
            tuple: (motion_detected, motion_intensity)
        """
        # Вычисление абсолютной разницы между кадрами
        frame_diff = cv2.absdiff(prev_frame, curr_frame)
        
        # Применение threshold для бинаризации
        _, thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)
        
        # Дилатация для объединения близких изменений
        kernel = np.ones((5, 5), np.uint8)
        dilated = cv2.dilate(thresh, kernel, iterations=2)
        
        # Подсчет процента измененных пикселей
        total_pixels = dilated.size
        changed_pixels = np.count_nonzero(dilated)
        change_percentage = changed_pixels / total_pixels
        
        # Вычисление интенсивности движения
        motion_intensity = float(np.mean(frame_diff) / 255.0)
        
        # Определение наличия движения
        motion_detected = change_percentage > self.motion_threshold
        
        if motion_detected:
            logger.debug(
                f"Motion detected: change={change_percentage:.4f}, "
                f"intensity={motion_intensity:.4f}"
            )
        
        return motion_detected, motion_intensity
    
    def analyze_with_details(self, video_path: Path) -> Dict:
        """
        Анализ видео с подробной информацией
        
        Args:
            video_path: Путь к видеофайлу
            
        Returns:
            dict: Подробные результаты анализа
        """
        result = self.analyze(video_path)
        
        cap = cv2.VideoCapture(str(video_path))
        fps = cap.get(cv2.CAP_PROP_FPS)
        duration = result.total_frames / fps if fps > 0 else 0
        cap.release()
        
        return {
            **result.to_dict(),
            "video_info": {
                "fps": round(fps, 2),
                "duration_seconds": round(duration, 2),
                "resolution": f"{int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))}x{int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))}"
            }
        }

