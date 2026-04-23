#!/usr/bin/env python3
"""
Тестування функцій перекладу на вже запущеному боті.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Тестовий текст листа
TEST_LETTER = """Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)

Mit freundlichen Grüßen
Maria Schmidt"""

print("=" * 70)
print("  🔬 ТЕСТУВАННЯ ПЕРЕКЛАДУ")
print("=" * 70)

# 1️⃣ Тест перекладу з deep_translator (GoogleTranslator)
print("\n1️⃣ ТЕСТ ПЕРЕКЛАДУ (GoogleTranslator на українську):")
print("-" * 70)

try:
    from deep_translator import GoogleTranslator
    
    translator = GoogleTranslator(source_language='de', target_language='uk')
    translated = translator.translate(TEST_LETTER)
    
    print(f"✅ Переклад успішний!")
    print(f"\n📄 ОРИГІНАЛ (німецька):")
    print(f"{TEST_LETTER[:300]}...")
    print(f"\n🌐 ПЕРЕКЛАД (українська):")
    print(f"{translated[:300]}...")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()

# 2️⃣ Тест Advanced Translator
print("\n\n2️⃣ ТЕСТ ADVANCED TRANSLATOR:")
print("-" * 70)

try:
    from advanced_translator import translate_text
    result = translate_text(TEST_LETTER[:500], 'de', 'uk')
    
    if isinstance(result, dict):
        translated_adv = result.get('text', '')
        print(f"✅ Advanced Translator успішний!")
        print(f"   Сервіс: {result.get('service', 'unknown')}")
    else:
        translated_adv = str(result)
        print(f"✅ Advanced Translator успішний!")
    
    print(f"\n   Результат (перші 200 символів):")
    print(f"   {translated_adv[:200]}...")
    
except Exception as e:
    print(f"❌ Помилка: {e}")
    import traceback
    traceback.print_exc()

# 3️⃣ Тест перекладу на російську
print("\n\n3️⃣ ТЕСТ ПЕРЕКЛАДУ НА РОСІЙСЬКУ:")
print("-" * 70)

try:
    translator_ru = GoogleTranslator(source_language='de', target_language='ru')
    translated_ru = translator_ru.translate(TEST_LETTER)
    
    print(f"✅ Переклад на російську успішний!")
    print(f"\n   Результат (перші 300 символів):")
    print(f"   {translated_ru[:300]}...")
    
except Exception as e:
    print(f"❌ Помилка: {e}")

print("\n" + "=" * 70)
print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
print("=" * 70)
