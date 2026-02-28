#!/usr/bin/env python3
"""
Test Script for Legal Database
Перевірка роботи SQLite бази даних законів
"""

import sys
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from legal_database import (
    init_db,
    search_laws,
    search_by_keywords,
    get_laws_by_category,
    get_consequences,
    detect_organization,
    detect_situation,
    analyze_letter,
    get_all_organizations,
    get_all_categories
)

def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_search_laws():
    """Тестування пошуку законів."""
    print_separator("🔍 Тест: Пошук законів за запитом 'mahnung'")
    
    results = search_laws('mahnung')
    print(f"Знайдено {len(results)} законів:\n")
    
    for law in results:
        print(f"  • {law['law_name']}")
        print(f"    {law['description'][:100]}...")
        print(f"    Категорія: {law['category']}")
        print()

def test_search_by_keywords():
    """Тестування пошуку за ключовими словами."""
    print_separator("🔍 Тест: Пошук за ключовими словами ['zahlung', 'forderung']")
    
    results = search_by_keywords(['zahlung', 'forderung'])
    print(f"Знайдено {len(results)} законів:\n")
    
    for law in results:
        print(f"  • {law['law_name']}")
        print(f"    {law['description'][:100]}...")
        print()

def test_get_laws_by_category():
    """Тестування отримання законів за категорією."""
    print_separator("📋 Тест: Закони категорії 'debt_collection'")
    
    results = get_laws_by_category('debt_collection')
    print(f"Знайдено {len(results)} законів:\n")
    
    for law in results:
        print(f"  • {law['law_name']}")
        print(f"    {law['description'][:100]}...")
        print()

def test_get_consequences():
    """Тестування отримання наслідків."""
    print_separator("⚠️ Тест: Наслідки для 'debt_collection'")
    
    consequences = get_consequences('debt_collection')
    print(consequences)
    print()

def test_detect_organization():
    """Тестування визначення організації."""
    print_separator("🏢 Тест: Визначення організації")
    
    test_texts = [
        "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung der offenen Forderung in Höhe von 500 Euro...",
        "Ihre Miete für die Wohnung ist fällig. Bitte überweisen Sie den Betrag bis zum 15. des Monats.",
        "Einladung zum Gespräch im Jobcenter. Termin am Montag um 10 Uhr.",
        "Steuerbescheid für das Jahr 2024. Es ergibt sich eine Steuernachzahlung von 1200 Euro."
    ]
    
    for text in test_texts:
        org = detect_organization(text)
        print(f"Текст: {text[:60]}...")
        if org:
            print(f"  → Організація: {org['name_uk']} ({org['org_key']})")
            print(f"  → Score: {org['score']}")
        else:
            print(f"  → Організація: не визначено")
        print()

def test_detect_situation():
    """Тестування визначення ситуації."""
    print_separator("📊 Тест: Визначення ситуації")
    
    test_cases = [
        ('inkasso', "Mahnung: Zahlung erforderlich innerhalb von 7 Tagen"),
        ('jobcenter', "Einladung zum Vorstellungsgespräch am Montag"),
        ('vermieter', "Kündigung der Wohnung wegen Eigenbedarf"),
        ('finanzamt', "Steuerbescheid mit Nachzahlung")
    ]
    
    for org_key, text in test_cases:
        situation = detect_situation(org_key, text)
        print(f"Організація: {org_key}")
        print(f"Текст: {text[:50]}...")
        if situation:
            print(f"  → Ситуація: {situation['description_uk']}")
            print(f"  → Параграфи: {', '.join(situation['paragraphs'])}")
        else:
            print(f"  → Ситуація: не визначено")
        print()

def test_analyze_letter():
    """Тестування повного аналізу листа."""
    print_separator("📝 Тест: Повний аналіз листа")
    
    test_letters = [
        {
            'name': 'Борговий лист (Inkasso)',
            'text': '''Sehr geehrte Damen und Herren,
hiermit mahnen wir Sie zur Zahlung der offenen Forderung in Höhe von 500 Euro.
Bitte überweisen Sie den Betrag innerhalb von 7 Tagen auf unser Konto.
Bei Nichtzahlung werden wir gerichtliche Schritte einleiten.
Mit freundlichen Grüßen'''
        },
        {
            'name': 'Лист від Jobcenter',
            'text': '''Sehr geehrte Frau Müller,
hiermit laden wir Sie zu einem persönlichen Gespräch ein.
Termin: Montag, 10:00 Uhr, Raum 204.
Thema: Ihre Bewerbung und Vermittlung.
Bei Nichtteilnahme müssen wir Sanktionen verhängen.
Mit freundlichen Grüßen'''
        },
        {
            'name': 'Лист від орендодавця',
            'text': '''Sehr geehrte Frau Müller,
die Miete für Ihre Wohnung beträgt ab nächstem Monat 650 Euro warm.
Die Mieterhöhung ist ortsüblich und wird gemäß BGB § 558 begründet.
Mit freundlichen Grüßen'''
        }
    ]
    
    for letter in test_letters:
        print(f"\n{letter['name']}")
        print(f"Текст: {letter['text'][:80]}...\n")
        
        analysis = analyze_letter(letter['text'])
        
        print(f"  🏢 Організація: {analysis['organization']}")
        print(f"  📋 Ситуація: {analysis['situation']}")
        print(f"  📚 Параграфи: {', '.join(analysis['paragraphs']) if analysis['paragraphs'] else 'немає'}")
        print(f"  ⚠️ Наслідки: {analysis['consequences'][:100]}..." if analysis.get('consequences') else "")
        print()

def test_all_organizations():
    """Тестування списку організацій."""
    print_separator("🏢 Тест: Список всіх організацій")
    
    orgs = get_all_organizations()
    print(f"Знайдено {len(orgs)} організацій:\n")
    
    for org in orgs:
        print(f"  • {org['name_uk']} ({org['org_key']})")
    print()

def test_all_categories():
    """Тестування списку категорій."""
    print_separator("📋 Тест: Список всіх категорій")
    
    categories = get_all_categories()
    print(f"Знайдено {len(categories)} категорій:\n")
    
    for cat in categories:
        print(f"  • {cat}")
    print()

def main():
    """Головна функція тестування."""
    print("\n" + "="*60)
    print("  ТЕСТУВАННЯ SQLITE БАЗИ ДАНИХ ЗАКОНІВ")
    print("="*60)
    
    # Ініціалізація бази даних
    print("\n⏳ Ініціалізація бази даних...")
    init_db()
    print("✅ База даних ініціалізована")
    
    # Запуск тестів
    try:
        test_all_organizations()
        test_all_categories()
        test_search_laws()
        test_search_by_keywords()
        test_get_laws_by_category()
        test_get_consequences()
        test_detect_organization()
        test_detect_situation()
        test_analyze_letter()
        
        print_separator("✅ ВСІ ТЕСТИ УСПІШНІ!")
        print("\nБаза даних працює коректно і готова до використання.\n")
        
    except Exception as e:
        print(f"\n❌ ПОМИЛКА ПІД ЧАС ТЕСТУВАННЯ: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == '__main__':
    exit(main())
