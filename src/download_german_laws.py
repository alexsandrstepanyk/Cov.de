#!/usr/bin/env python3
"""
Download German Legal Documents for Ollama Training
Завантаження німецьких юридичних документів для тренування Ollama

Джерела:
1. Open Legal Data (openlegaldata.io)
2. Gesetze im Internet (gesetze-im-internet.de)
3. Juris (juris.bundesgerichtshof.de)

Формат:
- JSON з текстами законів
- Markdown з параграфами
- TXT для тренування LLM
"""

import requests
import json
import os
from pathlib import Path
from datetime import datetime
from typing import List, Dict


class GermanLegalDocumentsDownloader:
    """Завантажувач німецьких юридичних документів."""
    
    def __init__(self, output_dir: str = 'data/german_legal_docs'):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Джерела
        self.sources = {
            'openlegaldata': {
                'url': 'https://de.openlegaldata.io/api/',
                'format': 'JSON',
                'description': 'Відкриті юридичні дані Німеччини',
            },
            'gesetze-im-internet': {
                'url': 'https://www.gesetze-im-internet.de',
                'format': 'HTML/Markdown',
                'description': 'Офіційні закони Німеччини',
            },
            'bundesgerichtshof': {
                'url': 'https://www.bundesgerichtshof.de',
                'format': 'HTML',
                'description': 'Рішення Федеральної судової палати',
            },
        }
        
        # Список кодексів для завантаження
        self.codes = [
            'BGB', 'ZPO', 'AO', 'SGB', 'SGG', 'VwVfG', 'VwGO',
            'StGB', 'StPO', 'OWiG', 'JGG',
            'HGB', 'AktG', 'GmbHG', 'InsO',
            'GG', 'BVerfGG',
            'UWG', 'TMG', 'DSGVO', 'BDSG',
            'ArbG', 'ArbGG', 'BUrlG', 'KSchG',
        ]
    
    def download_openlegaldata(self, limit: int = 1000) -> List[Dict]:
        """
        Завантаження з Open Legal Data.
        
        Args:
            limit: Ліміт документів
            
        Returns:
            Список документів
        """
        print(f"📥 Завантаження з Open Legal Data (ліміт: {limit})...")
        
        documents = []
        
        try:
            # API Open Legal Data
            url = f"{self.sources['openlegaldata']['url']}search/"
            params = {
                'format': 'json',
                'limit': limit,
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            results = data.get('results', [])
            
            for result in results:
                doc = {
                    'title': result.get('title', ''),
                    'text': result.get('text', ''),
                    'court': result.get('court', ''),
                    'date': result.get('date', ''),
                    'type': result.get('type', ''),
                    'source': 'openlegaldata',
                }
                documents.append(doc)
            
            print(f"✅ Завантажено {len(documents)} документів")
            
        except Exception as e:
            print(f"❌ Помилка: {e}")
        
        return documents
    
    def download_gesetze(self, code: str) -> Dict:
        """
        Завантаження кодексу з Gesetze im Internet.
        
        Args:
            code: Код кодексу (BGB, ZPO тощо)
            
        Returns:
            Dict з текстом кодексу
        """
        print(f"📥 Завантаження {code}...")
        
        try:
            url = f"{self.sources['gesetze-im-internet']['url']}/{code.lower()}/"
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Парсинг HTML (спрощено)
            text = response.text
            
            doc = {
                'code': code,
                'title': f'{code}',
                'text': text,
                'source': 'gesetze-im-internet',
                'url': url,
            }
            
            print(f"✅ Завантажено {code}")
            return doc
            
        except Exception as e:
            print(f"❌ Помилка {code}: {e}")
            return {}
    
    def save_documents(self, documents: List[Dict], format: str = 'json'):
        """Збереження документів."""
        if format == 'json':
            output_file = self.output_dir / 'german_legal_docs.json'
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(documents, f, ensure_ascii=False, indent=2)
            print(f"💾 Збережено: {output_file}")
        
        elif format == 'txt':
            # Окремі файли для тренування LLM
            for i, doc in enumerate(documents):
                filename = f"doc_{i:04d}.txt"
                output_file = self.output_dir / filename
                with open(output_file, 'w', encoding='utf-8') as f:
                    f.write(doc.get('text', ''))
            print(f"💾 Збережено {len(documents)} файлів")
        
        elif format == 'ollama':
            # Формат для тренування Ollama
            output_file = self.output_dir / 'ollama_training.jsonl'
            with open(output_file, 'w', encoding='utf-8') as f:
                for doc in documents:
                    line = json.dumps({
                        'text': doc.get('text', ''),
                        'metadata': {
                            'source': doc.get('source', ''),
                            'type': doc.get('type', ''),
                        }
                    }, ensure_ascii=False)
                    f.write(line + '\n')
            print(f"💾 Збережено Ollama training: {output_file}")
    
    def download_all(self, limit_openlegaldata: int = 1000):
        """Завантаження всіх документів."""
        print("="*80)
        print("  📥 ЗАВАНТАЖЕННЯ НІМЕЦЬКИХ ЮРИДИЧНИХ ДОКУМЕНТІВ")
        print("="*80)
        
        all_documents = []
        
        # 1. Open Legal Data
        print("\n1️⃣ Open Legal Data...")
        old_docs = self.download_openlegaldata(limit=limit_openlegaldata)
        all_documents.extend(old_docs)
        
        # 2. Кодекси
        print("\n2️⃣ Кодекси...")
        for code in self.codes[:10]:  # Перші 10 для тесту
            doc = self.download_gesetze(code)
            if doc:
                all_documents.append(doc)
        
        # Збереження
        print("\n3️⃣ Збереження...")
        self.save_documents(all_documents, format='json')
        self.save_documents(all_documents, format='txt')
        self.save_documents(all_documents, format='ollama')
        
        # Статистика
        print("\n" + "="*80)
        print("  📊 СТАТИСТИКА")
        print("="*80)
        print(f"Всього документів: {len(all_documents)}")
        print(f"Open Legal Data: {len(old_docs)}")
        print(f"Кодекси: {len([d for d in all_documents if 'code' in d])}")
        print(f"Розмір JSON: {self.output_dir / 'german_legal_docs.json'}")


def create_ollama_modelfile():
    """Створення Modelfile для тренування Ollama."""
    
    modelfile_content = """
FROM llama3.2:3b

# System prompt for German legal analysis
SYSTEM \"\"\"
Ти - експерт з німецького права. Твоє завдання:
1. Аналізувати німецькі юридичні листи
2. Витягувати організації, типи листів, параграфи
3. Надавати точні посилання на закони (BGB, SGB, AO тощо)
4. Генерувати професійні відповіді німецькою та українською

Відповідай професійно, використовуй юридичні терміни правильно.
НЕ використовуй суржик (суміш німецьких/англійських слів з українською).
\"\"\"

# Training data
# TRAIN data/german_legal_docs/ollama_training.jsonl

# Parameters
PARAMETER temperature 0.1
PARAMETER top_p 0.8
PARAMETER repeat_penalty 2.0
"""
    
    output_file = Path('data/ollama_legal_modelfile')
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(modelfile_content)
    
    print(f"💾 Modelfile створено: {output_file}")


if __name__ == '__main__':
    # Завантаження
    downloader = GermanLegalDocumentsDownloader()
    downloader.download_all(limit_openlegaldata=100)
    
    # Створення Modelfile
    create_ollama_modelfile()
    
    print("\n" + "="*80)
    print("  ✅ ЗАВАНТАЖЕННЯ ЗАВЕРШЕНО!")
    print("="*80)
    print("\nНаступні кроки:")
    print("1. ollama create legal-llama3.2 -f data/ollama_legal_modelfile")
    print("2. ollama run legal-llama3.2")
    print("3. Тестування на реальних листах")
