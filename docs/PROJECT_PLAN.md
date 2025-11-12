# VisionGuard - План Разработки Микросервиса

## 🎯 Цель проекта

Разработать микросервис для анализа видео с производственных камер и выявления нарушений техники безопасности. 

**Текущая задача**: Реализовать минимальный рабочий прототип (MVP) с фокусом на инженерную основу и качество кода.

---

## 📋 Техническое задание

### Функциональные требования

#### 1. API Endpoints

**POST /analyze**
- Принимает видеофайл через multipart/form-data
- Проверяет наличие движения в кадре (OpenCV)
- Сохраняет результаты в PostgreSQL
- Возвращает результат анализа

**GET /metrics**
- Отдаёт метрики в формате Prometheus:
  - Количество обработанных видео
  - Среднее время обработки
  - Количество ошибок

**GET /health** (дополнительно)
- Проверка работоспособности сервиса
- Проверка подключения к БД

#### 2. База данных

**Таблица: video_analyses**
```sql
CREATE TABLE video_analyses (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    motion_detected BOOLEAN NOT NULL,
    frames_analyzed INTEGER NOT NULL,
    processing_time FLOAT NOT NULL,
    status VARCHAR(50) NOT NULL,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_status ON video_analyses(status);
CREATE INDEX idx_created_at ON video_analyses(created_at);
```

#### 3. Метрики Prometheus

```python
# Counter - количество обработанных видео
videos_processed_total

# Gauge - среднее время обработки
videos_processing_time_seconds

# Counter - количество ошибок
videos_processing_errors_total

# Counter - количество видео с движением (дополнительно)
videos_motion_detected_total
```

### Нефункциональные требования

- **Производительность**: обработка видео до 100MB за разумное время
- **Надёжность**: корректная обработка ошибок и граничных случаев
- **Масштабируемость**: готовность к добавлению очередей (Celery/RabbitMQ)
- **Мониторинг**: полное логирование и метрики
- **Безопасность**: валидация входных файлов
- **Документация**: Swagger UI из коробки (FastAPI)

---

## 🗂️ Структура проекта

```
visionguard/
├── src/                          # Исходный код
│   ├── __init__.py
│   ├── main.py                   # Точка входа FastAPI приложения
│   ├── config.py                 # Конфигурация через Pydantic Settings
│   │
│   ├── api/                      # API слой
│   │   ├── __init__.py
│   │   ├── endpoints.py          # API routes
│   │   ├── models.py             # Pydantic модели (request/response)
│   │   └── dependencies.py       # FastAPI dependencies
│   │
│   ├── services/                 # Бизнес-логика
│   │   ├── __init__.py
│   │   ├── video_analyzer.py    # Анализ видео через OpenCV
│   │   └── metrics.py            # Prometheus metrics
│   │
│   ├── db/                       # Слой базы данных
│   │   ├── __init__.py
│   │   ├── database.py           # SQLAlchemy engine и session
│   │   ├── models.py             # ORM модели
│   │   └── repository.py         # Паттерн Repository
│   │
│   └── utils/                    # Утилиты
│       ├── __init__.py
│       ├── logging_config.py     # Настройка логирования
│       └── validators.py         # Валидаторы файлов
│
├── scripts/                      # Вспомогательные скрипты
│   ├── init_db.py               # Инициализация БД
│   └── generate_test_video.py   # Генерация тестовых видео
│
├── tests/                        # Тесты
│   ├── __init__.py
│   ├── conftest.py              # Pytest fixtures
│   ├── unit/                    # Unit-тесты
│   │   ├── test_video_analyzer.py
│   │   ├── test_metrics.py
│   │   └── test_validators.py
│   ├── integration/             # Интеграционные тесты
│   │   ├── test_api.py
│   │   └── test_database.py
│   └── fixtures/                # Тестовые данные
│       └── sample_video.mp4
│
├── docker/                       # Docker конфигурация
│   ├── Dockerfile               # Dockerfile для приложения
│   ├── Dockerfile.dev           # Dockerfile для разработки
│   └── init.sql                 # SQL скрипт инициализации
│
├── docs/                         # Документация
│   ├── PROJECT_PLAN.md          # Этот файл
│   ├── ANALYSIS.md              # Анализ задания
│   ├── ARCHITECTURE.md          # Архитектура системы
│   └── API.md                   # Подробная API документация
│
├── .github/                      # GitHub настройки
│   └── workflows/
│       └── ci.yml               # CI/CD pipeline
│
├── docker-compose.yml            # Docker Compose конфигурация
├── docker-compose.dev.yml        # Docker Compose для разработки
├── requirements.txt              # Production зависимости
├── requirements-dev.txt          # Dev зависимости
├── .env.example                  # Пример переменных окружения
├── .gitignore                    # Git ignore
├── pytest.ini                    # Pytest конфигурация
├── setup.py                      # Package setup
├── README.md                     # Главная документация
└── LICENSE                       # Лицензия

```

---

## 🚀 Этапы Разработки

### 📦 Этап 1: Инфраструктура и настройка (День 1)

**Цель**: Создать базовую структуру проекта и настроить окружение

#### Задачи:
- [x] Создать репозиторий на GitHub
- [x] Создать структуру директорий
- [ ] Настроить `.gitignore` для Python проектов
- [ ] Создать `requirements.txt` с основными зависимостями:
  ```
  fastapi==0.104.1
  uvicorn[standard]==0.24.0
  sqlalchemy==2.0.23
  psycopg2-binary==2.9.9
  opencv-python==4.8.1.78
  prometheus-client==0.19.0
  python-multipart==0.0.6
  pydantic-settings==2.1.0
  alembic==1.13.0
  ```
- [ ] Создать `requirements-dev.txt`:
  ```
  pytest==7.4.3
  pytest-cov==4.1.0
  pytest-asyncio==0.21.1
  httpx==0.25.2
  black==23.12.0
  flake8==6.1.0
  mypy==1.7.1
  ```
- [ ] Создать `.env.example` с примерами переменных окружения
- [ ] Настроить базовую структуру проекта

**Результат**: Готовая структура проекта и зависимости

---

### 🗄️ Этап 2: База данных (День 1-2)

**Цель**: Настроить PostgreSQL и создать модели данных

#### Задачи:
- [ ] Создать `docker/init.sql` со схемой БД
- [ ] Настроить SQLAlchemy подключение в `src/db/database.py`
- [ ] Создать ORM модели в `src/db/models.py`:
  ```python
  class VideoAnalysis(Base):
      __tablename__ = "video_analyses"
      
      id = Column(Integer, primary_key=True)
      filename = Column(String(255), nullable=False)
      motion_detected = Column(Boolean, nullable=False)
      frames_analyzed = Column(Integer, nullable=False)
      processing_time = Column(Float, nullable=False)
      status = Column(String(50), nullable=False)
      error_message = Column(Text, nullable=True)
      created_at = Column(DateTime, default=datetime.utcnow)
  ```
- [ ] Создать Repository класс в `src/db/repository.py`
- [ ] Создать скрипт `scripts/init_db.py` для инициализации
- [ ] Настроить `docker-compose.yml` с PostgreSQL:
  ```yaml
  services:
    db:
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: ${POSTGRES_USER}
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
        POSTGRES_DB: ${POSTGRES_DB}
      volumes:
        - postgres_data:/var/lib/postgresql/data
        - ./docker/init.sql:/docker-entrypoint-initdb.d/init.sql
      ports:
        - "5432:5432"
  ```

**Результат**: Работающая БД с моделями и миграциями

---

### 🎥 Этап 3: Анализ видео с OpenCV (День 2-3)

**Цель**: Реализовать логику анализа движения в видео

#### Задачи:
- [ ] Создать `src/services/video_analyzer.py`
- [ ] Реализовать класс `VideoAnalyzer`:
  ```python
  class VideoAnalyzer:
      def __init__(self, frame_sample_rate: int = 5):
          self.frame_sample_rate = frame_sample_rate
      
      def analyze_motion(self, video_path: str) -> dict:
          """Анализирует видео на наличие движения"""
          # 1. Открыть видео через cv2.VideoCapture
          # 2. Читать кадры с определённым интервалом
          # 3. Использовать cv2.absdiff для детекции движения
          # 4. Подсчитать процент изменений
          # 5. Вернуть результат
          pass
  ```
- [ ] Реализовать алгоритм детекции движения:
  - Background subtraction (cv2.createBackgroundSubtractorMOG2)
  - Frame differencing
  - Подсчёт изменённых пикселей
- [ ] Добавить обработку различных форматов видео (MP4, AVI, MOV)
- [ ] Добавить валидацию видеофайлов в `src/utils/validators.py`
- [ ] Оптимизировать производительность (sampling frames)
- [ ] Написать unit-тесты для `VideoAnalyzer`
- [ ] Создать скрипт генерации тестовых видео

**Алгоритм детекции движения**:
```python
def detect_motion(video_path: str, threshold: float = 0.02) -> bool:
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    motion_frames = 0
    prev_frame = None
    
    while True:
        ret, frame = cap.read()
        if not ret:
            break
            
        # Преобразовать в grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        gray = cv2.GaussianBlur(gray, (21, 21), 0)
        
        if prev_frame is not None:
            # Найти разницу между кадрами
            frame_diff = cv2.absdiff(prev_frame, gray)
            thresh = cv2.threshold(frame_diff, 25, 255, cv2.THRESH_BINARY)[1]
            
            # Подсчитать процент изменений
            change_percent = np.count_nonzero(thresh) / thresh.size
            
            if change_percent > threshold:
                motion_frames += 1
        
        prev_frame = gray
        frame_count += 1
    
    cap.release()
    
    # Если больше 10% кадров содержат движение
    return (motion_frames / frame_count) > 0.1 if frame_count > 0 else False
```

**Результат**: Работающий модуль анализа видео

---

### 🌐 Этап 4: FastAPI и API Endpoints (День 3-4)

**Цель**: Создать REST API с необходимыми эндпоинтами

#### Задачи:
- [ ] Настроить FastAPI приложение в `src/main.py`:
  ```python
  from fastapi import FastAPI
  from fastapi.middleware.cors import CORSMiddleware
  
  app = FastAPI(
      title="VisionGuard API",
      description="Video analysis microservice",
      version="0.1.0"
  )
  ```
- [ ] Создать Pydantic модели в `src/api/models.py`:
  ```python
  class VideoAnalysisResponse(BaseModel):
      id: int
      filename: str
      motion_detected: bool
      frames_analyzed: int
      processing_time: float
      status: str
      created_at: datetime
  ```
- [ ] Реализовать `POST /analyze` в `src/api/endpoints.py`:
  ```python
  @router.post("/analyze", response_model=VideoAnalysisResponse)
  async def analyze_video(
      file: UploadFile = File(...),
      db: Session = Depends(get_db)
  ):
      # 1. Валидировать файл
      # 2. Сохранить временно
      # 3. Запустить анализ
      # 4. Сохранить результат в БД
      # 5. Удалить временный файл
      # 6. Вернуть результат
  ```
- [ ] Реализовать `GET /health`:
  ```python
  @router.get("/health")
  async def health_check(db: Session = Depends(get_db)):
      # Проверить подключение к БД
      # Вернуть статус
  ```
- [ ] Добавить обработку ошибок (exception handlers)
- [ ] Настроить CORS middleware
- [ ] Добавить логирование запросов
- [ ] Написать интеграционные тесты для API

**Результат**: Работающий API с документацией Swagger

---

### 📊 Этап 5: Prometheus метрики (День 4)

**Цель**: Интегрировать Prometheus для мониторинга

#### Задачи:
- [ ] Создать `src/services/metrics.py`:
  ```python
  from prometheus_client import Counter, Gauge, Histogram
  
  # Метрики
  videos_processed = Counter(
      'videos_processed_total',
      'Total number of videos processed'
  )
  
  processing_time = Gauge(
      'videos_processing_time_seconds',
      'Average video processing time'
  )
  
  processing_errors = Counter(
      'videos_processing_errors_total',
      'Total number of processing errors'
  )
  
  videos_with_motion = Counter(
      'videos_motion_detected_total',
      'Total number of videos with detected motion'
  )
  ```
- [ ] Реализовать `GET /metrics`:
  ```python
  from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
  
  @app.get("/metrics")
  def metrics():
      return Response(
          generate_latest(),
          media_type=CONTENT_TYPE_LATEST
      )
  ```
- [ ] Интегрировать метрики в `/analyze` endpoint
- [ ] Добавить middleware для отслеживания времени запросов
- [ ] Написать тесты для метрик

**Результат**: Рабочие Prometheus метрики

---

### 🐳 Этап 6: Докеризация (День 5)

**Цель**: Упаковать приложение в Docker контейнеры

#### Задачи:
- [ ] Создать `docker/Dockerfile`:
  ```dockerfile
  FROM python:3.11-slim
  
  WORKDIR /app
  
  # Установить системные зависимости для OpenCV
  RUN apt-get update && apt-get install -y \
      libgl1-mesa-glx \
      libglib2.0-0 \
      && rm -rf /var/lib/apt/lists/*
  
  # Копировать зависимости
  COPY requirements.txt .
  RUN pip install --no-cache-dir -r requirements.txt
  
  # Копировать код
  COPY src/ ./src/
  COPY scripts/ ./scripts/
  
  # Создать директорию для временных файлов
  RUN mkdir -p /tmp/uploads
  
  EXPOSE 8000
  
  CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
  ```
- [ ] Создать `docker-compose.yml`:
  ```yaml
  version: '3.8'
  
  services:
    app:
      build:
        context: .
        dockerfile: docker/Dockerfile
      ports:
        - "8000:8000"
      environment:
        - DATABASE_URL=postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@db:5432/${POSTGRES_DB}
      depends_on:
        - db
      volumes:
        - ./src:/app/src
  
    db:
      image: postgres:15-alpine
      environment:
        POSTGRES_USER: ${POSTGRES_USER}
        POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
        POSTGRES_DB: ${POSTGRES_DB}
      volumes:
        - postgres_data:/var/lib/postgresql/data
        - ./docker/init.sql:/docker-entrypoint-initdb.d/init.sql
      ports:
        - "5432:5432"
  
  volumes:
    postgres_data:
  ```
- [ ] Создать `docker-compose.dev.yml` для разработки
- [ ] Добавить health checks в docker-compose
- [ ] Оптимизировать размер образа (multi-stage build)
- [ ] Протестировать запуск через docker-compose

**Результат**: Полностью докеризованное приложение

---

### ✅ Этап 7: Тестирование (День 5-6)

**Цель**: Написать комплексные тесты

#### Задачи:
- [ ] Настроить pytest в `pytest.ini`:
  ```ini
  [pytest]
  testpaths = tests
  python_files = test_*.py
  python_classes = Test*
  python_functions = test_*
  addopts = -v --cov=src --cov-report=html --cov-report=term
  ```
- [ ] Создать fixtures в `tests/conftest.py`:
  ```python
  @pytest.fixture
  def test_db():
      # Создать тестовую БД
      pass
  
  @pytest.fixture
  def test_client():
      # FastAPI TestClient
      pass
  
  @pytest.fixture
  def sample_video():
      # Тестовое видео
      pass
  ```
- [ ] Написать unit-тесты:
  - `test_video_analyzer.py` - тесты анализатора видео
  - `test_metrics.py` - тесты метрик
  - `test_validators.py` - тесты валидаторов
  - `test_repository.py` - тесты репозитория
- [ ] Написать интеграционные тесты:
  - `test_api.py` - тесты API endpoints
  - `test_database.py` - тесты БД операций
- [ ] Достичь покрытия тестами >80%
- [ ] Добавить тесты производительности

**Примеры тестов**:
```python
# tests/integration/test_api.py
def test_analyze_endpoint_success(test_client, sample_video):
    with open(sample_video, "rb") as f:
        response = test_client.post(
            "/analyze",
            files={"file": ("test.mp4", f, "video/mp4")}
        )
    
    assert response.status_code == 200
    data = response.json()
    assert "id" in data
    assert "motion_detected" in data
    assert data["status"] == "completed"

def test_metrics_endpoint(test_client):
    response = test_client.get("/metrics")
    assert response.status_code == 200
    assert "videos_processed_total" in response.text
```

**Результат**: Покрытие тестами >80%

---

### 📚 Этап 8: Документация и финализация (День 6-7)

**Цель**: Завершить документацию и подготовить к сдаче

#### Задачи:
- [x] Обновить `README.md` с подробными инструкциями
- [ ] Создать `docs/ARCHITECTURE.md` с описанием архитектуры
- [ ] Создать `docs/API.md` с примерами запросов
- [ ] Добавить комментарии в код (docstrings)
- [ ] Настроить pre-commit hooks (black, flake8, mypy)
- [ ] Создать `.github/workflows/ci.yml` для CI/CD:
  ```yaml
  name: CI
  
  on: [push, pull_request]
  
  jobs:
    test:
      runs-on: ubuntu-latest
      steps:
        - uses: actions/checkout@v3
        - name: Set up Python
          uses: actions/setup-python@v4
          with:
            python-version: '3.11'
        - name: Install dependencies
          run: |
            pip install -r requirements.txt
            pip install -r requirements-dev.txt
        - name: Run tests
          run: pytest --cov=src
        - name: Lint
          run: |
            black --check src/
            flake8 src/
  ```
- [ ] Проверить все пункты чеклиста
- [ ] Финальное тестирование всего функционала
- [ ] Подготовить демонстрацию

**Результат**: Готовый к сдаче проект

---

## ✅ Чеклист для сдачи

### Функциональность
- [ ] `POST /analyze` работает корректно
- [ ] `GET /metrics` возвращает метрики Prometheus
- [ ] `GET /health` показывает статус сервиса
- [ ] Анализ видео детектирует движение
- [ ] Результаты сохраняются в PostgreSQL
- [ ] Обработка ошибок работает корректно

### Инфраструктура
- [ ] Dockerfile собирается без ошибок
- [ ] docker-compose.yml запускает все сервисы
- [ ] Переменные окружения настроены через .env
- [ ] Логи пишутся в stdout
- [ ] Метрики доступны для Prometheus

### Качество кода
- [ ] Покрытие тестами >80%
- [ ] Код соответствует PEP 8
- [ ] Типизация (type hints) присутствует
- [ ] Docstrings для всех функций
- [ ] Нет критических уязвимостей

### Документация
- [ ] README с инструкциями по запуску
- [ ] Примеры запросов (curl/Postman)
- [ ] SQL скрипт для БД
- [ ] Swagger UI доступен по `/docs`
- [ ] Архитектурная документация

### Дополнительно (плюсы)
- [ ] Helm chart для Kubernetes
- [ ] CI/CD pipeline
- [ ] Алгоритм детекции более сложный
- [ ] Асинхронная обработка (Celery)
- [ ] Rate limiting
- [ ] Кеширование результатов

---

## 🏗️ Архитектурные решения

### Паттерны проектирования

1. **Repository Pattern** - изоляция логики БД
2. **Dependency Injection** - FastAPI dependencies
3. **Factory Pattern** - создание анализаторов
4. **Strategy Pattern** - различные алгоритмы детекции

### Структура кода

```
┌─────────────┐
│   FastAPI   │  ← REST API endpoints
└──────┬──────┘
       │
       ├─→ ┌──────────────┐
       │   │  Validators  │  ← Валидация входных данных
       │   └──────────────┘
       │
       ├─→ ┌──────────────┐
       │   │   Services   │  ← Бизнес-логика
       │   ├──────────────┤
       │   │VideoAnalyzer │  ← Анализ видео (OpenCV)
       │   │   Metrics    │  ← Prometheus метрики
       │   └──────────────┘
       │
       └─→ ┌──────────────┐
           │  Repository  │  ← Работа с БД
           └──────┬───────┘
                  │
                  ▼
           ┌──────────────┐
           │ PostgreSQL   │  ← Хранилище данных
           └──────────────┘
```

### Обработка ошибок

```python
# src/api/endpoints.py
from fastapi import HTTPException

try:
    result = analyzer.analyze(video_path)
except VideoTooLargeError:
    raise HTTPException(status_code=413, detail="Video file too large")
except UnsupportedFormatError:
    raise HTTPException(status_code=415, detail="Unsupported video format")
except Exception as e:
    logger.error(f"Analysis failed: {e}")
    raise HTTPException(status_code=500, detail="Internal server error")
```

---

## 📊 Метрики успеха

### Технические метрики
- ✅ Время обработки видео 100MB < 30 секунд
- ✅ API response time < 100ms (без обработки)
- ✅ Покрытие тестами > 80%
- ✅ Размер Docker образа < 500MB

### Качество кода
- ✅ Соответствие PEP 8
- ✅ Отсутствие critical issues (flake8, mypy)
- ✅ Читаемость кода (docstrings, комментарии)
- ✅ Модульность и расширяемость

---

## 🚀 Возможные улучшения

### Краткосрочные (после MVP)
1. **Асинхронная обработка** - Celery + RabbitMQ
2. **Более сложная детекция** - YOLO для детекции объектов
3. **WebSocket** - real-time обновления статуса
4. **Кеширование** - Redis для результатов
5. **Rate limiting** - защита от DDoS

### Долгосрочные
1. **Микросервисная архитектура** - разделение на сервисы
2. **Kubernetes deployment** - Helm charts
3. **ML модели** - детекция касок, жилетов и т.п.
4. **Stream processing** - обработка видеопотоков
5. **Dashboard** - веб-интерфейс для мониторинга

---

## 📅 Timeline

| День | Этапы | Статус |
|------|-------|--------|
| 1 | Инфраструктура + База данных | ⏳ |
| 2-3 | Анализ видео (OpenCV) | ⏳ |
| 3-4 | FastAPI и API endpoints | ⏳ |
| 4 | Prometheus метрики | ⏳ |
| 5 | Докеризация | ⏳ |
| 5-6 | Тестирование | ⏳ |
| 6-7 | Документация и финализация | ⏳ |

**Общее время**: 6-7 дней

---

## 🎓 Ключевые выводы

### Что демонстрирует проект:
- ✅ Умение строить REST API (FastAPI)
- ✅ Работа с базами данных (PostgreSQL, SQLAlchemy)
- ✅ Обработка видео (OpenCV)
- ✅ Мониторинг и метрики (Prometheus)
- ✅ Контейнеризация (Docker)
- ✅ Тестирование (pytest)
- ✅ Документирование кода

### Best practices:
- Чистая архитектура (слои)
- SOLID принципы
- Type hints
- Comprehensive testing
- Error handling
- Logging и monitoring
- Security (validation)

---

**Версия плана**: 1.0  
**Дата создания**: 12 ноября 2025  
**Статус**: 🟢 Готов к реализации
