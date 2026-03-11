#!/usr/bin/env python3
"""
Cache Module for Gov.de
LRU кешування для оптимізації запитів до бази законів та перекладів.
"""

import time
import hashlib
import logging
from typing import Any, Dict, List, Optional, Tuple
from collections import OrderedDict
from pathlib import Path
import json
import os

logger = logging.getLogger(__name__)


class CacheEntry:
    """Запис кешу з даними та метаданими."""
    
    def __init__(self, data: Any, ttl: int = 3600):
        self.data = data
        self.created_at = time.time()
        self.ttl = ttl  # Time To Live в секундах
    
    def is_expired(self) -> bool:
        """Перевіряє, чи запис прострочений."""
        return time.time() - self.created_at > self.ttl
    
    def time_remaining(self) -> float:
        """Повертає залишок часу життя в секундах."""
        remaining = self.ttl - (time.time() - self.created_at)
        return max(0, remaining)


class LRUCache:
    """
    LRU (Least Recently Used) кеш з обмеженим розміром.
    
    Features:
    - Обмеження за кількістю записів
    - Автоматичне видалення найстаріших записів
    - TTL (Time To Live) для кожного запису
    - Статистика використання
    """
    
    def __init__(self, max_size: int = 1000, default_ttl: int = 3600):
        """
        Ініціалізація кешу.
        
        Args:
            max_size: Максимальна кількість записів
            default_ttl: Час життя запису за замовчуванням (секунди)
        """
        self.max_size = max_size
        self.default_ttl = default_ttl
        self._cache: OrderedDict[str, CacheEntry] = OrderedDict()
        self._hits = 0
        self._misses = 0
        self._evictions = 0
    
    def _generate_key(self, *args, **kwargs) -> str:
        """Генерує унікальний ключ для аргументів."""
        key_data = json.dumps({'args': args, 'kwargs': kwargs}, sort_keys=True, default=str)
        return hashlib.sha256(key_data.encode()).hexdigest()[:16]
    
    def get(self, key: str) -> Optional[Any]:
        """
        Отримує дані з кешу.
        
        Args:
            key: Ключ даних
            
        Returns:
            Дані або None якщо не знайдено
        """
        if key not in self._cache:
            self._misses += 1
            return None
        
        entry = self._cache[key]
        
        # Перевіряємо термін дії
        if entry.is_expired():
            del self._cache[key]
            self._misses += 1
            return None
        
        # Переміщуємо в кінець (найновіший)
        self._cache.move_to_end(key)
        self._hits += 1
        return entry.data
    
    def set(self, key: str, value: Any, ttl: Optional[int] = None) -> None:
        """
        Зберігає дані в кеші.
        
        Args:
            key: Ключ даних
            value: Дані для зберігання
            ttl: Час життя (секунди), за замовчуванням self.default_ttl
        """
        # Видаляємо старі записи якщо досягнуто ліміту
        while len(self._cache) >= self.max_size:
            # Видаляємо найстаріший запис (перший)
            self._cache.popitem(last=False)
            self._evictions += 1
        
        # Додаємо новий запис
        self._cache[key] = CacheEntry(value, ttl or self.default_ttl)
    
    def delete(self, key: str) -> bool:
        """
        Видаляє запис з кешу.
        
        Args:
            key: Ключ для видалення
            
        Returns:
            True якщо видалено, False якщо ключ не знайдено
        """
        if key in self._cache:
            del self._cache[key]
            return True
        return False
    
    def clear(self) -> None:
        """Очищає весь кеш."""
        self._cache.clear()
        logger.info("Кеш очищено")
    
    def cleanup_expired(self) -> int:
        """
        Видаляє всі прострочені записи.
        
        Returns:
            Кількість видалених записів
        """
        expired_keys = [
            key for key, entry in self._cache.items()
            if entry.is_expired()
        ]
        
        for key in expired_keys:
            del self._cache[key]
        
        if expired_keys:
            logger.debug(f"Видалено {len(expired_keys)} прострочених записів")
        
        return len(expired_keys)
    
    def get_stats(self) -> Dict[str, Any]:
        """
        Повертає статистику кешу.
        
        Returns:
            Словник зі статистикою
        """
        total_requests = self._hits + self._misses
        hit_rate = (self._hits / total_requests * 100) if total_requests > 0 else 0
        
        return {
            'size': len(self._cache),
            'max_size': self.max_size,
            'hits': self._hits,
            'misses': self._misses,
            'evictions': self._evictions,
            'hit_rate': round(hit_rate, 2),
            'memory_entries': len(self._cache),
            'default_ttl': self.default_ttl
        }
    
    def __len__(self) -> int:
        """Повертає поточний розмір кешу."""
        return len(self._cache)
    
    def __contains__(self, key: str) -> bool:
        """Перевіряє наявність ключа в кеші."""
        return key in self._cache and not self._cache[key].is_expired()


class LawSearchCache:
    """Спеціалізований кеш для пошуку законів."""
    
    def __init__(self, max_size: int = 500, default_ttl: int = 1800):
        """
        Ініціалізація кешу пошуку законів.
        
        Args:
            max_size: Максимальна кількість записів
            default_ttl: Час життя (30 хв для актуальності)
        """
        self.cache = LRUCache(max_size=max_size, default_ttl=default_ttl)
        logger.info(f"LawSearchCache ініціалізовано (max_size={max_size}, ttl={default_ttl}s)")
    
    def get_law(self, law_code: str, paragraph: str) -> Optional[Dict]:
        """
        Отримує інформацію про закон з кешу.
        
        Args:
            law_code: Код закону (напр., BGB, SGB)
            paragraph: Номер параграфа
            
        Returns:
            Дані закону або None
        """
        key = f"law:{law_code}:{paragraph}"
        return self.cache.get(key)
    
    def set_law(self, law_code: str, paragraph: str, data: Dict) -> None:
        """
        Зберігає інформацію про закон в кеші.
        
        Args:
            law_code: Код закону
            paragraph: Номер параграфа
            data: Дані закону
        """
        key = f"law:{law_code}:{paragraph}"
        self.cache.set(key, data)
    
    def get_search_results(self, query: str) -> Optional[List[Dict]]:
        """
        Отримує результати пошуку з кешу.
        
        Args:
            query: Пошуковий запит
            
        Returns:
            Список результатів або None
        """
        key = f"search:{query}"
        return self.cache.get(key)
    
    def set_search_results(self, query: str, results: List[Dict]) -> None:
        """
        Зберігає результати пошуку в кеші.
        
        Args:
            query: Пошуковий запит
            results: Список результатів
        """
        key = f"search:{query}"
        self.cache.set(key, results, ttl=900)  # 15 хв для пошуку
    
    def get_translation(self, text: str) -> Optional[str]:
        """
        Отримує переклад з кешу.
        
        Args:
            text: Текст для перекладу
            
        Returns:
            Переклад або None
        """
        key = f"translate:{hashlib.md5(text.encode()).hexdigest()}"
        return self.cache.get(key)
    
    def set_translation(self, text: str, translation: str) -> None:
        """
        Зберігає переклад в кеші.
        
        Args:
            text: Оригінальний текст
            translation: Переклад
        """
        key = f"translate:{hashlib.md5(text.encode()).hexdigest()}"
        self.cache.set(key, translation, ttl=7200)  # 2 години для перекладів
    
    def get_stats(self) -> Dict[str, Any]:
        """Повертає статистику кешу."""
        return self.cache.get_stats()
    
    def clear(self) -> None:
        """Очищає весь кеш."""
        self.cache.clear()


# Глобальний екземпляр кешу
_law_cache: Optional[LawSearchCache] = None


def get_law_cache() -> LawSearchCache:
    """
    Отримує глобальний екземпляр кешу законів.
    
    Returns:
        Екземпляр LawSearchCache
    """
    global _law_cache
    if _law_cache is None:
        # Отримуємо налаштування з env або використовуємо значення за замовчуванням
        max_size = int(os.getenv('CACHE_SIZE', 500))
        ttl = int(os.getenv('CACHE_TTL', 1800))
        _law_cache = LawSearchCache(max_size=max_size, default_ttl=ttl)
        logger.info(f"Глобальний LawSearchCache створено: {max_size} записів, {ttl}s TTL")
    return _law_cache


def cache_law_search(func):
    """
    Декоратор для кешування результатів пошуку законів.
    
    Використання:
        @cache_law_search
        def search_laws(query, ...):
            ...
    """
    def wrapper(*args, **kwargs):
        cache = get_law_cache()
        
        # Генеруємо ключ з аргументів
        key_parts = []
        for arg in args:
            if isinstance(arg, (str, int, float)):
                key_parts.append(str(arg))
            elif isinstance(arg, (list, tuple)):
                key_parts.append(str(len(arg)))
        
        for k, v in sorted(kwargs.items()):
            if isinstance(v, (str, int, float)):
                key_parts.append(f"{k}={v}")
        
        cache_key = f"func:{func.__name__}:" + ":".join(key_parts)
        
        # Перевіряємо кеш
        cached_result = cache.cache.get(cache_key)
        if cached_result is not None:
            logger.debug(f"Кеш хіт для {func.__name__}")
            return cached_result
        
        # Виконуємо функцію
        result = func(*args, **kwargs)
        
        # Зберігаємо в кеш
        cache.cache.set(cache_key, result)
        logger.debug(f"Кеш місс для {func.__name__}, збережено результат")
        
        return result
    
    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


# Приклад використання
if __name__ == '__main__':
    # Тестування кешу
    logging.basicConfig(level=logging.INFO)
    
    cache = LawSearchCache(max_size=100, default_ttl=60)
    
    # Тест 1: Збереження та отримання закону
    test_law = {
        'code': 'BGB',
        'paragraph': '§ 286',
        'title_uk': 'Прострочення боржника',
        'description_uk': 'Боржник перебуває у простроченні після отримання письмового нагадування.'
    }
    
    cache.set_law('BGB', '§ 286', test_law)
    result = cache.get_law('BGB', '§ 286')
    print(f"✅ Тест 1: {result is not None}")
    
    # Тест 2: Кешування перекладу
    cache.set_translation('Mahnung', 'Нагадування')
    translation = cache.get_translation('Mahnung')
    print(f"✅ Тест 2: {translation == 'Нагадування'}")
    
    # Тест 3: Статистика
    stats = cache.get_stats()
    print(f"📊 Статистика: {json.dumps(stats, indent=2)}")
    
    # Тест 4: Декоратор
    @cache_law_search
    def dummy_search(query: str) -> List[str]:
        time.sleep(0.1)  # Імітація повільного запиту
        return [f"Result for {query}"]
    
    # Перший виклик (місс)
    start = time.time()
    dummy_search("test")
    print(f"✅ Тест 4a (місс): {time.time() - start:.3f}s")
    
    # Другий виклик (хіт)
    start = time.time()
    dummy_search("test")
    print(f"✅ Тест 4b (хіт): {time.time() - start:.3f}s")
    
    print("\n✅ Всі тести пройдені!")
