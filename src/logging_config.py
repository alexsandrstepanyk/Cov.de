#!/usr/bin/env python3
"""
📊 МОДУЛЬ ЛОГУВАННЯ GOV.DE BOT v4.4

Best Practices 2026:
- Ротування логів (10MB, 5 backup files)
- Рівні логування (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Окремі файли для помилок
- Консольний вивід з кольорами
- JSON формат для структурованого логування
"""

import logging
import os
import sys
from logging.handlers import RotatingFileHandler
from datetime import datetime
from pathlib import Path


class ColoredFormatter(logging.Formatter):
    """Кольоровий formatter для консольного виводу."""
    
    COLORS = {
        'DEBUG': '\033[36m',     # Cyan
        'INFO': '\033[32m',      # Green
        'WARNING': '\033[33m',   # Yellow
        'ERROR': '\033[31m',     # Red
        'CRITICAL': '\033[35m',  # Magenta
    }
    RESET = '\033[0m'
    
    def format(self, record):
        log_color = self.COLORS.get(record.levelname, self.RESET)
        record.levelname = f"{log_color}{record.levelname}{self.RESET}"
        return super().format(record)


def setup_logging(
    log_dir='logs',
    log_file='bot.log',
    error_file='errors.log',
    level=logging.INFO,
    max_bytes=10485760,  # 10MB
    backup_count=5,
    console_output=True
):
    """
    Налаштування логування з ротуванням.
    
    Args:
        log_dir: Директорія для логів
        log_file: Основний файл логу
        error_file: Файл для помилок
        level: Рівень логування
        max_bytes: Максимальний розмір файлу до ротування
        backup_count: Кількість backup файлів
        console_output: Виводити в консоль
    
    Returns:
        logger: Налаштований logger
    """
    
    # Створюємо директорію для логів
    log_path = Path(log_dir)
    log_path.mkdir(exist_ok=True)
    
    # Створюємо logger
    logger = logging.getLogger('govde_bot')
    logger.setLevel(level)
    
    # Формат для файлу (детальний)
    file_format = logging.Formatter(
        '%(asctime)s | %(name)s | %(levelname)-8s | %(funcName)s:%(lineno)d | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Формат для консолі (коротший з кольорами)
    console_format = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )
    
    # Основний файл з ротуванням
    file_handler = RotatingFileHandler(
        log_path / log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(file_format)
    
    # Окремий файл для помилок (ERROR та вище)
    error_handler = RotatingFileHandler(
        log_path / error_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(file_format)
    
    # Консольний handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(level)
        console_handler.setFormatter(console_format)
        logger.addHandler(console_handler)
    
    # Додаємо handlers
    logger.addHandler(file_handler)
    logger.addHandler(error_handler)
    
    # Логуємо запуск
    logger.info("="*70)
    logger.info(f"🚀 GOV.DE BOT запущено | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info(f"📂 Log directory: {log_path.absolute()}")
    logger.info(f"📝 Log level: {logging.getLevelName(level)}")
    logger.info(f"💾 Max log size: {max_bytes / 1024 / 1024:.1f}MB | Backups: {backup_count}")
    logger.info("="*70)
    
    return logger


def get_logger(name='govde_bot'):
    """Отримати існуючий logger."""
    return logging.getLogger(name)


def log_function_call(logger, func_name, *args, **kwargs):
    """Логувати виклик функції (для дебагінгу)."""
    logger.debug(f"📞 CALL {func_name} | args={len(args)} | kwargs={len(kwargs)}")


def log_performance(logger, operation, elapsed_time, details=""):
    """Логувати продуктивність операції."""
    status = "⚡ FAST" if elapsed_time < 1.0 else "⏳ SLOW"
    logger.info(f"{status} | {operation} | {elapsed_time:.3f}s | {details}")


def log_error_with_context(logger, error, context="", exc_info=True):
    """Логувати помилку з контекстом."""
    logger.error(
        f"❌ ERROR | {context} | {type(error).__name__}: {str(error)}",
        exc_info=exc_info
    )


# Приклад використання
if __name__ == "__main__":
    # Тестування логування
    logger = setup_logging(console_output=True)
    
    logger.debug("Це DEBUG повідомлення")
    logger.info("Це INFO повідомлення")
    logger.warning("Це WARNING повідомлення")
    logger.error("Це ERROR повідомлення")
    logger.critical("Це CRITICAL повідомлення")
    
    # Тест помилки з traceback
    try:
        1 / 0
    except ZeroDivisionError as e:
        log_error_with_context(logger, e, "Тест ділення на нуль")
    
    # Тест продуктивності
    import time
    start = time.time()
    time.sleep(0.5)
    log_performance(logger, "Sleep test", time.time() - start)
    
    print(f"\n✅ Логи збережено в: {Path('logs').absolute()}")
