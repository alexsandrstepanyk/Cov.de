#!/usr/bin/env python3
"""
Rebuild Fast Law Index
Перебудова JSON індексу для fast_law_search.py

Цей скрипт:
1. Сканує всі .md файли в data/german_laws_complete/
2. Витягує назви законів та параграфів
3. Створює повний JSON індекс
4. Зберігає в data/fast_law_index.json

Час виконання: ~2-5 хвилин
"""

import re
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('rebuild_index')


class FastIndexBuilder:
    """Швидкий будівник індексу законів."""

    def __init__(self, laws_dir: str = 'data/german_laws_complete'):
        self.laws_dir = Path(laws_dir)
        self.output_file = Path('data/fast_law_index.json')
        
        self.stats = {
            'files_scanned': 0,
            'laws_found': 0,
            'paragraphs_found': 0,
            'errors': 0,
        }

    def extract_law_name(self, file_path: Path) -> str:
        """
        Витягнути назву закону з шляху.
        
        Приклад:
          data/german_laws_complete/b/bgb/index.md → BGB
          data/german_laws_complete/s/sgb_2/index.md → SGB_II
        """
        # Отримуємо назву з кінця шляху
        law_name = file_path.stem
        
        # Якщо це index.md - беремо назву з батьківської директорії
        if law_name.lower() == 'index':
            # Беремо назву директорії (напр. 'bgb' → 'BGB')
            law_name = file_path.parent.name.upper()
        
        return law_name

    def extract_paragraphs(self, content: str) -> List[str]:
        """
        Витягнути всі параграфи з контенту.
        
        Знаходить всі входження § XX
        """
        paragraphs = set()
        
        # Патерн для пошуку параграфів: § 123 або §123
        pattern = r'§\s*(\d+[a-z]*)'
        
        matches = re.findall(pattern, content, re.IGNORECASE)
        
        for match in matches:
            para = f'§ {match}'
            paragraphs.add(para)
        
        return sorted(list(paragraphs))

    def scan_all_files(self) -> Dict[str, List[str]]:
        """
        Сканувати всі .md файли і створити індекс.
        
        Returns:
            Dict {law_name: [paragraphs]}
        """
        logger.info("🔍 Сканування всіх .md файлів...")
        
        md_files = list(self.laws_dir.rglob('*.md'))
        logger.info(f"   Знайдено {len(md_files):,} файлів")
        
        laws_index = {}
        processed = 0
        
        for i, file_path in enumerate(md_files):
            try:
                # Пропускаємо службові файли
                if file_path.name.lower() in ['readme.md', 'license.md']:
                    continue
                
                # Витягуємо назву закону
                law_name = self.extract_law_name(file_path)
                
                # Пропускаємо якщо назва занадто коротка
                if len(law_name) < 2:
                    continue
                
                # Читаємо файл
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Витягуємо параграфи
                paragraphs = self.extract_paragraphs(content)
                
                if paragraphs:
                    # Додаємо до індексу
                    if law_name not in laws_index:
                        laws_index[law_name] = []
                    
                    # Додаємо унікальні параграфи
                    existing = set(laws_index[law_name])
                    for para in paragraphs:
                        if para not in existing:
                            laws_index[law_name].append(para)
                            existing.add(para)
                    
                    self.stats['paragraphs_found'] += len(paragraphs)
                
                processed += 1
                self.stats['files_scanned'] += 1
                
                if (i + 1) % 500 == 0:
                    logger.info(f"   Оброблено {i + 1}/{len(md_files)} файлів")
                    logger.info(f"   Законів: {len(laws_index)}, Параграфів: {self.stats['paragraphs_found']}")
                    
            except Exception as e:
                logger.warning(f"⚠️ Помилка {file_path}: {e}")
                self.stats['errors'] += 1
        
        self.stats['laws_found'] = len(laws_index)
        
        logger.info(f"\n   Всього оброблено: {processed} файлів")
        
        return laws_index

    def build_index(self) -> Dict:
        """
        Побудувати повний індекс.
        
        Returns:
            Dict з індексом
        """
        logger.info("="*70)
        logger.info("  🏗️  ПОБУДОВА ІНДЕКСУ ЗАКОНІВ")
        logger.info("="*70)
        
        # Сканування
        laws_index = self.scan_all_files()
        
        # Формування фінальної структури
        index_data = {
            'created_at': datetime.now().isoformat(),
            'total_laws': len(laws_index),
            'total_paragraphs': self.stats['paragraphs_found'],
            'laws': {}
        }
        
        # Додаємо кожен закон
        for law_name, paragraphs in sorted(laws_index.items()):
            index_data['laws'][law_name] = {
                'paragraph_count': len(paragraphs),
                'paragraphs': paragraphs
            }
        
        # Збереження
        self._save_index(index_data)
        
        return index_data

    def _save_index(self, index_data: Dict):
        """Зберегти індекс в файл."""
        logger.info(f"\n💾 Збереження індексу...")
        
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(self.output_file, 'w', encoding='utf-8') as f:
            json.dump(index_data, f, indent=2, ensure_ascii=False)
        
        file_size = self.output_file.stat().st_size / 1024 / 1024
        logger.info(f"✅ Збережено: {self.output_file}")
        logger.info(f"   Розмір: {file_size:.2f} MB")

    def print_stats(self, index_data: Dict):
        """Вивести статистику."""
        logger.info("\n" + "="*70)
        logger.info("  📊 СТАТИСТИКА")
        logger.info("="*70)
        
        logger.info(f"   Файлів проскановано: {self.stats['files_scanned']:,}")
        logger.info(f"   Законів знайдено: {index_data['total_laws']:,}")
        logger.info(f"   Параграфів знайдено: {index_data['total_paragraphs']:,}")
        logger.info(f"   Помилок: {self.stats['errors']}")
        
        # Топ 10 законів
        logger.info(f"\n  📚 ТОП 10 ЗАКОНІВ (за кількістю параграфів):")
        
        sorted_laws = sorted(
            index_data['laws'].items(),
            key=lambda x: x[1]['paragraph_count'],
            reverse=True
        )[:10]
        
        for i, (law_name, law_data) in enumerate(sorted_laws, 1):
            count = law_data['paragraph_count']
            logger.info(f"   {i}. {law_name}: {count:,} параграфів")


def main():
    """Головна функція."""
    builder = FastIndexBuilder()
    
    # Побудова індексу
    index_data = builder.build_index()
    
    # Статистика
    builder.print_stats(index_data)
    
    # Перевірка
    logger.info("\n" + "="*70)
    logger.info("  ✅ ПЕРЕВІРКА")
    logger.info("="*70)
    
    # Завантажуємо назад і перевіряємо
    with open(builder.output_file, 'r', encoding='utf-8') as f:
        verified = json.load(f)
    
    logger.info(f"   Законів в індексі: {verified['total_laws']:,}")
    logger.info(f"   Параграфів в індексі: {verified['total_paragraphs']:,}")
    
    if verified['total_laws'] > 100:
        logger.info("\n   ✅ Індекс успішно побудовано!")
    else:
        logger.info("\n   ⚠️  Мало законів! Перевірте вихідні дані.")
    
    logger.info("\n" + "="*70)


if __name__ == '__main__':
    main()
