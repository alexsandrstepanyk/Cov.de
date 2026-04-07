#!/usr/bin/env python3
"""
Build RAG Database with FULL TEXT
Перебудова RAG бази з ПОВНИМ ТЕКСТОМ законів
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(message)s')
logger = logging.getLogger('build_rag_full_text')

LAWS_DIR = Path('data/german_laws_complete')
OUTPUT_FILE = Path('data/fast_law_index_full.json')

# Основні закони для початку
MAIN_LAWS = ['SGB_2', 'SGB_3', 'SGB_5', 'SGB_8', 'SGB_12', 'BGB', 'AO_1977', 'ZPO', 'GG']

def find_law_file(law_name: str) -> Path:
    """Знайти файл закону."""
    for file_path in LAWS_DIR.rglob('*.md'):
        if file_path.name.lower() == 'index.md':
            dir_name = file_path.parent.name.lower()
            if law_name.lower().replace('_', '') in dir_name.replace('_', ''):
                return file_path
    return None

def extract_paragraphs_with_text(file_path: Path) -> dict:
    """Витягнути параграфи з ПОВНИМ ТЕКСТОМ."""
    if not file_path or not file_path.exists():
        return {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    paragraphs = {}
    
    # Патерн для ### § X ...
    pattern = r'^###\s*§\s*(\d+[a-z]?)\s*(.*?)\n(.*?)(?=^###\s*§|\Z)'
    
    matches = re.findall(pattern, content, re.DOTALL | re.MULTILINE)
    
    for para_num, title, text in matches:
        para_name = f'§ {para_num}'
        full_text = f"{title}\n{text}".strip()
        full_text = re.sub(r'\n\s*\n', '\n', full_text)
        
        if full_text and len(full_text) > 20:
            paragraphs[para_name] = full_text
    
    return paragraphs

def build_index():
    """Побудувати індекс з повним текстом."""
    logger.info("="*70)
    logger.info("  🏗️  БУДІВНИЦТВО RAG БАЗИ З ПОВНИМ ТЕКСТОМ")
    logger.info("="*70)
    
    index_data = {
        'created_at': datetime.now().isoformat(),
        'total_laws': 0,
        'total_paragraphs': 0,
        'laws': {}
    }
    
    for law_name in MAIN_LAWS:
        logger.info(f"\n📖 {law_name}...")
        
        file_path = find_law_file(law_name)
        
        if not file_path:
            logger.warning(f"   ❌ Файл не знайдено")
            continue
        
        paragraphs = extract_paragraphs_with_text(file_path)
        
        if not paragraphs:
            logger.warning(f"   ❌ Параграфи не знайдено")
            continue
        
        # Додаємо в індекс
        index_data['laws'][law_name] = {
            'paragraph_count': len(paragraphs),
            'paragraphs': list(paragraphs.keys()),  # Для сумісності
            'paragraphs_full': paragraphs  # ПОВНИЙ ТЕКСТ!
        }
        
        index_data['total_laws'] += 1
        index_data['total_paragraphs'] += len(paragraphs)
        
        logger.info(f"   ✅ {len(paragraphs)} параграфів з текстом")
    
    # Збереження
    logger.info(f"\n💾 Збереження в {OUTPUT_FILE}...")
    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    file_size = OUTPUT_FILE.stat().st_size / 1024 / 1024
    logger.info(f"   Розмір: {file_size:.2f} MB")
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    logger.info(f"   Законів: {index_data['total_laws']}")
    logger.info(f"   Параграфів: {index_data['total_paragraphs']}")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ RAG БАЗА З ПОВНИМ ТЕКСТОМ ГОТОВА!")
    logger.info("="*70)

if __name__ == '__main__':
    build_index()
