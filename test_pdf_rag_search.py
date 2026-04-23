#!/usr/bin/env python3
"""
Тест пошуку в RAG базі після імпорту PDF
Перевіряє чи працює пошук по законах з PDF файлів
"""

import chromadb
from pathlib import Path

print("="*70)
print("  🧪 ТЕСТ ПОШУКУ В RAG БАЗІ (PDF + Markdown)")
print("="*70)

# Підключення до ChromaDB
client = chromadb.PersistentClient(path='data/chroma_db')
collection = client.get_collection('german_laws')

count = collection.count()
print(f"\n📊 ЗАГАЛЬНА КІЛЬКІСТЬ: {count:,} документів")

# Тестові запити
test_queries = [
    # Jobcenter
    "§ 59 SGB II запрошення",
    "§ 309 SGB III праця",
    
    # BGB
    "BGB § 286 прострочення Mahnung",
    "BGB § 241 зобов'язання",
    "BGB § 535 оренда Mietvertrag",
    
    # AO
    "AO § 172 податкова Steuerbescheid",
    
    # GG
    "GG Grundgesetz конституція",
    
    # StGB
    "StGB § 263 шахрайство Betrug",
    
    # ZPO
    "ZPO § 253 позов Klage",
    
    # Загальні запити
    "Jobcenter",
    "Kündigung звільнення",
    "Inkasso борг",
]

print("\n" + "="*70)
print("  🔍 ТЕСТОВІ ЗАПИТИ")
print("="*70)

for query in test_queries:
    print(f"\n📌 Запит: '{query}'")
    print("-"*60)
    
    try:
        # Пошук в ChromaDB
        results = collection.query(
            query_texts=[query],
            n_results=3,
            include=['documents', 'metadatas', 'distances']
        )
        
        if results and results['documents'] and results['documents'][0]:
            for i, (doc, meta, distance) in enumerate(zip(
                results['documents'][0],
                results['metadatas'][0],
                results['distances'][0]
            ), 1):
                # Витягуємо метаінформацію
                law = meta.get('law', 'N/A') if meta else 'N/A'
                para = meta.get('paragraph', 'N/A') if meta else 'N/A'
                source = meta.get('source', 'Markdown') if meta else 'N/A'
                
                # Показуємо прев'ю
                preview = doc[:200].replace('\n', ' ')
                
                print(f"  {i}. [{source}] {law} {para}")
                print(f"     {preview}...")
                print(f"     Distance: {distance:.4f}")
        else:
            print("  ⚠️ Нічого не знайдено")
            
    except Exception as e:
        print(f"  ❌ Помилка: {e}")

print("\n" + "="*70)
print("  📊 ФІНАЛЬНИЙ ВИСНОВОК")
print("="*70)

# Перевіряємо які закони додано з PDF
sample = collection.get(limit=2000, include=['metadatas'])
pdf_count = 0
md_count = 0

for meta in sample['metadatas']:
    if meta:
        source = meta.get('source', 'Markdown')
        if source == 'PDF':
            pdf_count += 1
        else:
            md_count += 1

print(f"\n✅ Markdown документів: {md_count:,}")
print(f"✅ PDF документів: {pdf_count:,}")
print(f"📊 Всього: {count:,}")

if pdf_count > 0:
    print("\n🎉 PDF успішно імпортовано в RAG базу!")
else:
    print("\n⚠️ PDF документи не знайдено в метаданих")

print("="*70)
