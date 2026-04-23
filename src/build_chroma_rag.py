#!/usr/bin/env python3
"""
Build ChromaDB RAG Index with Progress Bar
Завантаження ПОВНИХ текстів німецьких законів у векторну RAG базу
З ВІЗУАЛЬНИМ ІНТЕРФЕЙСОМ ПРОГРЕСУ
"""

import json
import logging
from pathlib import Path
from datetime import datetime
import hashlib
import sys
import time

import chromadb
from chromadb.config import Settings

# Налаштування
JSON_FILE = Path('data/complete_law_json/german_laws_complete.json')
CHROMA_DB_PATH = Path('data/legal_database_chroma')
BATCH_SIZE = 100
MAX_CHUNK_SIZE = 800
OVERLAP_SIZE = 100


class ProgressBar:
    """Простий прогрес бар для терміналу."""
    
    def __init__(self, total: int, title: str = "Прогрес"):
        self.total = total
        self.title = title
        self.current = 0
        self.start_time = time.time()
    
    def update(self, amount: int = 1):
        self.current += amount
    
    def render(self, extra_info: str = ""):
        percent = (self.current / self.total * 100) if self.total > 0 else 0
        elapsed = time.time() - self.start_time
        rate = self.current / elapsed if elapsed > 0 else 0
        
        # Форматування часу
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        eta_seconds = (self.total - self.current) / rate if rate > 0 else 0
        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
        
        # Прогрес бар
        bar_width = 40
        filled = int(bar_width * self.current / self.total)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        # Очищення лінії
        sys.stdout.write('\r' + ' ' * 100 + '\r')
        
        # Вивід
        line = f"{self.title}: [{bar}] {percent:5.1f}% ({self.current:,}/{self.total:,})"
        if extra_info:
            line += f" | {extra_info}"
        line += f" | ⏱️ {elapsed_str} | ETA: {eta_str} | {rate:.1f} док/сек"
        
        sys.stdout.write(line)
        sys.stdout.flush()
    
    def finish(self):
        elapsed = time.time() - self.start_time
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        sys.stdout.write(f'\n✅ Завершено за {elapsed_str}\n')
        sys.stdout.flush()


def split_text_into_chunks(text: str, max_size: int = MAX_CHUNK_SIZE, overlap: int = OVERLAP_SIZE) -> list:
    """Розбити текст на чанки з перекриттям."""
    if len(text) <= max_size:
        return [text]
    
    chunks = []
    start = 0
    
    while start < len(text):
        end = start + max_size
        
        if end < len(text):
            last_period = text.rfind('.', start, end)
            last_semicolon = text.rfind(';', start, end)
            last_newline = text.rfind('\n', start, end)
            
            split_point = max(last_period, last_semicolon, last_newline)
            if split_point > start + (max_size // 2):
                end = split_point + 1
        
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        
        start = end - overlap if end < len(text) else len(text)
    
    return chunks


def generate_chunk_id(law_name: str, para_num: str, chunk_idx: int, law_idx: int, global_idx: int) -> str:
    """Унікальний ID для чанку."""
    # Додаємо global_idx для 100% унікальності
    unique_str = f"law{law_idx:05d}_{global_idx:07d}_{law_name}_{para_num}_{chunk_idx}"
    return hashlib.md5(unique_str.encode()).hexdigest()


def build_rag_database():
    """Основна функція побудови RAG бази."""
    print("\n" + "="*80)
    print("  🏗️  ПОБУДОВА RAG БАЗИ НІМЕЦЬКИХ ЗАКОНІВ")
    print("="*80)
    
    # Завантаження JSON
    print(f"\n📖 Завантаження {JSON_FILE}...")
    if not JSON_FILE.exists():
        print(f"❌ Файл не знайдено: {JSON_FILE}")
        return
    
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        all_laws = json.load(f)
    
    print(f"✅ Завантажено {len(all_laws):,} законів")
    
    total_paragraphs = sum(law.get('paragraph_count', 0) for law in all_laws)
    print(f"📊 Всього параграфів: {total_paragraphs:,}")
    
    # Підключення до ChromaDB
    print(f"\n🔌 Підключення до ChromaDB...")
    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Створення колекції
    collection_name = 'german_laws_full'
    try:
        client.delete_collection(name=collection_name)
        print(f"🗑️  Стару колекцію видалено")
    except:
        pass
    
    collection = client.create_collection(
        name=collection_name,
        metadata={'description': 'Повні тексти німецьких законів з параграфами'}
    )
    print(f"✅ Колекцію '{collection_name}' створено")
    
    # Підготовка даних
    print("\n📝 Підготовка документів...")
    prepare_progress = ProgressBar(len(all_laws), "📝 Підготовка")

    all_documents = []
    all_metadatas = []
    all_ids = []
    total_chunks = 0
    global_chunk_idx = 0

    for law_idx, law in enumerate(all_laws):
        law_name = law.get('law_name', 'Unknown')
        paragraphs = law.get('paragraphs', [])

        for para in paragraphs:
            para_num = para.get('paragraph', '')
            content = para.get('content', '')

            if not content or len(content.strip()) < 50:
                continue

            chunks = split_text_into_chunks(content)

            for chunk_idx, chunk_text in enumerate(chunks):
                doc_id = generate_chunk_id(law_name, para_num, chunk_idx, law_idx, global_chunk_idx)
                global_chunk_idx += 1

                metadata = {
                    'law_name': law_name,
                    'paragraph': para_num,
                    'chunk_index': chunk_idx,
                    'total_chunks': len(chunks),
                    'content_preview': content[:200],
                }

                all_documents.append(chunk_text)
                all_metadatas.append(metadata)
                all_ids.append(doc_id)
                total_chunks += 1
        
        prepare_progress.update()
        if (law_idx + 1) % 100 == 0:
            prepare_progress.render(f"Чанків: {total_chunks:,}")
    
    prepare_progress.finish()
    print(f"\n📊 Всього підготовлено чанків: {total_chunks:,}")
    
    # Batch додавання до ChromaDB
    print(f"\n📥 Завантаження до ChromaDB (batch по {BATCH_SIZE})...")
    print("")
    
    upload_progress = ProgressBar(len(all_documents), "📥 Завантаження")
    
    added_count = 0
    start_time = datetime.now()
    
    for i in range(0, len(all_documents), BATCH_SIZE):
        batch_docs = all_documents[i:i + BATCH_SIZE]
        batch_metas = all_metadatas[i:i + BATCH_SIZE]
        batch_ids = all_ids[i:i + BATCH_SIZE]
        
        collection.add(
            documents=batch_docs,
            metadatas=batch_metas,
            ids=batch_ids
        )
        
        added_count += len(batch_docs)
        upload_progress.update(len(batch_docs))
        
        # Оновлення прогресу кожні 500 документів
        if added_count % 500 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = added_count / elapsed if elapsed > 0 else 0
            upload_progress.render(f"Швидкість: {rate:.1f} док/сек")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    upload_progress.finish()
    
    # Фінальна статистика
    print("\n" + "="*80)
    print("  📊 СТАТИСТИКА")
    print("="*80)
    print(f"Законів оброблено:       {len(all_laws):,}")
    print(f"Параграфів оброблено:    {total_paragraphs:,}")
    print(f"Чанків створено:         {total_chunks:,}")
    print(f"Додано до ChromaDB:      {added_count:,}")
    print(f"Час виконання:           {elapsed:.1f} сек ({elapsed/60:.1f} хв)")
    print(f"Швидкість:               {added_count/elapsed:.1f} документів/сек")
    
    final_count = collection.count()
    print(f"\n✅ Фінальна кількість:   {final_count:,}")
    
    # Тестовий пошук
    print("\n" + "="*80)
    print("  🔍 ТЕСТОВИЙ ПОШУК")
    print("="*80)
    
    test_queries = [
        "BGB § 1",
        "SGB II Leistung",
        "Kündigung Mieter",
    ]
    
    for query in test_queries:
        try:
            results = collection.query(
                query_texts=[query],
                n_results=2
            )
            
            print(f"\n📌 Запит: '{query}'")
            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0][:2], 1):
                    meta = results['metadatas'][0][i-1] if results['metadatas'] else {}
                    law = meta.get('law_name', 'Unknown')
                    para = meta.get('paragraph', '')
                    preview = doc[:80].replace('\n', ' ')
                    print(f"   {i}. {law} {para}: {preview}...")
            else:
                print("   ❌ Нічого не знайдено")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    print("\n" + "="*80)
    print("  ✅ RAG БАЗУ ПОБУДОВАНО УСПІШНО!")
    print("="*80)
    print(f"\n📁 Шлях до бази: {CHROMA_DB_PATH.absolute()}\n")


if __name__ == '__main__':
    try:
        build_rag_database()
    except KeyboardInterrupt:
        print("\n\n⚠️  Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
