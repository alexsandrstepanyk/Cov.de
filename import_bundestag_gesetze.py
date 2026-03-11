#!/usr/bin/env python3
"""
Import German Laws from Bundestag/Gesetze GitHub Repository
Імпорт німецьких законів з репозиторію Bundestag/Gesetze

Джерело: https://github.com/bundestag/gesetze
Формат: Markdown файли
"""

import sqlite3
import re
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('import_bundestag')

# Шляхи
GESETZE_DIR = Path('data/german_laws_complete')
DB_FILE = Path('data/legal_database.db')

# Мапінг абревіатур кодексів
CODE_ABBREVIATIONS = {
    'bgb': 'BGB',
    'gg': 'GG',
    'zbgb': 'BGB',  # Zivilgesetzbuch
    'sgb': 'SGB',
    'sgb_1': 'SGB_I',
    'sgb_2': 'SGB_II',
    'sgb_3': 'SGB_III',
    'sgb_4': 'SGB_IV',
    'sgb_5': 'SGB_V',
    'sgb_6': 'SGB_VI',
    'sgb_7': 'SGB_VII',
    'sgb_8': 'SGB_VIII',
    'sgb_9': 'SGB_IX',
    'sgb_10': 'SGB_X',
    'sgb_11': 'SGB_XI',
    'sgb_12': 'SGB_XII',
    'zpo': 'ZPO',
    'ao': 'AO',
    'stgb': 'StGB',
    'stpo': 'StPO',
    'hgb': 'HGB',
    'vwvfg': 'VwVfG',
    'vwgo': 'VwGO',
    'fgo': 'FGO',
    'sgg': 'SGG',
    'arbgg': 'ArbGG',
    'kschg': 'KSchG',
    'burlg': 'BUrlG',
    'tzbg': 'TzBfG',
    'betrvg': 'BetrVG',
    'aufenthg': 'AufenthG',
    'asylg': 'AsylG',
    'estg': 'EStG',
    'ustg': 'UStG',
    'gewo': 'GewO',
    'ino': 'InsO',
    'gmbhg': 'GmbHG',
    'aktg': 'AktG',
    'uwg': 'UWG',
    'bdsg': 'BDSG',
    'dsgvo': 'DSGVO',
    'tmg': 'TMG',
    'enwg': 'EnWG',
    'vvg': 'VVG',
    'bvg': 'BVG',
    'lfzg': 'LFZG',
    'muschg': 'MuSchG',
    'beeg': 'BEEG',
}

CODE_NAMES_UK = {
    'BGB': 'Цивільний кодекс',
    'GG': 'Основний закон (Конституція)',
    'SGB': 'Соціальний кодекс',
    'SGB_I': 'Соціальний кодекс I',
    'SGB_II': 'Соціальний кодекс II (Jobcenter)',
    'SGB_III': 'Соціальний кодекс III (Агентство з праці)',
    'SGB_IV': 'Соціальний кодекс IV',
    'SGB_V': 'Соціальний кодекс V (Здоров\'я)',
    'SGB_VI': 'Соціальний кодекс VI (Пенсії)',
    'SGB_VII': 'Соціальний кодекс VII (Страхування)',
    'SGB_VIII': 'Соціальний кодекс VIII (Молодь)',
    'SGB_IX': 'Соціальний кодекс IX (Інваліди)',
    'SGB_X': 'Соціальний кодекс X',
    'SGB_XI': 'Соціальний кодекс XI (Догляд)',
    'SGB_XII': 'Соціальний кодекс XII',
    'ZPO': 'Цивільний процесуальний кодекс',
    'AO': 'Податковий кодекс',
    'StGB': 'Кримінальний кодекс',
    'StPO': 'Кримінально-процесуальний кодекс',
    'HGB': 'Торговельний кодекс',
    'VwVfG': 'Закон про адмінпроцедури',
    'VwGO': 'Кодекс адмінсудочинства',
    'FGO': 'Кодекс фінансового судочинства',
    'SGG': 'Кодекс соціального судочинства',
    'ArbGG': 'Кодекс трудового судочинства',
    'KSchG': 'Закон про захист від звільнення',
    'BUrlG': 'Закон про відпустки',
    'TzBfG': 'Закон про часткову зайнятість',
    'BetrVG': 'Закон про виробничі ради',
    'AufenthG': 'Закон про перебування іноземців',
    'AsylG': 'Закон про притулок',
    'EStG': 'Закон про прибутковий податок',
    'UStG': 'Закон про ПДВ',
    'GewO': 'Промисловий кодекс',
    'InsO': 'Закон про банкрутство',
    'GmbHG': 'Закон про ТОВ',
    'AktG': 'Закон про акціонерні товариства',
    'UWG': 'Закон про недобросовісну конкуренцію',
    'BDSG': 'Закон про захист даних',
    'DSGVO': 'GDPR',
    'TMG': 'Закон про телемедіа',
    'EnWG': 'Закон про енергетику',
    'VVG': 'Закон про страхування',
    'BVG': 'Закон про федеральну пенсію',
    'LFZG': 'Закон про оплату праці',
    'MuSchG': 'Закон про охорону материнства',
    'BEEG': 'Закон про батьківську відпустку',
}


def extract_code_from_filename(filename: str, file_path: Path) -> str:
    """Визначити код кодексу з імені файлу або шляху."""
    
    # Спробуємо з назви файлу
    name_lower = filename.lower().replace('.md', '').replace('index', '').strip()
    
    # Прямі співпадіння
    for abbrev, code in CODE_ABBREVIATIONS.items():
        if name_lower == abbrev or name_lower.startswith(abbrev + '_') or name_lower.startswith(abbrev + '-'):
            return code
    
    # Якщо шлях містить sgX де X цифра
    match = re.search(r'sgb[_-]?(\d+)', name_lower)
    if match:
        num = match.group(1)
        return f'SGB_{num}'
    
    # Спробуємо з шляху
    parts = file_path.parts
    if len(parts) >= 2:
        parent_dir = parts[-2].lower()
        
        # Перевірка для SGB
        if parent_dir == 's':
            if 'sgb_1' in name_lower or 'sgb1' in name_lower:
                return 'SGB_I'
            elif 'sgb_2' in name_lower or 'sgb2' in name_lower:
                return 'SGB_II'
            elif 'sgb_3' in name_lower or 'sgb3' in name_lower:
                return 'SGB_III'
            elif 'sgb_4' in name_lower or 'sgb4' in name_lower:
                return 'SGB_IV'
            elif 'sgb_5' in name_lower or 'sgb5' in name_lower:
                return 'SGB_V'
            elif 'sgb_6' in name_lower or 'sgb6' in name_lower:
                return 'SGB_VI'
            elif 'sgb_7' in name_lower or 'sgb7' in name_lower:
                return 'SGB_VII'
            elif 'sgb_8' in name_lower or 'sgb8' in name_lower:
                return 'SGB_VIII'
            elif 'sgb_9' in name_lower or 'sgb9' in name_lower:
                return 'SGB_IX'
            elif 'sgb_10' in name_lower or 'sgb10' in name_lower:
                return 'SGB_X'
            elif 'sgb_11' in name_lower or 'sgb11' in name_lower:
                return 'SGB_XI'
            elif 'sgb_12' in name_lower or 'sgb12' in name_lower:
                return 'SGB_XII'
            else:
                return 'SGB'
        
        # Перевірка для інших кодексів
        for abbrev, code in CODE_ABBREVIATIONS.items():
            if abbrev in parent_dir or name_lower.startswith(abbrev):
                return code
    
    return 'OTHER'


def parse_markdown_law(content: str) -> Tuple[str, List[Dict]]:
    """
    Парсинг Markdown файлу закону.
    
    Returns:
        (law_name, paragraphs)
    """
    law_name = "Unknown"
    paragraphs = []
    
    # Витягнення назви закону з front matter
    title_match = re.search(r'Title:\s*(.+?)(?:\n|$)', content)
    if title_match:
        law_name = title_match.group(1).strip()
    
    jurabk_match = re.search(r'jurabk:\s*(\S+)', content)
    if jurabk_match:
        law_name = jurabk_match.group(1).upper()
    
    # Парсинг параграфів
    # Формат: ## § 123 або ## §123 або # § 123
    paragraph_pattern = r'(?:^|\n)#{1,3}\s*§\s*(\d+[a-zA-Z]?(?:\s*[a-zA-Z])?)\s*(?:\n|$)'
    
    # Знаходимо всі позиції параграфів
    matches = list(re.finditer(paragraph_pattern, content))
    
    for i, match in enumerate(matches):
        paragraph_num = match.group(1).strip()
        start_pos = match.end()
        
        # Кінець параграфу - початок наступного параграфу або кінець файлу
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)
        
        # Витягуємо текст параграфу
        paragraph_text = content[start_pos:end_pos].strip()
        
        # Очищаємо від Markdown форматування
        paragraph_text = re.sub(r'#{1,3}\s*', '', paragraph_text)
        paragraph_text = re.sub(r'\*\*(.+?)\*\*', r'\1', paragraph_text)
        paragraph_text = re.sub(r'\[(.+?)\]\(.+?\)', r'\1', paragraph_text)
        
        # Обрізаємо довгі параграфи
        if len(paragraph_text) > 10000:
            paragraph_text = paragraph_text[:10000] + '...'
        
        paragraphs.append({
            'paragraph': f'§ {paragraph_num}',
            'text_de': paragraph_text,
            'text_uk': None,  # Потрібен переклад
        })
    
    return law_name, paragraphs


def import_gesetze_to_sqlite():
    """Іморт законів з Bundestag/Geselize до SQLite."""
    logger.info("="*80)
    logger.info("  📚 ІМПОРТ ЗАКОНІВ З BUNDESTAG/GESETZE")
    logger.info("="*80)
    
    # Підключення до БД
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Статистика
    total_files = 0
    total_paragraphs = 0
    codes_added = set()
    laws_processed = 0
    
    # Отримання існуючих кодів
    cursor.execute("SELECT code_name FROM codes")
    existing_codes = {row[0] for row in cursor.fetchall()}
    
    logger.info(f"\n📊 В базі вже є {len(existing_codes)} кодексів")
    
    # Пошук всіх Markdown файлів
    logger.info("\n🔍 Пошук Markdown файлів...")
    md_files = list(GESETZE_DIR.rglob('*.md'))
    logger.info(f"✅ Знайдено {len(md_files):,} файлів")
    
    # Імпорт
    logger.info("\n🔄 Імпорт законів...")
    
    for idx, file_path in enumerate(md_files):
        try:
            # Пропускаємо README та LICENSE
            if file_path.name.lower() in ['readme.md', 'license', 'license.md']:
                continue
            
            total_files += 1
            
            # Читання файлу
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг
            law_name, paragraphs = parse_markdown_law(content)
            
            if not paragraphs:
                continue
            
            laws_processed += 1
            
            # Визначення кодексу
            code = extract_code_from_filename(file_path.name, file_path)
            codes_added.add(code)
            
            # Додавання кодексу до таблиці codes
            if code not in existing_codes and code != 'OTHER':
                name_uk = CODE_NAMES_UK.get(code, law_name)
                name_de = law_name
                url = f"https://github.com/bundestag/gesetze/tree/main/{file_path.parent.relative_to(GESETZE_DIR)}/{file_path.name}"
                
                cursor.execute("""
                    INSERT OR IGNORE INTO codes (code_name, name_de, name_uk, url, categories, created_at)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (code, name_de, name_uk, url, '[]', datetime.now()))
                existing_codes.add(code)
            
            # Додавання параграфів
            for para in paragraphs:
                cursor.execute("""
                    INSERT OR IGNORE INTO paragraphs (code_name, paragraph_number, text_de, text_uk, category, keywords, created_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (code, para['paragraph'], para['text_de'], para['text_preview'] if 'text_preview' in para else None, law_name, '[]', datetime.now()))
                
                if cursor.rowcount > 0:
                    total_paragraphs += 1
            
            # Прогрес кожні 1000 файлів
            if (idx + 1) % 1000 == 0:
                logger.info(f"  Оброблено {idx + 1}/{len(md_files)} файлів ({laws_processed} законів, {total_paragraphs} параграфів)")
        
        except Exception as e:
            logger.error(f"❌ Помилка {file_path}: {e}")
    
    # Збереження
    conn.commit()
    
    logger.info("\n" + "="*80)
    logger.info("  ✅ ІМПОРТ ЗАВЕРШЕНО!")
    logger.info("="*80)
    logger.info(f"\n📊 СТАТИСТИКА:")
    logger.info(f"  Файлів оброблено: {total_files:,}")
    logger.info(f"  Законів знайдено: {laws_processed:,}")
    logger.info(f"  Параграфів додано: {total_paragraphs:,}")
    logger.info(f"  Кодексів додано: {len(codes_added)}")
    
    # Підсумковий запит
    cursor.execute("SELECT COUNT(*) FROM paragraphs")
    total_in_db = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM codes")
    codes_in_db = cursor.fetchone()[0]
    
    logger.info(f"\n📈 ВСЬОГО В БАЗІ:")
    logger.info(f"  Кодексів: {codes_in_db}")
    logger.info(f"  Параграфів: {total_in_db:,}")
    
    # Статистика по кодексах
    logger.info(f"\n📋 ПАРАГРАФИ ПО КОДЕКСАХ (ТОП-20):")
    cursor.execute("""
        SELECT code_name, COUNT(*) as count 
        FROM paragraphs 
        GROUP BY code_name 
        ORDER BY count DESC 
        LIMIT 20
    """)
    for row in cursor.fetchall():
        logger.info(f"  {row[0]}: {row[1]:,} параграфів")
    
    conn.close()


if __name__ == '__main__':
    import_gesetze_to_sqlite()
