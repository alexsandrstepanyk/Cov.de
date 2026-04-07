#!/usr/bin/env python3
"""
Fast Law Search for Ollama LLM
Швидкий пошук по німецьких законах без ChromaDB
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Optional

logger = logging.getLogger('fast_law_search')

class FastLawSearch:
    """Швидкий пошук по німецьких законах."""
    
    def __init__(self, index_file: str = 'data/fast_law_index.json'):
        self.index_file = Path(index_file)
        self.index = None
        self.load_index()
    
    def load_index(self):
        """Завантаження індексу."""
        if not self.index_file.exists():
            logger.warning(f"⚠️ Індекс не знайдено: {self.index_file}")
            return
        
        with open(self.index_file, 'r', encoding='utf-8') as f:
            self.index = json.load(f)
        
        logger.info(f"✅ Індекс завантажено: {self.index.get('total_laws', 0)} законів, {self.index.get('total_paragraphs', 0)} параграфів")
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        """
        Розумний пошук законів за запитом.

        Args:
            query: Пошуковий запит (наприклад, "§ 59 SGB II")
            limit: Максимальна кількість результатів

        Returns:
            Список знайдених параграфів
        """
        if not self.index:
            return []

        results = []
        query_lower = query.lower()
        
        # Витягуємо номер параграфа з запиту (напр. "§ 59 SGB II" → "59")
        import re
        para_match = re.search(r'§\s*(\d+[a-z]?)', query, re.IGNORECASE)
        query_para_num = para_match.group(1) if para_match else None
        
        # Витягуємо назву закону (напр. "SGB II" або "SGB_2" з запиту)
        # Нормалізуємо: SGB II → SGB_2, SGB III → SGB_3, і т.д.
        query_law = None
        
        # Спочатку шукаємо формат SGB_2, BGB, AO, і т.д.
        law_match = re.search(r'\b(SGB_\d+|BGB|AO_?\d*|ZPO|StGB|HGB|GG|VwVfG|SGB\s*\d+)\b', query, re.IGNORECASE)
        if law_match:
            query_law = law_match.group(1).upper().replace(' ', '_')
            # Нормалізація римських цифр: SGB_II → SGB_2
            roman_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
            for roman, arabic in roman_map.items():
                query_law = query_law.replace(f'SGB_{roman}', f'SGB_{arabic}')
        else:
            # Шукаємо формат "SGB II" (з пробілом і римською цифрою)
            law_match2 = re.search(r'\bSGB\s+(I{1,3}|IV|V|VI|VII|VIII|IX|X)\b', query, re.IGNORECASE)
            if law_match2:
                roman = law_match2.group(1).upper()
                roman_map = {'I': '1', 'II': '2', 'III': '3', 'IV': '4', 'V': '5', 'VI': '6', 'VII': '7', 'VIII': '8', 'IX': '9', 'X': '10'}
                query_law = f'SGB_{roman_map.get(roman, roman)}'

        # Пошук по всіх законах
        for law_name, law_data in self.index.get('laws', {}).items():
            law_name_lower = law_name.lower()
            
            # 1. Прямий пошук назви закону
            if query_law:
                # Точний збіг назви закону
                if query_law.lower() == law_name_lower:
                    if query_para_num:
                        # Шукаємо конкретний параграф в цьому законі
                        target_para = f'§ {query_para_num}'
                        if target_para in law_data.get('paragraphs', []):
                            results.append({
                                'law': law_name,
                                'paragraph': target_para,
                                'relevance': 1.0
                            })
                            if len(results) >= limit:
                                return results
                    else:
                        # Просто повертаємо закон
                        results.append({
                            'law': law_name,
                            'paragraphs': law_data.get('paragraphs', []),
                            'relevance': 1.0
                        })
                        if len(results) >= limit:
                            return results
            
            # 2. Пошук по всіх параграфах (якщо запит містить § але не знайшли закон)
            elif query_para_num and '§' in query and not query_law:
                target_para = f'§ {query_para_num}'
                if target_para in law_data.get('paragraphs', []):
                    results.append({
                        'law': law_name,
                        'paragraph': target_para,
                        'relevance': 0.5
                    })

            if len(results) >= limit:
                return results

        return results
    
    def get_law(self, law_name: str) -> Optional[Dict]:
        """Отримати закон за назвою."""
        if not self.index:
            return None
        
        return self.index.get('laws', {}).get(law_name)
    
    def get_all_codes(self) -> List[str]:
        """Отримати список всіх кодексів."""
        if not self.index:
            return []
        
        return list(self.index.get('laws', {}).keys())


# Глобальний екземпляр
_searcher = None

def get_searcher() -> FastLawSearch:
    """Отримати або створити searcher."""
    global _searcher
    if _searcher is None:
        _searcher = FastLawSearch()
    return _searcher

def search_laws(query: str, limit: int = 10) -> List[Dict]:
    """Пошук законів."""
    searcher = get_searcher()
    return searcher.search(query, limit)


if __name__ == '__main__':
    # Тестування
    print("="*70)
    print("  🚑 ШВИДКИЙ ПОШУК ПО НІМЕЦЬКИХ ЗАКОНАХ")
    print("="*70)
    
    searcher = FastLawSearch()
    
    # Тестові запити
    test_queries = [
        "§ 59 SGB II",
        "BGB § 286",
        "AO § 172",
        "Jobcenter",
        "Kündigung"
    ]
    
    for query in test_queries:
        print(f"\n🔍 Запит: {query}")
        results = searcher.search(query, limit=3)
        print(f"   Знайдено: {len(results)} результатів")
        for r in results[:2]:
            print(f"   - {r.get('law', 'N/A')}: {r.get('paragraph', 'N/A')}")
