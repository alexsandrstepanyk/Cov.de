#!/usr/bin/env python3
"""
Simple monitor for RAG upload
Простий монітор прогресу завантаження
"""

import time
import chromadb
from pathlib import Path
from datetime import datetime

CHROMA_DB_PATH = Path('data/legal_database_chroma')

def monitor():
    print("\n" + "="*80)
    print("  📊 МОНІТОРИНГ RAG БАЗИ")
    print("="*80)
    print("\nНатисніть Ctrl+C для виходу\n")
    
    start_time = time.time()
    last_count = 0
    
    while True:
        try:
            client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
            
            # Перевірка всіх колекцій
            collections_info = []
            
            for coll_name in ['german_laws_general', 'german_laws_full']:
                try:
                    collection = client.get_collection(coll_name)
                    count = collection.count()
                    collections_info.append((coll_name, count))
                except:
                    pass
            
            elapsed = time.time() - start_time
            elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
            now = datetime.now().strftime('%H:%M:%S')
            
            print(f"\r{'='*80}", end='')
            print(f"\n⏰ Час: {elapsed_str} | {now}")
            print(f"📊 Колекції:")
            
            total = 0
            for name, count in collections_info:
                delta = count - last_count
                delta_str = f" (+{delta})" if delta > 0 else ""
                print(f"   • {name}: {count:,}{delta_str}")
                total += count
            
            print(f"\n📈 Всього записів: {total:,}")
            print(f"{'='*80}", end='', flush=True)
            
            last_count = total
            time.sleep(3)
            
        except KeyboardInterrupt:
            print("\n\n👋 Моніторинг зупинено")
            break
        except Exception as e:
            print(f"\n❌ Помилка: {e}")
            time.sleep(5)

if __name__ == '__main__':
    monitor()
