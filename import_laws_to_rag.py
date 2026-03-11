#!/usr/bin/env python3
"""
Import German Laws to ChromaDB RAG
Імпорт німецьких законів з SQLite до ChromaDB для RAG пошуку

Це дозволить LLM (Ollama) робити розумний пошук по законах.
"""

import sqlite3
import chromadb
from chromadb.config import Settings
import logging
from pathlib import Path
from datetime import datetime
from typing import List, Dict

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('import_to_rag')

# Шляхи
DB_FILE = Path('data/legal_database.db')
CHROMA_DIR = Path('data/chroma_db')

# Налаштування ChromaDB
CHROMA_SETTINGS = Settings(
    anonymized_telemetry=False,
    allow_reset=True,
    is_persistent=True,
)


def create_chroma_collection():
    """Створення колекції ChromaDB для законів."""
    logger.info("📇 Створення ChromaDB колекції...")
    
    # Створення persistent client
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    # Видалення старої колекції (якщо є)
    try:
        client.delete_collection("german_laws")
        logger.info("🗑️  Стару колекцію видалено")
    except:
        pass
    
    # Створення нової колекції з HNSW індексом
    collection = client.create_collection(
        name="german_laws",
        metadata={"hnsw:space": "cosine"},
        get_or_create=True
    )
    
    logger.info("✅ ChromaDB колекцію створено")
    return client, collection


def import_laws_to_chroma():
    """Іморт законів з SQLite до ChromaDB."""
    logger.info("="*80)
    logger.info("  📚 ІМПОРТ ЗАКОНІВ ДО CHROMADB RAG")
    logger.info("="*80)
    
    # Підключення до SQLite
    logger.info(f"\n📥 Підключення до {DB_FILE}...")
    conn = sqlite3.connect(DB_FILE)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Отримання всіх параграфів
    logger.info("📊 Отримання параграфів з бази...")
    cursor.execute("""
        SELECT id, code_name, paragraph_number, text_de, text_uk, category
        FROM paragraphs
        WHERE text_de IS NOT NULL AND text_de != ''
    """)
    rows = cursor.fetchall()
    
    logger.info(f"✅ Знайдено {len(rows):,} параграфів")
    
    # Створення ChromaDB колекції
    client, collection = create_chroma_collection()
    
    # Підготовка даних для імпорту
    logger.info("\n🔄 Підготовка даних...")
    
    ids = []
    documents = []
    metadatas = []
    
    for idx, row in enumerate(rows):
        para_id = f"para_{row['id']}"
        code = row['code_name'] or 'UNKNOWN'
        para_num = row['paragraph_number'] or ''
        text_de = row['text_de'] or ''
        text_uk = row['text_uk'] or ''
        category = row['category'] or ''
        
        # Формування повного тексту для пошуку
        # Німецька версія + український переклад (якщо є)
        full_text = f"{code} {para_num}\n{text_de}"
        if text_uk:
            full_text += f"\n\nУкраїнською: {text_uk}"
        
        # Обрізаємо до максимальної довжини (ChromaDB має ліміт)
        max_length = 30000
        if len(full_text) > max_length:
            full_text = full_text[:max_length] + "..."
        
        ids.append(para_id)
        documents.append(full_text)
        metadatas.append({
            "code": code,
            "paragraph": para_num,
            "category": category,
            "language": "de",
            "source": "bundestag_gesetze",
        })
        
        # Прогрес кожні 1000
        if (idx + 1) % 1000 == 0:
            logger.info(f"  Підготовлено {idx + 1:,}/{len(rows):,}")
    
    # Імпорт партіями (batch)
    logger.info("\n📥 Імпорт до ChromaDB...")
    
    batch_size = 500
    total_imported = 0
    
    for i in range(0, len(ids), batch_size):
        batch_ids = ids[i:i + batch_size]
        batch_docs = documents[i:i + batch_size]
        batch_meta = metadatas[i:i + batch_size]
        
        collection.add(
            ids=batch_ids,
            documents=batch_docs,
            metadatas=batch_meta
        )
        
        total_imported += len(batch_ids)
        logger.info(f"  Імпортовано {total_imported:,}/{len(ids):,}")
    
    # Збереження
    logger.info("\n💾 Збереження індексу...")
    
    conn.close()
    
    logger.info("\n" + "="*80)
    logger.info("  ✅ ІМПОРТ ДО CHROMADB ЗАВЕРШЕНО!")
    logger.info("="*80)
    logger.info(f"\n📊 СТАТИСТИКА:")
    logger.info(f"  Параграфів імпортовано: {total_imported:,}")
    logger.info(f"  ChromaDB шлях: {CHROMA_DIR}")
    logger.info(f"  Колекція: german_laws")
    
    # Тестовий запит
    logger.info("\n🧪 Тестовий пошук...")
    
    test_query = "BGB § 241 Schuldverhältnis"
    results = collection.query(
        query_texts=[test_query],
        n_results=3
    )
    
    if results and results['documents'] and len(results['documents'][0]) > 0:
        logger.info(f"✅ Запит: '{test_query}'")
        logger.info(f"   Знайдено {len(results['documents'][0])} результатів")
        for i, doc in enumerate(results['documents'][0][:2]):
            preview = doc[:100].replace('\n', ' ')
            logger.info(f"   [{i+1}] {preview}...")
    else:
        logger.info("⚠️  Пошук не повернув результатів")
    
    logger.info("\n🎉 RAG система готова до використання!")


if __name__ == '__main__':
    import_laws_to_chroma()
