#!/usr/bin/env python3
"""
RAG Database Quality Check
Перевірка якості RAG бази даних

Цей скрипт показує:
1. Скільки документів в ChromaDB
2. Які закони доступні
3. Чи працює пошук
"""

import json
import sys
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("="*70)
print("  🔍 ПЕРЕВІРКА ЯКОСТІ RAG БАЗИ")
print("="*70)

# ============================================================================
# 1. ПЕРЕВІРКА fast_law_index.json
# ============================================================================
print("\n" + "="*70)
print("  1️⃣  ПЕРЕВІРКА JSON ІНДЕКСУ")
print("="*70)

index_file = Path('data/fast_law_index.json')
if index_file.exists():
    print(f"\n✅ Файл існує: {index_file}")
    print(f"   Розмір: {index_file.stat().st_size / 1024 / 1024:.2f} MB")
    
    with open(index_file, 'r', encoding='utf-8') as f:
        index_data = json.load(f)
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"   Загальна кількість законів: {index_data.get('total_laws', 0):,}")
    print(f"   Загальна кількість параграфів: {index_data.get('total_paragraphs', 0):,}")
    print(f"   Дата створення: {index_data.get('created_at', 'N/A')}")
    
    # Показуємо перші 10 законів
    laws = index_data.get('laws', {})
    print(f"\n📚 ПЕРШІ 10 ЗАКОНІВ:")
    for i, (law_name, law_info) in enumerate(list(laws.items())[:10], 1):
        para_count = law_info.get('paragraph_count', 0)
        print(f"   {i}. {law_name}: {para_count} параграфів")
else:
    print(f"\n❌ Файл не знайдено: {index_file}")

# ============================================================================
# 2. ПЕРЕВІРКА ChromaDB
# ============================================================================
print("\n" + "="*70)
print("  2️⃣  ПЕРЕВІРКА ChromaDB")
print("="*70)

try:
    import chromadb
    
    chroma_path = Path('data/chroma_db')
    if chroma_path.exists():
        print(f"\n✅ ChromaDB існує: {chroma_path}")
        print(f"   Розмір: {sum(f.stat().st_size for f in chroma_path.rglob('*') if f.is_file()) / 1024 / 1024:.2f} MB")
        
        # Підключення до бази
        client = chromadb.PersistentClient(path=str(chroma_path))
        
        # Отримуємо список колекцій
        collections = client.list_collections()
        print(f"\n📊 КОЛЕКЦІЇ:")
        print(f"   Кількість колекцій: {len(collections)}")
        
        for collection in collections:
            print(f"\n   📁 Колекція: {collection.name}")
            try:
                count = collection.count()
                print(f"      Кількість документів: {count:,}")
                
                # Пробуємо отримати кілька документів для перевірки
                if count > 0:
                    sample = collection.get(limit=1)
                    if sample and sample['documents']:
                        doc = sample['documents'][0]
                        print(f"      Приклад документу: {doc[:100]}...")
            except Exception as e:
                print(f"      ⚠️ Помилка: {e}")
    else:
        print(f"\n❌ ChromaDB не знайдено: {chroma_path}")
        
except ImportError:
    print("\n❌ ChromaDB не встановлено")
    print("   Встановіть: pip3 install chromadb")
except Exception as e:
    print(f"\n❌ Помилка перевірки ChromaDB: {e}")

# ============================================================================
# 3. ПЕРЕВІРКА fast_law_search.py
# ============================================================================
print("\n" + "="*70)
print("  3️⃣  ТЕСТУВАННЯ ПОШУКУ")
print("="*70)

try:
    from src.fast_law_search import FastLawSearch
    
    searcher = FastLawSearch()
    
    if searcher.index:
        print("\n✅ FastLawSearch завантажено")
        
        # Тестові запити
        test_queries = [
            "§ 59 SGB II",
            "BGB § 286",
            "AO § 172",
            "Jobcenter",
            "Kündigung"
        ]
        
        print("\n🧪 ТЕСТОВІ ЗАПИТИ:")
        for query in test_queries:
            print(f"\n   🔍 Запит: '{query}'")
            results = searcher.search(query, limit=3)
            print(f"      Знайдено: {len(results)} результатів")
            
            if results:
                for i, r in enumerate(results[:2], 1):
                    law = r.get('law', 'N/A')
                    para = r.get('paragraph', 'N/A')
                    print(f"      {i}. {law}: {para}")
            else:
                print("      ⚠️ Нічого не знайдено")
    else:
        print("\n❌ FastLawSearch не завантажив індекс")
        
except Exception as e:
    print(f"\n❌ Помилка FastLawSearch: {e}")

# ============================================================================
# 4. ПЕРЕВІРКА вихідних даних (git clone)
# ============================================================================
print("\n" + "="*70)
print("  4️⃣  ПЕРЕВІРКА ВИХІДНИХ ДАНИХ")
print("="*70)

german_laws_path = Path('data/german_laws_complete')
if german_laws_path.exists():
    print(f"\n✅ Директорія існує: {german_laws_path}")
    
    # Рахуємо кількість .md файлів
    md_files = list(german_laws_path.rglob('*.md'))
    print(f"   Кількість .md файлів: {len(md_files):,}")
    
    # Показуємо структуру
    subdirs = [d for d in german_laws_path.iterdir() if d.is_dir() and not d.name.startswith('.')]
    print(f"\n   📁 Піддиректорії ({len(subdirs)}):")
    for subdir in sorted(subdirs)[:10]:
        files_count = len(list(subdir.rglob('*.md')))
        print(f"      {subdir.name}: {files_count} файлів")
    
    if len(subdirs) > 10:
        print(f"      ... і ще {len(subdirs) - 10} директорій")
else:
    print(f"\n❌ Директорія не знайдено: {german_laws_path}")

# ============================================================================
# 5. ФІНАЛЬНИЙ ВИСНОВОК
# ============================================================================
print("\n" + "="*70)
print("  📊 ФІНАЛЬНИЙ ВИСНОВОК")
print("="*70)

issues = []

# Перевірка JSON індексу
if not index_file.exists():
    issues.append("❌ JSON індекс відсутній")
elif index_data.get('total_paragraphs', 0) == 0:
    issues.append("❌ JSON індекс порожній")

# Перевірка ChromaDB
if not chroma_path.exists():
    issues.append("❌ ChromaDB відсутній")

# Перевірка вихідних даних
if not german_laws_path.exists():
    issues.append("❌ Вихідні дані відсутні")
elif len(md_files) == 0:
    issues.append("❌ Вихідні дані порожні")

if issues:
    print("\n⚠️  ЗНАЙДЕНО ПРОБЛЕМИ:")
    for issue in issues:
        print(f"   {issue}")
    print("\n🔧 Потрібно перебудувати базу!")
else:
    print("\n✅ ВСЕ В ПОРЯДКУ!")
    print("   RAG база готова до використання")

print("\n" + "="*70)
