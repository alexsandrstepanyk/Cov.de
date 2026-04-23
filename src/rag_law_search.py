#!/usr/bin/env python3
"""
RAG Law Search for Gov.de
Пошук законів у RAG базі (ChromaDB) для Telegram бота
"""

import logging
from pathlib import Path
from typing import List, Dict, Optional

logger = logging.getLogger('rag_search')

# Глобальна змінна для кешування клієнта
_chroma_client = None
_collections = {}


def get_chroma_client():
    """Отримати клієнт ChromaDB (кешується)."""
    global _chroma_client

    if _chroma_client is None:
        try:
            import chromadb
            # Спочатку пробуємо нову базу (data/chroma_db), потім стару
            db_paths = [
                Path('data/chroma_db'),           # Нова база з PDF (65,186 документів)
                Path('data/legal_database_chroma')  # Стара база
            ]
            
            for db_path in db_paths:
                if db_path.exists():
                    _chroma_client = chromadb.PersistentClient(path=str(db_path))
                    count = _chroma_client.get_collection('german_laws').count() if _chroma_client else 0
                    logger.info(f"✅ Підключено до ChromaDB: {db_path} ({count:,} документів)")
                    break
                    
            if _chroma_client is None:
                logger.error("❌ Жодна база ChromaDB не знайдена")
                return None
                
        except Exception as e:
            logger.error(f"❌ Помилка підключення до ChromaDB: {e}")
            return None

    return _chroma_client


def get_collection(collection_name: str = 'german_laws'):
    """Отримати колекцію з кешуванням."""
    global _collections

    if collection_name not in _collections:
        try:
            client = get_chroma_client()
            if client is None:
                return None

            # Спробуємо отримати колекцію
            try:
                collection = client.get_collection(collection_name)
            except Exception:
                # Якщо не знайдено, пробуємо старі назви
                alt_names = ['german_laws_general', 'german_laws_full']
                for alt_name in alt_names:
                    try:
                        collection = client.get_collection(alt_name)
                        collection_name = alt_name
                        break
                    except Exception:
                        continue
                else:
                    # Якщо жодна не знайдена, повертаємо першу доступну
                    collections = client.list_collections()
                    if collections:
                        collection = client.get_collection(collections[0].name)
                        collection_name = collections[0].name
                        logger.info(f"⚠️ Використовуємо колекцію '{collection_name}' за замовчуванням")
                    else:
                        return None

            _collections[collection_name] = collection
            count = collection.count()
            logger.info(f"✅ Колекцію '{collection_name}' завантажено ({count:,} документів)")
        except Exception as e:
            logger.warning(f"⚠️ Колекцію не знайдено: {e}")
            return None

    return _collections[collection_name]


def search_laws(
    query: str,
    n_results: int = 5,
    collections: List[str] = None
) -> List[Dict]:
    """
    Пошук законів у RAG базі.

    Args:
        query: Текст запиту (німецькою або українською)
        n_results: Кількість результатів
        collections: Список колекцій для пошуку (за замовчуванням нова база)

    Returns:
        Список знайдених законів з metadata
    """
    # Використовуємо тільки нову базу з PDF (65,186 документів)
    if collections is None:
        collections = ['german_laws']

    all_results = []

    for coll_name in collections:
        collection = get_collection(coll_name)

        if collection is None:
            continue

        try:
            results = collection.query(
                query_texts=[query],
                n_results=n_results,
                include=['documents', 'metadatas', 'distances']
            )

            if results and results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    metadata = results['metadatas'][0][i] if results['metadatas'] else {}
                    distance = results['distances'][0][i] if results['distances'] else 0

                    # Витягуємо назву закону з metadata або з документу
                    law_name = metadata.get('law', 'Unknown')
                    if law_name == 'Unknown' or not law_name:
                        # Спробуємо витягнути з документу (напр. "BGB 286 § 286...")
                        import re
                        match = re.match(r'^([A-Z_]+(?:_\d+)?)\s*\d+', doc)
                        if match:
                            law_name = match.group(1)
                    
                    all_results.append({
                        'law_name': law_name,
                        'paragraph': metadata.get('paragraph', ''),
                        'chunk_index': metadata.get('chunk_index', 0),
                        'total_chunks': metadata.get('total_chunks', 1),
                        'content': doc,
                        'source': metadata.get('source', coll_name),
                        'file_name': metadata.get('file_name', ''),
                        'distance': distance,
                        'collection': coll_name
                    })
        
        except Exception as e:
            logger.warning(f"⚠️ Помилка пошуку в {coll_name}: {e}")
    
    # Сортуємо по відстані (найближчі спочатку)
    all_results.sort(key=lambda x: x['distance'])
    
    # Обрізаємо до n_results
    return all_results[:n_results]


def search_laws_by_paragraph(
    law_name: str,
    paragraph: str,
    n_results: int = 3
) -> List[Dict]:
    """
    Пошук конкретного параграфу закону.
    
    Args:
        law_name: Назва закону (наприклад, 'BGB', 'SGB_2')
        paragraph: Номер параграфу (наприклад, '§ 1', '§ 196')
        n_results: Кількість результатів
    
    Returns:
        Список знайдених чанків
    """
    query = f"{law_name} {paragraph}"
    
    results = search_laws(query, n_results=n_results)
    
    # Фільтруємо по назві закону
    filtered = [
        r for r in results 
        if law_name.upper() in r['law_name'].upper()
    ]
    
    return filtered if filtered else results


def get_law_text(
    law_name: str,
    paragraph: str = None,
    max_chunks: int = 10
) -> str:
    """
    Отримати повний текст закону або параграфу.
    
    Args:
        law_name: Назва закону
        paragraph: Номер параграфу (опціонально)
        max_chunks: Максимальна кількість чанків
    
    Returns:
        Текст закону
    """
    if paragraph:
        query = f"{law_name} {paragraph}"
    else:
        query = law_name
    
    results = search_laws(query, n_results=max_chunks * 2)
    
    # Фільтруємо по назві закону
    filtered = [
        r for r in results 
        if law_name.upper() in r['law_name'].upper()
    ]
    
    if not filtered:
        return f"❌ Закон {law_name} не знайдено в базі"
    
    # Сортуємо по chunk_index
    filtered.sort(key=lambda x: x['chunk_index'])
    
    # Об'єднуємо текст
    texts = []
    seen_indices = set()
    
    for chunk in filtered[:max_chunks]:
        if chunk['chunk_index'] not in seen_indices:
            texts.append(chunk['content'])
            seen_indices.add(chunk['chunk_index'])
    
    return "\n\n---\n\n".join(texts)


def analyze_query_with_rag(
    query: str,
    language: str = 'uk'
) -> Dict:
    """
    Аналіз запиту з використанням RAG пошуку.
    
    Args:
        query: Текст запиту
        language: Мова відповіді
    
    Returns:
        Словник з результатами аналізу
    """
    # Пошук законів
    search_results = search_laws(query, n_results=5)
    
    if not search_results:
        return {
            'found': False,
            'message': '❌ На жаль, закони не знайдено в базі.',
            'laws': [],
            'paragraphs': []
        }
    
    # Групуємо по законах
    laws_by_name = {}
    for result in search_results:
        law_name = result['law_name']
        
        if law_name not in laws_by_name:
            laws_by_name[law_name] = {
                'name': law_name,
                'paragraphs': set(),
                'chunks': [],
                'source': result['source']
            }
        
        if result['paragraph']:
            laws_by_name[law_name]['paragraphs'].add(result['paragraph'])
        laws_by_name[law_name]['chunks'].append(result)
    
    # Формуємо відповідь
    laws_list = []
    all_paragraphs = []
    
    for law_name, law_data in laws_by_name.items():
        paragraphs_list = sorted(law_data['paragraphs'])
        all_paragraphs.extend(paragraphs_list)
        
        laws_list.append({
            'law_name': law_name,
            'paragraphs': paragraphs_list,
            'source': law_data['source'],
            'preview': law_data['chunks'][0]['content'][:200] if law_data['chunks'] else ''
        })
    
    # Формуємо повідомлення
    if language == 'uk':
        message = f"✅ Знайдено законів: {len(laws_list)}\n\n"
        for law in laws_list:
            paras = ', '.join(law['paragraphs'][:5])
            if len(law['paragraphs']) > 5:
                paras += f' ... (ще {len(law["paragraphs"]) - 5})'
            message += f"📚 **{law['law_name']}**\n"
            message += f"   Параграфи: {paras}\n"
            message += f"   Джерело: {law['source']}\n\n"
    else:
        message = f"Found {len(laws_list)} laws\n\n"
        for law in laws_list:
            paras = ', '.join(law['paragraphs'][:5])
            message += f"📚 **{law['law_name']}**: {paras}\n"
    
    return {
        'found': True,
        'message': message,
        'laws': laws_list,
        'paragraphs': all_paragraphs,
        'search_results': search_results
    }


# Тестова функція
def test_rag_search():
    """Тестування RAG пошуку."""
    print("\n" + "="*80)
    print("  🔍 ТЕСТУВАННЯ RAG ПОШУКУ")
    print("="*80)
    
    test_queries = [
        "BGB § 1",
        "Kündigung frist wohnung",
        "SGB II leistung antrag",
        "параграф 196 BGB",
    ]
    
    for query in test_queries:
        print(f"\n📌 Запит: '{query}'")
        results = search_laws(query, n_results=3)
        
        if results:
            for i, result in enumerate(results[:2], 1):
                print(f"   {i}. {result['law_name']} {result['paragraph']}")
                print(f"      {result['content'][:100]}...")
        else:
            print("   ❌ Нічого не знайдено")
    
    print("\n" + "="*80)
    print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("="*80 + "\n")


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_rag_search()
