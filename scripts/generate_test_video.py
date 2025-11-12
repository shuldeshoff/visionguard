"""
Скрипт для генерации тестовых видео

Создает простые видео для тестирования анализатора движения
"""
import cv2
import numpy as np
from pathlib import Path
import sys
import os

# Добавляем корневую директорию в PYTHONPATH
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


def generate_static_video(output_path: Path, duration_seconds: int = 3, fps: int = 30):
    """
    Генерация статичного видео (без движения)
    
    Args:
        output_path: Путь для сохранения видео
        duration_seconds: Длительность в секундах
        fps: Частота кадров
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    # Создаем статичный кадр
    frame = np.zeros((height, width, 3), dtype=np.uint8)
    frame[:] = (100, 100, 100)  # Серый фон
    
    # Добавляем текст
    cv2.putText(
        frame, 
        "Static Video - No Motion", 
        (50, height // 2),
        cv2.FONT_HERSHEY_SIMPLEX, 
        1, 
        (255, 255, 255), 
        2
    )
    
    # Записываем одинаковые кадры
    total_frames = duration_seconds * fps
    for _ in range(total_frames):
        out.write(frame)
    
    out.release()
    print(f"✓ Static video created: {output_path}")


def generate_motion_video(output_path: Path, duration_seconds: int = 3, fps: int = 30):
    """
    Генерация видео с движением
    
    Args:
        output_path: Путь для сохранения видео
        duration_seconds: Длительность в секундах
        fps: Частота кадров
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    total_frames = duration_seconds * fps
    
    for frame_num in range(total_frames):
        # Создаем кадр
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (50, 50, 50)  # Темный фон
        
        # Движущийся объект (круг)
        x = int((frame_num / total_frames) * width)
        y = height // 2
        radius = 30
        
        cv2.circle(frame, (x, y), radius, (0, 255, 0), -1)
        
        # Текст
        cv2.putText(
            frame,
            f"Motion Video - Frame {frame_num}",
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (255, 255, 255),
            2
        )
        
        out.write(frame)
    
    out.release()
    print(f"✓ Motion video created: {output_path}")


def generate_partial_motion_video(output_path: Path, duration_seconds: int = 6, fps: int = 30):
    """
    Генерация видео с частичным движением (статика + движение)
    
    Args:
        output_path: Путь для сохранения видео
        duration_seconds: Длительность в секундах
        fps: Частота кадров
    """
    width, height = 640, 480
    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(str(output_path), fourcc, fps, (width, height))
    
    total_frames = duration_seconds * fps
    motion_start = total_frames // 3  # Движение начинается с 1/3
    motion_end = 2 * total_frames // 3  # Заканчивается на 2/3
    
    for frame_num in range(total_frames):
        frame = np.zeros((height, width, 3), dtype=np.uint8)
        frame[:] = (70, 70, 70)
        
        # Движение только в определенном интервале
        if motion_start <= frame_num < motion_end:
            progress = (frame_num - motion_start) / (motion_end - motion_start)
            x = int(progress * width)
            y = height // 2
            cv2.circle(frame, (x, y), 25, (255, 0, 0), -1)
            text = "Motion Active"
        else:
            text = "Static Phase"
        
        cv2.putText(
            frame,
            text,
            (10, 30),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.8,
            (255, 255, 255),
            2
        )
        
        out.write(frame)
    
    out.release()
    print(f"✓ Partial motion video created: {output_path}")


def main():
    """Главная функция для генерации тестовых видео"""
    # Создаем директорию для тестовых файлов
    fixtures_dir = Path(__file__).parent.parent / "tests" / "fixtures"
    fixtures_dir.mkdir(parents=True, exist_ok=True)
    
    print("Generating test videos...")
    print(f"Output directory: {fixtures_dir}")
    print()
    
    # Генерация тестовых видео
    generate_static_video(fixtures_dir / "static_video.mp4")
    generate_motion_video(fixtures_dir / "motion_video.mp4")
    generate_partial_motion_video(fixtures_dir / "partial_motion_video.mp4")
    
    print()
    print("✓ All test videos generated successfully!")
    print()
    print("Generated files:")
    for video_file in fixtures_dir.glob("*.mp4"):
        size_mb = video_file.stat().st_size / (1024 * 1024)
        print(f"  - {video_file.name} ({size_mb:.2f} MB)")


if __name__ == "__main__":
    main()

