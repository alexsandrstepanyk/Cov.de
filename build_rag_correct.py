#!/usr/bin/env python3
"""
Build RAG Database with FULL TEXT v2
Правильна перебудова RAG бази з ПОВНИМ ТЕКСТОМ
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('build_rag_correct')

LAWS_DIR = Path('data/german_laws_complete')
OUTPUT_FILE = Path('data/fast_law_index.json')

def extract_law_name(file_path: Path) -> str:
    """Витягнути назву закону."""
    if file_path.stem.lower() == 'index':
        return file_path.parent.name.upper()
    return file_path.stem.upper()

def parse_law_file(file_path: Path) -> dict:
    """
    Розпарсити файл і витягнути ВСІ параграфи з ТЕКСТОМ.
    """
    if not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    paragraphs = {}
    
    # Різні формати файлів
    patterns = [
        # Формат 1: ### § 123 Title\nText
        (r'^###\s*§\s*(\d+[a-z]?)\s*(.*?)\n(.*?)(?=^###\s*§|\Z)', re.DOTALL | re.MULTILINE),
        # Формат 2: ##### § 123\nText
        (r'^#####\s*§\s*(\d+[a-z]?)\s*\n(.*?)(?=^#####\s*§|\Z)', re.DOTALL | re.MULTILINE),
    ]
    
    for pattern, flags in patterns:
        matches = re.findall(pattern, content, flags)
        
        if len(matches) > 0:  # Знайшли хоч щось
            for match in matches:
                if len(match) == 3:  # Формат 1
                    para_num, title, text = match
                    full_text = f"{title}\n{text}".strip()
                else:  # Формат 2
                    para_num, text = match
                    full_text = text.strip()
                
                para_name = f'§ {para_num}'
                full_text = re.sub(r'\n\s*\n', '\n', full_text)
                
                if full_text and len(full_text) > 30:
                    paragraphs[para_name] = full_text
            
            if paragraphs:  # Якщо знайшли хоч щось - повертаємо
                return paragraphs
    
    return {}

def build_index():
    """Побудувати індекс з повним текстом."""
    logger.info("="*70)
    logger.info("  🏗️  БУДІВНИЦТВО RAG БАЗИ З ПОВНИМ ТЕКСТОМ")
    logger.info("="*70)
    
    # Знаходимо всі файли
    logger.info("\n🔍 Пошук законів...")
    md_files = list(LAWS_DIR.rglob('*.md'))
    md_files = [f for f in md_files if f.name.lower() not in ['readme.md', 'license.md']]
    logger.info(f"   Знайдено: {len(md_files):,} файлів")
    
    index_data = {
        'created_at': datetime.now().isoformat(),
        'total_laws': 0,
        'total_paragraphs': 0,
        'laws': {}
    }
    
    logger.info("\n📖 Парсинг законів...")
    
    for i, file_path in enumerate(md_files):
        try:
            law_name = extract_law_name(file_path)
            
            if len(law_name) < 2:
                continue
            
            paragraphs = parse_law_file(file_path)
            
            if not paragraphs:
                continue
            
            # Додаємо в індекс
            index_data['laws'][law_name] = {
                'paragraph_count': len(paragraphs),
                'paragraphs': list(paragraphs.keys()),
                'paragraphs_full': paragraphs  # ПОВНИЙ ТЕКСТ!
            }
            
            index_data['total_laws'] += 1
            index_data['total_paragraphs'] += len(paragraphs)
            
            # Прогрес
            if (i + 1) % 500 == 0:
                logger.info(f"   Прогрес: {i + 1}/{len(md_files)} | Законів: {index_data['total_laws']} | Параграфів: {index_data['total_paragraphs']:,}")
                
        except Exception as e:
            logger.warning(f"⚠️ Помилка {file_path}: {e}")
    
    # Збереження
    logger.info(f"\n💾 Збереження...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    file_size = OUTPUT_FILE.stat().st_size / 1024 / 1024
    logger.info(f"   Розмір: {file_size:.2f} MB")
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    logger.info(f"   Законів: {index_data['total_laws']:,}")
    logger.info(f"   Параграфів з текстом: {index_data['total_paragraphs']:,}")
    
    # Топ 10
    logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ:")
    sorted_laws = sorted(index_data['laws'].items(), key=lambda x: x[1]['paragraph_count'], reverse=True)[:10]
    for i, (law, data) in enumerate(sorted_laws, 1):
        logger.info(f"   {i}. {law}: {data['paragraph_count']} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ RAG БАЗА З ПОВНИМ ТЕКСТОМ ГОТОВА!")
    logger.info("="*70)
    logger.info(f"\n📁 Файл: {OUTPUT_FILE.absolute()}")
    logger.info("")
    
    # Перевірка
    logger.info("\n🔍 ПЕРЕВІРКА:")
    test_laws = ['SGB_2', 'SGB_3', 'BGB']
    for law in test_laws:
        if law in index_data['laws']:
            data = index_data['laws'][law]
            first_para = data['paragraphs'][0]
            text_preview = data['paragraphs_full'].get(first_para, '')[:100]
            logger.info(f"   ✅ {law}: {data['paragraph_count']} параграфів")
            logger.info(f"      {first_para}: {text_preview}...")
        else:
            logger.warning(f"   ❌ {law}: не знайдено")

if __name__ == '__main__':
    build_index()
