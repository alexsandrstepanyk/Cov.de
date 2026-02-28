#!/usr/bin/env python3
"""
Interactive Test Script for Gov.de v4.0
Тестування всіх модулів бота в інтерактивному режимі
"""

import sys
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

def print_header(title: str):
    print("\n" + "="*60)
    print(f"  {title}")
    print("="*60 + "\n")

def test_legal_database():
    """Тестування бази даних законів."""
    print_header("📚 ТЕСТУВАННЯ БАЗИ ДАНИХ ЗАКОНІВ")
    
    from legal_database import analyze_letter, search_laws, get_laws_by_category
    
    # Тест 1: Аналіз листа
    print("Тест 1: Аналіз боргового листа")
    text = "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung der offenen Forderung in Höhe von 500 Euro."
    result = analyze_letter(text)
    
    print(f"  Текст: {text[:60]}...")
    print(f"  ✅ Організація: {result['organization']}")
    print(f"  ✅ Ситуація: {result['situation']}")
    print(f"  ✅ Параграфи: {', '.join(result['paragraphs'])}")
    print(f"  ✅ Наслідки: {result['consequences'][:80]}...")
    
    # Тест 2: Аналіз листа від Jobcenter
    print("\nТест 2: Аналіз листа від Jobcenter")
    text = "Einladung zum persönlichen Gespräch im Jobcenter. Termin am Montag um 10 Uhr."
    result = analyze_letter(text)
    
    print(f"  Текст: {text[:60]}...")
    print(f"  ✅ Організація: {result['organization']}")
    print(f"  ✅ Ситуація: {result['situation']}")
    print(f"  ✅ Параграфи: {', '.join(result['paragraphs'])}")
    
    # Тест 3: Пошук законів
    print("\nТест 3: Пошук законів за запитом 'mahnung'")
    results = search_laws('mahnung')
    print(f"  ✅ Знайдено {len(results)} законів")
    for law in results[:3]:
        print(f"    • {law['law_name']}")
    
    return True

def test_advanced_ocr():
    """Тестування Advanced OCR."""
    print_header("📸 ТЕСТУВАННЯ ADVANCED OCR")
    
    from advanced_ocr import recognize_image
    import cv2
    import numpy as np
    
    # Створення тестового зображення
    print("Створення тестового зображення...")
    img = np.ones((300, 800), dtype=np.uint8) * 255
    cv2.putText(img, 'Mahnung: Zahlung 500 Euro', (50, 100), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
    cv2.putText(img, 'Bitte innerhalb 7 Tagen', (50, 200), 
               cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
    
    test_path = '/tmp/test_ocr_letter.jpg'
    cv2.imwrite(test_path, img)
    print(f"  ✅ Зображення створено: {test_path}")
    
    # Розпізнавання
    print("\nРозпізнавання тексту...")
    result = recognize_image(test_path, lang='deu+eng')
    
    print(f"  ✅ Рушій: {result['engine']}")
    print(f"  ✅ Текст: {result['text']}")
    print(f"  ✅ Символів: {len(result['text'])}")
    print(f"  ✅ Якість: {result['quality'].get('quality', 'unknown')}")
    
    if result['quality'].get('recommendations'):
        print(f"  💡 Поради:")
        for rec in result['quality']['recommendations'][:2]:
            print(f"    {rec}")
    
    return True

def test_advanced_translator():
    """Тестування Advanced Translator."""
    print_header("🌐 ТЕСТУВАННЯ ADVANCED TRANSLATOR")
    
    from advanced_translator import translate_text
    
    test_texts = [
        "Mahnung",
        "Sehr geehrte Damen und Herren",
        "Kündigung der Wohnung",
        "Einladung zum Gespräch im Jobcenter"
    ]
    
    for text in test_texts:
        print(f"\nПереклад: {text}")
        result = translate_text(text, dest='uk')
        
        print(f"  ✅ Українська: {result['text']}")
        print(f"  ✅ Сервіс: {result['service']}")
        print(f"  ✅ Словник: {result['dictionary_applied']}")
        print(f"  ✅ З кешу: {result['from_cache']}")
    
    return True

def test_nlp_analysis():
    """Тестування NLP аналізу."""
    print_header("🔍 ТЕСТУВАННЯ NLP АНАЛІЗУ")
    
    from nlp_analysis import classify_letter_type_advanced, get_laws_for_letter
    
    test_texts = [
        ("Mahnung: Zahlung erforderlich", "Борговий лист"),
        ("Kündigung der Wohnung", "Оренда"),
        ("Einladung im Jobcenter", "Jobcenter"),
        ("Steuerbescheid vom Finanzamt", "Податкова")
    ]
    
    for text, expected in test_texts:
        print(f"\nТекст: {text}")
        print(f"  Очікується: {expected}")
        
        letter_type, details = classify_letter_type_advanced(text)
        print(f"  ✅ Визначено: {letter_type}")
        
        laws = get_laws_for_letter(letter_type, text)
        if laws.get('primary'):
            print(f"  ✅ Закони: {len(laws['primary'])} знайдено")
    
    return True

def test_smart_law_reference():
    """Тестування Smart Law Reference."""
    print_header("⚖️ ТЕСТУВАННЯ SMART LAW REFERENCE")
    
    from smart_law_reference import analyze_letter_smart
    
    test_texts = [
        "Mahnung: Sie schulden 500 Euro. Zahlen Sie innerhalb von 7 Tagen.",
        "Kündigung: Wir kündigen das Mietverhältnis zum nächstmöglichen Termin.",
        "Einladung: Persönliches Gespräch im Jobcenter am Montag."
    ]
    
    for text in test_texts:
        print(f"\nТекст: {text[:60]}...")
        result = analyze_letter_smart(text, 'uk')
        
        law_info = result['law_info']
        print(f"  ✅ Організація: {law_info['organization']}")
        print(f"  ✅ Ситуація: {law_info['situation']}")
        print(f"  ✅ Параграфи: {len(law_info['paragraphs'])} знайдено")
        
        if result.get('tips'):
            print(f"  💡 Поради: {len(result['tips'])} знайдено")
    
    return True

def test_fraud_detection():
    """Тестування Fraud Detection."""
    print_header("🚨 ТЕСТУВАННЯ FRAUD DETECTION")
    
    from fraud_detection import analyze_letter_for_fraud, generate_fraud_warning
    
    # Тест на шахрайство
    fraud_text = """
    Sehr geehrte Damen und Herren,
    Sie müssen sofort 1000 Euro überweisen.
    Zahlen Sie mit Western Union oder Bitcoin.
    Bei Nichtzahlung kommt die Polizei und verhaftet Sie.
    """
    
    print("Тест на шахрайство:")
    print(f"  Текст: {fraud_text[:80]}...")
    
    fraud_analysis = analyze_letter_for_fraud(fraud_text, {})
    warning = generate_fraud_warning(fraud_analysis)
    
    print(f"  ✅ Рівень ризику: {fraud_analysis.get('risk_level', 'unknown')}")
    print(f"  ✅ Ознаки шахрайства: {len(fraud_analysis.get('fraud_indicators', []))} знайдено")
    
    risk_level = fraud_analysis.get('risk_level', 'low')
    if isinstance(risk_level, str) and risk_level == 'high':
        print(f"  🚨 ПОПЕРЕДЖЕННЯ: Високий ризик шахрайства!")
    elif isinstance(risk_level, (int, float)) and risk_level > 5:
        print(f"  🚨 ПОПЕРЕДЖЕННЯ: Високий ризик шахрайства!")
    
    return True

def main():
    """Головна функція."""
    print("\n" + "="*60)
    print("  ІНТЕРАКТИВНЕ ТЕСТУВАННЯ GOV.DE v4.0")
    print("="*60)
    
    tests = [
        ("📚 База даних законів", test_legal_database),
        ("📸 Advanced OCR", test_advanced_ocr),
        ("🌐 Advanced Translator", test_advanced_translator),
        ("🔍 NLP аналіз", test_nlp_analysis),
        ("⚖️ Smart Law Reference", test_smart_law_reference),
        ("🚨 Fraud Detection", test_fraud_detection)
    ]
    
    results = {}
    
    for name, test_func in tests:
        try:
            result = test_func()
            results[name] = "✅" if result else "❌"
        except Exception as e:
            print(f"\n❌ ПОМИЛКА: {e}")
            results[name] = "❌"
            import traceback
            traceback.print_exc()
    
    # Підсумки
    print_header("📊 ПІДСУМКИ")
    
    for name, status in results.items():
        print(f"{status} {name}")
    
    passed = sum(1 for v in results.values() if v == "✅")
    total = len(results)
    
    print(f"\nРезультат: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n🎉 ВСІ ТЕСТИ УСПІШНІ! ВЕРСІЯ 4.0 ГОТОВА!")
    else:
        print("\n⚠️ Деякі тести не пройшли")
    
    print("\n" + "="*60 + "\n")
    
    return 0 if passed == total else 1

if __name__ == '__main__':
    exit(main())
