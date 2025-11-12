"""
E2E тесты полного цикла обработки видео
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path

from src.main import app

client = TestClient(app)


@pytest.mark.skipif(
    not Path("tests/fixtures/motion_video.mp4").exists(),
    reason="Test video not found"
)
class TestFullVideoAnalysisFlow:
    """Тесты полного цикла анализа видео"""
    
    def test_complete_analysis_flow(self):
        """
        Тест полного цикла: загрузка → анализ → сохранение → получение
        """
        video_path = Path("tests/fixtures/motion_video.mp4")
        
        # 1. Загрузка и анализ видео
        with open(video_path, "rb") as f:
            files = {"file": ("motion_video.mp4", f, "video/mp4")}
            analyze_response = client.post("/api/v1/analyze", files=files)
        
        assert analyze_response.status_code == 200
        analysis_data = analyze_response.json()
        analysis_id = analysis_data["id"]
        
        # 2. Получение конкретного анализа по ID
        get_response = client.get(f"/api/v1/analyses/{analysis_id}")
        
        assert get_response.status_code == 200
        retrieved_data = get_response.json()
        
        assert retrieved_data["id"] == analysis_id
        assert retrieved_data["filename"] == analysis_data["filename"]
        assert retrieved_data["motion_detected"] == analysis_data["motion_detected"]
        
        # 3. Проверка что анализ присутствует в списке
        list_response = client.get("/api/v1/analyses")
        
        assert list_response.status_code == 200
        list_data = list_response.json()
        
        # Ищем наш анализ в списке
        found = any(item["id"] == analysis_id for item in list_data["items"])
        assert found, f"Analysis {analysis_id} not found in list"
        
        # 4. Проверка обновления метрик
        metrics_response = client.get("/api/v1/metrics")
        
        assert metrics_response.status_code == 200
        metrics_content = metrics_response.text
        
        # Метрики должны быть обновлены
        assert "videos_processed_total" in metrics_content
    
    def test_multiple_videos_analysis(self):
        """Тест анализа нескольких видео подряд"""
        video_paths = [
            Path("tests/fixtures/static_video.mp4"),
            Path("tests/fixtures/motion_video.mp4")
        ]
        
        analysis_ids = []
        
        for video_path in video_paths:
            if not video_path.exists():
                continue
            
            with open(video_path, "rb") as f:
                files = {"file": (video_path.name, f, "video/mp4")}
                response = client.post("/api/v1/analyze", files=files)
            
            assert response.status_code == 200
            data = response.json()
            analysis_ids.append(data["id"])
        
        # Проверяем что все анализы были созданы
        assert len(analysis_ids) > 0
        
        # Проверяем что все ID уникальны
        assert len(analysis_ids) == len(set(analysis_ids))
        
        # Проверяем что все анализы можно получить
        for analysis_id in analysis_ids:
            response = client.get(f"/api/v1/analyses/{analysis_id}")
            assert response.status_code == 200

