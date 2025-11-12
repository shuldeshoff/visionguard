"""
Утилиты для работы с файлами
"""
import os
import tempfile
import shutil
from pathlib import Path
from typing import BinaryIO
import logging

from src.config import settings

logger = logging.getLogger(__name__)


def ensure_upload_dir() -> Path:
    """
    Создание директории для загруженных файлов если её нет
    
    Returns:
        Path: Путь к директории загрузок
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    upload_dir.mkdir(parents=True, exist_ok=True)
    return upload_dir


def save_upload_file(upload_file: BinaryIO, filename: str) -> Path:
    """
    Сохранение загруженного файла во временную директорию
    
    Args:
        upload_file: Файловый объект
        filename: Имя файла
        
    Returns:
        Path: Путь к сохраненному файлу
    """
    upload_dir = ensure_upload_dir()
    
    # Создаем уникальное имя файла с timestamp
    import time
    timestamp = int(time.time() * 1000)
    safe_filename = f"{timestamp}_{filename}"
    file_path = upload_dir / safe_filename
    
    logger.info(f"Saving uploaded file to: {file_path}")
    
    try:
        with open(file_path, "wb") as f:
            shutil.copyfileobj(upload_file, f)
        
        logger.info(f"File saved successfully: {file_path}")
        return file_path
        
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        # Попытка удалить частично записанный файл
        if file_path.exists():
            file_path.unlink()
        raise


def create_temp_file(suffix: str = ".mp4") -> Path:
    """
    Создание временного файла
    
    Args:
        suffix: Расширение файла
        
    Returns:
        Path: Путь к временному файлу
    """
    fd, path = tempfile.mkstemp(suffix=suffix, dir=settings.UPLOAD_DIR)
    os.close(fd)
    return Path(path)


def cleanup_file(file_path: Path) -> None:
    """
    Безопасное удаление файла
    
    Args:
        file_path: Путь к файлу
    """
    try:
        if file_path.exists():
            file_path.unlink()
            logger.info(f"File deleted: {file_path}")
    except Exception as e:
        logger.warning(f"Failed to delete file {file_path}: {e}")


def cleanup_old_files(max_age_hours: int = 24) -> int:
    """
    Очистка старых файлов из директории загрузок
    
    Args:
        max_age_hours: Максимальный возраст файлов в часах
        
    Returns:
        int: Количество удаленных файлов
    """
    upload_dir = Path(settings.UPLOAD_DIR)
    
    if not upload_dir.exists():
        return 0
    
    import time
    current_time = time.time()
    max_age_seconds = max_age_hours * 3600
    deleted_count = 0
    
    logger.info(f"Cleaning up old files (older than {max_age_hours}h)")
    
    for file_path in upload_dir.iterdir():
        if not file_path.is_file():
            continue
        
        file_age = current_time - file_path.stat().st_mtime
        
        if file_age > max_age_seconds:
            try:
                file_path.unlink()
                deleted_count += 1
                logger.debug(f"Deleted old file: {file_path}")
            except Exception as e:
                logger.warning(f"Failed to delete {file_path}: {e}")
    
    logger.info(f"Cleaned up {deleted_count} old files")
    return deleted_count


def get_file_size_mb(file_path: Path) -> float:
    """
    Получение размера файла в МБ
    
    Args:
        file_path: Путь к файлу
        
    Returns:
        float: Размер в МБ
    """
    size_bytes = file_path.stat().st_size
    return size_bytes / (1024 * 1024)

