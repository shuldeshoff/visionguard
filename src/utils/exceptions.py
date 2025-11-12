"""
Кастомные исключения для VisionGuard
"""


class VisionGuardException(Exception):
    """Базовое исключение для VisionGuard"""
    pass


class VideoProcessingError(VisionGuardException):
    """Ошибка при обработке видео"""
    pass


class VideoTooLargeError(VisionGuardException):
    """Видеофайл слишком большой"""
    def __init__(self, size_mb: float, max_size_mb: int):
        self.size_mb = size_mb
        self.max_size_mb = max_size_mb
        super().__init__(
            f"Video file size ({size_mb:.2f}MB) exceeds maximum allowed size ({max_size_mb}MB)"
        )


class UnsupportedFormatError(VisionGuardException):
    """Неподдерживаемый формат видео"""
    def __init__(self, format_type: str, supported_formats: list):
        self.format_type = format_type
        self.supported_formats = supported_formats
        super().__init__(
            f"Unsupported video format: {format_type}. "
            f"Supported formats: {', '.join(supported_formats)}"
        )


class InvalidVideoError(VisionGuardException):
    """Невалидный или поврежденный видеофайл"""
    pass


class VideoNotFoundError(VisionGuardException):
    """Видеофайл не найден"""
    pass

