-- VisionGuard Database Schema
-- Инициализация базы данных для хранения результатов анализа видео

-- Создание расширения для UUID (опционально, для будущего использования)
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Таблица для хранения результатов анализа видео
CREATE TABLE IF NOT EXISTS video_analyses (
    id SERIAL PRIMARY KEY,
    filename VARCHAR(255) NOT NULL,
    motion_detected BOOLEAN NOT NULL,
    frames_analyzed INTEGER NOT NULL CHECK (frames_analyzed >= 0),
    processing_time FLOAT NOT NULL CHECK (processing_time >= 0),
    status VARCHAR(50) NOT NULL CHECK (status IN ('pending', 'processing', 'completed', 'failed')),
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Индексы для оптимизации запросов
CREATE INDEX IF NOT EXISTS idx_video_analyses_status ON video_analyses(status);
CREATE INDEX IF NOT EXISTS idx_video_analyses_created_at ON video_analyses(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_video_analyses_motion_detected ON video_analyses(motion_detected);
CREATE INDEX IF NOT EXISTS idx_video_analyses_filename ON video_analyses(filename);

-- Триггер для автоматического обновления updated_at
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

CREATE TRIGGER update_video_analyses_updated_at 
    BEFORE UPDATE ON video_analyses
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Комментарии к таблице и полям
COMMENT ON TABLE video_analyses IS 'Результаты анализа видеофайлов на наличие движения';
COMMENT ON COLUMN video_analyses.id IS 'Уникальный идентификатор записи';
COMMENT ON COLUMN video_analyses.filename IS 'Название загруженного видеофайла';
COMMENT ON COLUMN video_analyses.motion_detected IS 'Флаг обнаружения движения в видео';
COMMENT ON COLUMN video_analyses.frames_analyzed IS 'Количество проанализированных кадров';
COMMENT ON COLUMN video_analyses.processing_time IS 'Время обработки видео в секундах';
COMMENT ON COLUMN video_analyses.status IS 'Статус обработки: pending, processing, completed, failed';
COMMENT ON COLUMN video_analyses.error_message IS 'Сообщение об ошибке (если status = failed)';
COMMENT ON COLUMN video_analyses.created_at IS 'Дата и время создания записи';
COMMENT ON COLUMN video_analyses.updated_at IS 'Дата и время последнего обновления';

