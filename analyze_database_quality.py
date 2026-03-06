#!/usr/bin/env python3
"""Аналіз якості бази законів"""

import sqlite3

conn = sqlite3.connect('data/legal_database.db')
cursor = conn.cursor()

print("="*80)
print("  АНАЛІЗ ЯКОСТІ БАЗИ ЗАКОНІВ")
print("="*80)

# 1. Загальна статистика
cursor.execute("SELECT COUNT(*) FROM paragraphs")
total = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE text_de IS NULL OR text_de = ''")
empty = cursor.fetchone()[0]

cursor.execute("SELECT COUNT(DISTINCT code_name) FROM paragraphs")
codes = cursor.fetchone()[0]

print(f"\n📊 ЗАГАЛЬНА СТАТИСТИКА:")
print(f"  • Всього параграфів: {total:,}")
print(f"  • Пусті параграфи: {empty:,} ({empty/total*100:.1f}%)")
print(f"  • Унікальних кодексів: {codes}")

# 2. Перевірка якості тексту
cursor.execute("SELECT code_name, paragraph_number, text_de FROM paragraphs WHERE text_de IS NOT NULL LIMIT 100")
samples = cursor.fetchall()

print(f"\n🔍 ПЕРЕВІРКА ЯКОСТІ ТЕКСТУ (100 зразків):")

errors = {'no_paragraph_mark': 0, 'too_short': 0, 'html_tags': 0, 'markdown_headers': 0, 'valid': 0}

for code, para_num, text in samples:
    if not text:
        continue
    if '§' not in text and 'Absatz' not in text and 'Satz' not in text:
        errors['no_paragraph_mark'] += 1
    elif len(text) < 50:
        errors['too_short'] += 1
    elif '<' in text and '>' in text:
        errors['html_tags'] += 1
    elif text.startswith('#'):
        errors['markdown_headers'] += 1
    else:
        errors['valid'] += 1

print(f"  ✅ Коректні: {errors['valid']} ({errors['valid']}%)")
print(f"  ⚠️  Без § маркера: {errors['no_paragraph_mark']}")
print(f"  ⚠️  Занадто короткі: {errors['too_short']}")
print(f"  ⚠️  З HTML тегами: {errors['html_tags']}")
print(f"  ⚠️  З Markdown заголовками: {errors['markdown_headers']}")

# 3. Розподіл по кодексах
print(f"\n📋 РОЗПОДІЛ ПО КОДЕКСАХ (ТОП-15):")
cursor.execute("""
    SELECT code_name, COUNT(*) as count, AVG(LENGTH(text_de)) as avg_len
    FROM paragraphs 
    WHERE code_name IS NOT NULL AND code_name != 'OTHER'
    GROUP BY code_name 
    ORDER BY count DESC 
    LIMIT 15
""")

for row in cursor.fetchall():
    code, count, avg_len = row
    print(f"  {code}: {count:,} параграфів (серед. довжина: {avg_len:.0f})")

# 4. OTHER категорія
print(f"\n🔍 OTHER КАТЕГОРІЯ:")
cursor.execute("SELECT COUNT(*) FROM paragraphs WHERE code_name = 'OTHER'")
other_count = cursor.fetchone()[0]
print(f"  • Всього OTHER: {other_count:,} ({other_count/total*100:.1f}%)")

# 5. Дублікати
print(f"\n🔄 ДУБЛІКАТИ:")
cursor.execute("""
    SELECT code_name, paragraph_number, COUNT(*) as count
    FROM paragraphs
    WHERE code_name IS NOT NULL AND paragraph_number IS NOT NULL
    GROUP BY code_name, paragraph_number
    HAVING count > 1
    ORDER BY count DESC
    LIMIT 10
""")

duplicates = cursor.fetchall()
if duplicates:
    print(f"  Знайдено дублікатів: {len(duplicates)}")
    for code, para, count in duplicates[:5]:
        print(f"    {code} {para}: {count} разів")
else:
    print(f"  ✅ Дублікатів не знайдено")

# 6. Приклади параграфів
print(f"\n📄 ПРИКЛАДИ ПАРАГРАФІВ:")
cursor.execute("""
    SELECT code_name, paragraph_number, SUBSTR(text_de, 1, 100) as preview
    FROM paragraphs 
    WHERE text_de IS NOT NULL AND code_name NOT IN ('OTHER')
    ORDER BY RANDOM()
    LIMIT 5
""")

for code, para, preview in cursor.fetchall():
    print(f"  {code} {para}:")
    print(f"    {preview}...")
    print()

conn.close()
print("="*80)
print("  АНАЛІЗ ЗАВЕРШЕНО")
print("="*80)
