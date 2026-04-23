#!/usr/bin/env python3
"""
Тестування функцій перекладу та LLM обробки.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Тестовий текст листа
TEST_LETTER = """Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)

Mit freundlichen Grüßen
Maria Schmidt
Beraterin"""

print("=" * 70)
print("  🔬 ТЕСТУВАННЯ ПЕРЕКЛАДУ І LLM")
print("=" * 70)

# 1️⃣ Тест перекладу
print("\n1️⃣ ТЕСТ ПЕРЕКЛАДУ")
print("-" * 70)

try:
    from deep_translator import GoogleTranslator
    translator = GoogleTranslator(source_language='de', target_language='uk')
    translated = translator.translate(TEST_LETTER[:500])
    print(f"✅ GoogleTranslator работает!")
    print(f"   Оригінал (первих 200 символів): {TEST_LETTER[:200]}")
    print(f"\n   Переклад (перші 200 символів): {translated[:200]}")
except Exception as e:
    print(f"❌ GoogleTranslator помилка: {e}")

# 2️⃣ Тест Advanced Translator
print("\n\n2️⃣ ТЕСТ ADVANCED TRANSLATOR")
print("-" * 70)

try:
    from advanced_translator import translate_text
    result = translate_text(TEST_LETTER[:500], source_lang='de', target_lang='uk')
    print(f"✅ Advanced Translator работает!")
    print(f"   Результат тип: {type(result)}")
    print(f"   Результат: {str(result)[:200]}")
except Exception as e:
    print(f"❌ Advanced Translator помилка: {e}")

# 3️⃣ Тест LLM Orchestrator
print("\n\n3️⃣ ТЕСТ LLM ORCHESTRATOR")
print("-" * 70)

try:
    from llm_orchestrator import process_letter_with_llm
    print(f"   Обробка листа...")
    result = process_letter_with_llm(TEST_LETTER, lang='uk')
    
    print(f"\n   ✅ LLM обробка успішна!")
    print(f"   Success: {result.get('success')}")
    print(f"   Організація: {result.get('analysis', {}).get('organization', 'N/A')}")
    print(f"   Тип листа: {result.get('analysis', {}).get('letter_type', 'N/A')}")
    print(f"\n   📊 Довжина відповідей:")
    print(f"   - response_user: {result.get('response_user_length', 0)} символів")
    print(f"   - response_de: {result.get('response_de_length', 0)} символів")
    
    if result.get('response_user'):
        print(f"\n   📝 ВІДПОВІДЬ (UK, перші 300 символів):")
        print(f"   {result.get('response_user', '')[:300]}...")
    else:
        print(f"\n   ⚠️ response_user пуста!")
        
    if result.get('response_de'):
        print(f"\n   📝 ANTWORT (DE, перші 300 символів):")
        print(f"   {result.get('response_de', '')[:300]}...")
    else:
        print(f"\n   ⚠️ response_de пуста!")
        
except Exception as e:
    print(f"❌ LLM помилка: {e}")
    import traceback
    traceback.print_exc()

print("\n" + "=" * 70)
print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
print("=" * 70)
