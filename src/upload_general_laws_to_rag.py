#!/usr/bin/env python3
"""
Upload General Laws PDFs to RAG Database
Завантаження PDF кодексів з папки general у RAG базу
ВАЖЛИВО: Кожен закон має унікальний ID і не перезаписує інші
"""

import os
import logging
from pathlib import Path
from datetime import datetime
import hashlib
import time
import sys

import chromadb

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('upload_general_laws')

# Шляхи
GENERAL_DIR = Path('general')
CHROMA_DB_PATH = Path('data/legal_database_chroma')

# Налаштування
BATCH_SIZE = 200  # Збільшено для швидкості
MAX_CHUNK_SIZE = 800
OVERLAP_SIZE = 100


class ProgressBar:
    """Прогрес бар для терміналу."""
    
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
        
        elapsed_str = time.strftime('%H:%M:%S', time.gmtime(elapsed))
        eta_seconds = (self.total - self.current) / rate if rate > 0 else 0
        eta_str = time.strftime('%H:%M:%S', time.gmtime(eta_seconds))
        
        bar_width = 40
        filled = int(bar_width * self.current / self.total)
        bar = '█' * filled + '░' * (bar_width - filled)
        
        sys.stdout.write('\r' + ' ' * 120 + '\r')
        
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


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Витягнути текст з PDF."""
    try:
        from pdfminer.high_level import extract_text
        text = extract_text(str(pdf_path))
        return text if text else ""
    except Exception as e:
        logger.warning(f"❌ Помилка читання {pdf_path}: {e}")
        return ""


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


def generate_unique_id(law_name: str, chunk_idx: int, file_path: str) -> str:
    """
    Генерація УНІКАЛЬНОГО ID для чанку.
    ВАЖЛИВО: Використовуємо повний шлях до файлу для унікальності.
    """
    unique_str = f"general_{law_name}_{file_path}_{chunk_idx}"
    return hashlib.md5(unique_str.encode()).hexdigest()


def upload_general_laws():
    """Завантажити всі PDF з папки general у RAG базу."""
    print("\n" + "="*80)
    print("  📚 ЗАВАНТАЖЕННЯ PDF КОДЕКСІВ У RAG БАЗУ")
    print("="*80)
    print("\n❗ УВАГА: Кожен закон має унікальний ID і НЕ перезаписує інші!")
    
    # Знаходимо всі PDF
    print(f"\n📁 Пошук PDF у {GENERAL_DIR}...")
    if not GENERAL_DIR.exists():
        print(f"❌ Папка не знайдено: {GENERAL_DIR}")
        return
    
    pdf_files = list(GENERAL_DIR.glob('*.pdf'))
    print(f"✅ Знайдено {len(pdf_files)} PDF файлів")
    
    # Підключення до ChromaDB
    print(f"\n🔌 Підключення до ChromaDB...")
    CHROMA_DB_PATH.mkdir(parents=True, exist_ok=True)
    
    client = chromadb.PersistentClient(path=str(CHROMA_DB_PATH))
    
    # Отримуємо або створюємо колекцію
    collection_name = 'german_laws_general'
    try:
        collection = client.get_collection(name=collection_name)
        current_count = collection.count()
        print(f"✅ Колекцію '{collection_name}' знайдено")
        print(f"   Поточна кількість записів: {current_count:,}")
    except:
        collection = client.create_collection(
            name=collection_name,
            metadata={'description': 'Загальні німецькі кодекси з папки general (PDF)'}
        )
        print(f"✅ Колекцію '{collection_name}' створено")
        current_count = 0
    
    # Обробка кожного PDF
    print(f"\n📖 Обробка PDF файлів...")
    total_chunks = 0
    all_documents = []
    all_metadatas = []
    all_ids = []
    
    extract_progress = ProgressBar(len(pdf_files), "📖 Читання PDF")
    
    for pdf_file in pdf_files:
        # Назва закону з файлу
        law_name = pdf_file.stem  # наприклад "BGB", "SGB_2"
        
        # Витягуємо текст
        text = extract_text_from_pdf(pdf_file)
        
        if not text or len(text.strip()) < 100:
            logger.warning(f"⚠️  {law_name}: текст не витягнуто або занадто короткий")
            extract_progress.update()
            extract_progress.render()
            continue
        
        # Розбиваємо на чанки
        chunks = split_text_into_chunks(text)
        
        for chunk_idx, chunk_text in enumerate(chunks):
            # УНІКАЛЬНИЙ ID для кожного чанку
            doc_id = generate_unique_id(law_name, chunk_idx, str(pdf_file))
            
            # Metadata
            metadata = {
                'law_name': law_name,
                'file_name': pdf_file.name,
                'file_path': str(pdf_file),
                'chunk_index': chunk_idx,
                'total_chunks': len(chunks),
                'source': 'general',
                'content_preview': text[:200],
            }
            
            all_documents.append(chunk_text)
            all_metadatas.append(metadata)
            all_ids.append(doc_id)
            total_chunks += 1
        
        extract_progress.update()
        extract_progress.render(f"Чанків: {total_chunks:,}")
    
    extract_progress.finish()
    
    if total_chunks == 0:
        print("\n❌ Не вдалося витягнути жодного чанку з PDF")
        return
    
    print(f"\n📊 Всього підготовлено чанків: {total_chunks:,}")
    
    # Завантаження до ChromaDB
    print(f"\n📥 Завантаження до ChromaDB (batch по {BATCH_SIZE})...")
    print("")
    
    upload_progress = ProgressBar(len(all_documents), "📥 Завантаження")
    
    added_count = 0
    start_time = datetime.now()
    skipped_count = 0
    
    for i in range(0, len(all_documents), BATCH_SIZE):
        batch_docs = all_documents[i:i + BATCH_SIZE]
        batch_metas = all_metadatas[i:i + BATCH_SIZE]
        batch_ids = all_ids[i:i + BATCH_SIZE]
        
        try:
            collection.add(
                documents=batch_docs,
                metadatas=batch_metas,
                ids=batch_ids
            )
            added_count += len(batch_docs)
        except Exception as e:
            # Якщо ID вже існує - пропускаємо
            if "duplicate" in str(e).lower():
                skipped_count += len(batch_docs)
            else:
                logger.warning(f"⚠️  Помилка додавання batch: {e}")
        
        upload_progress.update(len(batch_docs))
        
        if added_count % 200 == 0:
            elapsed = (datetime.now() - start_time).total_seconds()
            rate = added_count / elapsed if elapsed > 0 else 0
            upload_progress.render(f"Додано: {added_count:,} | Пропущено: {skipped_count:,} | {rate:.1f} док/сек")
    
    elapsed = (datetime.now() - start_time).total_seconds()
    upload_progress.finish()
    
    # Фінальна статистика
    print("\n" + "="*80)
    print("  📊 СТАТИСТИКА")
    print("="*80)
    print(f"PDF файлів оброблено:     {len(pdf_files)}")
    print(f"Чанків створено:          {total_chunks:,}")
    print(f"Додано до ChromaDB:       {added_count:,}")
    print(f"Пропущено (дублікати):    {skipped_count:,}")
    print(f"Час виконання:            {elapsed:.1f} сек ({elapsed/60:.1f} хв)")
    if elapsed > 0:
        print(f"Швидкість:                {added_count/elapsed:.1f} документів/сек")
    
    final_count = collection.count()
    print(f"\n✅ Фінальна кількість:    {final_count:,}")
    
    # Список законів
    print(f"\n📚 ЗАКОНИ В БАЗІ:")
    results = collection.get(include=['metadatas'])
    
    laws_found = {}
    for metadata in results['metadatas']:
        law = metadata.get('law_name', 'Unknown')
        if law not in laws_found:
            laws_found[law] = 0
        laws_found[law] += 1
    
    for law, count in sorted(laws_found.items()):
        print(f"   • {law}: {count} чанків")
    
    # Тестовий пошук
    print("\n" + "="*80)
    print("  🔍 ТЕСТОВИЙ ПОШУК")
    print("="*80)
    
    test_queries = [
        "BGB параграф 1",
        "Kündigung frist",
        "SGB leistung",
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
                    preview = doc[:80].replace('\n', ' ')
                    print(f"   {i}. {law}: {preview}...")
            else:
                print("   ❌ Нічого не знайдено")
        except Exception as e:
            print(f"   ❌ Помилка: {e}")
    
    print("\n" + "="*80)
    print("  ✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!")
    print("="*80)
    print(f"\n📁 Шлях до бази: {CHROMA_DB_PATH.absolute()}\n")


if __name__ == '__main__':
    try:
        upload_general_laws()
    except KeyboardInterrupt:
        print("\n\n⚠️  Зупинено користувачем")
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
