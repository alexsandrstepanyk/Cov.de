#!/usr/bin/env python3
"""
Build Complete German Law Database for Ollama LLM
Створення повної бази всіх німецьких законів для Ollama LLM

Архітектура "Адвокат":
1. Завантажити ВСІ німецькі кодекси з офіційних джерел
2. Парсинг кожного параграфу
3. Створення векторного індексу в ChromaDB
4. LLM може шукати по ВСІЙ базі законів
5. Перехресна перевірка декількох джерел
6. Точні цитати з законів
"""

import requests
import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('build_law_database')

# Офіційні джерела німецьких законів
OFFICIAL_SOURCES = {
    'gesetze-im-internet': {
        'base_url': 'https://www.gesetze-im-internet.de',
        'reliable': True,
        'official': True,
    }
}

# Список всіх кодексів які потрібно завантажити
CODES_TO_DOWNLOAD = {
    # Основні кодекси
    'BGB': {
        'name': 'Bürgerliches Gesetzbuch',
        'name_uk': 'Цивільний кодекс Німеччини',
        'url': 'https://www.gesetze-im-internet.de/bgb/',
        'priority': 1,  # Найвищий пріоритет
    },
    
    # Соціальні кодекси
    'SGB_I': {
        'name': 'Sozialgesetzbuch I',
        'name_uk': 'Соціальний кодекс I (Загальна частина)',
        'url': 'https://www.gesetze-im-internet.de/sgb_1/',
        'priority': 2,
    },
    'SGB_II': {
        'name': 'Sozialgesetzbuch II',
        'name_uk': 'Соціальний кодекс II (Jobcenter)',
        'url': 'https://www.gesetze-im-internet.de/sgb_2/',
        'priority': 1,
    },
    'SGB_III': {
        'name': 'Sozialgesetzbuch III',
        'name_uk': 'Соціальний кодекс III (Агентство з праці)',
        'url': 'https://www.gesetze-im-internet.de/sgb_3/',
        'priority': 1,
    },
    'SGB_IV': {
        'name': 'Sozialgesetzbuch IV',
        'name_uk': 'Соціальний кодекс IV',
        'url': 'https://www.gesetze-im-internet.de/sgb_4/',
        'priority': 3,
    },
    'SGB_V': {
        'name': 'Sozialgesetzbuch V',
        'name_uk': 'Соціальний кодекс V (Здоров\'я)',
        'url': 'https://www.gesetze-im-internet.de/sgb_5/',
        'priority': 2,
    },
    'SGB_VI': {
        'name': 'Sozialgesetzbuch VI',
        'name_uk': 'Соціальний кодекс VI (Пенсії)',
        'url': 'https://www.gesetze-im-internet.de/sgb_6/',
        'priority': 3,
    },
    'SGB_VII': {
        'name': 'Sozialgesetzbuch VII',
        'name_uk': 'Соціальний кодекс VII (Страхування від нещасних випадків)',
        'url': 'https://www.gesetze-im-internet.de/sgb_7/',
        'priority': 3,
    },
    'SGB_VIII': {
        'name': 'Sozialgesetzbuch VIII',
        'name_uk': 'Соціальний кодекс VIII (Діти та молодь)',
        'url': 'https://www.gesetze-im-internet.de/sgb_8/',
        'priority': 3,
    },
    'SGB_IX': {
        'name': 'Sozialgesetzbuch IX',
        'name_uk': 'Соціальний кодекс IX (Інваліди)',
        'url': 'https://www.gesetze-im-internet.de/sgb_9/',
        'priority': 3,
    },
    'SGB_X': {
        'name': 'Sozialgesetzbuch X',
        'name_uk': 'Соціальний кодекс X (Адміністративні процедури)',
        'url': 'https://www.gesetze-im-internet.de/sgb_10/',
        'priority': 2,
    },
    
    # Податкові кодекси
    'AO': {
        'name': 'Abgabenordnung',
        'name_uk': 'Податковий кодекс Німеччини',
        'url': 'https://www.gesetze-im-internet.de/ao/',
        'priority': 1,
    },
    'EStG': {
        'name': 'Einkommensteuergesetz',
        'name_uk': 'Закон про прибутковий податок',
        'url': 'https://www.gesetze-im-internet.de/estg/',
        'priority': 2,
    },
    'UStG': {
        'name': 'Umsatzsteuergesetz',
        'name_uk': 'Закон про податок на додану вартість',
        'url': 'https://www.gesetze-im-internet.de/ustg/',
        'priority': 2,
    },
    
    # Судочинство
    'ZPO': {
        'name': 'Zivilprozessordnung',
        'name_uk': 'Кодекс цивільного судочинства',
        'url': 'https://www.gesetze-im-internet.de/zpo/',
        'priority': 1,
    },
    'StPO': {
        'name': 'Strafprozessordnung',
        'name_uk': 'Кодекс кримінального судочинства',
        'url': 'https://www.gesetze-im-internet.de/stpo/',
        'priority': 2,
    },
    'VwVfG': {
        'name': 'Verwaltungsverfahrensgesetz',
        'name_uk': 'Закон про адміністративні процедури',
        'url': 'https://www.gesetze-im-internet.de/vwvfg/',
        'priority': 2,
    },
    
    # Інші важливі закони
    'GG': {
        'name': 'Grundgesetz',
        'name_uk': 'Основний закон (Конституція) Німеччини',
        'url': 'https://www.gesetze-im-internet.de/gg/',
        'priority': 1,
    },
    'BGBINFO': {
        'name': 'BGB-Informationspflicht-Verordnung',
        'name_uk': 'Закон про інформаційні обов\'язки',
        'url': 'https://www.gesetze-im-internet.de/bgbinfo/',
        'priority': 3,
    },
}


class GermanLawDatabase:
    """
    Повна база німецьких законів для Ollama LLM.
    
    Працює як "Адвокат":
    1. Завантажує всі закони з офіційних джерел
    2. Парсить кожен параграф
    3. Створює векторний індекс
    4. Надає пошук по всій базі
    5. Перехресна перевірка
    6. Точні цитати
    """
    
    def __init__(self, db_path: str = 'data/complete_law_database'):
        """Ініціалізація бази."""
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Імпорт ChromaDB
        try:
            import chromadb
            from chromadb.config import Settings
            self.chromadb = chromadb
            self.chroma_available = True
        except:
            self.chromadb = None
            self.chroma_available = False
            logger.warning("⚠️ ChromaDB недоступний")
        
        # Ініціалізація векторної бази
        self.collection = None
        if self.chroma_available:
            self._init_vector_db()
    
    def _init_vector_db(self):
        """Ініціалізація векторної бази даних."""
        if not self.chroma_available:
            return
        
        client = self.chromadb.PersistentClient(path=str(self.db_path))
        
        try:
            self.collection = client.get_collection(name='complete_german_laws')
            logger.info(f"✅ Векторна база підключено")
        except:
            self.collection = client.create_collection(
                name='complete_german_laws',
                metadata={'description': 'Повна база німецьких законів'}
            )
            logger.info(f"✅ Векторна база створено")
    
    def download_code(self, code_key: str) -> Optional[Dict]:
        """
        Завантажити кодекс з офіційного джерела.
        
        Args:
            code_key: Ключ кодексу (наприклад, 'BGB')
        
        Returns:
            Dict з даними кодексу або None
        """
        if code_key not in CODES_TO_DOWNLOAD:
            logger.error(f"❌ Кодекс {code_key} не знайдено в списку")
            return None
        
        code_info = CODES_TO_DOWNLOAD[code_key]
        url = code_info['url']
        
        logger.info(f"📥 Завантаження {code_info['name']}...")
        
        try:
            # Завантаження головної сторінки кодексу
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Парсинг списку параграфів
            paragraphs = self._parse_code_index(response.text, code_key)
            
            logger.info(f"✅ Завантажено {len(paragraphs)} параграфів")
            
            return {
                'code': code_key,
                'name': code_info['name'],
                'name_uk': code_info['name_uk'],
                'url': url,
                'paragraphs': paragraphs,
                'downloaded_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка завантаження {code_key}: {e}")
            return None
    
    def _parse_code_index(self, html: str, code_key: str) -> List[Dict]:
        """
        Парсинг списку параграфів з HTML.
        
        Args:
            html: HTML сторінки
            code_key: Ключ кодексу
        
        Returns:
            Список параграфів
        """
        paragraphs = []
        
        # Регулярні вирази для пошуку параграфів
        patterns = [
            r'<a\s+href="[^"]*__jlr-\w+[^"]*"\s*>([^<]+)</a>',
            r'<span\s+class="jlr-\w+">\s*(§\s*\d+[a-z]*)',
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, html, re.IGNORECASE)
            for match in matches:
                paragraph_text = match.strip()
                if paragraph_text and '§' in paragraph_text:
                    paragraphs.append({
                        'paragraph': paragraph_text,
                        'code': code_key,
                    })
        
        return paragraphs
    
    def download_all_codes(self):
        """Завантажити всі кодекси."""
        logger.info("="*70)
        logger.info("  📚 ЗАВАНТАЖЕННЯ ВСІХ НІМЕЦЬКИХ КОДЕКСІВ")
        logger.info("="*70)
        
        downloaded = []
        failed = []
        
        # Сортуємо за пріоритетом
        sorted_codes = sorted(
            CODES_TO_DOWNLOAD.items(),
            key=lambda x: x[1]['priority']
        )
        
        for code_key, code_info in sorted_codes:
            logger.info(f"\n📖 {code_info['name']} (Пріоритет: {code_info['priority']})")
            
            result = self.download_code(code_key)
            
            if result:
                downloaded.append(result)
                # Збереження на диск
                self._save_code(result)
            else:
                failed.append(code_key)
        
        # Статистика
        logger.info(f"\n" + "="*70)
        logger.info(f"  📊 СТАТИСТИКА")
        logger.info("="*70)
        logger.info(f"✅ Завантажено: {len(downloaded)} кодексів")
        logger.info(f"❌ Не вдалося: {len(failed)} кодексів")
        
        if failed:
            logger.warning(f"   Не вдалося: {', '.join(failed)}")
        
        return downloaded, failed
    
    def _save_code(self, code_data: Dict):
        """Зберегти кодекс на диск."""
        code_key = code_data['code']
        file_path = self.db_path / f'{code_key}.json'
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(code_data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Збережено: {file_path}")
    
    def add_to_vector_db(self, code_data: Dict):
        """
        Додати кодекс до векторної бази.
        
        Args:
            code_data: Дані кодексу
        """
        if not self.collection:
            logger.warning("⚠️ Векторна база не ініціалізована")
            return
        
        code_key = code_data['code']
        paragraphs = code_data.get('paragraphs', [])
        
        logger.info(f"📇 Додавання {code_key} до векторної бази...")
        
        added_count = 0
        
        for para in paragraphs:
            try:
                # Формуємо текст для пошуку
                text = f"""
{code_key} {para.get('paragraph', '')}
{para.get('title_de', '')}
{para.get('content_de', '')}
"""
                
                # Metadata
                metadata = {
                    'code': code_key,
                    'paragraph': para.get('paragraph', ''),
                    'title_de': para.get('title_de', ''),
                    'content_preview': para.get('content_de', '')[:200],
                }
                
                # Додаємо до колекції
                law_id = f"{code_key}_{para.get('paragraph', '').replace(' ', '_').replace('§', '')}"
                
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[law_id]
                )
                
                added_count += 1
                
            except Exception as e:
                logger.debug(f"⚠️ Помилка додавання параграфу: {e}")
        
        logger.info(f"✅ Додано {added_count} параграфів")


def main():
    """Головна функція."""
    # Створення бази
    db = GermanLawDatabase()
    
    # Завантаження всіх кодексів
    downloaded, failed = db.download_all_codes()
    
    # Додавання до векторної бази
    if db.collection:
        logger.info("\n📇 Додавання до векторної бази...")
        for code_data in downloaded:
            db.add_to_vector_db(code_data)
    
    # Фінальна статистика
    logger.info("\n" + "="*70)
    logger.info("  ✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!")
    logger.info("="*70)
    
    if db.collection:
        total_count = db.collection.count()
        logger.info(f"📊 Всього в векторній базі: {total_count} параграфів")


if __name__ == '__main__':
    main()
