#!/usr/bin/env python3
"""
Import Complete German Laws from JSON to SQLite Database
Імпорт повної бази німецьких законів з JSON у SQLite
"""

import json
import sqlite3
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('import_laws')

# Шляхи
JSON_FILE = Path('data/complete_law_json/german_laws_complete.json')
DB_FILE = Path('data/legal_database.db')

# Мапінг кодів кодексів
CODE_MAPPING = {
    'BGB': 'BGB',
    'ZPO': 'ZPO',
    'AO': 'AO',
    'SGB': 'SGB',
    'SGB II': 'SGB_II',
    'SGB III': 'SGB_III',
    'SGB V': 'SGB_V',
    'SGB VI': 'SGB_VI',
    'SGB VII': 'SGB_VII',
    'SGB VIII': 'SGB_VIII',
    'SGB IX': 'SGB_IX',
    'SGB X': 'SGB_X',
    'SGB XI': 'SGB_XI',
    'SGB XII': 'SGB_XII',
    'GG': 'GG',
    'StGB': 'StGB',
    'StPO': 'StPO',
    'HGB': 'HGB',
    'VwVfG': 'VwVfG',
    'VwGO': 'VwGO',
    'FGO': 'FGO',
    'SGG': 'SGG',
    'ArbGG': 'ArbGG',
    'BUrlG': 'BUrlG',
    'KSchG': 'KSchG',
    'TzBfG': 'TzBfG',
    'BetrVG': 'BetrVG',
    'AufenthG': 'AufenthG',
    'AsylG': 'AsylG',
    'BVG': 'BVG',
    'LFZG': 'LFZG',
    'MuSchG': 'MuSchG',
    'BEEG': 'BEEG',
    'EStG': 'EStG',
    'UStG': 'UStG',
    'GewO': 'GewO',
    'InsO': 'InsO',
    'GmbHG': 'GmbHG',
    'AktG': 'AktG',
    'UWG': 'UWG',
    'BDSG': 'BDSG',
    'DSGVO': 'DSGVO',
    'TMG': 'TMG',
    'Musterbauordnung': 'MBO',
    'LBO': 'LBO',
}

CODE_NAMES_UK = {
    'BGB': 'Цивільний кодекс',
    'ZPO': 'Цивільний процесуальний кодекс',
    'AO': 'Податковий кодекс',
    'SGB': 'Соціальний кодекс',
    'SGB_II': 'Соціальний кодекс II (Jobcenter)',
    'SGB_III': 'Соціальний кодекс III (Агентство з праці)',
    'SGB_V': 'Соціальний кодекс V (Здоров\'я)',
    'SGB_VI': 'Соціальний кодекс VI (Пенсії)',
    'SGB_VII': 'Соціальний кодекс VII (Страхування)',
    'SGB_VIII': 'Соціальний кодекс VIII (Молодь)',
    'SGB_IX': 'Соціальний кодекс IX (Інваліди)',
    'SGB_X': 'Соціальний кодекс X (Процедури)',
    'SGB_XI': 'Соціальний кодекс XI (Догляд)',
    'SGB_XII': 'Соціальний кодекс XII (Соцдопомога)',
    'GG': 'Основний закон (Конституція)',
    'StGB': 'Кримінальний кодекс',
    'StPO': 'Кримінально-процесуальний кодекс',
    'HGB': 'Торговельний кодекс',
    'VwVfG': 'Закон про адмінпроцедури',
    'VwGO': 'Кодекс адмінсудочинства',
    'FGO': 'Кодекс фінансового судочинства',
    'SGG': 'Кодекс соціального судочинства',
    'ArbGG': 'Кодекс трудового судочинства',
    'BUrlG': 'Закон про відпустки',
    'KSchG': 'Закон про захист від звільнення',
    'TzBfG': 'Закон про часткову зайнятість',
    'BetrVG': 'Закон про виробничі ради',
    'AufenthG': 'Закон про перебування іноземців',
    'AsylG': 'Закон про притулок',
    'BVG': 'Закон про федеральну пенсію',
    'LFZG': 'Закон про оплату праці',
    'MuSchG': 'Закон про охорону материнства',
    'BEEG': 'Закон про батьківську відпустку',
    'EStG': 'Закон про прибутковий податок',
    'UStG': 'Закон про ПДВ',
    'GewO': 'Промисловий кодекс',
    'InsO': 'Закон про банкрутство',
    'GmbHG': 'Закон про ТОВ',
    'AktG': 'Закон про акціонерні товариства',
    'UWG': 'Закон про недобросовісну конкуренцію',
    'BDSG': 'Закон про захист даних',
    'DSGVO': 'GDPR (Загальний регламент про захист даних)',
    'TMG': 'Закон про телемедіа',
    'MBO': 'Типове будівельне положення',
    'LBO': 'Земельне будівельне положення',
}


def extract_code_from_law_name(law_name: str) -> str:
    """Витягти код кодексу з назви закону."""
    law_upper = law_name.upper()
    
    # Пріоритетні співпадіння
    for code in CODE_MAPPING.keys():
        if law_upper.startswith(code.upper()) or f'({code.upper()})' in law_upper:
            return CODE_MAPPING.get(code, code)
    
    # Пошук за ключовими словами
    if 'SOZIALGESETZBUCH' in law_upper:
        if 'II' in law_upper:
            return 'SGB_II'
        elif 'III' in law_upper:
            return 'SGB_III'
        elif ' V ' in law_upper or 'FÜNFTES' in law_upper:
            return 'SGB_V'
        elif ' VI ' in law_upper or 'SECHSTES' in law_upper:
            return 'SGB_VI'
        elif ' VII ' in law_upper or 'SIEBENTES' in law_upper:
            return 'SGB_VII'
        elif ' VIII ' in law_upper or 'ACHTES' in law_upper:
            return 'SGB_VIII'
        elif ' IX ' in law_upper or 'NEUNTES' in law_upper:
            return 'SGB_IX'
        elif ' X ' in law_upper or 'ZEHNTE' in law_upper:
            return 'SGB_X'
        elif ' XI ' in law_upper or 'ELFTES' in law_upper:
            return 'SGB_XI'
        elif ' XII ' in law_upper or 'ZWÖLFTES' in law_upper:
            return 'SGB_XII'
        else:
            return 'SGB'
    
    if 'BÜRGERLICHES GESETZBUCH' in law_upper or 'BGB' in law_upper:
        return 'BGB'
    
    if 'GRUNDGESETZ' in law_upper or 'GG' in law_upper:
        return 'GG'
    
    if 'ABGABENORDNUNG' in law_upper or 'AO' in law_upper:
        return 'AO'
    
    if 'ZIVILPROZESSORDNUNG' in law_upper or 'ZPO' in law_upper:
        return 'ZPO'
    
    if 'STRAFGESETZBUCH' in law_upper or 'STGB' in law_upper:
        return 'StGB'
    
    if 'STRAFPROZESSORDNUNG' in law_upper or 'STPO' in law_upper:
        return 'StPO'
    
    if 'HANDELSGESETZBUCH' in law_upper or 'HGB' in law_upper:
        return 'HGB'
    
    return 'OTHER'


def init_database(conn: sqlite3.Connection):
    """Ініціалізація таблиць - використовуємо існуючу схему."""
    cursor = conn.cursor()
    
    # Таблиця codes вже існує з колонкою code_name
    # Таблиця paragraphs вже існує з колонкою code_name, paragraph_number, text_de, text_uk
    logger.info("✅ Таблиці вже існують")


def import_laws_to_sqlite():
    """Іморт законів з JSON в SQLite."""
    logger.info("="*80)
    logger.info("  📚 ІМПОРТ ПОВНОЇ БАЗИ НІМЕЦЬКИХ ЗАКОНІВ")
    logger.info("="*80)
    
    # Завантаження JSON
    logger.info(f"\n📥 Завантаження JSON ({JSON_FILE.stat().st_size / 1024 / 1024:.1f} MB)...")
    with open(JSON_FILE, 'r', encoding='utf-8') as f:
        laws_data = json.load(f)
    
    logger.info(f"✅ Завантажено {len(laws_data)} законів")
    
    # Підключення до БД
    conn = sqlite3.connect(DB_FILE)
    init_database(conn)
    cursor = conn.cursor()
    
    # Статистика
    total_paragraphs = 0
    codes_added = set()
    
    # Отримання існуючих кодів
    cursor.execute("SELECT code_name FROM codes")
    existing_codes = {row[0] for row in cursor.fetchall()}
    
    logger.info(f"\n📊 В базі вже є {len(existing_codes)} кодексів")
    
    # Імпорт
    logger.info("\n🔄 Імпорт законів...")
    
    for idx, law in enumerate(laws_data):
        law_name = law.get('law_name', 'Unknown')
        file_path = law.get('file', '')
        paragraphs = law.get('paragraphs', [])
        
        if not paragraphs:
            continue
        
        # Визначення кодексу
        code = extract_code_from_law_name(law_name)
        codes_added.add(code)
        
        # Додавання кодексу до таблиці codes
        if code not in existing_codes:
            name_uk = CODE_NAMES_UK.get(code, law_name)
            name_de = law_name
            url = f"https://www.gesetze-im-internet.de/{code.lower()}/"
            
            cursor.execute("""
                INSERT OR IGNORE INTO codes (code_name, name_de, name_uk, url, categories, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (code, name_de, name_uk, url, '[]', datetime.now()))
            existing_codes.add(code)
        
        # Додавання параграфів
        for para in paragraphs:
            paragraph_num = para.get('paragraph', '')
            content = para.get('content', '')
            content_preview = para.get('content_preview', '')
            
            if not paragraph_num:
                continue
            
            cursor.execute("""
                INSERT OR IGNORE INTO paragraphs (code_name, paragraph_number, text_de, text_uk, category, keywords, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (code, paragraph_num, content, content_preview, law_name, '[]', datetime.now()))
            
            if cursor.rowcount > 0:
                total_paragraphs += 1
        
        # Прогрес кожні 500 законів
        if (idx + 1) % 500 == 0:
            logger.info(f"  Оброблено {idx + 1}/{len(laws_data)} законів ({total_paragraphs} параграфів)")
    
    # Збереження
    conn.commit()
    
    logger.info("\n" + "="*80)
    logger.info("  ✅ ІМПОРТ ЗАВЕРШЕНО!")
    logger.info("="*80)
    logger.info(f"\n📊 СТАТИСТИКА:")
    logger.info(f"  Законів оброблено: {len(laws_data)}")
    logger.info(f"  Параграфів додано: {total_paragraphs:,}")
    logger.info(f"  Кодексів додано: {len(codes_added)}")
    logger.info(f"  Файл БД: {DB_FILE}")
    
    # Підсумковий запит
    cursor.execute("SELECT COUNT(*) FROM paragraphs")
    total_in_db = cursor.fetchone()[0]
    
    cursor.execute("SELECT COUNT(*) FROM codes")
    codes_in_db = cursor.fetchone()[0]
    
    logger.info(f"\n📈 ВСЬОГО В БАЗІ:")
    logger.info(f"  Кодексів: {codes_in_db}")
    logger.info(f"  Параграфів: {total_in_db:,}")
    
    # Статистика по кодексах
    logger.info(f"\n📋 ПАРАГРАФИ ПО КОДЕКСАХ:")
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
    import_laws_to_sqlite()
