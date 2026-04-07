#!/usr/bin/env python3
"""Build RAG index from complete laws database."""

import json
from datetime import datetime
import os

SOURCE_FILE = 'data/complete_law_json/german_laws_complete.json'
OUTPUT_FILE = 'data/fast_law_index.json'

print("=" * 70)
print("  📚 ПОБУДОВА ІНДЕКСУ ДЛЯ RAG")
print("=" * 70)

print(f"\n📖 Завантаження {SOURCE_FILE}...")

with open(SOURCE_FILE, 'r', encoding='utf-8') as f:
    laws_list = json.load(f)

print(f"   Законів у списку: {len(laws_list)}")

# Побудова індексу
index = {
    'created_at': str(datetime.now()),
    'total_laws': 0,
    'total_paragraphs': 0,
    'laws': {}
}

total_paragraphs = 0
processed = 0

for law_item in laws_list:
    law_name = law_item.get('law_name', 'Unknown')
    paragraphs_data = law_item.get('paragraphs', [])
    
    # Витягуємо номери параграфів
    paragraph_numbers = []
    for para in paragraphs_data:
        if isinstance(para, dict):
            para_num = para.get('paragraph', '')
            if para_num:
                paragraph_numbers.append(para_num)
    
    # Додаємо до індексу
    if paragraph_numbers:
        index['laws'][law_name] = {
            'paragraph_count': len(paragraph_numbers),
            'paragraphs': paragraph_numbers[:100]  # Обмежуємо для економії
        }
        total_paragraphs += len(paragraph_numbers)
        index['total_laws'] += 1
        processed += 1
        
        if processed % 1000 == 0:
            print(f"   Оброблено: {processed} законів...")

index['total_paragraphs'] = total_paragraphs

# Збереження
print(f"\n💾 Збереження індексу...")
print(f"   Законів: {index['total_laws']}")
print(f"   Параграфів: {index['total_paragraphs']}")

with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
    json.dump(index, f, ensure_ascii=False, indent=2)

output_size = os.path.getsize(OUTPUT_FILE) / (1024 * 1024)
print(f"   Розмір: {output_size:.1f} MB")

print(f"\n✅ Індекс побудовано: {OUTPUT_FILE}")
print("=" * 70)
