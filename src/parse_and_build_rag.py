#!/usr/bin/env python3
"""
Parse German Laws from Markdown files
Парсинг німецьких законів з Markdown файлів (bundestag/gesetze)

Структура:
1. Сканування всіх .md файлів
2. Витягування параграфів (§)
3. Створення JSON структури
4. Додавання в ChromaDB RAG базу
"""

import re
import json
import logging
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('parse_german_laws')


class GermanLawsParser:
    """Парсер німецьких законів з Markdown."""
    
    def __init__(self, laws_dir: str = 'data/german_laws_complete'):
        self.laws_dir = Path(laws_dir)
        self.output_dir = Path('data/complete_law_json')
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Статистика
        self.stats = {
            'files_scanned': 0,
            'laws_found': 0,
            'paragraphs_found': 0,
            'errors': 0,
        }
    
    def scan_markdown_files(self) -> List[Path]:
        """Сканування всіх .md файлів."""
        logger.info("🔍 Сканування Markdown файлів...")
        
        md_files = list(self.laws_dir.rglob('*.md'))
        
        logger.info(f"✅ Знайдено {len(md_files)} Markdown файлів")
        self.stats['files_scanned'] = len(md_files)
        
        return md_files
    
    def parse_law_file(self, file_path: Path) -> Optional[Dict]:
        """
        Парсинг одного файлу закону.
        
        Args:
            file_path: Шлях до файлу
        
        Returns:
            Dict з даними закону або None
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Витягуємо назву закону
            law_name = file_path.stem.replace('_', ' ').title()
            
            # Витягуємо параграфи (§)
            paragraphs = self._extract_paragraphs(content)
            
            if not paragraphs:
                return None
            
            return {
                'law_name': law_name,
                'file': str(file_path),
                'paragraphs': paragraphs,
                'paragraph_count': len(paragraphs),
                'parsed_at': datetime.now().isoformat(),
            }
            
        except Exception as e:
            logger.error(f"❌ Помилка парсингу {file_path}: {e}")
            self.stats['errors'] += 1
            return None
    
    def _extract_paragraphs(self, content: str) -> List[Dict]:
        """
        Витягування параграфів з контенту.
        
        Args:
            content: Текст закону
        
        Returns:
            Список параграфів
        """
        paragraphs = []
        
        # Регулярні вирази для пошуку параграфів
        # Формат: § 123 або §123
        pattern = r'§\s*(\d+[a-z]*)\s*([^§]+?)(?=§|\Z)'
        
        matches = re.findall(pattern, content, re.DOTALL)
        
        for match in matches:
            paragraph_num = match[0].strip()
            paragraph_text = match[1].strip()
            
            # Очищаємо текст
            paragraph_text = re.sub(r'\n\s*\n', '\n', paragraph_text)
            paragraph_text = paragraph_text.strip()
            
            if len(paragraph_text) < 20:  # Пропускаємо занадто короткі
                continue
            
            paragraphs.append({
                'paragraph': f'§ {paragraph_num}',
                'content': paragraph_text,
                'content_preview': paragraph_text[:200],
            })
        
        return paragraphs
    
    def parse_all(self) -> List[Dict]:
        """Парсинг всіх законів."""
        logger.info("="*70)
        logger.info("  📖 ПАРСИНГ НІМЕЦЬКИХ ЗАКОНІВ")
        logger.info("="*70)
        
        md_files = self.scan_markdown_files()
        
        all_laws = []
        
        for i, file_path in enumerate(md_files):
            law_data = self.parse_law_file(file_path)
            
            if law_data:
                all_laws.append(law_data)
                self.stats['laws_found'] += 1
                self.stats['paragraphs_found'] += law_data['paragraph_count']
            
            if (i + 1) % 100 == 0:
                logger.info(f"   Оброблено {i + 1}/{len(md_files)} файлів")
        
        # Збереження
        self._save_all(all_laws)
        
        # Статистика
        self._print_stats()
        
        return all_laws
    
    def _save_all(self, all_laws: List[Dict]):
        """Збереження всіх законів в JSON."""
        output_file = self.output_dir / 'german_laws_complete.json'
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(all_laws, f, ensure_ascii=False, indent=2)
        
        logger.info(f"💾 Збережено: {output_file}")
    
    def _print_stats(self):
        """Друк статистики."""
        logger.info("\n" + "="*70)
        logger.info("  📊 СТАТИСТИКА ПАРСИНГУ")
        logger.info("="*70)
        logger.info(f"Файлів скановано: {self.stats['files_scanned']}")
        logger.info(f"Законів знайдено: {self.stats['laws_found']}")
        logger.info(f"Параграфів знайдено: {self.stats['paragraphs_found']}")
        logger.info(f"Помилок: {self.stats['errors']}")


class LawsToRAG:
    """Конвертація законів в RAG базу."""
    
    def __init__(self, db_path: str = 'data/complete_law_rag_v2'):
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
    
    def add_laws_to_rag(self, all_laws: List[Dict]):
        """
        Додавання законів до RAG бази.
        
        Args:
            all_laws: Список законів з парсера
        """
        if not self.collection:
            logger.warning("⚠️ RAG база не ініціалізована")
            return
        
        logger.info("\n" + "="*70)
        logger.info("  📇 ДОДАВАННЯ ДО RAG БАЗИ")
        logger.info("="*70)
        
        added_count = 0
        
        for law in all_laws:
            law_name = law.get('law_name', 'Unknown')
            
            for para in law.get('paragraphs', []):
                try:
                    paragraph_id = para.get('paragraph', '')
                    content = para.get('content', '')
                    
                    if not paragraph_id or not content:
                        continue
                    
                    # Формуємо текст для пошуку
                    text = f"""
{law_name} {paragraph_id}
{content}
"""
                    
                    # Metadata
                    metadata = {
                        'law_name': law_name,
                        'paragraph': paragraph_id,
                        'content_preview': content[:200],
                    }
                    
                    # ID
                    rag_id = f"{law_name}_{paragraph_id.replace(' ', '_').replace('§', '').replace('.', '')}"
                    
                    # Додаємо до колекції
                    self.collection.add(
                        documents=[text],
                        metadatas=[metadata],
                        ids=[rag_id]
                    )
                    
                    added_count += 1
                    
                except Exception as e:
                    logger.debug(f"⚠️ Помилка додавання {paragraph_id}: {e}")
            
            if added_count % 1000 == 0:
                logger.info(f"   Додано {added_count} параграфів...")
        
        logger.info(f"✅ Додано {added_count} параграфів до RAG бази")
        
        # Фінальна статистика
        if self.collection:
            total = self.collection.count()
            logger.info(f"📊 Всього в RAG базі: {total} записів")


def main():
    """Головна функція."""
    # Парсинг
    parser = GermanLawsParser()
    all_laws = parser.parse_all()
    
    # RAG
    if all_laws:
        rag = LawsToRAG()
        rag.add_laws_to_rag(all_laws)


if __name__ == '__main__':
    main()
