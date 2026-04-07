#!/usr/bin/env python3
"""
Simple Fast Rebuild (Batch Processing)
Проста швидка перебудова з прогресом

Обробляє файли пачками по 100 з показом прогресу
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
import sys

logging.basicConfig(
    level=logging.INFO,
    format='%(message)s',
    stream=sys.stdout
)
logger = logging.getLogger('simple_rebuild')

def main():
    print("="*70)
    print("  🚀 ПЕРЕБУДОВА ІНДЕКСУ (BATCH PROCESSING)")
    print("="*70)
    
    laws_dir = Path('data/german_laws_complete')
    output_file = Path('data/fast_law_index.json')
    
    # Знаходимо всі .md файли
    print("\n🔍 Пошук .md файлів...")
    md_files = list(laws_dir.rglob('*.md'))
    md_files = [f for f in md_files if f.name.lower() not in ['readme.md', 'license.md']]
    
    total = len(md_files)
    print(f"   Знайдено: {total:,} файлів")
    
    # Парсинг
    print("\n📖 Парсинг законів...")
    laws_index = {}
    total_paragraphs = 0
    
    for i, file_path in enumerate(md_files):
        try:
            # Назва закону
            law_name = file_path.parent.name.upper() if file_path.stem.lower() == 'index' else file_path.stem.upper()
            
            if len(law_name) < 2:
                continue
            
            # Читаємо і парсимо
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Дуже простий regex
            matches = re.findall(r'§\s*(\d+[a-z]?)', content, re.IGNORECASE)
            paragraphs = sorted(list(set([f'§ {m}' for m in matches])))
            
            if paragraphs:
                if law_name not in laws_index:
                    laws_index[law_name] = []
                
                existing = set(laws_index[law_name])
                new_paras = [p for p in paragraphs if p not in existing]
                laws_index[law_name].extend(new_paras)
                total_paragraphs += len(new_paras)
            
            # Прогрес кожні 100 файлів
            if (i + 1) % 100 == 0:
                progress = (i + 1) / total * 100
                eta_minutes = (total - (i + 1)) / ((i + 1) / ((datetime.now().timestamp() - start_time) + 0.001)) / 60
                print(f"   Прогрес: {i + 1}/{total} ({progress:.1f}%) | Законів: {len(laws_index)} | Параграфів: {total_paragraphs:,} | ETA: {eta_minutes:.0f}хв")
                
        except Exception as e:
            pass
    
    # Фінальний індекс
    print(f"\n💾 Збереження...")
    
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
    
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(index_data, f, indent=2, ensure_ascii=False)
    
    file_size = output_file.stat().st_size / 1024 / 1024
    print(f"✅ Збережено: {output_file}")
    print(f"   Розмір: {file_size:.2f} MB")
    
    # Статистика
    print("\n" + "="*70)
    print("  📊 СТАТИСТИКА")
    print("="*70)
    print(f"   Законів: {len(laws_index):,}")
    print(f"   Параграфів: {total_paragraphs:,}")
    
    # Топ 10
    print(f"\n  📚 ТОП 10 ЗАКОНІВ:")
    sorted_laws = sorted(laws_index.items(), key=lambda x: len(x[1]), reverse=True)[:10]
    for i, (law, paras) in enumerate(sorted_laws, 1):
        print(f"   {i}. {law}: {len(paras):,} параграфів")
    
    print("\n" + "="*70)
    print("  ✅ ГОТОВО!")
    print("="*70)

if __name__ == '__main__':
    start_time = datetime.now().timestamp()
    main()
