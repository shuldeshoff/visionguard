"""
Pytest fixtures и конфигурация
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# TODO: Добавить fixtures после создания моделей БД


@pytest.fixture
def test_client():
    """Fixture для FastAPI тестового клиента"""
    from src.main import app
    return TestClient(app)

