#!/usr/bin/env python3
"""
Fix 'OTHER' Code Classification - Simple Version
Виправлення класифікації параграфів з кодом 'OTHER'
"""

import sqlite3
import re
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger('fix_other')

DB_FILE = 'data/legal_database.db'

# Прості ключові слова для визначення кодексу
CODE_KEYWORDS = {
    'BGB': ['bürgerliches gesetzbuch', 'schuldverhältnis', 'vertrag', 'eigentum', 'anspruch', '§ 105', '§ 104', '§ 241', '§ 242', '§ 280', '§ 311', '§ 433', '§ 535', '§ 611', '§ 823'],
    'GG': ['grundgesetz', 'freiheit', 'gleichheit', 'grundrecht', 'demokratie', '§ 1 GG', '§ 2 GG', '§ 3 GG', '§ 5 GG'],
    'SGB_II': ['sozialgesetzbuch ii', 'sgb ii', 'grundsicherung', 'jobcenter', 'arbeitslosengeld ii', 'hartz'],
    'SGB_III': ['sozialgesetzbuch iii', 'sgb iii', 'arbeitsförderung', 'arbeitsagentur', 'arbeitslosengeld'],
    'SGB_V': ['sozialgesetzbuch v', 'sgb v', 'gesetzliche krankenversicherung'],
    'AO': ['abgabenordnung', 'steuer', 'finanzamt', 'steuerbescheid'],
    'ZPO': ['zivilprozessordnung', 'klage', 'gericht', 'urteil', 'vollstreckung'],
    'StGB': ['strafgesetzbuch', 'strafe', 'straftat'],
    'HGB': ['handelsgesetzbuch', 'kaufmann', 'firma'],
    'VwVfG': ['verwaltungsverfahrensgesetz', 'verwaltungsakt'],
    'VwGO': ['verwaltungsgerichtsordnung', 'verwaltungsgericht'],
    'AufenthG': ['aufenthaltsgesetz', 'aufenthaltstitel', 'ausländer'],
    'AsylG': ['asylgesetz', 'asyl'],
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
}

def fix_other_codes():
    """Виправлення кодів для 'OTHER' параграфів."""
    logger.info("="*60)
    logger.info("  🔧 ВИПРАВЛЕННЯ 'OTHER' КОДІВ")
    logger.info("="*60)
    
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    
    # Отримати кількість OTHER
    cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
    other_count = cursor.fetchone()[0]
    logger.info(f"\n📊 Параграфів з 'OTHER': {other_count:,}")
    
    if other_count == 0:
        logger.info("✅ Немає 'OTHER' для виправлення")
        return
    
    updated = 0
    batch_size = 1000
    
    # Спочатку видалимо дублікати OTHER де вже є такі самі параграфи з іншим кодом
    logger.info("\n🗑️  Видалення дублікатів...")
    cursor.execute("""
        DELETE FROM paragraphs 
        WHERE code_name = 'OTHER' 
        AND (code_name, paragraph_number) IN (
            SELECT code_name, paragraph_number 
            FROM paragraphs 
            GROUP BY code_name, paragraph_number 
            HAVING COUNT(*) > 1
        )
        AND id NOT IN (
            SELECT MIN(id) 
            FROM paragraphs 
            GROUP BY code_name, paragraph_number
        )
    """)
    deleted = cursor.rowcount
    logger.info(f"   Видалено дублікатів: {deleted}")
    conn.commit()
    
    # Отримуємо ВСІ параграфі
    cursor.execute("SELECT id, paragraph_number, text_de FROM paragraphs WHERE code_name = 'OTHER'")
    rows = cursor.fetchall()
    
    logger.info(f"\n🔄 Обробка {len(rows)} параграфів...")
    
    for row_id, para_num, text_de in rows:
        if not text_de:
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
            # Спробуємо оновити, якщо конфлікт - видалити OTHER
            try:
                cursor.execute("UPDATE paragraphs SET code_name = ? WHERE id = ?", (new_code, row_id))
                if cursor.rowcount > 0:
                    updated += 1
            except sqlite3.IntegrityError:
                # Такий параграф вже є з іншим кодом - видаляємо OTHER
                cursor.execute("DELETE FROM paragraphs WHERE id = ?", (row_id,))
    
    conn.commit()
    
    logger.info("\n" + "="*60)
    logger.info("  ✅ ВИПРАВЛЕННЯ ЗАВЕРШЕНО!")
    logger.info("="*60)
    logger.info(f"📊 Оновлено параграфів: {updated}")
    
    # Нова статистика
    cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
    remaining = cursor.fetchone()[0]
    logger.info(f"📊 Залишилось 'OTHER': {remaining:,}")
    
    # Топ кодексів
    logger.info("\n📋 ТОП-10 КОДЕКСІВ:")
    cursor.execute("""
        SELECT code_name, COUNT(*) as count 
        FROM paragraphs 
        GROUP BY code_name 
        ORDER BY count DESC 
        LIMIT 10
    """)
    for row in cursor.fetchall():
        logger.info(f"  {row[0]}: {row[1]:,}")
    
    conn.close()

if __name__ == '__main__':
    fix_other_codes()
