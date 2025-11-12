"""
Валидаторы для входных данных
"""
from pathlib import Path
from typing import Optional
import logging

try:
    import magic
    HAS_MAGIC = True
except ImportError:
    HAS_MAGIC = False

from src.config import settings
from src.utils.exceptions import (
    VideoTooLargeError,
    UnsupportedFormatError,
    InvalidVideoError
)

logger = logging.getLogger(__name__)


class VideoValidator:
    """
    Валидатор для видеофайлов
    
    Проверяет размер, формат и корректность видеофайлов
    """
    
    # Поддерживаемые MIME типы
    ALLOWED_MIME_TYPES = [
        'video/mp4',
        'video/x-msvideo',      # AVI
        'video/avi',            # AVI (альтернативный)
        'video/quicktime',      # MOV
        'video/x-matroska',     # MKV
    ]
    
    # Поддерживаемые расширения
    ALLOWED_EXTENSIONS = ['.mp4', '.avi', '.mov', '.mkv']
    
    def __init__(self, max_size_mb: Optional[int] = None):
        """
        Инициализация валидатора
        
        Args:
            max_size_mb: Максимальный размер файла в МБ
        """
        self.max_size_mb = max_size_mb or settings.MAX_VIDEO_SIZE_MB
        self.max_size_bytes = self.max_size_mb * 1024 * 1024
    
    def validate_file_size(self, file_path: Path) -> None:
        """
        Проверка размера файла
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            VideoTooLargeError: Если файл слишком большой
        """
        file_size = file_path.stat().st_size
        size_mb = file_size / (1024 * 1024)
        
        if file_size > self.max_size_bytes:
            logger.warning(f"File too large: {size_mb:.2f}MB (max: {self.max_size_mb}MB)")
            raise VideoTooLargeError(size_mb, self.max_size_mb)
        
        logger.debug(f"File size OK: {size_mb:.2f}MB")
    
    def validate_file_extension(self, file_path: Path) -> None:
        """
        Проверка расширения файла
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            UnsupportedFormatError: Если расширение не поддерживается
        """
        ext = file_path.suffix.lower()
        
        if ext not in self.ALLOWED_EXTENSIONS:
            logger.warning(f"Unsupported extension: {ext}")
            raise UnsupportedFormatError(ext, self.ALLOWED_EXTENSIONS)
        
        logger.debug(f"File extension OK: {ext}")
    
    def validate_mime_type(self, file_path: Path) -> None:
        """
        Проверка MIME типа файла
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            UnsupportedFormatError: Если MIME тип не поддерживается
        """
        if not HAS_MAGIC:
            logger.debug("python-magic not installed, skipping MIME type check")
            return
        
        try:
            mime = magic.Magic(mime=True)
            mime_type = mime.from_file(str(file_path))
            
            if mime_type not in self.ALLOWED_MIME_TYPES:
                logger.warning(f"Unsupported MIME type: {mime_type}")
                raise UnsupportedFormatError(mime_type, self.ALLOWED_MIME_TYPES)
            
            logger.debug(f"MIME type OK: {mime_type}")
        except Exception as e:
            logger.debug(f"Error checking MIME type: {e}, skipping check")
    
    def validate_file_exists(self, file_path: Path) -> None:
        """
        Проверка существования файла
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            InvalidVideoError: Если файл не существует или не является файлом
        """
        if not file_path.exists():
            raise InvalidVideoError(f"File does not exist: {file_path}")
        
        if not file_path.is_file():
            raise InvalidVideoError(f"Path is not a file: {file_path}")
    
    def validate(self, file_path: Path) -> None:
        """
        Полная валидация видеофайла
        
        Args:
            file_path: Путь к файлу
            
        Raises:
            VideoTooLargeError: Если файл слишком большой
            UnsupportedFormatError: Если формат не поддерживается
            InvalidVideoError: Если файл некорректный
        """
        logger.info(f"Validating video file: {file_path}")
        
        self.validate_file_exists(file_path)
        self.validate_file_size(file_path)
        self.validate_file_extension(file_path)
        self.validate_mime_type(file_path)
        
        logger.info(f"Video file validation passed: {file_path}")


def validate_video_file(file_path: Path) -> None:
    """
    Удобная функция для валидации видеофайла
    
    Args:
        file_path: Путь к файлу
    """
    validator = VideoValidator()
    validator.validate(file_path)

