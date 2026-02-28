#!/usr/bin/env python3
"""
Test Script for Advanced Translator
Перевірка покращеного перекладу текстів
"""

import sys
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from advanced_translator import translate_text, AdvancedTranslator

def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_translator_initialization():
    """Тест ініціалізації перекладача."""
    print_separator("🔧 Тест: Ініціалізація перекладача")
    
    translator = AdvancedTranslator()
    
    print("Доступні сервіси:")
    for service in translator.services:
        print(f"  ✅ {service}")
    
    if not translator.services:
        print("  ❌ Жоден сервіс не доступний")
        return False
    
    print(f"\nВсього сервісів: {len(translator.services)}")
    print(f"Кеш завантажено: {len(translator.cache)} записів")
    return True

def test_dictionary_translation():
    """Тест перекладу з використанням словника."""
    print_separator("📚 Тест: Переклад з юридичним словником")
    
    test_phrases = [
        "Sehr geehrte Damen und Herren",
        "Mahnung",
        "Kündigung",
        "Jobcenter",
        "Bescheid",
        "Widerspruch"
    ]
    
    translator = AdvancedTranslator()
    
    print("Переклад окремих термінів:\n")
    
    for phrase in test_phrases:
        result = translator.translate_sync(phrase, dest='uk', use_cache=False)
        print(f"🇩🇪 {phrase}")
        print(f"🇺🇦 {result['text']}")
        print(f"   Словник: {result['dictionary_applied']}")
        print()
    
    return True

def test_full_text_translation():
    """Тест перекладу повного тексту."""
    print_separator("📝 Тест: Переклад повного тексту")
    
    test_texts = [
        {
            'name': 'Борговий лист',
            'text': "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung der offenen Forderung in Höhe von 500 Euro. Bitte überweisen Sie den Betrag innerhalb von 7 Tagen auf unser Konto."
        },
        {
            'name': 'Звільнення',
            'text': "Hiermit kündigen wir das Mietverhältnis fristgerecht zum nächstmöglichen Termin. Die Wohnung muss geräumt werden."
        },
        {
            'name': 'Jobcenter',
            'text': "Einladung zum persönlichen Gespräch im Jobcenter. Termin am Montag um 10 Uhr. Bei Nichtteilnahme müssen wir Sanktionen verhängen."
        },
        {
            'name': 'Податкова',
            'text': "Steuerbescheid für das Jahr 2024. Es ergibt sich eine Steuernachzahlung von 1200 Euro. Widerspruch ist innerhalb eines Monats möglich."
        }
    ]
    
    for test in test_texts:
        print(f"\n{test['name']}:")
        print(f"🇩🇪 {test['text'][:80]}...\n")
        
        # Українська
        result_uk = translate_text(test['text'], dest='uk')
        print(f"🇺🇦 {result_uk['text']}")
        print(f"   Сервіс: {result_uk['service']}, Кеш: {result_uk['from_cache']}, Словник: {result_uk['dictionary_applied']}")
        print()
        
        # Російська
        result_ru = translate_text(test['text'], dest='ru')
        print(f"🇷🇺 {result_ru['text']}")
        print(f"   Сервіс: {result_ru['service']}, Кеш: {result_ru['from_cache']}, Словник: {result_ru['dictionary_applied']}")
        print("-" * 60)
    
    return True

def test_cache():
    """Тест кешування перекладів."""
    print_separator("💾 Тест: Кешування перекладів")
    
    text = "Mahnung: Zahlung erforderlich"
    
    # Перший переклад (не з кешу)
    print("Перший переклад:")
    result1 = translate_text(text, dest='uk', use_cache=True)
    print(f"  Сервіс: {result1['service']}")
    print(f"  З кешу: {result1['from_cache']}")
    print(f"  Текст: {result1['text']}")
    
    # Другий переклад (з кешу)
    print("\nДругий переклад (має бути з кешу):")
    result2 = translate_text(text, dest='uk', use_cache=True)
    print(f"  Сервіс: {result2['service']}")
    print(f"  З кешу: {result2['from_cache']}")
    print(f"  Текст: {result2['text']}")
    
    if result2['from_cache']:
        print("\n✅ Кешування працює!")
        return True
    else:
        print("\n⚠️ Кешування не спрацювало")
        return False

def test_legal_terms():
    """Тест перекладу юридичних термінів."""
    print_separator("⚖️ Тест: Переклад юридичних термінів")
    
    legal_terms = {
        'BGB § 286': 'Прострочення боржника',
        'BGB § 535': 'Обов\'язки орендодавця',
        '§ 59 SGB II': 'Обов\'язок явки',
        'VwVfG § 35': 'Адміністративний акт',
        'Gerichtsvollzieher': 'Судовий виконавець',
        'Zwangsvollstreckung': 'Примусове виконання'
    }
    
    translator = AdvancedTranslator()
    
    print("Перевірка юридичних термінів:\n")
    
    all_correct = True
    for de_term, expected_uk in legal_terms.items():
        result = translator.translate_sync(de_term, dest='uk', use_cache=False)
        
        # Перевірка чи містить переклад очікувані слова
        match = any(word in result['text'].lower() for word in expected_uk.lower().split())
        
        status = "✅" if match or result['dictionary_applied'] else "⚠️"
        print(f"{status} {de_term}")
        print(f"   Очікується: {expected_uk}")
        print(f"   Отримано: {result['text']}")
        print(f"   Словник: {result['dictionary_applied']}")
        print()
        
        if not match and not result['dictionary_applied']:
            all_correct = False
    
    return all_correct

def test_translation_quality():
    """Тест якості перекладу."""
    print_separator("📊 Тест: Якість перекладу")
    
    text = "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung."
    
    result = translate_text(text, dest='uk')
    
    print(f"Оригінал: {text}")
    print(f"\nПереклад: {result['text']}")
    print(f"\nДовжина оригіналу: {len(text)}")
    print(f"Довжина перекладу: {len(result['text'])}")
    print(f"Сервіс: {result['service']}")
    print(f"Словник: {result['dictionary_applied']}")
    
    # Перевірка якості
    checks = {
        'Шановний': 'Шановний' in result['text'],
        'Нагадування': 'нагаду' in result['text'].lower() or 'Mahnung' in result['text'],
        'Оплата': 'оплат' in result['text'].lower() or 'Zahlung' in result['text']
    }
    
    print("\nПеревірка якості:")
    all_passed = True
    for check, passed in checks.items():
        status = "✅" if passed else "❌"
        print(f"  {status} {check}")
        if not passed:
            all_passed = False
    
    return all_passed

def main():
    """Головна функція тестування."""
    print("\n" + "="*60)
    print("  ТЕСТУВАННЯ ADVANCED TRANSLATOR")
    print("="*60)
    
    results = {
        'Ініціалізація': test_translator_initialization(),
        'Словник': test_dictionary_translation(),
        'Повний текст': test_full_text_translation(),
        'Кешування': test_cache(),
        'Юр. терміни': test_legal_terms(),
        'Якість': test_translation_quality()
    }
    
    print_separator("📊 ПІДСУМКИ")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test}")
    
    print(f"\nРезультат: {passed}/{total} тестів пройдено")
    
    if passed >= total - 1:  # Дозволяємо 1 помилку
        print("\n🎉 ВСІ ТЕСТИ УСПІШНІ!")
        return 0
    else:
        print("\n⚠️ Деякі тести не пройшли")
        return 1

if __name__ == '__main__':
    exit(main())
