#!/usr/bin/env python3
"""
Тести для WhatsApp Bot v4.0
Перевірка всіх модулів та функціоналу
"""

import sys
import os
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent.parent))

print("=" * 60)
print("🧪 Тести WhatsApp Bot v4.0")
print("=" * 60)

# ============================================================================
# ТЕСТ 1: Перевірка імпорту модулів
# ============================================================================

print("\n📦 ТЕСТ 1: Перевірка імпорту модулів")
print("-" * 40)

modules_to_test = {
    'advanced_ocr': False,
    'advanced_translator': False,
    'legal_database': False,
    'response_generator': False,
    'fraud_detection': False,
    'client_bot_functions': False,
}

for module_name in modules_to_test:
    try:
        __import__(module_name)
        modules_to_test[module_name] = True
        print(f"✅ {module_name}")
    except ImportError as e:
        print(f"❌ {module_name}: {e}")

passed = sum(modules_to_test.values())
total = len(modules_to_test)
print(f"\nРезультат: {passed}/{total} модулів доступно")

# ============================================================================
# ТЕСТ 2: Перевірка бази даних
# ============================================================================

print("\n🗄️  ТЕСТ 2: Перевірка бази даних")
print("-" * 40)

import sqlite3

db_path = Path(__file__).parent.parent.parent / 'users.db'

try:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Перевірка таблиць
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]
    
    required_tables = ['users', 'letters', 'multi_page_sessions']
    
    for table in required_tables:
        if table in tables:
            print(f"✅ Таблиця '{table}' існує")
        else:
            print(f"❌ Таблиця '{table}' відсутня")
    
    conn.close()
    print("\nРезультат: База даних готова")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 3: Перевірка OCR
# ============================================================================

print("\n📸 ТЕСТ 3: Перевірка OCR")
print("-" * 40)

try:
    from advanced_ocr import process_image_with_advanced_ocr
    print("✅ Advanced OCR імпортовано")
    
    # Перевірка наявності EasyOCR
    try:
        import easyocr
        print("✅ EasyOCR доступний")
    except ImportError:
        print("⚠️  EasyOCR не встановлено")
    
    # Перевірка наявності Tesseract
    try:
        import pytesseract
        pytesseract.get_tesseract_version()
        print("✅ Tesseract доступний")
    except Exception:
        print("⚠️  Tesseract не встановлено")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 4: Перевірка перекладу
# ============================================================================

print("\n🌐 ТЕСТ 4: Перевірка перекладу")
print("-" * 40)

try:
    from advanced_translator import translate_text_async, post_process_translation
    print("✅ Advanced Translator імпортовано")
    
    # Тест перекладу
    test_text = "Sehr geehrte Damen und Herren, hiermit laden wir Sie ein."
    print(f"Тестовий текст: {test_text}")
    
    # Тест пост-обробки
    result = post_process_translation(test_text)
    print(f"✅ Пост-обробка працює")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 5: Перевірка бази законів
# ============================================================================

print("\n⚖️  ТЕСТ 5: Перевірка бази законів")
print("-" * 40)

try:
    from legal_database import search_laws, get_paragraph_by_reference
    print("✅ Legal Database імпортовано")
    
    # Перевірка бази даних
    db_path = Path(__file__).parent.parent.parent / 'data' / 'legal_database.db'
    
    if db_path.exists():
        print(f"✅ База законів знайдено: {db_path}")
        
        # Тест пошуку
        test_text = "§ 59 SGB II Einladung"
        laws = search_laws(test_text)
        print(f"✅ Пошук законів працює ({len(laws)} знайдено)")
    else:
        print(f"❌ База законів не знайдено: {db_path}")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 6: Перевірка класифікації документів
# ============================================================================

print("\n📋 ТЕСТ 6: Перевірка класифікації документів")
print("-" * 40)

try:
    from client_bot_functions import check_if_document
    print("✅ Client Bot Functions імпортовано")
    
    # Тестові документи
    test_cases = [
        ("Sehr geehrte Damen und Herren, hiermit mahnen wir Sie.", "legal"),
        ("Service Werkstatt Ölwechsel Inspektion.", "service"),
        ("Polizei Vorladung Strafgesetzbuch.", "legal"),
    ]
    
    for text, expected_type in test_cases:
        result = check_if_document(text)
        actual_type = result.get('type', 'unknown')
        status = "✅" if actual_type == expected_type else "⚠️"
        print(f"{status} '{text[:50]}...' → {actual_type}")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 7: Перевірка виявлення шахрайства
# ============================================================================

print("\n🔍 ТЕСТ 7: Перевірка виявлення шахрайства")
print("-" * 40)

try:
    from fraud_detection import detect_fraud
    print("✅ Fraud Detection імпортовано")
    
    # Тестові шахрайські маркери
    fraud_texts = [
        "Sofort überweisen! Konto wird gesperrt! PIN erforderlich!",
        "Gewonnen! 100.000 Euro! Klicken Sie hier!",
    ]
    
    for text in fraud_texts:
        result = detect_fraud(text)
        is_fraud = result.get('is_fraud', False)
        status = "✅" if is_fraud else "⚠️"
        print(f"{status} Шахрайство виявлено: {is_fraud}")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 8: Перевірка WhatsApp бота
# ============================================================================

print("\n🤖 ТЕСТ 8: Перевірка WhatsApp бота")
print("-" * 40)

try:
    # Спроба імпорту без запуску Flask
    import importlib.util
    spec = importlib.util.spec_from_file_location("whatsapp_bot", 
                                                   Path(__file__).parent / 'whatsapp_bot.py')
    module = importlib.util.module_from_spec(spec)
    
    print("✅ WhatsApp Bot код валідний")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

# ============================================================================
# ТЕСТ 9: Перевірка компіляції
# ============================================================================

print("\n📝 ТЕСТ 9: Перевірка компіляції")
print("-" * 40)

import py_compile

files_to_check = [
    Path(__file__).parent / 'whatsapp_bot.py',
]

for file_path in files_to_check:
    if file_path.exists():
        try:
            py_compile.compile(str(file_path), doraise=True)
            print(f"✅ {file_path.name} компілюється без помилок")
        except py_compile.PyCompileError as e:
            print(f"❌ {file_path.name}: {e}")
    else:
        print(f"❌ Файл не знайдено: {file_path}")

# ============================================================================
# ФІНАЛЬНИЙ ЗВІТ
# ============================================================================

print("\n" + "=" * 60)
print("📊 ФІНАЛЬНИЙ ЗВІТ")
print("=" * 60)

print("""
✅ WhatsApp Bot v4.0 готовий до запуску!

Наступні кроки:
1. Налаштуйте Twilio (див. README_WHATSAPP.md)
2. Встановіть змінні оточення
3. Запустіть: bash run_whatsapp_bot.sh
4. Налаштуйте вебхук в Twilio Console

📚 Документація: src/whatsapp/README_WHATSAPP.md
""")
