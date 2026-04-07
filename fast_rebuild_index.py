#!/usr/bin/env python3
"""
Fast Rebuild Index (Optimized)
Швидка перебудова індексу законів

Оптимізації:
- Простіший regex
- Менше перевірок
- Більше логування прогресу
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('fast_rebuild')

# Швидкий парсинг
def extract_law_name(file_path: Path) -> str:
    """Витягнути назву закону."""
    if file_path.stem.lower() == 'index':
        return file_path.parent.name.upper()
    return file_path.stem.upper()

def extract_paragraphs(content: str) -> list:
    """Швидке витягування параграфів."""
    # Простий патерн - шукаємо тільки § цифри
    pattern = r'§\s*(\d+[a-z]?)'
    matches = re.findall(pattern, content, re.IGNORECASE)
    
    # Унікальні параграфи
    paragraphs = sorted(list(set([f'§ {m}' for m in matches])))
    return paragraphs

def main():
    logger.info("="*70)
    logger.info("  🚀 ШВИДКА ПЕРЕБУДОВА ІНДЕКСУ")
    logger.info("="*70)
    
    laws_dir = Path('data/german_laws_complete')
    output_file = Path('data/fast_law_index.json')
    
    # Знаходимо всі .md файли
    logger.info("\n🔍 Пошук .md файлів...")
    md_files = list(laws_dir.rglob('*.md'))
    logger.info(f"   Знайдено: {len(md_files):,} файлів")
    
    # Фільтруємо службові
    md_files = [f for f in md_files if f.name.lower() not in ['readme.md', 'license.md']]
    logger.info(f"   Після фільтрації: {len(md_files):,} файлів")
    
    # Парсимо
    logger.info("\n📖 Парсинг законів...")
    laws_index = {}
    total_paragraphs = 0
    
    for i, file_path in enumerate(md_files):
        try:
            law_name = extract_law_name(file_path)
            
            if len(law_name) < 2:
                continue
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            paragraphs = extract_paragraphs(content)
            
            if paragraphs:
                if law_name not in laws_index:
                    laws_index[law_name] = []
                
                # Додаємо тільки нові
                existing = set(laws_index[law_name])
                new_paras = [p for p in paragraphs if p not in existing]
                laws_index[law_name].extend(new_paras)
                total_paragraphs += len(new_paras)
            
            # Прогрес
            if (i + 1) % 1000 == 0:
                logger.info(f"   Прогрес: {i + 1}/{len(md_files)} | Законів: {len(laws_index)} | Параграфів: {total_paragraphs:,}")
                
        except Exception as e:
            logger.warning(f"⚠️ Помилка {file_path}: {e}")
    
    # Фінальний індекс
    index_data = {
        'created_at': datetime.now().isoformat(),
        'total_laws': len(laws_index),
        'total_paragraphs': total_paragraphs,
        'laws': {
            law_name: {
                'paragraph_count': len(paras),
                'paragraphs': paras
            }
            for law_name, paras in sorted(laws_index.items())
        }
    }
    
    # Збереження
    logger.info(f"\n💾 Збереження...")
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    logger.info(f"✅ Збережено: {output_file}")
    logger.info(f"   Розмір: {file_size:.2f} MB")
    
    # Статистика
    logger.info("\n" + "="*70)
    logger.info("  📊 СТАТИСТИКА")
    logger.info("="*70)
    logger.info(f"   Законів: {len(laws_index):,}")
    logger.info(f"   Параграфів: {total_paragraphs:,}")
    
    # Топ 10
    logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ:")
    sorted_laws = sorted(laws_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (law, paras) in enumerate(sorted_laws, 1):
        logger.info(f"   {i}. {law}: {len(paras):,} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ГОТОВО!")
    logger.info("="*70)

if __name__ == '__main__':
    main()
