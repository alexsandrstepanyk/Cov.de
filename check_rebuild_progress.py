#!/usr/bin/env python3
"""
Check Rebuild Progress
Перевірка прогресу перебудови індексу
"""

import json
import logging
from pathlib import Path

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s: %(message)s'
)
logger = logging.getLogger('check_progress')

index_file = Path('data/fast_law_index.json')
log_file = Path('logs/rebuild_index.log')

print("="*70)
print("  📊 ПЕРЕВІРКА ПРОГРЕСУ ПЕРЕБУДОВИ ІНДЕКСУ")
print("="*70)

# Перевірка лог файлу
if log_file.exists():
    logger.info("\n📄 ОСТАННІ РЯДКИ ЛОГУ:")
    with open(log_file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines[-10:]:
            print(f"   {line.strip()}")
else:
    logger.warning("⚠️ Лог файл не знайдено")

# Перевірка поточного індексу
if index_file.exists():
    logger.info(f"\n💾 ПОТОЧНИЙ ІНДЕКС:")
    logger.info(f"   Файл: {index_file}")
    logger.info(f"   Розмір: {index_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    try:
        with open(index_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"   Законів: {data.get('total_laws', 0):,}")
        logger.info(f"   Параграфів: {data.get('total_paragraphs', 0):,}")
        logger.info(f"   Дата: {data.get('created_at', 'N/A')}")
    except Exception as e:
        logger.warning(f"⚠️ Не вдалося прочитати: {e}")
else:
    logger.info("\n⏳ Індекс ще не створено")

print("\n" + "="*70)
