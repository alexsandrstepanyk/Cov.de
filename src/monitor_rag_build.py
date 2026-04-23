#!/usr/bin/env python3
"""
Monitor RAG Build Progress
Моніторинг прогресу побудови RAG бази в реальному часі
"""

import time
import os
from pathlib import Path
from datetime import datetime

LOG_FILE = Path('logs/build_rag_progress.log')
CHROMA_DB_PATH = Path('data/legal_database_chroma')

def get_chroma_count():
    """Отримати кількість записів у ChromaDB."""
    try:
        import chromadb
        client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
        try:
            collection = client.get_collection('german_laws_full')
            return collection.count()
        except:
            return 0
    except:
        return 0

def monitor():
    """Моніторинг прогресу."""
    print("\n" + "="*80)
    print("  📊 МОНІТОРИНГ ПОБУДОВИ RAG БАЗИ")
    print("="*80)
    print(f"\n📁 Лог файл: {LOG_FILE.absolute()}")
    print("Натисніть Ctrl+C для виходу\n")
    
    last_line = ""
    last_count = 0
    start_time = time.time()
    
    while True:
        now = datetime.now().strftime('%H:%M:%S')
        
        # Читання останніх рядків логу
        if LOG_FILE.exists():
            with open(LOG_FILE, 'r', encoding='utf-8') as f:
                lines = f.readlines()
                if lines:
                    # Останній рядок з прогресом
                    for line in reversed(lines[-20:]):
                        if 'Прогрес' in line or 'Завантаження' in line or 'Підготовка' in line:
                            last_line = line.strip()
                            break
                    
                    # Останні 3 рядки
                    recent = ''.join(lines[-3:]).strip()
        
        # Отримання кількості записів
        current_count = get_chroma_count()
        
        # Розрахунок статистики
        elapsed = time.time() - start_time
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        rate = current_count / elapsed if elapsed > 0 and current_count > 0 else 0
        
        # Вивід
        print(f"\r{'='*80}", end='')
        print(f"\n⏰ Час: {elapsed_str} | {now}")
        print(f"📊 Записів у ChromaDB: {current_count:,}")
        if rate > 0:
            print(f"⚡ Швидкість: {rate:.1f} записів/сек")
        
        if last_line:
            print(f"\n📝 Остання дія:")
            print(f"   {last_line[:100]}...")
        
        # Оцінка прогресу (очікується ~382,000 чанків)
        expected_total = 382690
        if current_count > 0:
            percent = (current_count / expected_total * 100)
            remaining = expected_total - current_count
            eta_seconds = remaining / rate if rate > 0 else 0
            eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
            
            print(f"\n📈 Прогрес: {percent:.1f}% ({current_count:,}/{expected_total:,})")
            print(f"⏳ ETA: {eta_str}")
        
        print(f"\r{'='*80}", end='', flush=True)
        
        time.sleep(2)


if __name__ == '__main__':
    try:
        monitor()
    except KeyboardInterrupt:
        print("\n\n👋 Моніторинг зупинено")
