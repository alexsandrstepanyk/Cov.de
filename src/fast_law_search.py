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
        Пошук законів за запитом.
        
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
        
        # Пошук по всіх законах
        for law_name, law_data in self.index.get('laws', {}).items():
            # Перевірка чи закон відповідає запиту
            if query_lower in law_name.lower():
                results.append({
                    'law': law_name,
                    'paragraphs': law_data.get('paragraphs', []),
                    'relevance': 1.0
                })
            
            # Пошук по параграфах
            for para in law_data.get('paragraphs', []):
                if query_lower in para.lower():
                    results.append({
                        'law': law_name,
                        'paragraph': para,
                        'relevance': 0.9
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
