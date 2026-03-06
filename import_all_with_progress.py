#!/usr/bin/env python3
"""
Complete German Laws Import with Progress Bar
Повний імпорт німецьких законів з прогрес-баром

Виконує всі 3 задачі:
1. Дозавантажити всі закони
2. Виправити OTHER категорію
3. Завантажити повні версії кодексів
"""

import sqlite3
import json
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List
import sys

# Налаштування логування
logging.basicConfig(
    level=logging.INFO,
    format='%(message)s'
)
logger = logging.getLogger('import_all')

# Шляхи
DB_FILE = Path('data/legal_database.db')
JSON_FILE = Path('data/complete_law_json/german_laws_complete.json')
GESETZE_DIR = Path('data/german_laws_complete')
CHROMA_DIR = Path('data/chroma_db')

# Мапінг кодексів
CODE_ABBREVIATIONS = {
    'bgb': 'BGB', 'gg': 'GG', 'sgb': 'SGB', 'zpo': 'ZPO', 'ao': 'AO',
    'stgb': 'StGB', 'stpo': 'StPO', 'hgb': 'HGB', 'vwvfg': 'VwVfG',
    'vwgo': 'VwGO', 'estg': 'EStG', 'ustg': 'UStG', 'gmbhg': 'GmbHG',
    'aktg': 'AktG', 'uwg': 'UWG', 'bdsg': 'BDSG', 'dsgvo': 'DSGVO',
    'tmg': 'TMG', 'enwg': 'EnWG', 'vvg': 'VVG', 'bvg': 'BVG',
    'kschg': 'KSchG', 'burlg': 'BUrlG', 'betrvg': 'BetrVG',
    'aufenthg': 'AufenthG', 'asylg': 'AsylG', 'ino': 'InsO',
}

CODE_KEYWORDS = {
    'BGB': ['bürgerliches gesetzbuch', 'schuldverhältnis', 'vertrag', 'eigentum', '§ 105', '§ 241', '§ 280', '§ 311', '§ 433', '§ 535', '§ 611', '§ 823'],
    'GG': ['grundgesetz', 'freiheit', 'gleichheit', 'grundrecht', 'demokratie', '§ 1 GG', '§ 2 GG', '§ 3 GG'],
    'SGB_II': ['sozialgesetzbuch ii', 'sgb ii', 'grundsicherung', 'jobcenter', 'hartz'],
    'SGB_III': ['sozialgesetzbuch iii', 'sgb iii', 'arbeitsförderung', 'arbeitsagentur'],
    'SGB_V': ['sozialgesetzbuch v', 'sgb v', 'krankenversicherung'],
    'AO': ['abgabenordnung', 'steuer', 'finanzamt', 'steuerbescheid'],
    'ZPO': ['zivilprozessordnung', 'klage', 'gericht', 'urteil', 'vollstreckung'],
    'StGB': ['strafgesetzbuch', 'strafe', 'straftat'],
    'HGB': ['handelsgesetzbuch', 'kaufmann', 'firma'],
    'VwVfG': ['verwaltungsverfahrensgesetz', 'verwaltungsakt'],
    'VwGO': ['verwaltungsgerichtsordnung', 'verwaltungsgericht'],
    'EStG': ['einkommensteuergesetz', 'einkommensteuer'],
    'UStG': ['umsatzsteuergesetz', 'umsatzsteuer', 'mehrwertsteuer'],
    'InsO': ['insolvenzordnung', 'insolvenz', 'konkurs'],
    'GmbHG': ['gmbh-gesetz', 'gesellschaft mit beschränkter haftung'],
    'AktG': ['aktiengesetz', 'aktiengesellschaft'],
    'BetrVG': ['betriebsverfassungsgesetz', 'betriebsrat'],
    'KSchG': ['kündigungsschutzgesetz', 'kündigungsschutz'],
    'BUrlG': ['bundesurlaubsgesetz', 'urlaub'],
    'DSGVO': ['datenschutz-grundverordnung', 'dsgvo'],
    'BDSG': ['bundesdatenschutzgesetz'],
    'AufenthG': ['aufenthaltsgesetz', 'aufenthaltstitel'],
    'AsylG': ['asylgesetz', 'asyl'],
}


class ProgressBar:
    """Простий прогрес-бар для терміналу."""
    
    def __init__(self, total: int, prefix: str = '', suffix: str = '', length: int = 50):
        self.total = total
        self.prefix = prefix
        self.suffix = suffix
        self.length = length
        self.current = 0
        self.update(0)
    
    def update(self, value: int):
        """Оновлення прогресу."""
        self.current = value
        percent = f"{100 * (value / float(self.total)):.1f}" if self.total > 0 else "0.0"
        filled = int(self.length * value // self.total) if self.total > 0 else 0
        bar = '█' * filled + '░' * (self.length - filled)
        print(f'\r{self.prefix} |{bar}| {percent}% {self.suffix}', end='', flush=True)
        if value >= self.total:
            print()
    
    def increment(self, amount: int = 1):
        """Збільшення прогресу."""
        self.current += amount
        self.update(self.current)


def print_header(text: str):
    """Друк заголовку."""
    print(f"\n{'='*80}")
    print(f"  {text}")
    print(f"{'='*80}\n")


def print_step(step: int, total_steps: int, text: str):
    """Друк кроку."""
    print(f"\n{'─'*80}")
    print(f"  Крок {step}/{total_steps}: {text}")
    print(f"{'─'*80}\n")


# ============================================================================
# ЗАДАЧА 1: Дозавантажити всі закони з JSON
# ============================================================================

def task1_import_remaining_laws():
    """Завдання 1: Іморт решти законів з JSON."""
    print_step(1, 3, "Дозавантаження всіх законів з репозиторію")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Завантаження JSON
    print("  📥 Завантаження JSON файлу...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        laws_data = json.load(f)
    
    total_laws = len(laws_data)
    print(f"  ✅ Знайдено {total_laws:,} законів")
    
    # Отримання існуючих
    cursor.execute("SELECT COUNT(*) FROM paragraphs")
    existing = cursor.fetchone()[0]
    print(f"  📊 Вже є {existing:,} параграфів")
    
    # Імпорт
    imported = 0
    duplicates = 0
    
    progress = ProgressBar(total_laws, prefix='  Імпорт:', suffix=f'0/{total_laws}')
    
    for idx, law in enumerate(laws_data):
        law_name = law.get('law_name', 'Unknown')
        file_path = law.get('file', '')
        paragraphs = law.get('paragraphs', [])
        
        # Визначення кодексу
        code = 'OTHER'
        for abbrev, code_name in CODE_ABBREVIATIONS.items():
            if abbrev in law_name.lower() or abbrev in file_path.lower():
                code = code_name
                break
        
        # Імпорт параграфів
        for para in paragraphs:
            para_num = para.get('paragraph', '')
            content = para.get('content', '')
            
            if not para_num or not content:
                continue
            
            try:
                cursor.execute("""
                    INSERT OR IGNORE INTO paragraphs 
                    (code_name, paragraph_number, text_de, text_uk, category, keywords, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (code, para_num, content[:10000], None, law_name, '[]', datetime.now()))
                
                if cursor.rowcount > 0:
                    imported += 1
                else:
                    duplicates += 1
            except:
                pass
        
        progress.increment(1)
    
    conn.commit()
    conn.close()
    
    print(f"\n  ✅ Імпортовано: {imported:,} параграфів")
    print(f"  ⚠️  Дублікатів: {duplicates:,}")
    
    return imported


# ============================================================================
# ЗАДАЧА 2: Виправити OTHER категорію
# ============================================================================

def task2_fix_other_codes():
    """Завдання 2: Розподіл OTHER параграфів по кодексах."""
    print_step(2, 3, "Виправлення OTHER категорії")
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Отримання OTHER
    cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
    other_count = cursor.fetchone()[0]
    print(f"  📊 OTHER параграфів: {other_count:,}")
    
    if other_count == 0:
        print("  ✅ Немає OTHER для виправлення")
        return 0
    
    # Отримання параграфів
    cursor.execute("SELECT id, text_de FROM paragraphs WHERE code_name = 'OTHER'")
    rows = cursor.fetchall()
    
    updated = 0
    progress = ProgressBar(len(rows), prefix='  Виправлення:', suffix=f'0/{len(rows)}')
    
    for row_id, text_de in rows:
        if not text_de:
            progress.increment(1)
            continue
        
        text_lower = text_de.lower()
        new_code = None
        
        # Пошук відповідності
        for code, keywords in CODE_KEYWORDS.items():
            for keyword in keywords:
                if keyword in text_lower:
                    new_code = code
                    break
            if new_code:
                break
        
        if new_code:
            try:
                cursor.execute("UPDATE paragraphs SET code_name = ? WHERE id = ?", (new_code, row_id))
                if cursor.rowcount > 0:
                    updated += 1
            except:
                pass
        
        progress.increment(1)
    
    conn.commit()
    conn.close()
    
    print(f"\n  ✅ Виправлено: {updated:,} параграфів")
    
    return updated


# ============================================================================
# ЗАДАЧА 3: Оновити ChromaDB RAG
# ============================================================================

def task3_update_chromadb():
    """Завдання 3: Оновлення ChromaDB RAG індексу."""
    print_step(3, 3, "Оновлення ChromaDB RAG індексу")
    
    import chromadb
    from chromadb.config import Settings
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Отримання всіх параграфів
    cursor.execute("""
        SELECT id, code_name, paragraph_number, text_de 
        FROM paragraphs 
        WHERE text_de IS NOT NULL AND text_de != ''
    """)
    rows = cursor.fetchall()
    
    conn.close()
    
    print(f"  📊 Всього параграфів: {len(rows):,}")
    
    # ChromaDB
    client = chromadb.PersistentClient(path=str(CHROMA_DIR))
    
    try:
        client.delete_collection("german_laws")
        print("  🗑️  Стару колекцію видалено")
    except:
        pass
    
    collection = client.create_collection(
        name="german_laws",
        metadata={"hnsw:space": "cosine"},
        get_or_create=True
    )
    
    # Імпорт партіями
    batch_size = 500
    total_imported = 0
    
    progress = ProgressBar(len(rows), prefix='  RAG імпорт:', suffix=f'0/{len(rows)}')
    
    for i in range(0, len(rows), batch_size):
        batch = rows[i:i + batch_size]
        
        ids = [f"para_{row[0]}" for row in batch]
        documents = []
        metadatas = []
        
        for row in batch:
            code = row[1] or 'UNKNOWN'
            para_num = row[2] or ''
            text = row[3] or ''
            
            full_text = f"{code} {para_num}\n{text[:30000]}"
            
            documents.append(full_text)
            metadatas.append({
                "code": code,
                "paragraph": para_num,
                "language": "de",
            })
        
        collection.add(
            ids=ids,
            documents=documents,
            metadatas=metadatas
        )
        
        total_imported += len(batch)
        progress.update(total_imported)
    
    print(f"\n  ✅ Імпортовано до RAG: {total_imported:,} документів")
    
    return total_imported


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def main():
    """Виконання всіх 3 задач."""
    print_header("🚀 ПОВНИЙ ІМПОРТ НІМЕЦЬКИХ ЗАКОНІВ")
    
    start_time = datetime.now()
    
    # Задача 1
    result1 = task1_import_remaining_laws()
    
    # Задача 2
    result2 = task2_fix_other_codes()
    
    # Задача 3
    result3 = task3_update_chromadb()
    
    # Фінал
    end_time = datetime.now()
    duration = end_time - start_time
    
    print_header("✅ ІМПОРТ ЗАВЕРШЕНО!")
    
    print(f"📊 РЕЗУЛЬТАТИ:")
    print(f"  • Задача 1: Імпортовано {result1:,} параграфів")
    print(f"  • Задача 2: Виправлено {result2:,} OTHER")
    print(f"  • Задача 3: RAG оновлено ({result3:,} документів)")
    
    # Статистика
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    cursor.execute("SELECT COUNT(*) FROM paragraphs")
    total = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM codes")
    codes = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
    other = cursor.fetchone()[0]
    
    conn.close()
    
    print(f"\n📈 ЗАГАЛЬНА СТАТИСТИКА:")
    print(f"  • Всього параграфів: {total:,}")
    print(f"  • Всього кодексів: {codes}")
    print(f"  • Розподілено: {total - other:,} ({(total - other) / total * 100:.1f}%)")
    print(f"  • OTHER: {other:,} ({other / total * 100:.1f}%)")
    
    print(f"\n⏱️  Час виконання: {duration.seconds // 60} хв {duration.seconds % 60} сек")
    
    print(f"\n🎉 ВСІ 3 ЗАДАЧІ ВИКОНАНІ!")
    print(f"\n" + "="*80)


if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⚠️  Перервано користувачем")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
