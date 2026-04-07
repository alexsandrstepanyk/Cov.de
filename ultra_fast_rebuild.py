#!/usr/bin/env python3
"""
Ultra Fast Rebuild Index (Multiprocessing)
НАДШВИДКА перебудова індексу з використанням всіх ядер

Час виконання: 3-5 хвилин (замість 50-60)
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from multiprocessing import Pool, cpu_count
from typing import Tuple, Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('ultra_fast_rebuild')

def process_file(file_path: Path) -> Tuple[str, List[str]]:
    """Обробка одного файлу."""
    try:
        # Витягуємо назву закону
        if file_path.stem.lower() == 'index':
            law_name = file_path.parent.name.upper()
        else:
            law_name = file_path.stem.upper()
        
        if len(law_name) < 2:
            return None, []
        
        # Читаємо файл
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Витягуємо параграфи (дуже швидко)
        pattern = r'§\s*(\d+[a-z]?)'
        matches = re.findall(pattern, content, re.IGNORECASE)
        paragraphs = sorted(list(set([f'§ {m}' for m in matches])))
        
        return law_name, paragraphs
        
    except Exception as e:
        return None, []

def merge_results(results: List[Tuple[str, List[str]]]) -> Dict[str, List[str]]:
    """Об'єднання результатів."""
    laws_index = {}
    
    for law_name, paragraphs in results:
        if law_name is None:
            continue
        
        if law_name not in laws_index:
            laws_index[law_name] = []
        
        existing = set(laws_index[law_name])
        for para in paragraphs:
            if para not in existing:
                laws_index[law_name].append(para)
                existing.add(para)
    
    return laws_index

def main():
    logger.info("="*70)
    logger.info("  🚀 НАДШВИДКА ПЕРЕБУДОВА ІНДЕКСУ (MULTIPROCESSING)")
    logger.info("="*70)
    
    laws_dir = Path('data/german_laws_complete')
    output_file = Path('data/fast_law_index.json')
    
    # Знаходимо всі .md файли
    logger.info("\n🔍 Пошук .md файлів...")
    md_files = list(laws_dir.rglob('*.md'))
    md_files = [f for f in md_files if f.name.lower() not in ['readme.md', 'license.md']]
    
    logger.info(f"   Знайдено: {len(md_files):,} файлів")
    logger.info(f"   Ядер CPU: {cpu_count()}")
    
    # Паралельна обробка
    logger.info("\n⚡ Паралельний парсинг...")
    
    with Pool(processes=cpu_count()) as pool:
        results = list(pool.imap(process_file, md_files, chunksize=10))
    
    # Об'єднання
    logger.info("\n🔗 Об'єднання результатів...")
    laws_index = merge_results(results)
    
    # Статистика
    total_paragraphs = sum(len(paras) for paras in laws_index.values())
    
    logger.info(f"   Законів: {len(laws_index):,}")
    logger.info(f"   Параграфів: {total_paragraphs:,}")
    
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
    
    # Топ 10 законів
    logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ:")
    sorted_laws = sorted(laws_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (law, paras) in enumerate(sorted_laws, 1):
        logger.info(f"   {i}. {law}: {len(paras):,} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ГОТОВО!")
    logger.info("="*70)

if __name__ == '__main__':
    # Для Windows/Mac потрібно if __name__ == '__main__'
    main()
