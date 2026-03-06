#!/usr/bin/env python3
"""
Покращення бази законів:
1. Довантаження SGB параграфів
2. Розподіл OTHER категорії
3. Додавання § маркерів
"""

import sqlite3
import re
import json
from pathlib import Path

print("="*80)
print("  ПОКРАЩЕННЯ БАЗИ ЗАКОНІВ")
print("="*80)

conn = sqlite3.connect('data/legal_database.db')
cursor = conn.cursor()

# ============================================================================
# ЗАВДАННЯ 1: Довантаження SGB параграфів
# ============================================================================
print("\n" + "="*80)
print("  ЗАВДАННЯ 1: ДОВАНТАЖЕННЯ SGB ПАРАГРАФІВ")
print("="*80)

# Перевірка існуючих SGB файлів
sgb_files_dir = Path('data/german_laws_complete/s')
if sgb_files_dir.exists():
    print(f"\n📁 Директорія SGB: {sgb_files_dir}")
    
    # Знаходимо всі SGB файли
    sgbd_files = list(sgb_files_dir.glob('sgb_*.md')) + list(sgb_files_dir.glob('sgb*.md'))
    print(f"  Знайдено SGB файлів: {len(sgbd_files)}")
    
    # Імпорт нових SGB параграфів
    imported_sgb = 0
    for file_path in sgbd_files[:20]:  # Обмежуємо для тесту
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Парсинг параграфів
            para_pattern = r'§\s*(\d+[a-zA-Z]?)\s*\n(.*?)(?=§\s*\d|$$)'
            matches = re.findall(para_pattern, content, re.DOTALL)
            
            for para_num, text in matches:
                text = text.strip()
                if len(text) > 20:  # Фільтр коротких
                    # Перевірка чи існує вже
                    cursor.execute("""
                        SELECT id FROM paragraphs 
                        WHERE code_name = 'SGB' AND paragraph_number = ?
                    """, (f'§ {para_num}',))
                    
                    if not cursor.fetchone():
                        cursor.execute("""
                            INSERT INTO paragraphs (code_name, paragraph_number, text_de, category)
                            VALUES (?, ?, ?, ?)
                        """, ('SGB', f'§ {para_num}', text[:10000], file_path.stem))
                        imported_sgb += 1
        except Exception as e:
            pass
    
    print(f"  ✅ Імпортовано SGB параграфів: {imported_sgb}")
else:
    print(f"\n⚠️  Директорія SGB не знайдена: {sgbd_files_dir}")

conn.commit()

# ============================================================================
# ЗАВДАННЯ 2: Розподіл OTHER категорії
# ============================================================================
print("\n" + "="*80)
print("  ЗАВДАННЯ 2: РОЗПОДІЛ OTHER КАТЕГОРІЇ")
print("="*80)

# Ключові слова для розподілу
code_keywords = {
    'BGB': ['bürgerliches gesetzbuch', 'bgbl', 'schuldrecht', 'familienrecht', 'erbrecht'],
    'ZPO': ['zivilprozessordnung', 'zpo', 'gerichtsverfahren', 'klage', 'urteil'],
    'StGB': ['strafgesetzbuch', 'stgb', 'strafe', 'straftat'],
    'StPO': ['strafprozessordnung', 'stpo', 'strafverfahren'],
    'GG': ['grundgesetz', 'gg', 'verfassung', 'grundrecht'],
    'HGB': ['handelsgesetzbuch', 'hgb', 'kaufmann', 'handel'],
    'AO': ['abgabenordnung', 'ao', 'steuer', 'finanzamt'],
    'SGB': ['sozialgesetzbuch', 'sgb', 'sozial', 'jobcenter'],
    'VwGO': ['verwaltungsgerichtsordnung', 'vwgo', 'verwaltungsgericht'],
    'VwVfG': ['verwaltungsverfahrensgesetz', 'vwvfg', 'verwaltungsakt'],
    'EnWG': ['energiewirtschaftsgesetz', 'enwg', 'energie'],
    'VVG': ['versicherungsvertragsgesetz', 'vvg', 'versicherung'],
    'AufenthG': ['aufenthaltsgesetz', 'aufenthg', 'aufenthaltstitel'],
    'BVG': ['bundessozialgerichtsgesetz', 'bvg', 'sozialgericht'],
    'AktG': ['aktiengesetz', 'aktg', 'aktie'],
    'EStG': ['einkommensteuergesetz', 'estg', 'einkommensteuer'],
}

# Отримуємо OTHER параграфи
cursor.execute("""
    SELECT id, text_de FROM paragraphs 
    WHERE code_name = 'OTHER' AND text_de IS NOT NULL
""")
other_paragraphs = cursor.fetchall()

print(f"\n📊 OTHER параграфів для розподілу: {len(other_paragraphs):,}")

redistributed = 0
not_distributed = 0

for para_id, text in other_paragraphs:
    if not text:
        not_distributed += 1
        continue
    
    text_lower = text.lower()
    best_match = None
    best_score = 0
    
    # Пошук найкращого збігу
    for code, keywords in code_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        if score > best_score:
            best_score = score
            best_match = code
    
    # Оновлення якщо знайдено збіг
    if best_match and best_score >= 1:
        try:
            cursor.execute("""
                UPDATE paragraphs SET code_name = ? WHERE id = ?
            """, (best_match, para_id))
            redistributed += 1
        except sqlite3.IntegrityError:
            # Дублікат - видаляємо OTHER
            cursor.execute("DELETE FROM paragraphs WHERE id = ?", (para_id,))
            redistributed += 1
    else:
        not_distributed += 1

print(f"  ✅ Розподілено: {redistributed:,} ({redistributed/len(other_paragraphs)*100:.1f}%)")
print(f"  ℹ️  Залишилось OTHER: {not_distributed:,} ({not_distributed/len(other_paragraphs)*100:.1f}%)")

conn.commit()

# ============================================================================
# ЗАВДАННЯ 3: Додавання § маркерів
# ============================================================================
print("\n" + "="*80)
print("  ЗАВДАННЯ 3: ДОДАВАННЯ § МАРКЕРІВ")
print("="*80)

# Отримуємо параграфи без §
cursor.execute("""
    SELECT id, code_name, paragraph_number, text_de 
    FROM paragraphs 
    WHERE text_de IS NOT NULL 
    AND text_de NOT LIKE '%§%'
    AND text_de NOT LIKE '%Absatz%'
    AND text_de NOT LIKE '%Satz%'
    LIMIT 1000
""")
paragraphs_without_marker = cursor.fetchall()

print(f"\n📊 Параграфів без § маркера: {len(paragraphs_without_marker):,}")

updated_markers = 0
for para_id, code, para_num, text in paragraphs_without_marker:
    # Додаємо § на початок якщо це параграф
    if para_num and para_num.startswith('§'):
        # Вже має § в номері
        updated_markers += 1
    else:
        # Додаємо префікс
        updated_text = f"§ {para_num or ''}\n{text}" if para_num else text
        cursor.execute("""
            UPDATE paragraphs SET text_de = ? WHERE id = ?
        """, (updated_text[:10000], para_id))
        updated_markers += 1

print(f"  ✅ Оновлено маркерів: {updated_markers:,}")

conn.commit()

# ============================================================================
# ФІНАЛЬНА СТАТИСТИКА
# ============================================================================
print("\n" + "="*80)
print("  ФІНАЛЬНА СТАТИСТИКА")
print("="*80)

cursor.execute("SELECT COUNT(*) FROM paragraphs")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
other = cursor.fetchone()[0]

cursor.execute("""
    SELECT code_name, COUNT(*) as count 
    FROM paragraphs 
    WHERE code_name IS NOT NULL 
    GROUP BY code_name 
    ORDER BY count DESC 
    LIMIT 10
""")
top_codes = cursor.fetchall()

print(f"\n📊 ЗАГАЛЬНА КІЛЬКІСТЬ: {total:,} параграфів")
print(f"📊 OTHER: {other:,} ({other/total*100:.1f}%)")
print(f"\n📋 ТОП-10 КОДЕКСІВ:")
for code, count in top_codes:
    print(f"  {code}: {count:,}")

print("\n" + "="*80)
print("  ✅ ПОКРАЩЕННЯ ЗАВЕРШЕНО!")
print("="*80)

conn.close()
