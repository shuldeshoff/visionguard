"""
Скрипт инициализации базы данных

Использование:
    python scripts/init_db.py
"""
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.db.database import engine, Base, check_db_connection
from src.db.models import VideoAnalysis
import logging

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def init_database():
    """Инициализация базы данных"""
    logger.info("Starting database initialization...")
    
    # Проверка подключения
    logger.info("Checking database connection...")
    if not check_db_connection():
        logger.error("Failed to connect to database. Please check your configuration.")
        sys.exit(1)
    
    logger.info("Database connection successful!")
    
    # Создание таблиц
    logger.info("Creating database tables...")
    try:
        Base.metadata.create_all(bind=engine)
        logger.info("✓ Tables created successfully!")
        
        # Вывод списка созданных таблиц
        tables = Base.metadata.tables.keys()
        logger.info(f"Created tables: {', '.join(tables)}")
        
    except Exception as e:
        logger.error(f"Error creating tables: {e}")
        sys.exit(1)
    
    logger.info("Database initialization completed successfully!")


def drop_all_tables():
    """Удаление всех таблиц (для тестирования)"""
    logger.warning("Dropping all tables...")
    try:
        Base.metadata.drop_all(bind=engine)
        logger.info("✓ All tables dropped successfully!")
    except Exception as e:
        logger.error(f"Error dropping tables: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Database initialization script")
    parser.add_argument(
        "--drop",
        action="store_true",
        help="Drop all tables before creating (DESTRUCTIVE!)"
    )
    
    args = parser.parse_args()
    
    if args.drop:
        response = input("Are you sure you want to drop all tables? (yes/no): ")
        if response.lower() == "yes":
            drop_all_tables()
        else:
            logger.info("Operation cancelled.")
            sys.exit(0)
    
    init_database()

