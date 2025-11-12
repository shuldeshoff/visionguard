# API Examples - Примеры использования VisionGuard API

## 🚀 Быстрый старт

### Запуск сервиса

```bash
# Локально
python -m src.main

# Через Docker
docker-compose up --build
```

Сервис будет доступен на: `http://localhost:8000`

**Swagger UI**: `http://localhost:8000/docs`  
**ReDoc**: `http://localhost:8000/redoc`

---

## 📡 API Endpoints

### 1. Health Check

Проверка состояния сервиса и подключения к БД.

```bash
curl http://localhost:8000/health
```

**Ответ:**
```json
{
  "status": "healthy",
  "service": "VisionGuard",
  "version": "0.1.0",
  "database": "connected"
}
```

---

### 2. POST /api/v1/analyze - Анализ видео

Загрузка и анализ видеофайла на наличие движения.

#### Через curl

```bash
curl -X POST "http://localhost:8000/api/v1/analyze" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@/path/to/video.mp4"
```

#### Через Python requests

```python
import requests

url = "http://localhost:8000/api/v1/analyze"
files = {"file": open("video.mp4", "rb")}

response = requests.post(url, files=files)
print(response.json())
```

#### Через Python httpx (async)

```python
import httpx
import asyncio

async def analyze_video():
    async with httpx.AsyncClient() as client:
        with open("video.mp4", "rb") as f:
            files = {"file": f}
            response = await client.post(
                "http://localhost:8000/api/v1/analyze",
                files=files
            )
        return response.json()

result = asyncio.run(analyze_video())
print(result)
```

**Успешный ответ (200):**
```json
{
  "id": 1,
  "filename": "security_camera_001.mp4",
  "motion_detected": true,
  "frames_analyzed": 150,
  "processing_time": 2.34,
  "status": "completed",
  "error_message": null,
  "created_at": "2025-11-12T10:30:00"
}
```

**Ошибка - файл слишком большой (413):**
```json
{
  "error": "VideoTooLargeError",
  "message": "Video file size (150.5MB) exceeds maximum allowed size (100MB)",
  "details": {
    "size_mb": 150.5,
    "max_size_mb": 100
  }
}
```

**Ошибка - неподдерживаемый формат (415):**
```json
{
  "error": "UnsupportedFormatError",
  "message": "Unsupported video format: .txt. Supported formats: .mp4, .avi, .mov, .mkv",
  "details": {
    "format": ".txt",
    "supported": [".mp4", ".avi", ".mov", ".mkv"]
  }
}
```

---

### 3. GET /api/v1/analyses - Список анализов

Получение списка всех проведенных анализов с пагинацией.

#### Базовый запрос

```bash
curl http://localhost:8000/api/v1/analyses
```

#### С пагинацией

```bash
curl "http://localhost:8000/api/v1/analyses?skip=0&limit=10"
```

#### С фильтрацией по статусу

```bash
curl "http://localhost:8000/api/v1/analyses?status_filter=completed"
```

**Ответ:**
```json
{
  "total": 42,
  "items": [
    {
      "id": 1,
      "filename": "video1.mp4",
      "motion_detected": true,
      "frames_analyzed": 150,
      "processing_time": 2.34,
      "status": "completed",
      "error_message": null,
      "created_at": "2025-11-12T10:30:00"
    },
    {
      "id": 2,
      "filename": "video2.mp4",
      "motion_detected": false,
      "frames_analyzed": 75,
      "processing_time": 1.12,
      "status": "completed",
      "error_message": null,
      "created_at": "2025-11-12T10:35:00"
    }
  ]
}
```

---

### 4. GET /api/v1/analyses/{id} - Получить анализ по ID

Получение информации о конкретном анализе.

```bash
curl http://localhost:8000/api/v1/analyses/1
```

**Ответ:**
```json
{
  "id": 1,
  "filename": "security_camera_001.mp4",
  "motion_detected": true,
  "frames_analyzed": 150,
  "processing_time": 2.34,
  "status": "completed",
  "error_message": null,
  "created_at": "2025-11-12T10:30:00"
}
```

**Ошибка - не найдено (404):**
```json
{
  "error": "NotFound",
  "message": "Analysis with ID 999 not found"
}
```

---

### 5. GET /api/v1/metrics - Prometheus метрики

Получение метрик для мониторинга.

```bash
curl http://localhost:8000/api/v1/metrics
```

**Ответ (Prometheus format):**
```
# HELP videos_processed_total Total number of videos processed
# TYPE videos_processed_total counter
videos_processed_total 42.0

# HELP videos_processing_time_seconds Average video processing time in seconds
# TYPE videos_processing_time_seconds gauge
videos_processing_time_seconds 2.34

# HELP videos_processing_errors_total Total number of processing errors
# TYPE videos_processing_errors_total counter
videos_processing_errors_total{error_type="VideoTooLargeError"} 3.0
videos_processing_errors_total{error_type="UnsupportedFormatError"} 1.0

# HELP videos_motion_detected_total Total number of videos with detected motion
# TYPE videos_motion_detected_total counter
videos_motion_detected_total 28.0

# HELP processing_duration_seconds Video processing duration distribution
# TYPE processing_duration_seconds histogram
processing_duration_seconds_bucket{le="0.5"} 5.0
processing_duration_seconds_bucket{le="1.0"} 12.0
processing_duration_seconds_bucket{le="2.0"} 25.0
processing_duration_seconds_bucket{le="5.0"} 38.0
processing_duration_seconds_bucket{le="10.0"} 42.0
processing_duration_seconds_bucket{le="+Inf"} 42.0
processing_duration_seconds_count 42.0
processing_duration_seconds_sum 98.52
```

---

## 🧪 Примеры использования

### Пакетная обработка видео

```python
import requests
from pathlib import Path

def analyze_videos(video_dir: Path):
    """Анализ всех видео в директории"""
    url = "http://localhost:8000/api/v1/analyze"
    results = []
    
    for video_file in video_dir.glob("*.mp4"):
        print(f"Analyzing: {video_file.name}")
        
        with open(video_file, "rb") as f:
            files = {"file": (video_file.name, f, "video/mp4")}
            response = requests.post(url, files=files)
        
        if response.status_code == 200:
            result = response.json()
            results.append(result)
            print(f"  ✓ Motion detected: {result['motion_detected']}")
        else:
            print(f"  ✗ Error: {response.json()}")
    
    return results

# Использование
results = analyze_videos(Path("./videos"))
print(f"\nTotal analyzed: {len(results)}")
```

### Фильтрация результатов

```python
import requests

def get_videos_with_motion():
    """Получить все видео с обнаруженным движением"""
    url = "http://localhost:8000/api/v1/analyses"
    response = requests.get(url, params={"limit": 100})
    
    data = response.json()
    
    with_motion = [
        item for item in data["items"]
        if item["motion_detected"]
    ]
    
    return with_motion

videos = get_videos_with_motion()
for video in videos:
    print(f"{video['filename']}: {video['processing_time']}s")
```

### Мониторинг производительности

```python
import requests
import re

def get_metrics_summary():
    """Получить сводку метрик"""
    response = requests.get("http://localhost:8000/api/v1/metrics")
    content = response.text
    
    metrics = {}
    
    # Парсинг метрик
    for line in content.split('\n'):
        if line.startswith('videos_processed_total'):
            metrics['total_processed'] = float(line.split()[-1])
        elif line.startswith('videos_processing_time_seconds'):
            metrics['avg_time'] = float(line.split()[-1])
        elif line.startswith('videos_motion_detected_total'):
            metrics['with_motion'] = float(line.split()[-1])
    
    return metrics

metrics = get_metrics_summary()
print(f"Total processed: {metrics.get('total_processed', 0)}")
print(f"Average time: {metrics.get('avg_time', 0):.2f}s")
print(f"With motion: {metrics.get('with_motion', 0)}")
```

---

## 🔧 Postman Collection

### Импорт в Postman

Создайте новую коллекцию "VisionGuard" и добавьте следующие запросы:

#### 1. Analyze Video

```
POST http://localhost:8000/api/v1/analyze
Body: form-data
  - Key: file
  - Type: File
  - Value: [Select video file]
```

#### 2. Get All Analyses

```
GET http://localhost:8000/api/v1/analyses?skip=0&limit=10
```

#### 3. Get Analysis by ID

```
GET http://localhost:8000/api/v1/analyses/1
```

#### 4. Get Metrics

```
GET http://localhost:8000/api/v1/metrics
```

---

## 🐛 Обработка ошибок

### Типы ошибок

| Код | Ошибка | Описание |
|-----|--------|----------|
| 413 | VideoTooLargeError | Файл превышает 100MB |
| 415 | UnsupportedFormatError | Неподдерживаемый формат |
| 422 | ValidationError | Ошибка валидации запроса |
| 500 | VideoProcessingError | Ошибка при обработке видео |

### Пример обработки ошибок

```python
import requests

def safe_analyze_video(video_path):
    """Безопасный анализ с обработкой ошибок"""
    try:
        with open(video_path, "rb") as f:
            files = {"file": f}
            response = requests.post(
                "http://localhost:8000/api/v1/analyze",
                files=files
            )
        
        if response.status_code == 200:
            return {"success": True, "data": response.json()}
        elif response.status_code == 413:
            return {"success": False, "error": "File too large"}
        elif response.status_code == 415:
            return {"success": False, "error": "Unsupported format"}
        else:
            return {"success": False, "error": response.json()}
    
    except FileNotFoundError:
        return {"success": False, "error": "File not found"}
    except Exception as e:
        return {"success": False, "error": str(e)}

result = safe_analyze_video("video.mp4")
if result["success"]:
    print(f"Motion detected: {result['data']['motion_detected']}")
else:
    print(f"Error: {result['error']}")
```

---

## 📊 Интеграция с Grafana

### Prometheus scrape config

```yaml
scrape_configs:
  - job_name: 'visionguard'
    scrape_interval: 15s
    static_configs:
      - targets: ['localhost:8000']
    metrics_path: '/api/v1/metrics'
```

### Grafana queries

```promql
# Всего обработано видео
videos_processed_total

# Среднее время обработки
rate(processing_duration_seconds_sum[5m]) / rate(processing_duration_seconds_count[5m])

# Процент видео с движением
(videos_motion_detected_total / videos_processed_total) * 100

# Количество ошибок за последний час
increase(videos_processing_errors_total[1h])
```

---

## 🔐 Аутентификация (будущее)

В будущих версиях планируется добавить JWT аутентификацию:

```python
headers = {
    "Authorization": "Bearer YOUR_JWT_TOKEN"
}

response = requests.post(url, files=files, headers=headers)
```

---

**Версия API**: 1.0  
**Дата обновления**: 12 ноября 2025

