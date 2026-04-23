#!/usr/bin/env python3
"""
Import PDF Laws to RAG Database
Обробка PDF файлів з кодексами та додавання їх до RAG бази (ChromaDB)

Цей скрипт:
1. Витягує текст з PDF файлів в папці general/
2. Парсить параграфи (§) з тексту
3. Додає їх до ChromaDB RAG бази
"""

import re
import logging
from pathlib import Path
from datetime import datetime
from pdfminer.high_level import extract_text

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger('import_pdf_laws')

# Шляхи
PDF_DIR = Path('general')
RAG_DIR = Path('data/chroma_db')

# PDF файли для обробки
PDF_FILES = [
    'AO.pdf',
    'BGB.pdf',
    'GG.pdf',
    'SGB_2.pdf',
    'SGB_3.pdf',
    'SGB_5.pdf',
    'SGB_6.pdf',
    'StGB.pdf',
    'ZPO.pdf',
    'EStG.pdf',
    'KSchG.pdf',
    'MiLoG.pdf',
    'OWiG.pdf',
    'StVO.pdf',
    'UStG.pdf',
    'EntgFG.pdf'
]

# Мапінг назв файлів до кодів законів
LAW_CODE_MAP = {
    'AO.pdf': 'AO',
    'BGB.pdf': 'BGB',
    'GG.pdf': 'GG',
    'SGB_2.pdf': 'SGB_II',
    'SGB_3.pdf': 'SGB_III',
    'SGB_5.pdf': 'SGB_V',
    'SGB_6.pdf': 'SGB_VI',
    'StGB.pdf': 'StGB',
    'ZPO.pdf': 'ZPO',
    'EStG.pdf': 'EStG',
    'KSchG.pdf': 'KSchG',
    'MiLoG.pdf': 'MiLoG',
    'OWiG.pdf': 'OWiG',
    'StVO.pdf': 'StVO',
    'UStG.pdf': 'UStG',
    'EntgFG.pdf': 'EntgFG'
}


def extract_text_from_pdf(pdf_path: Path) -> str:
    """Витягнути текст з PDF файлу."""
    try:
        text = extract_text(str(pdf_path))
        logger.info(f"✅ Текст витягнуто: {len(text)} символів")
        return text
    except Exception as e:
        logger.error(f"❌ Помилка витягування тексту: {e}")
        return ""


def parse_paragraphs_from_text(text: str, law_code: str) -> list:
    """
    Розпарсити параграфи з тексту.
    
    Повертає список словників:
    [
        {
            'law': 'BGB',
            'paragraph': '§ 241',
            'title': 'Обов'язки зі зобов'язання',
            'text': 'Повний текст параграфу...',
            'full_text': '§ 241 Обов'язки зі зобов'язання\\nПовний текст...'
        }
    ]
    """
    paragraphs = []
    
    # Патерн 1: § X [Назва]
    # Шукаємо § з цифрами та можливою назвою
    pattern1 = r'§\s*(\d+[a-z]?(?:\s*[A-Z]§)?)\s*\n?\s*([^\n]+)?\n(.*?)(?=§\s*\d+|\Z)'
    
    # Патерн 2: § X (без назви)
    pattern2 = r'§\s*(\d+[a-z]?(?:\s*[A-Z]§)?)\s*\n(.*?)(?=§\s*\d+|\Z)'
    
    # Спроба знайти параграфи з назвами
    matches = re.findall(pattern1, text, re.DOTALL)
    
    if not matches:
        # Якщо не знайдено, шукаємо прості параграфи
        matches = re.findall(pattern2, text, re.DOTALL)
        for match in matches:
            para_num = match[0]
            para_text = match[1].strip()
            paragraphs.append({
                'law': law_code,
                'paragraph': f'§ {para_num}',
                'title': '',
                'text': para_text,
                'full_text': f'§ {para_num}\n{para_text}'
            })
    else:
        for match in matches:
            para_num = match[0]
            para_title = match[1].strip() if match[1] else ''
            para_text = match[2].strip()
            
            # Очищаємо текст від зайвих нових рядків
            para_text = re.sub(r'\n\s*\n', '\n', para_text)
            para_text = re.sub(r'\s+', ' ', para_text)
            
            full_text = f"§ {para_num} {para_title}\n{para_text}".strip()
            
            if full_text and len(full_text) > 20:
                paragraphs.append({
                    'law': law_code,
                    'paragraph': f'§ {para_num}',
                    'title': para_title,
                    'text': para_text,
                    'full_text': full_text
                })
    
    return paragraphs


def add_to_chromadb(paragraphs: list, collection_name: str = 'german_laws'):
    """Додати параграфи до ChromaDB."""
    try:
        import chromadb
        
        client = chromadb.PersistentClient(path=str(RAG_DIR))
        
        # Отримуємо або створюємо колекцію
        try:
            collection = client.get_collection(name=collection_name)
            logger.info(f"✅ Колекція '{collection_name}' знайдена")
        except Exception:
            collection = client.create_collection(name=collection_name)
            logger.info(f"✅ Колекція '{collection_name}' створена")
        
        # Поточна кількість документів
        current_count = collection.count()
        logger.info(f"📊 Поточна кількість документів: {current_count:,}")
        
        # Готуємо дані для додавання
        ids = []
        documents = []
        metadatas = []
        
        for i, para in enumerate(paragraphs):
            doc_id = f"{para['law']}_{para['paragraph'].replace('§', '').replace(' ', '').replace('(', '').replace(')', '')}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{i}"
            
            ids.append(doc_id)
            documents.append(para['full_text'])
            metadatas.append({
                'law': para['law'],
                'paragraph': para['paragraph'],
                'title': para['title'][:100] if para['title'] else '',
                'source': 'PDF',
                'added_at': datetime.now().isoformat()
            })
        
        # Додаємо документи частинами по 100
        batch_size = 100
        total_added = 0
        
        for i in range(0, len(ids), batch_size):
            end_idx = min(i + batch_size, len(ids))
            
            collection.add(
                ids=ids[i:end_idx],
                documents=documents[i:end_idx],
                metadatas=metadatas[i:end_idx]
            )
            
            total_added += (end_idx - i)
            if total_added % 500 == 0:
                logger.info(f"   Додано {total_added:,} з {len(ids):,}...")
        
        new_count = collection.count()
        logger.info(f"✅ Додано {total_added:,} параграфів")
        logger.info(f"📊 Нова кількість документів: {new_count:,}")
        
        return total_added
        
    except ImportError:
        logger.error("❌ ChromaDB не встановлено")
        return 0
    except Exception as e:
        logger.error(f"❌ Помилка додавання до ChromaDB: {e}")
        return 0


def process_pdf(pdf_path: Path, law_code: str) -> int:
    """Обробити один PDF файл та додати до RAG."""
    logger.info(f"\n{'='*60}")
    logger.info(f"📄 Обробка: {pdf_path.name} → {law_code}")
    logger.info(f"{'='*60}")
    
    # Витягуємо текст
    text = extract_text_from_pdf(pdf_path)
    
    if not text:
        logger.warning("⚠️ Текст порожній, пропускаємо")
        return 0
    
    # Парсимо параграфи
    paragraphs = parse_paragraphs_from_text(text, law_code)
    
    if not paragraphs:
        logger.warning("⚠️ Параграфи не знайдено, пропускаємо")
        return 0
    
    logger.info(f"✅ Знайдено {len(paragraphs)} параграфів")
    
    # Додаємо до ChromaDB
    added = add_to_chromadb(paragraphs)
    
    return added


def main():
    """Головна функція."""
    logger.info("="*70)
    logger.info("  📚 ІМПОРТ PDF ЗАКОНІВ ДО RAG БАЗИ")
    logger.info("="*70)
    
    # Перевіряємо наявність PDF файлів
    pdf_files_to_process = []
    for pdf_name in PDF_FILES:
        pdf_path = PDF_DIR / pdf_name
        if pdf_path.exists():
            code_name = Path(pdf_name).stem.upper().replace('_', '')
            pdf_files_to_process.append((pdf_path, LAW_CODE_MAP.get(pdf_name, code_name)))
        else:
            logger.warning(f"❌ Файл не знайдено: {pdf_path}")
    
    if not pdf_files_to_process:
        logger.error("❌ Немає PDF файлів для обробки!")
        return
    
    logger.info(f"\n📋 Знайдено {len(pdf_files_to_process)} PDF файлів для обробки")
    
    # Обробляємо кожен файл
    total_added = 0
    successful = 0
    failed = 0
    
    for pdf_path, law_code in pdf_files_to_process:
        try:
            added = process_pdf(pdf_path, law_code)
            if added > 0:
                total_added += added
                successful += 1
            else:
                failed += 1
        except Exception as e:
            logger.error(f"❌ Помилка обробки {pdf_path.name}: {e}")
            failed += 1
    
    # Фінальний звіт
    logger.info("\n" + "="*70)
    logger.info("  📊 ФІНАЛЬНИЙ ЗВІТ")
    logger.info("="*70)
    logger.info(f"✅ Успішно оброблено: {successful} файлів")
    logger.info(f"❌ Не вдалося: {failed} файлів")
    logger.info(f"📚 Всього додано параграфів: {total_added:,}")
    logger.info("="*70)
    
    if total_added > 0:
        logger.info("\n🎉 RAG базу оновлено!")
        logger.info("Тепер бот може шукати закони з PDF файлів.")
    else:
        logger.warning("\n⚠️ Жодного параграфу не додано.")
        logger.warning("Перевірте PDF файли та спробуйте ще раз.")


if __name__ == '__main__':
    main()
