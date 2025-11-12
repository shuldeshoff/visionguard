"""
Точка входа FastAPI приложения
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.config import settings

# Создание FastAPI приложения
app = FastAPI(
    title=settings.APP_NAME,
    description="Микросервис для анализа видео с производственных камер и выявления нарушений",
    version=settings.APP_VERSION,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def root():
    """Корневой endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "status": "running"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "src.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.DEBUG
    )

