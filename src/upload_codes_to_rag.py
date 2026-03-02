#!/usr/bin/env python3
"""
Upload German Law Codes to RAG Database
Завантаження повних німецьких кодексів в RAG базу для Ollama LLM
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import chromadb
from smart_law_reference import LAW_DATABASE

print("="*70)
print("  📚 ЗАВАНТАЖЕННЯ НІМЕЦЬКИХ КОДЕКСІВ В RAG БАЗУ")
print("="*70)

# Підключення до RAG бази
db_path = Path('data/legal_database_chroma')
db_path.mkdir(parents=True, exist_ok=True)

client = chromadb.PersistentClient(path=str(db_path))

# Отримуємо або створюємо колекцію
try:
    collection = client.get_collection(name='german_laws')
    print(f"✅ Колекцію 'german_laws' знайдено")
    current_count = collection.count()
    print(f"   Поточна кількість записів: {current_count}")
except:
    collection = client.create_collection(
        name='german_laws',
        metadata={'description': 'Німецькі юридичні кодекси та параграфи'}
    )
    print("✅ Колекцію 'german_laws' створено")
    current_count = 0

# Імпорт з smart_law_reference.py
print(f"\n📖 Імпорт з LAW_DATABASE...")
print(f"   Знайдено {len(LAW_DATABASE)} організацій")

added_count = 0

for org_key, org_data in LAW_DATABASE.items():
    org_name = org_data.get('name_de', org_key)
    
    for sit_key, sit_data in org_data.get('laws', {}).items():
        try:
            # Формуємо ID
            law_id = f"{org_key}_{sit_key}"
            
            # Формуємо текст для пошуку
            text = f"""
Організація: {org_name}
Ситуація: {sit_key}
{sit_data.get('description_uk', '')}
{sit_data.get('description_de', '')}
Параграфи: {', '.join(sit_data.get('paragraphs', []))}
Ключові слова: {', '.join(sit_data.get('keywords', []))}
"""
            
            # Metadata
            metadata = {
                'code': org_key.upper(),
                'organization': org_name,
                'situation': sit_key,
                'paragraphs': ', '.join(sit_data.get('paragraphs', [])),
                'keywords': ', '.join(sit_data.get('keywords', [])),
                'description_uk': sit_data.get('description_uk', '')[:200],
                'description_de': sit_data.get('description_de', '')[:200],
            }
            
            # Додаємо до колекції
            collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[law_id]
            )
            
            added_count += 1
            
        except Exception as e:
            print(f"⚠️ Помилка додавання {org_key}/{sit_key}: {e}")

print(f"\n✅ Додано {added_count} записів")

# Статистика
new_count = collection.count()
print(f"\n" + "="*70)
print("  📊 СТАТИСТИКА")
print("="*70)
print(f"Було: {current_count} записів")
print(f"Додано: {added_count} записів")
print(f"Всього: {new_count} записів")

# Показуємо кодекси
print(f"\n📚 КОДЕКСИ В БАЗІ:")

codes = {}
results = collection.get(include=['metadatas'])
for metadata in results['metadatas']:
    code = metadata.get('code', 'UNKNOWN')
    if code not in codes:
        codes[code] = 0
    codes[code] += 1

for code, count in sorted(codes.items()):
    code_names = {
        'BGB': 'Цивільний кодекс (Bürgerliches Gesetzbuch)',
        'SGB': 'Соціальний кодекс (Sozialgesetzbuch)',
        'AO': 'Податковий кодекс (Abgabenordnung)',
        'ZPO': 'Кодекс цивільного судочинства (Zivilprozessordnung)',
        'SGB_V': 'Соціальний кодекс V (Здоров\'я)',
    }
    name = code_names.get(code, '')
    print(f"\n{code}: {count} параграфів")
    if name:
        print(f"   {name}")

print(f"\n" + "="*70)
print("  ✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!")
print("="*70)
