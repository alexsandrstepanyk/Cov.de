#!/usr/bin/env python3
"""
Download Complete German Laws from Official Sources
Завантаження всіх німецьких законів з офіційних GitHub репозиторіїв

Джерела:
1. bundestag/gesetze - Markdown (офіційне)
2. maxsagt/de_laws_to_json - JSON (>6000 законів)

Інтеграція з Ollama LLM через RAG (ChromaDB)
"""

import requests
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('download_german_laws')


class GermanLawsDownloader:
    """Завантажувач німецьких законів з GitHub."""
    
    def __init__(self, output_dir: str = 'data/german_laws_raw'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Джерела
        self.sources = {
            'bundestag_markdown': {
                'url': 'https://raw.githubusercontent.com/bundestag/gesetze/master/',
                'format': 'md',
                'priority': 1,
            },
            'de_laws_json': {
                'url': 'https://raw.githubusercontent.com/maxsagt/de_laws_to_json/master/de_federal.json',
                'format': 'json',
                'priority': 2,
            }
        }
    
    def download_bundestag_index(self) -> List[str]:
        """
        Завантажити індекс законів з bundestag/gesetze.
        
        Returns:
            Список URL до законів
        """
        logger.info("📥 Завантаження індексу з bundestag/gesetze...")
        
        # Головна сторінка репозиторію
        index_url = 'https://api.github.com/repos/bundestag/gesetze/contents/'
        
        try:
            response = requests.get(index_url, timeout=30)
            response.raise_for_status()
            
            items = response.json()
            law_urls = []
            
            for item in items:
                if item['type'] == 'dir' and item['name'].islower():
                    # Це директорія з законами (a, b, c, ...)
                    dir_url = f"{item['url']}?ref=master"
                    dir_response = requests.get(dir_url, timeout=30)
                    dir_items = dir_response.json()
                    
                    for file in dir_items:
                        if file['name'].endswith('.md'):
                            law_urls.append(file['download_url'])
            
            logger.info(f"✅ Знайдено {len(law_urls)} законів")
            return law_urls
            
        except Exception as e:
            logger.error(f"❌ Помилка: {e}")
            return []
    
    def download_json_database(self) -> Optional[Dict]:
        """
        Завантажити JSON базу з de_laws_to_json.
        
        Returns:
            Dict з усіма законами або None
        """
        logger.info("📥 Завантаження JSON бази (>6000 законів)...")
        
        json_url = self.sources['de_laws_json']['url']
        
        try:
            response = requests.get(json_url, timeout=60)
            response.raise_for_status()
            
            data = response.json()
            
            logger.info(f"✅ Завантажено {len(data.get('laws', []))} законів")
            
            # Збереження
            output_file = self.output_dir / 'de_federal_laws.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"💾 Збережено: {output_file}")
            
            return data
            
        except Exception as e:
            logger.error(f"❌ Помилка завантаження JSON: {e}")
            return None
    
    def download_markdown_laws(self, urls: List[str], limit: int = 100):
        """
        Завантажити закони в Markdown форматі.
        
        Args:
            urls: Список URL
            limit: Ліміт для тестування
        """
        logger.info(f"📥 Завантаження Markdown законів (ліміт: {limit})...")
        
        downloaded = 0
        
        for url in urls[:limit]:
            try:
                response = requests.get(url, timeout=30)
                response.raise_for_status()
                
                # Витягуємо назву файлу
                filename = url.split('/')[-1]
                output_file = self.output_dir / filename
                
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(response.text)
                
                downloaded += 1
                
                if downloaded % 10 == 0:
                    logger.info(f"   Завантажено {downloaded}/{limit}")
                
            except Exception as e:
                logger.debug(f"⚠️ Помилка {url}: {e}")
        
        logger.info(f"✅ Завантажено {downloaded} Markdown файлів")


class LawsToRAG:
    """Конвертація законів в RAG формат для Ollama."""
    
    def __init__(self, db_path: str = 'data/complete_law_rag'):
        self.db_path = Path(db_path)
        self.db_path.mkdir(parents=True, exist_ok=True)
        
        # Імпорт ChromaDB
        try:
            import chromadb
            self.chromadb = chromadb
            self.available = True
        except:
            self.chromadb = None
            self.available = False
            logger.warning("⚠️ ChromaDB недоступний")
        
        self.collection = None
        if self.available:
            self._init_db()
    
    def _init_db(self):
        """Ініціалізація векторної бази."""
        client = self.chromadb.PersistentClient(path=str(self.db_path))
        
        try:
            self.collection = client.get_collection(name='complete_german_laws_v2')
            logger.info(f"✅ RAG база підключено")
        except:
            self.collection = client.create_collection(
                name='complete_german_laws_v2',
                metadata={'description': 'Повна база німецьких законів v2'}
            )
            logger.info(f"✅ RAG база створено")
    
    def process_json_database(self, json_data: Dict):
        """
        Обробити JSON базу і додати до RAG.
        
        Args:
            json_data: Дані з de_laws_to_json
        """
        if not self.collection:
            logger.warning("⚠️ RAG база не ініціалізована")
            return
        
        logger.info("📇 Обробка JSON бази для RAG...")
        
        laws = json_data.get('laws', [])
        added_count = 0
        
        for law in laws:
            try:
                code = law.get('key', 'UNKNOWN')
                norms = law.get('output', {}).get('norms', [])
                
                for norm in norms:
                    paragraph_id = norm.get('meta', {}).get('norm_id', '')
                    content = ' '.join([
                        p.get('content', '')
                        for p in norm.get('paragraphs', [])
                    ])
                    
                    if not paragraph_id or not content:
                        continue
                    
                    # Формуємо текст для пошуку
                    text = f"""
{code} {paragraph_id}
{content}
"""
                    
                    # Metadata
                    metadata = {
                        'code': code,
                        'paragraph': paragraph_id,
                        'content_preview': content[:200],
                    }
                    
                    # ID
                    law_id = f"{code}_{paragraph_id.replace(' ', '_').replace('§', '').replace('.', '')}"
                    
                    # Додаємо до колекції
                    self.collection.add(
                        documents=[text],
                        metadatas=[metadata],
                        ids=[law_id]
                    )
                    
                    added_count += 1
                    
            except Exception as e:
                logger.debug(f"⚠️ Помилка обробки закону: {e}")
        
        logger.info(f"✅ Додано {added_count} параграфів до RAG бази")


def main():
    """Головна функція."""
    logger.info("="*70)
    logger.info("  📚 ЗАВАНТАЖЕННЯ ПОВНОЇ БАЗИ НІМЕЦЬКИХ ЗАКОНІВ")
    logger.info("="*70)
    
    # Крок 1: Завантаження
    downloader = GermanLawsDownloader()
    
    # JSON база (>6000 законів)
    json_data = downloader.download_json_database()
    
    # Markdown закони (опціонально, для тесту)
    # markdown_urls = downloader.download_bundestag_index()
    # downloader.download_markdown_laws(markdown_urls, limit=50)
    
    # Крок 2: Конвертація в RAG
    if json_data:
        logger.info("\n" + "="*70)
        logger.info("  📇 КОНВЕРТАЦІЯ В RAG ФОРМАТ")
        logger.info("="*70)
        
        rag = LawsToRAG()
        rag.process_json_database(json_data)
        
        # Статистика
        if rag.collection:
            total = rag.collection.count()
            logger.info(f"\n📊 Всього в RAG базі: {total} параграфів")
    
    logger.info("\n" + "="*70)
    logger.info("  ✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!")
    logger.info("="*70)


if __name__ == '__main__':
    main()
