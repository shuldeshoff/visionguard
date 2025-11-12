# База данных - Инструкция по работе

## 🗄️ Структура базы данных

### Таблица: video_analyses

| Поле | Тип | Описание |
|------|-----|----------|
| id | SERIAL | Уникальный идентификатор |
| filename | VARCHAR(255) | Название видеофайла |
| motion_detected | BOOLEAN | Обнаружено ли движение |
| frames_analyzed | INTEGER | Количество кадров |
| processing_time | FLOAT | Время обработки (сек) |
| status | VARCHAR(50) | Статус: pending, processing, completed, failed |
| error_message | TEXT | Сообщение об ошибке |
| created_at | TIMESTAMP | Дата создания |
| updated_at | TIMESTAMP | Дата обновления |

### Индексы

- `idx_video_analyses_status` - по статусу
- `idx_video_analyses_created_at` - по дате создания
- `idx_video_analyses_motion_detected` - по обнаружению движения
- `idx_video_analyses_filename` - по названию файла

## 🚀 Запуск PostgreSQL

### Через Docker Compose

```bash
# Запуск только БД
docker-compose up -d db

# Проверка статуса
docker-compose ps

# Просмотр логов
docker-compose logs db

# Остановка
docker-compose down
```

### Для разработки (с pgAdmin)

```bash
# Запуск БД + pgAdmin
docker-compose -f docker-compose.dev.yml up -d

# pgAdmin будет доступен на http://localhost:5050
# Email: admin@visionguard.local
# Password: admin
```

## 🔧 Инициализация базы данных

### Автоматическая (через Docker)

При запуске `docker-compose up`, PostgreSQL автоматически выполнит `docker/init.sql`.

### Ручная инициализация

```bash
# Через скрипт Python
python scripts/init_db.py

# С удалением существующих таблиц
python scripts/init_db.py --drop

# Через psql напрямую
psql -h localhost -U visionguard -d visionguard_db -f docker/init.sql
```

## 🧪 Тестирование подключения

### Через Python

```python
from src.db.database import check_db_connection

if check_db_connection():
    print("✓ Database connection OK")
else:
    print("✗ Database connection FAILED")
```

### Через curl

```bash
# Health check включает проверку БД
curl http://localhost:8000/health

# Ожидаемый ответ:
# {
#   "status": "healthy",
#   "service": "VisionGuard",
#   "version": "0.1.0",
#   "database": "connected"
# }
```

## 📝 Примеры использования Repository

```python
from src.db.database import SessionLocal
from src.db.repository import VideoAnalysisRepository

# Создание сессии
db = SessionLocal()
repo = VideoAnalysisRepository(db)

# Создание записи
analysis = repo.create(
    filename="video.mp4",
    motion_detected=True,
    frames_analyzed=150,
    processing_time=2.5,
    status="completed"
)

# Получение по ID
analysis = repo.get_by_id(1)

# Получение всех записей
all_analyses = repo.get_all(skip=0, limit=10)

# Получение по имени файла
analyses = repo.get_by_filename("video.mp4")

# Обновление статуса
repo.update_status(1, "failed", "Processing error")

# Удаление
repo.delete(1)

# Статистика
total = repo.count_total()
with_motion = repo.count_with_motion()
failed = repo.count_by_status("failed")

# Закрытие сессии
db.close()
```

## 🔍 Полезные SQL запросы

```sql
-- Все записи с движением
SELECT * FROM video_analyses WHERE motion_detected = true;

-- Статистика по статусам
SELECT status, COUNT(*) as count 
FROM video_analyses 
GROUP BY status;

-- Средее время обработки
SELECT AVG(processing_time) as avg_time 
FROM video_analyses 
WHERE status = 'completed';

-- Последние 10 записей
SELECT * FROM video_analyses 
ORDER BY created_at DESC 
LIMIT 10;

-- Записи с ошибками
SELECT * FROM video_analyses 
WHERE status = 'failed' 
ORDER BY created_at DESC;
```

## 🛠️ Подключение к БД

### Параметры подключения

```
Host: localhost
Port: 5432
Database: visionguard_db
Username: visionguard
Password: password (из .env файла)
```

### Через psql

```bash
psql -h localhost -U visionguard -d visionguard_db
```

### Через pgAdmin

1. Открыть http://localhost:5050
2. Добавить новый сервер:
   - Name: VisionGuard
   - Host: db (или localhost если вне Docker)
   - Port: 5432
   - Database: visionguard_db
   - Username: visionguard
   - Password: password

## 🔄 Миграции (будущее)

В production рекомендуется использовать Alembic:

```bash
# Инициализация Alembic
alembic init alembic

# Создание миграции
alembic revision --autogenerate -m "Initial migration"

# Применение миграций
alembic upgrade head

# Откат
alembic downgrade -1
```

## ⚠️ Troubleshooting

### Ошибка подключения

```bash
# Проверить, запущен ли PostgreSQL
docker-compose ps

# Проверить логи
docker-compose logs db

# Перезапустить БД
docker-compose restart db
```

### Конфликт портов

Если порт 5432 занят:

```bash
# В docker-compose.yml изменить:
ports:
  - "5433:5432"  # Использовать другой порт

# Или остановить локальный PostgreSQL
brew services stop postgresql  # macOS
sudo systemctl stop postgresql # Linux
```

### Пересоздание БД

```bash
# Остановить и удалить контейнеры и volumes
docker-compose down -v

# Запустить заново
docker-compose up -d db
```

