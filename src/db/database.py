"""
Настройка подключения к базе данных
"""
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from typing import Generator
import logging

from src.config import settings

logger = logging.getLogger(__name__)

# Создание engine для подключения к PostgreSQL
engine = create_engine(
    settings.DATABASE_URL,
    pool_size=10,           # Размер пула соединений
    max_overflow=20,        # Максимальное количество дополнительных соединений
    pool_timeout=30,        # Timeout ожидания свободного соединения
    pool_recycle=3600,      # Переиспользование соединения через час
    pool_pre_ping=True,     # Проверка соединения перед использованием
    echo=settings.DEBUG,    # Логирование SQL запросов в debug режиме
)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# Base class для ORM моделей
Base = declarative_base()


# Event listeners для логирования
@event.listens_for(engine, "connect")
def receive_connect(dbapi_conn, connection_record):
    """Логирование успешного подключения к БД"""
    logger.info("Database connection established")


@event.listens_for(engine, "close")
def receive_close(dbapi_conn, connection_record):
    """Логирование закрытия соединения с БД"""
    logger.debug("Database connection closed")


def get_db() -> Generator[Session, None, None]:
    """
    Dependency для получения database session в FastAPI endpoints
    
    Yields:
        Session: SQLAlchemy database session
        
    Example:
        @app.get("/items")
        def get_items(db: Session = Depends(get_db)):
            return db.query(Item).all()
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    Инициализация базы данных - создание всех таблиц
    
    Note:
        В production лучше использовать Alembic для миграций
    """
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("Database tables created successfully")
    except Exception as e:
        logger.error(f"Error creating database tables: {e}")
        raise


def check_db_connection() -> bool:
    """
    Проверка подключения к базе данных
    
    Returns:
        bool: True если подключение успешно, False в противном случае
    """
    try:
        with engine.connect() as conn:
            conn.execute("SELECT 1")
        logger.info("Database connection check: OK")
        return True
    except Exception as e:
        logger.error(f"Database connection check failed: {e}")
        return False

