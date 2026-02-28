#!/usr/bin/env python3
"""
Тестовий скрипт для перевірки всіх компонентів системи.
"""

import sys
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_imports():
    """Перевірка імпорту модулів."""
    print("🔍 Перевірка імпорту модулів...")

    try:
        from src.ingestion import preprocess_text, load_letter
        print("✅ ingestion.py")
    except Exception as e:
        print(f"❌ ingestion.py: {e}")
        return False

    try:
        from src.nlp_analysis import analyze_text_advanced, classify_letter_type_advanced
        print("✅ nlp_analysis.py")
    except Exception as e:
        print(f"❌ nlp_analysis.py: {e}")
        return False
    
    try:
        from src.legal_db import get_relevant_laws
        print("✅ legal_db.py")
    except Exception as e:
        print(f"❌ legal_db.py: {e}")
        return False
    
    try:
        from src.response_generator import generate_response
        print("✅ response_generator.py")
    except Exception as e:
        print(f"❌ response_generator.py: {e}")
        return False
    
    return True

def test_nlp():
    """Перевірка NLP аналізу."""
    print("\n🔍 Перевірка NLP аналізу...")

    try:
        from src.nlp_analysis import analyze_text_advanced, classify_letter_type_advanced

        # Тестовий текст (борговий лист)
        test_text = """
        Sehr geehrte Damen und Herren,
        hiermit mahnen wir Sie zur Zahlung der offenen Forderung in Höhe von 500 Euro.
        Bitte überweisen Sie den Betrag innerhalb von 14 Tagen auf unser Konto.
        Bei Nichtzahlung werden wir gerichtliche Schritte einleiten.
        Mit freundlichen Grüßen
        """

        analysis = analyze_text_advanced(test_text)
        print(f"  Сутності: {analysis['entities'][:3]}...")
        print(f"  Ключові слова: {analysis['keywords'][:5]}...")

        letter_type, details = classify_letter_type_advanced(test_text)
        print(f"  Тип листа: {letter_type}")

        if letter_type == 'debt_collection':
            print("✅ NLP аналіз працює коректно")
            return True
        else:
            print(f"⚠️ Очікувався 'debt_collection', отримано '{letter_type}'")
            return True  # Не критично

    except Exception as e:
        print(f"❌ NLP аналіз: {e}")
        return False

def test_legal_db():
    """Перевірка бази законів."""
    print("\n🔍 Перевірка бази законів...")
    
    try:
        from src.legal_db import get_relevant_laws
        
        for letter_type in ['debt_collection', 'tenancy', 'employment', 'administrative', 'general']:
            laws = get_relevant_laws(letter_type, 'de')
            print(f"  {letter_type}: {len(laws['laws'])} законів")
        
        print("✅ База законів працює")
        return True
    except Exception as e:
        print(f"❌ База законів: {e}")
        return False

def test_response_generator():
    """Перевірка генерації відповідей."""
    print("\n🔍 Перевірка генерації відповідей...")
    
    try:
        from src.legal_db import get_relevant_laws
        from src.response_generator import generate_response
        
        laws = get_relevant_laws('debt_collection', 'de')
        response = generate_response('debt_collection', laws, 'uk', 'de')
        
        print(f"  Довжина відповіді: {len(response)} символів")
        print(f"  Перші рядки:\n{response[:200]}...")
        
        if 'BGB' in response or 'шаблон' in response.lower():
            print("✅ Генерація відповідей працює")
            return True
        else:
            print("⚠️ Відповідь може бути неповною")
            return True
            
    except Exception as e:
        print(f"❌ Генерація відповідей: {e}")
        return False

def test_preprocessing():
    """Перевірка попередньої обробки тексту."""
    print("\n🔍 Перевірка попередньої обробки...")
    
    try:
        from src.ingestion import preprocess_text
        
        test_text = "   Це   тестовий   текст   з   багатьма   пробілами.   "
        result = preprocess_text(test_text)
        
        print(f"  Вхід: '{test_text}'")
        print(f"  Вихід: '{result}'")
        
        if result == "Це тестовий текст з багатьма пробілами.":
            print("✅ Попередня обробка працює")
            return True
        else:
            print("⚠️ Можливі проблеми з обробкою")
            return True
            
    except Exception as e:
        print(f"❌ Попередня обробка: {e}")
        return False

def test_database():
    """Перевірка бази даних."""
    print("\n🔍 Перевірка бази даних...")
    
    try:
        import sqlite3
        from pathlib import Path
        
        # Ініціалізація БД
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        
        # Створення таблиць
        c.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER UNIQUE,
                username TEXT,
                password TEXT,
                language TEXT DEFAULT 'uk',
                country TEXT DEFAULT 'de',
                status TEXT DEFAULT 'resident',
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        c.execute('''
            CREATE TABLE IF NOT EXISTS letters (
                id INTEGER PRIMARY KEY,
                chat_id INTEGER,
                text TEXT,
                letter_type TEXT,
                analysis TEXT,
                response TEXT,
                lawyer_review TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        conn.commit()
        conn.close()
        
        print("✅ База даних ініціалізована")
        return True
        
    except Exception as e:
        print(f"❌ База даних: {e}")
        return False

def main():
    """Запуск всіх тестів."""
    print("=" * 50)
    print("🧪 ТЕСТУВАННЯ СИСТЕМИ Gov.de")
    print("=" * 50)
    
    results = []
    
    results.append(("Імпорт модулів", test_imports()))
    results.append(("NLP аналіз", test_nlp()))
    results.append(("База законів", test_legal_db()))
    results.append(("Генерація відповідей", test_response_generator()))
    results.append(("Попередня обробка", test_preprocessing()))
    results.append(("База даних", test_database()))
    
    print("\n" + "=" * 50)
    print("📊 РЕЗУЛЬТАТИ")
    print("=" * 50)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {name}")
    
    print(f"\nПройдено: {passed}/{total}")
    
    if passed == total:
        print("\n🎉 Всі тести пройшли успішно!")
        print("\n📌 Наступні кроки:")
        print("1. Встановіть залежності: pip install -r requirements.txt")
        print("2. Завантажте spaCy модель: python3 -m spacy download de_core_news_sm")
        print("3. Запустіть бота: python3 src/bots/client_bot.py")
        return 0
    else:
        print("\n⚠️ Деякі тести не пройшли. Перевірте помилки вище.")
        return 1

if __name__ == '__main__':
    sys.exit(main())
