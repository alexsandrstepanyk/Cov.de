#!/usr/bin/env python3
"""
RAG Law Search v2.0 for Gov.de - IMPROVED
Покращений пошук законів у RAG базі (ChromaDB) для Telegram бота

Покращення:
1. Гібридний пошук (semantic + keyword)
2. Краща обробка § номерів
3. Нормалізація SGB (II → 2, III → 3)
4. Пріоритет для точних співпадінь
5. Краще витягування law_name
"""

import re
import logging
from pathlib import Path
from typing import List, Dict, Optional, Tuple

logger = logging.getLogger('rag_search')

# Глобальна змінна для кешування клієнта
_chroma_client = None
_collections = {}

# Мапа римських цифр для SGB
SGB_ROMAN_MAP = {
    'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5',
    'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'
}

# Пріоритетні закони для покращеного пошуку
PRIORITY_LAWS = [
    'BGB', 'SGB_II', 'SGB_III', 'SGB_V', 'SGB_VI', 'SGB_XII',
    'AO', 'ZPO', 'StGB', 'StPO', 'GG', 'HGB', 'VVG', 'EStG'
]


def normalize_sgb(query: str) -> str:
    """
    Нормалізація SGB з римськими цифрами.
    
    Приклади:
    - "SGB II" → "SGB_2"
    - "SGB III" → "SGB_3"
    - "SGB V" → "SGB_5"
    """
    result = query
    
    # SGB II → SGB_2, SGB III → SGB_3, і т.д.
    for roman, arabic in SGB_ROMAN_MAP.items():
        result = re.sub(
            rf'\bSGB\s*{roman}\b',
            f'SGB_{arabic}',
            result,
            flags=re.IGNORECASE
        )
    
    return result


def extract_paragraph_number(query: str) -> Optional[str]:
    """
    Витягнути номер параграфа з запиту.
    
    Приклади:
    - "§ 286 BGB" → "286"
    - "параграф 196" → "196"
    - "§ 59 SGB II" → "59"
    """
    # Шукаємо § X
    match = re.search(r'§\s*(\d+[a-z]?)', query, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Шукаємо "параграф X"
    match = re.search(r'параграф\s*(\d+[a-z]?)', query, re.IGNORECASE)
    if match:
        return match.group(1)
    
    # Шукаємо "paragraph X"
    match = re.search(r'paragraph\s*(\d+[a-z]?)', query, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return None


def extract_law_name(query: str) -> Optional[str]:
    """
    Витягнути назву закону з запиту.
    
    Приклади:
    - "§ 286 BGB" → "BGB"
    - "SGB II Leistung" → "SGB_II"
    - "AO Steuerbescheid" → "AO"
    """
    # Нормалізуємо запит спочатку
    normalized = normalize_sgb(query)
    
    # Шукаємо відомі закони
    for law in PRIORITY_LAWS:
        if re.search(rf'\b{law}\b', normalized, re.IGNORECASE):
            return law
    
    # Шукаємо загальний формат (3-4 літери верхнього регістру)
    match = re.search(r'\b([A-Z]{2,4}(?:_\d+)?)\b', normalized)
    if match:
        return match.group(1)
    
    return None


def extract_law_name_from_doc(doc: str) -> str:
    """
    Витягнути назву закону з тексту документу.
    
    Приклади:
    - "BGB 286 § 286..." → "BGB"
    - "SGB_II § 59..." → "SGB_II"
    - "AO § 172..." → "AO"
    """
    # Патерн 1: BGB 286, SGB_II § 59, AO § 172
    match = re.match(r'^([A-Z_]+(?:_\d+)?)\s*(?:§?\s*\d+)?', doc)
    if match:
        law = match.group(1)
        # Нормалізуємо SGB
        if law.startswith('SGB') and '_' not in law:
            for roman, arabic in SGB_ROMAN_MAP.items():
                if roman in law:
                    return f'SGB_{arabic}'
        return law
    
    # Патерн 2: § 286 BGB (закон після параграфу)
    match = re.search(r'§\s*\d+[a-z]?\s*([A-Z]{2,4}(?:_\d+)?)', doc)
    if match:
        return match.group(1)
    
    return 'Unknown'


def keyword_search(
    collection,
    query: str,
    n_results: int = 10
) -> List[Dict]:
    """
    Пошук по ключових словах (exact match).
    
    Шукає документи які містять точні слова з запиту.
    """
    try:
        # Витягуємо ключові слова
        words = set(re.findall(r'\b[A-Za-zÄÖÜäöüß]{3,}\b', query.lower()))
        
        # Отримуємо більше документів для фільтрації
        results = collection.query(
            query_texts=[query],
            n_results=n_results * 3,  # Більше результатів для фільтрації
            include=['documents', 'metadatas', 'distances']
        )
        
        if not results or not results['documents'] or not results['documents'][0]:
            return []
        
        keyword_results = []
        
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            distance = results['distances'][0][i] if results['distances'] else 0
            
            doc_lower = doc.lower()
            
            # Рахуємо скільки ключових слів знайдено
            matches = sum(1 for word in words if word in doc_lower)
            match_ratio = matches / len(words) if words else 0
            
            # Додаємо рейтинг ключових слів
            keyword_results.append({
                'keyword_matches': matches,
                'keyword_ratio': match_ratio,
                'doc_lower': doc_lower
            })
            
            # Додаємо metadata
            for k, v in metadata.items():
                if k not in keyword_results[-1]:
                    keyword_results[-1][k] = v
            keyword_results[-1]['content'] = doc
            keyword_results[-1]['distance'] = distance
        
        # Фільтруємо - залишаємо тільки з хоча б 1 співпадінням
        filtered = [r for r in keyword_results if r['keyword_matches'] > 0]
        
        # Сортуємо по кількості співпадінь
        filtered.sort(key=lambda x: (-x['keyword_matches'], x['distance']))
        
        return filtered[:n_results]
        
    except Exception as e:
        logger.warning(f"⚠️ Keyword search error: {e}")
        return []


def semantic_search(
    collection,
    query: str,
    n_results: int = 5
) -> List[Dict]:
    """
    Семантичний пошук (vector similarity).
    """
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            include=['documents', 'metadatas', 'distances']
        )
        
        if not results or not results['documents'] or not results['documents'][0]:
            return []
        
        semantic_results = []
        
        for i, doc in enumerate(results['documents'][0]):
            metadata = results['metadatas'][0][i] if results['metadatas'] else {}
            distance = results['distances'][0][i] if results['distances'] else 0
            
            result = {
                'content': doc,
                'distance': distance
            }
            
            # Додаємо metadata
            for k, v in metadata.items():
                result[k] = v
            
            semantic_results.append(result)
        
        return semantic_results
        
    except Exception as e:
        logger.warning(f"⚠️ Semantic search error: {e}")
        return []


def hybrid_search(
    query: str,
    n_results: int = 5,
    collections: List[str] = None,
    use_keyword: bool = True
) -> List[Dict]:
    """
    Гібридний пошук (semantic + keyword).
    
    Комбінує результати обох методів з пріоритетом keyword для точних запитів.
    """
    if collections is None:
        collections = ['german_laws']
    
    all_results = []
    
    for coll_name in collections:
        collection = get_collection(coll_name)
        
        if collection is None:
            continue
        
        try:
            # Визначаємо тип запиту
            has_paragraph = extract_paragraph_number(query) is not None
            has_law = extract_law_name(query) is not None
            is_exact_query = has_paragraph or has_law
            
            # Для точних запитів (§ номер) використовуємо keyword search
            if is_exact_query and use_keyword:
                keyword_results = keyword_search(collection, query, n_results * 2)
                
                # Додаємо keyword результати з високим пріоритетом
                for r in keyword_results:
                    r['score'] = r['keyword_ratio'] * 100  # Високий score для keyword
                    r['search_type'] = 'keyword'
                    all_results.append(r)
            
            # Семантичний пошук для всіх запитів
            semantic_results = semantic_search(collection, query, n_results)
            
            for r in semantic_results:
                # Рахуємо keyword matches для семантичних результатів
                words = set(re.findall(r'\b[A-Za-zÄÖÜäöüß]{3,}\b', query.lower()))
                doc_lower = r['content'].lower()
                matches = sum(1 for word in words if word in doc_lower)
                
                r['keyword_matches'] = matches
                r['keyword_ratio'] = matches / len(words) if words else 0
                r['score'] = r['keyword_ratio'] * 50 + (1 - r['distance']) * 50
                r['search_type'] = 'semantic'
                all_results.append(r)
                
        except Exception as e:
            logger.warning(f"⚠️ Search error in {coll_name}: {e}")
    
    # Сортуємо по score
    all_results.sort(key=lambda x: -x.get('score', 0))
    
    # Прибираємо дублікати (по content)
    seen = set()
    unique_results = []
    for r in all_results:
        content_hash = hash(r['content'][:100])
        if content_hash not in seen:
            seen.add(content_hash)
            unique_results.append(r)
    
    return unique_results[:n_results]


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
                    try:
                        count = _chroma_client.get_collection('german_laws').count()
                    except:
                        count = 0
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
                    collections_list = client.list_collections()
                    if collections_list:
                        collection = client.get_collection(collections_list[0].name)
                        collection_name = collections_list[0].name
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
    Покращений пошук законів у RAG базі.
    
    Використовує гібридний пошук (semantic + keyword) для кращих результатів.
    """
    # Нормалізуємо запит
    normalized_query = normalize_sgb(query)
    
    # Гібридний пошук
    results = hybrid_search(
        query=normalized_query,
        n_results=n_results,
        collections=collections,
        use_keyword=True
    )
    
    # Покращуємо metadata
    for result in results:
        # Витягуємо law_name з документу якщо немає в metadata
        law_name = result.get('law', result.get('law_name', 'Unknown'))
        if law_name == 'Unknown' or not law_name:
            law_name = extract_law_name_from_doc(result['content'])
            result['law_name'] = law_name
        
        # Витягуємо paragraph з документу
        if not result.get('paragraph'):
            para_num = extract_paragraph_number(result['content'])
            if para_num:
                result['paragraph'] = f'§ {para_num}'
    
    return results


def search_laws_by_paragraph(
    law_name: str,
    paragraph: str,
    n_results: int = 3
) -> List[Dict]:
    """
    Пошук конкретного параграфу закону.
    """
    # Нормалізуємо назву закону
    normalized_law = normalize_sgb(law_name)
    
    query = f"{normalized_law} {paragraph}"
    
    results = search_laws(query, n_results=n_results * 2)
    
    # Фільтруємо по назві закону
    filtered = []
    for r in results:
        r_law = r.get('law_name', '').upper()
        if normalized_law.upper() in r_law or r_law in normalized_law.upper():
            filtered.append(r)
    
    # Якщо нічого не знайдено, повертаємо всі результати
    return filtered if filtered else results


def get_law_text(
    law_name: str,
    paragraph: str = None,
    max_chunks: int = 10
) -> str:
    """
    Отримати повний текст закону або параграфу.
    """
    if paragraph:
        query = f"{law_name} {paragraph}"
    else:
        query = law_name
    
    results = search_laws(query, n_results=max_chunks * 2)
    
    # Фільтруємо по назві закону
    filtered = [
        r for r in results
        if law_name.upper().replace(' ', '_') in r.get('law_name', '').upper()
    ]
    
    if not filtered:
        return f"❌ Закон {law_name} не знайдено в базі"
    
    # Сортуємо по paragraph number
    def get_para_num(r):
        para = r.get('paragraph', '')
        match = re.search(r'§\s*(\d+)', para)
        return int(match.group(1)) if match else 0
    
    filtered.sort(key=get_para_num)
    
    # Об'єднуємо текст
    texts = []
    seen_paras = set()
    
    for chunk in filtered[:max_chunks]:
        para = chunk.get('paragraph', '')
        if para and para not in seen_paras:
            texts.append(f"{para}\n{chunk['content'][:500]}")
            seen_paras.add(para)
    
    if not texts:
        return f"⚠️ Текст для {law_name} {paragraph} не знайдено"
    
    return "\n\n---\n\n".join(texts)


def analyze_query_with_rag(
    query: str,
    language: str = 'uk'
) -> Dict:
    """
    Аналіз запиту з використанням RAG пошуку.
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
        law_name = result.get('law_name', 'Unknown')
        
        if law_name not in laws_by_name:
            laws_by_name[law_name] = {
                'name': law_name,
                'paragraphs': set(),
                'chunks': [],
                'source': result.get('source', 'unknown')
            }
        
        if result.get('paragraph'):
            laws_by_name[law_name]['paragraphs'].add(result['paragraph'])
        laws_by_name[law_name]['chunks'].append(result)
    
    # Формуємо відповідь
    laws_list = []
    all_paragraphs = []
    
    for law_name, law_data in laws_by_name.items():
        paragraphs_list = sorted(list(law_data['paragraphs']))
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
def test_improved_search():
    """Тестування покращеного пошуку."""
    print("\n" + "="*80)
    print("  🔍 ТЕСТУВАННЯ ПОКРАЩЕНОГО RAG ПОШУКУ v2.0")
    print("="*80)
    
    test_queries = [
        # Точні запити з §
        ("§ 286 BGB Mahnung", ["BGB"]),
        ("§ 172 AO Steuerbescheid", ["AO"]),
        ("§ 59 SGB II", ["SGB_II", "SGB II"]),
        
        # Запити без §
        ("BGB Kündigung Wohnung", ["BGB"]),
        ("Jobcenter Leistung Bürgergeld", ["SGB_II", "SGB II"]),
        ("Finanzamt Steuern", ["AO", "EStG"]),
        
        # Українські запити
        ("параграф 196 BGB оренда", ["BGB"]),
        ("SGB II допомога", ["SGB_II", "SGB II"]),
    ]
    
    total = len(test_queries)
    success = 0
    
    for query, expected_laws in test_queries:
        print(f"\n📌 Запит: '{query}'")
        print(f"   Очікувано: {expected_laws}")
        
        results = search_laws(query, n_results=3)
        
        if results:
            # Перевіряємо чи знайдено хоча б один очікуваний закон
            found_match = False
            for r in results:
                law = r.get('law_name', 'Unknown')
                for exp in expected_laws:
                    if exp.upper().replace(' ', '_') in law.upper() or law.upper() in exp.upper().replace(' ', '_'):
                        found_match = True
                        break
                
                if found_match:
                    break
            
            if found_match:
                print(f"   ✅ УСПІХ")
                success += 1
            else:
                print(f"   ⚠️ Частково (інший закон)")
            
            # Показуємо перший результат
            top = results[0]
            law = top.get('law_name', 'Unknown')
            para = top.get('paragraph', 'N/A')
            search_type = top.get('search_type', 'unknown')
            score = top.get('score', 0)
            print(f"   → {law} {para} [{search_type}, score: {score:.1f}]")
        else:
            print(f"   ❌ НІЧОГО НЕ ЗНАЙДЕНО")
    
    print("\n" + "="*80)
    print(f"  РЕЗУЛЬТАТ: {success}/{total} ({success/total*100:.1f}%)")
    print("="*80 + "\n")
    
    return success / total


if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    test_improved_search()
