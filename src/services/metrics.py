"""
Prometheus метрики для мониторинга
"""
from prometheus_client import Counter, Gauge, Histogram, generate_latest, CONTENT_TYPE_LATEST
import logging

logger = logging.getLogger(__name__)


# Counter - всегда растёт
videos_processed_total = Counter(
    'videos_processed_total',
    'Total number of videos processed'
)

videos_processing_errors_total = Counter(
    'videos_processing_errors_total',
    'Total number of processing errors',
    ['error_type']
)

videos_motion_detected_total = Counter(
    'videos_motion_detected_total',
    'Total number of videos with detected motion'
)

# Gauge - может увеличиваться и уменьшаться
videos_processing_time_seconds = Gauge(
    'videos_processing_time_seconds',
    'Average video processing time in seconds'
)

# Histogram - для распределения времени обработки
processing_duration_histogram = Histogram(
    'processing_duration_seconds',
    'Video processing duration distribution',
    buckets=(0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0, 120.0)
)


class MetricsCollector:
    """
    Класс для сбора и обновления метрик
    """
    
    @staticmethod
    def record_video_processed() -> None:
        """Записать успешно обработанное видео"""
        videos_processed_total.inc()
        logger.debug("Metric: videos_processed_total incremented")
    
    @staticmethod
    def record_processing_error(error_type: str) -> None:
        """
        Записать ошибку обработки
        
        Args:
            error_type: Тип ошибки
        """
        videos_processing_errors_total.labels(error_type=error_type).inc()
        logger.debug(f"Metric: processing error recorded - {error_type}")
    
    @staticmethod
    def record_motion_detected() -> None:
        """Записать обнаружение движения"""
        videos_motion_detected_total.inc()
        logger.debug("Metric: motion detected recorded")
    
    @staticmethod
    def update_processing_time(seconds: float) -> None:
        """
        Обновить время обработки
        
        Args:
            seconds: Время обработки в секундах
        """
        videos_processing_time_seconds.set(seconds)
        processing_duration_histogram.observe(seconds)
        logger.debug(f"Metric: processing time updated - {seconds:.2f}s")
    
    @staticmethod
    def get_metrics_output() -> tuple[str, str]:
        """
        Получить метрики в формате Prometheus
        
        Returns:
            tuple: (metrics_content, content_type)
        """
        return generate_latest(), CONTENT_TYPE_LATEST


# Singleton instance
metrics_collector = MetricsCollector()

