#!/usr/bin/env python3
"""
Setup Script for LLM Database
Імпорт німецьких кодексів у ChromaDB для RAG
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

# Імпорт ChromaDB
try:
    import chromadb
    from chromadb.config import Settings
    print("✅ ChromaDB імпортовано")
except Exception as e:
    print(f"❌ ChromaDB недоступний: {e}")
    print("\nВстановіть: pip3 install chromadb")
    sys.exit(1)

# Імпорт кодексів з legal_database.py
try:
    from legal_database import PARAGRAPHS
    print(f"✅ Завантажено {len(PARAGRAPHS)} параграфів")
except Exception as e:
    print(f"⚠️ legal_database недоступний: {e}")
    PARAGRAPHS = []

# Імпорт з smart_law_reference.py
try:
    from smart_law_reference import LAW_DATABASE
    print(f"✅ Завантажено {len(LAW_DATABASE)} організацій")
except Exception as e:
    print(f"⚠️ smart_law_reference недоступний: {e}")
    LAW_DATABASE = {}


def setup_database():
    """Створення векторної бази даних кодексів."""
    
    print("\n" + "="*70)
    print("  📚 СТВОРЕННЯ БАЗИ НІМЕЦЬКИХ КОДЕКСІВ")
    print("="*70)
    
    # Створити директорію
    db_path = Path('data/legal_database_chroma')
    db_path.mkdir(parents=True, exist_ok=True)
    
    # Створити persistent client
    print(f"\n📂 Шлях до бази: {db_path.absolute()}")
    
    client = chromadb.PersistentClient(path=str(db_path))
    
    # Отримати або створити колекцію
    try:
        collection = client.get_collection(name='german_laws')
        print("✅ Колекція 'german_laws' знайдена")
    except:
        collection = client.create_collection(
            name='german_laws',
            metadata={'description': 'Німецькі юридичні кодекси'}
        )
        print("✅ Колекцію 'german_laws' створено")
    
    # Додати параграфи
    print(f"\n📖 Імпорт параграфів...")
    
    laws_added = 0
    
    for para in PARAGRAPHS:
        try:
            # Формувати ID
            law_id = f"{para.get('code', 'XXX')}_{para.get('paragraph', '000')}"
            
            # Формувати текст для пошуку
            text = f"""
{para.get('paragraph', '')} {para.get('title_de', '')}
{para.get('description_uk', '')}
{para.get('description_de', '')}
Код: {para.get('code', '')}
"""
            
            # Metadata
            metadata = {
                'code': para.get('code', ''),
                'paragraph': para.get('paragraph', ''),
                'title_de': para.get('title_de', ''),
                'title_uk': para.get('title_uk', ''),
            }
            
            # Додати до колекції
            collection.add(
                documents=[text],
                metadatas=[metadata],
                ids=[law_id]
            )
            
            laws_added += 1
            
        except Exception as e:
            print(f"⚠️ Помилка додавання {para.get('paragraph', 'N/A')}: {e}")
    
    print(f"✅ Додано {laws_added} параграфів")
    
    # Додати ситуації з організаціями
    print(f"\n🏢 Імпорт організацій та ситуацій...")
    
    orgs_added = 0
    
    for org_key, org_data in LAW_DATABASE.items():
        for sit_key, sit_data in org_data.get('laws', {}).items():
            try:
                law_id = f"{org_key}_{sit_key}"
                
                text = f"""
Організація: {org_data.get('name_en', org_key)}
Ситуація: {sit_key}
{sit_data.get('description_uk', '')}
{sit_data.get('description_de', '')}
Параграфи: {', '.join(sit_data.get('paragraphs', []))}
Ключові слова: {', '.join(sit_data.get('keywords', []))}
"""
                
                metadata = {
                    'organization': org_key,
                    'situation': sit_key,
                    'name_en': org_data.get('name_en', org_key),
                }
                
                collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[law_id]
                )
                
                orgs_added += 1
                
            except Exception as e:
                print(f"⚠️ Помилка додавання {org_key}/{sit_key}: {e}")
    
    print(f"✅ Додано {orgs_added} організацій/ситуацій")
    
    # Статистика
    print(f"\n" + "="*70)
    print("  📊 СТАТИСТИКА")
    print("="*70)
    
    count = collection.count()
    print(f"Всього записів: {count}")
    
    # Приклад пошуку
    print(f"\n🔍 ТЕСТОВИЙ ПОШУК...")
    
    test_queries = [
        "Jobcenter Einladung Termin",
        "Inkasso Mahnung Zahlung",
        "Finanzamt Steuerbescheid",
    ]
    
    for query in test_queries:
        results = collection.query(
            query_texts=[query],
            n_results=2
        )
        
        if results['documents'] and results['documents'][0]:
            print(f"\n  Запит: '{query}'")
            for doc in results['documents'][0]:
                print(f"  - {doc[:100]}...")
    
    print(f"\n" + "="*70)
    print("  ✅ БАЗУ СТВОРЕНО УСПІШНО!")
    print("="*70)
    print(f"\nШлях: {db_path.absolute()}")
    print(f"Записів: {count}")
    print(f"\nТепер запустіть: python3 src/test_llm_system.py")


if __name__ == '__main__':
    setup_database()
