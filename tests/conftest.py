"""
Pytest fixtures и конфигурация
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path

from src.main import app
from src.db.database import Base, get_db


# Тестовая база данных в памяти
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def test_db():
    """Fixture для тестовой базы данных"""
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_client(test_db):
    """Fixture для FastAPI тестового клиента с тестовой БД"""
    def override_get_db():
        try:
            yield test_db
        finally:
            pass
    
    app.dependency_overrides[get_db] = override_get_db
    
    with TestClient(app) as client:
        yield client
    
    app.dependency_overrides.clear()


@pytest.fixture(scope="session")
def test_videos_path():
    """Fixture для пути к тестовым видео"""
    return Path("tests/fixtures")


@pytest.fixture(scope="session", autouse=True)
def generate_test_videos(test_videos_path):
    """Автоматическая генерация тестовых видео перед запуском тестов"""
    static_video = test_videos_path / "static_video.mp4"
    
    if not static_video.exists():
        # Генерируем тестовые видео если их нет
        import subprocess
        try:
            subprocess.run(
                ["python", "scripts/generate_test_video.py"],
                check=True,
                capture_output=True
            )
        except subprocess.CalledProcessError:
            pytest.skip("Could not generate test videos")
