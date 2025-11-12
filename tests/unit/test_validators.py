"""
Тесты для валидаторов
"""
import pytest
from pathlib import Path
import tempfile

from src.utils.validators import VideoValidator
from src.utils.exceptions import (
    VideoTooLargeError,
    UnsupportedFormatError,
    InvalidVideoError
)


class TestVideoValidator:
    """Тесты для VideoValidator"""
    
    def test_validator_initialization(self):
        """Тест инициализации валидатора"""
        validator = VideoValidator(max_size_mb=50)
        
        assert validator.max_size_mb == 50
        assert validator.max_size_bytes == 50 * 1024 * 1024
    
    def test_validate_file_exists_success(self):
        """Тест проверки существования файла - успех"""
        validator = VideoValidator()
        
        # Создаем временный файл
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            temp_path = Path(f.name)
        
        try:
            validator.validate_file_exists(temp_path)
        finally:
            temp_path.unlink()
    
    def test_validate_file_exists_failure(self):
        """Тест проверки существования файла - ошибка"""
        validator = VideoValidator()
        non_existent = Path("/nonexistent/video.mp4")
        
        with pytest.raises(InvalidVideoError):
            validator.validate_file_exists(non_existent)
    
    def test_validate_file_extension_success(self):
        """Тест проверки расширения - успех"""
        validator = VideoValidator()
        
        valid_extensions = [".mp4", ".avi", ".mov", ".mkv"]
        
        for ext in valid_extensions:
            path = Path(f"test{ext}")
            validator.validate_file_extension(path)  # Не должно выбросить исключение
    
    def test_validate_file_extension_failure(self):
        """Тест проверки расширения - ошибка"""
        validator = VideoValidator()
        invalid_path = Path("test.txt")
        
        with pytest.raises(UnsupportedFormatError) as exc_info:
            validator.validate_file_extension(invalid_path)
        
        assert ".txt" in str(exc_info.value)
    
    def test_validate_file_size_success(self):
        """Тест проверки размера - успех"""
        validator = VideoValidator(max_size_mb=10)
        
        # Создаем небольшой файл (1MB)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(b"0" * (1024 * 1024))  # 1MB
            temp_path = Path(f.name)
        
        try:
            validator.validate_file_size(temp_path)  # Не должно выбросить исключение
        finally:
            temp_path.unlink()
    
    def test_validate_file_size_failure(self):
        """Тест проверки размера - ошибка"""
        validator = VideoValidator(max_size_mb=1)
        
        # Создаем файл больше допустимого (2MB)
        with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as f:
            f.write(b"0" * (2 * 1024 * 1024))  # 2MB
            temp_path = Path(f.name)
        
        try:
            with pytest.raises(VideoTooLargeError) as exc_info:
                validator.validate_file_size(temp_path)
            
            assert exc_info.value.max_size_mb == 1
            assert exc_info.value.size_mb > 1
        finally:
            temp_path.unlink()

