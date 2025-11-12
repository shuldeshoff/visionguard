"""
Интеграционные тесты для API endpoints
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import io

from src.main import app

client = TestClient(app)


class TestRootEndpoints:
    """Тесты для корневых endpoints"""
    
    def test_root_endpoint(self):
        """Тест корневого endpoint"""
        response = client.get("/")
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "VisionGuard"
        assert data["status"] == "running"
        assert "version" in data
    
    def test_health_endpoint(self):
        """Тест health check endpoint"""
        response = client.get("/health")
        
        assert response.status_code == 200
        data = response.json()
        assert "status" in data
        assert "service" in data
        assert "database" in data


class TestAnalyzeEndpoint:
    """Тесты для POST /api/v1/analyze endpoint"""
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/static_video.mp4").exists(),
        reason="Test video not found"
    )
    def test_analyze_static_video_success(self):
        """Тест анализа статичного видео - успех"""
        video_path = Path("tests/fixtures/static_video.mp4")
        
        with open(video_path, "rb") as f:
            files = {"file": ("static_video.mp4", f, "video/mp4")}
            response = client.post("/api/v1/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert "id" in data
        assert data["filename"] == "static_video.mp4"
        assert "motion_detected" in data
        assert data["motion_detected"] is False  # Статичное видео
        assert data["frames_analyzed"] > 0
        assert data["processing_time"] > 0
        assert data["status"] == "completed"
    
    @pytest.mark.skipif(
        not Path("tests/fixtures/motion_video.mp4").exists(),
        reason="Test video not found"
    )
    def test_analyze_motion_video_success(self):
        """Тест анализа видео с движением - успех"""
        video_path = Path("tests/fixtures/motion_video.mp4")
        
        with open(video_path, "rb") as f:
            files = {"file": ("motion_video.mp4", f, "video/mp4")}
            response = client.post("/api/v1/analyze", files=files)
        
        assert response.status_code == 200
        data = response.json()
        
        assert data["filename"] == "motion_video.mp4"
        assert data["motion_detected"] is True  # Видео с движением
        assert data["frames_analyzed"] > 0
        assert data["status"] == "completed"
    
    def test_analyze_unsupported_format(self):
        """Тест загрузки файла неподдерживаемого формата"""
        # Создаем поддельный текстовый файл
        fake_file = io.BytesIO(b"This is not a video")
        files = {"file": ("test.txt", fake_file, "text/plain")}
        
        response = client.post("/api/v1/analyze", files=files)
        
        assert response.status_code == 415  # Unsupported Media Type
        data = response.json()
        assert "error" in data
    
    def test_analyze_no_file(self):
        """Тест запроса без файла"""
        response = client.post("/api/v1/analyze")
        
        assert response.status_code == 422  # Validation Error


class TestAnalysesEndpoints:
    """Тесты для endpoints списка анализов"""
    
    def test_get_analyses_list(self):
        """Тест получения списка анализов"""
        response = client.get("/api/v1/analyses")
        
        assert response.status_code == 200
        data = response.json()
        
        assert "total" in data
        assert "items" in data
        assert isinstance(data["items"], list)
    
    def test_get_analyses_with_pagination(self):
        """Тест пагинации списка анализов"""
        response = client.get("/api/v1/analyses?skip=0&limit=10")
        
        assert response.status_code == 200
        data = response.json()
        
        assert len(data["items"]) <= 10
    
    def test_get_analysis_by_id_not_found(self):
        """Тест получения несуществующего анализа"""
        response = client.get("/api/v1/analyses/999999")
        
        assert response.status_code == 404
        data = response.json()
        assert "error" in data


class TestMetricsEndpoint:
    """Тесты для GET /api/v1/metrics endpoint"""
    
    def test_metrics_endpoint(self):
        """Тест получения Prometheus метрик"""
        response = client.get("/api/v1/metrics")
        
        assert response.status_code == 200
        assert "text/plain" in response.headers["content-type"]
        
        content = response.text
        
        # Проверяем наличие ключевых метрик
        assert "videos_processed_total" in content
        assert "videos_processing_time_seconds" in content
        assert "videos_processing_errors_total" in content
        assert "videos_motion_detected_total" in content
    
    def test_metrics_format(self):
        """Тест формата Prometheus метрик"""
        response = client.get("/api/v1/metrics")
        
        content = response.text
        lines = content.split("\n")
        
        # Проверяем что есть строки с HELP и TYPE
        help_lines = [line for line in lines if line.startswith("# HELP")]
        type_lines = [line for line in lines if line.startswith("# TYPE")]
        
        assert len(help_lines) > 0
        assert len(type_lines) > 0

