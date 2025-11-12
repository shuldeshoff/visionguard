"""
API endpoints для VisionGuard
"""
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from fastapi.responses import Response
from sqlalchemy.orm import Session
from pathlib import Path
import logging

from src.api.models import (
    VideoAnalysisResponse,
    AnalysisListResponse,
    ErrorResponse
)
from src.db.database import get_db
from src.db.repository import VideoAnalysisRepository
from src.services.video_analyzer import VideoAnalyzer
from src.services.metrics import metrics_collector
from src.utils.file_utils import save_upload_file, cleanup_file
from src.utils.validators import validate_video_file
from src.utils.exceptions import (
    VideoTooLargeError,
    UnsupportedFormatError,
    InvalidVideoError,
    VideoProcessingError
)

logger = logging.getLogger(__name__)

# Создание роутера
router = APIRouter(tags=["video-analysis"])


@router.post(
    "/analyze",
    response_model=VideoAnalysisResponse,
    status_code=status.HTTP_200_OK,
    summary="Анализ видео на наличие движения",
    description="Загружает видеофайл, анализирует его на наличие движения и сохраняет результаты в БД",
    responses={
        200: {"description": "Видео успешно проанализировано"},
        413: {"model": ErrorResponse, "description": "Файл слишком большой"},
        415: {"model": ErrorResponse, "description": "Неподдерживаемый формат"},
        422: {"model": ErrorResponse, "description": "Ошибка валидации"},
        500: {"model": ErrorResponse, "description": "Внутренняя ошибка сервера"}
    }
)
async def analyze_video(
    file: UploadFile = File(..., description="Видеофайл для анализа"),
    db: Session = Depends(get_db)
) -> VideoAnalysisResponse:
    """
    Анализ видеофайла на наличие движения
    
    Процесс:
    1. Валидация видеофайла (размер, формат)
    2. Сохранение во временную директорию
    3. Анализ с помощью OpenCV
    4. Сохранение результатов в БД
    5. Обновление метрик Prometheus
    6. Очистка временных файлов
    
    Args:
        file: Загруженный видеофайл
        db: Database session
        
    Returns:
        VideoAnalysisResponse: Результаты анализа
        
    Raises:
        HTTPException: При ошибках валидации или обработки
    """
    video_path = None
    
    try:
        logger.info(f"Received video for analysis: {file.filename}")
        
        # 1. Сохранение файла
        video_path = save_upload_file(file.file, file.filename)
        logger.info(f"Video saved to: {video_path}")
        
        # 2. Валидация
        try:
            validate_video_file(video_path)
        except VideoTooLargeError as e:
            logger.warning(f"Video too large: {e}")
            metrics_collector.record_processing_error("VideoTooLargeError")
            raise HTTPException(
                status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
                detail={
                    "error": "VideoTooLargeError",
                    "message": str(e),
                    "details": {
                        "size_mb": e.size_mb,
                        "max_size_mb": e.max_size_mb
                    }
                }
            )
        except UnsupportedFormatError as e:
            logger.warning(f"Unsupported format: {e}")
            metrics_collector.record_processing_error("UnsupportedFormatError")
            raise HTTPException(
                status_code=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE,
                detail={
                    "error": "UnsupportedFormatError",
                    "message": str(e),
                    "details": {
                        "format": e.format_type,
                        "supported": e.supported_formats
                    }
                }
            )
        except InvalidVideoError as e:
            logger.warning(f"Invalid video: {e}")
            metrics_collector.record_processing_error("InvalidVideoError")
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail={
                    "error": "InvalidVideoError",
                    "message": str(e)
                }
            )
        
        # 3. Анализ видео
        analyzer = VideoAnalyzer()
        try:
            result = analyzer.analyze(video_path)
            logger.info(f"Analysis completed: motion={result.motion_detected}")
        except VideoProcessingError as e:
            logger.error(f"Processing error: {e}")
            metrics_collector.record_processing_error("VideoProcessingError")
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail={
                    "error": "VideoProcessingError",
                    "message": str(e)
                }
            )
        
        # 4. Сохранение в БД
        repo = VideoAnalysisRepository(db)
        analysis = repo.create(
            filename=file.filename,
            motion_detected=result.motion_detected,
            frames_analyzed=result.frames_analyzed,
            processing_time=result.processing_time,
            status="completed"
        )
        
        # 5. Обновление метрик
        metrics_collector.record_video_processed()
        metrics_collector.update_processing_time(result.processing_time)
        
        if result.motion_detected:
            metrics_collector.record_motion_detected()
        
        logger.info(f"Analysis saved with ID: {analysis.id}")
        
        # 6. Возврат результата
        return VideoAnalysisResponse(
            id=analysis.id,
            filename=analysis.filename,
            motion_detected=analysis.motion_detected,
            frames_analyzed=analysis.frames_analyzed,
            processing_time=analysis.processing_time,
            status=analysis.status,
            error_message=analysis.error_message,
            created_at=analysis.created_at
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Unexpected error: {e}", exc_info=True)
        metrics_collector.record_processing_error("UnexpectedError")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "error": "InternalServerError",
                "message": "An unexpected error occurred during video processing"
            }
        )
    finally:
        # Очистка временных файлов
        if video_path:
            cleanup_file(video_path)


@router.get(
    "/analyses",
    response_model=AnalysisListResponse,
    summary="Получить список всех анализов",
    description="Возвращает список всех проведенных анализов с пагинацией"
)
async def get_analyses(
    skip: int = 0,
    limit: int = 100,
    status_filter: str = None,
    db: Session = Depends(get_db)
) -> AnalysisListResponse:
    """
    Получение списка анализов с пагинацией
    
    Args:
        skip: Количество пропускаемых записей
        limit: Максимальное количество записей
        status_filter: Фильтр по статусу
        db: Database session
        
    Returns:
        AnalysisListResponse: Список анализов
    """
    repo = VideoAnalysisRepository(db)
    
    items = repo.get_all(skip=skip, limit=limit, status=status_filter)
    total = repo.count_total()
    
    return AnalysisListResponse(
        total=total,
        items=[
            VideoAnalysisResponse(
                id=item.id,
                filename=item.filename,
                motion_detected=item.motion_detected,
                frames_analyzed=item.frames_analyzed,
                processing_time=item.processing_time,
                status=item.status,
                error_message=item.error_message,
                created_at=item.created_at
            )
            for item in items
        ]
    )


@router.get(
    "/analyses/{analysis_id}",
    response_model=VideoAnalysisResponse,
    summary="Получить анализ по ID",
    description="Возвращает информацию о конкретном анализе",
    responses={
        404: {"description": "Анализ не найден"}
    }
)
async def get_analysis(
    analysis_id: int,
    db: Session = Depends(get_db)
) -> VideoAnalysisResponse:
    """
    Получение анализа по ID
    
    Args:
        analysis_id: ID анализа
        db: Database session
        
    Returns:
        VideoAnalysisResponse: Информация об анализе
        
    Raises:
        HTTPException: Если анализ не найден
    """
    repo = VideoAnalysisRepository(db)
    analysis = repo.get_by_id(analysis_id)
    
    if not analysis:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={
                "error": "NotFound",
                "message": f"Analysis with ID {analysis_id} not found"
            }
        )
    
    return VideoAnalysisResponse(
        id=analysis.id,
        filename=analysis.filename,
        motion_detected=analysis.motion_detected,
        frames_analyzed=analysis.frames_analyzed,
        processing_time=analysis.processing_time,
        status=analysis.status,
        error_message=analysis.error_message,
        created_at=analysis.created_at
    )


@router.get(
    "/metrics",
    summary="Prometheus метрики",
    description="Возвращает метрики в формате Prometheus для мониторинга"
)
async def get_metrics() -> Response:
    """
    Получение метрик Prometheus
    
    Метрики:
    - videos_processed_total: Количество обработанных видео
    - videos_processing_time_seconds: Среднее время обработки
    - videos_processing_errors_total: Количество ошибок
    - videos_motion_detected_total: Количество видео с движением
    - processing_duration_seconds: Распределение времени обработки
    
    Returns:
        Response: Метрики в формате Prometheus
    """
    metrics_content, content_type = metrics_collector.get_metrics_output()
    return Response(content=metrics_content, media_type=content_type)

