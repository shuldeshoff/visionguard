"""
Точка входа FastAPI приложения
"""
from fastapi import FastAPI, status, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from contextlib import asynccontextmanager
import logging
import time

from src.config import settings
from src.db.database import check_db_connection
from src.api.endpoints import router as api_router
from src.utils.exceptions import VisionGuardException

# Настройка логирования
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle manager для FastAPI приложения"""
    # Startup
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    
    # Проверка подключения к БД
    if check_db_connection():
        logger.info("Database connection: OK")
    else:
        logger.warning("Database connection: FAILED")
    
    # Создание директории для загрузок
    from src.utils.file_utils import ensure_upload_dir
    ensure_upload_dir()
    logger.info(f"Upload directory: {settings.UPLOAD_DIR}")
    
    yield
    
    # Shutdown
    logger.info(f"Shutting down {settings.APP_NAME}")


# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Микросервис для анализа видео с производственных камер и выявления нарушений",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Middleware для логирования запросов
@app.middleware("http")
async def log_requests(request: Request, call_next):
    """Логирование всех HTTP запросов"""
    start_time = time.time()
    
    response = await call_next(request)
    
    process_time = time.time() - start_time
    logger.info(
        f"{request.method} {request.url.path} "
        f"completed in {process_time:.3f}s "
        f"with status {response.status_code}"
    )
    
    return response


# Exception handlers
@app.exception_handler(VisionGuardException)
async def visionguard_exception_handler(request: Request, exc: VisionGuardException):
    """Обработчик кастомных исключений VisionGuard"""
    logger.error(f"VisionGuard exception: {exc}")
    return JSONResponse(
        status_code=status.HTTP_400_BAD_REQUEST,
        content={
            "error": exc.__class__.__name__,
            "message": str(exc)
        }
    )


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Обработчик ошибок валидации Pydantic"""
    logger.warning(f"Validation error: {exc}")
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": "ValidationError",
            "message": "Request validation failed",
            "details": exc.errors()
        }
    )


# Подключение роутеров
app.include_router(api_router, prefix="/api/v1")


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running",
        "docs": "/docs",
        "health": "/health"
    }


@app.get("/health")
async def health_check():
    """
    Health check endpoint
    
    Проверяет состояние приложения и подключение к базе данных
    """
    db_status = check_db_connection()
    
    health_status = {
        "status": "healthy" if db_status else "unhealthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "database": "connected" if db_status else "disconnected"
    }
    
    status_code = status.HTTP_200_OK if db_status else status.HTTP_503_SERVICE_UNAVAILABLE
    
    return health_status


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )

