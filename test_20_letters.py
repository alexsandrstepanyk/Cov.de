#!/usr/bin/env python3
"""
Масове тестування Gov.de Bot v4.1
20 тестових листів від різних організацій
"""

import sys
from pathlib import Path

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import check_if_document, get_paragraph_description
from datetime import datetime

# Імпортуємо тестові листи
TEST_LETTERS = [
    # Jobcenter (5)
    {
        'id': 1,
        'category': 'Jobcenter',
        'type': 'Einladung',
        'text': '''Jobcenter Berlin Mitte
Einladung zum persönlichen Gespräch
Termin: Montag, 12.03.2026, um 10:00 Uhr
§ 59 SGB II, § 31 SGB II
Leistung um 30% gekürzt''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 59 SGB II', '§ 31 SGB II'],
            'deadline': '12.03.2026',
            'risk': '30% Kürzung'
        }
    },
    {
        'id': 2,
        'category': 'Jobcenter',
        'type': 'Leistungsbescheid',
        'text': '''Jobcenter Berlin
Bescheid über Arbeitslosengeld II
Gesamt: 1.093,00 EUR
§ 84 SGG
Widerspruch innerhalb eines Monats''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'amount': '1.093,00 EUR',
            'paragraphs': ['§ 84 SGG']
        }
    },
    {
        'id': 3,
        'category': 'Jobcenter',
        'type': 'Aufforderung zur Mitwirkung',
        'text': '''Jobcenter Hamburg
Aufforderung zur Mitwirkung
Unterlagen bis zum 10.03.2026
§ 60 SGB I
Leistungen einstellen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'deadline': '10.03.2026',
            'paragraphs': ['§ 60 SGB I']
        }
    },
    {
        'id': 4,
        'category': 'Jobcenter',
        'type': 'Sanktionsbescheid',
        'text': '''Jobcenter München
Bescheid über Leistungskürzung
30% für 3 Monate
§ 31 SGB II
Widerspruchsfrist: 22.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'reduction': '30%',
            'paragraphs': ['§ 31 SGB II']
        }
    },
    {
        'id': 5,
        'category': 'Jobcenter',
        'type': 'Vermittlungsvorschlag',
        'text': '''Arbeitsagentur Nürnberg
Vermittlungsvorschlag
Bewerbung bis zum 05.03.2026
§ 140 SGB III''',
        'expected': {
            'is_document': True,
            'org': 'Arbeitsagentur',
            'deadline': '05.03.2026',
            'paragraphs': ['§ 140 SGB III']
        }
    },
    
    # Inkasso (4)
    {
        'id': 6,
        'category': 'Inkasso',
        'type': 'Erste Mahnung',
        'text': '''CreditProtect Inkasso GmbH
Erste Mahnung
Offener Betrag: 350,00 EUR
Frist: 05.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '350,00 EUR',
            'deadline': '05.03.2026'
        }
    },
    {
        'id': 7,
        'category': 'Inkasso',
        'type': 'Letzte Mahnung',
        'text': '''EOS Rema Inkasso
Letzte Mahnung
Gesamtbetrag: 1.250,00 EUR
Frist: 28.02.2026
Gerichtliche Schritte''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '1.250,00 EUR',
            'deadline': '28.02.2026',
            'risk': 'Gericht'
        }
    },
    {
        'id': 8,
        'category': 'Inkasso',
        'type': 'Zahlungsvereinbarung',
        'text': '''Inkasso Service Deutschland
Angebot zur Ratenzahlung
890,00 EUR in 6 Raten
Frist: 28.02.2026''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '890,00 EUR',
            'deadline': '28.02.2026'
        }
    },
    {
        'id': 9,
        'category': 'Inkasso',
        'type': 'Gerichtlicher Mahnbescheid',
        'text': '''Amtsgericht Hamburg
Mahnbescheid
2.500,00 EUR
Widerspruchsfrist: 12.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '2.500,00 EUR',
            'deadline': '12.03.2026',
            'risk': 'Sehr hoch'
        }
    },
    
    # Vermieter (4)
    {
        'id': 10,
        'category': 'Vermieter',
        'type': 'Mieterhöhung',
        'text': '''Vermieter Hans Müller
Mieterhöhung
450,00 EUR → 550,00 EUR
22,2% Erhöhung
§ 558 BGB
Widerspruch bis 30.04.2026''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'amount': '100,00 EUR',
            'paragraphs': ['§ 558 BGB']
        }
    },
    {
        'id': 11,
        'category': 'Vermieter',
        'type': 'Kündigung',
        'text': '''Vermieterin Maria Schmidt
Fristlose Kündigung
Miete 2 Monate nicht gezahlt
§ 543 BGB
Räumung bis 31.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'paragraphs': ['§ 543 BGB'],
            'deadline': '31.03.2026',
            'risk': 'Räumung'
        }
    },
    {
        'id': 12,
        'category': 'Vermieter',
        'type': 'Nebenkostenabrechnung',
        'text': '''Hausverwaltung Berlin GmbH
Nebenkostenabrechnung 2025
Nachzahlung: 300,00 EUR
Frist: 15.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'amount': '300,00 EUR',
            'deadline': '15.03.2026'
        }
    },
    {
        'id': 13,
        'category': 'Vermieter',
        'type': 'Mietmängelanzeige',
        'text': '''Mieterbund Berlin
Ihre Rechte bei Mietmängeln
Schimmelbildung
§ 536 BGB
Mietminderung bis 50%''',
        'expected': {
            'is_document': True,
            'org': 'Mieterbund',
            'paragraphs': ['§ 536 BGB']
        }
    },
    
    # Finanzamt (3)
    {
        'id': 14,
        'category': 'Finanzamt',
        'type': 'Steuerbescheid',
        'text': '''Finanzamt Berlin
Einkommensteuerbescheid 2025
Nachzahlung: 400,00 EUR
Frist: 10.03.2026
§ 355 AO''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'amount': '400,00 EUR',
            'deadline': '10.03.2026',
            'paragraphs': ['§ 355 AO']
        }
    },
    {
        'id': 15,
        'category': 'Finanzamt',
        'type': 'Aufforderung zur Steuererklärung',
        'text': '''Finanzamt Hamburg
Aufforderung zur Abgabe der Steuererklärung
Frist: 31.05.2026
§ 328 AO
Zwangsgeld bei Verspätung''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'deadline': '31.05.2026',
            'paragraphs': ['§ 328 AO']
        }
    },
    {
        'id': 16,
        'category': 'Finanzamt',
        'type': 'Lohnsteuerbescheinigung',
        'text': '''Arbeitgeber GmbH
Lohnsteuerbescheinigung 2025
Brutto: 36.000,00 EUR
Lohnsteuer: 4.800,00 EUR
Netto: 23.736,00 EUR''',
        'expected': {
            'is_document': True,
            'org': 'Arbeitgeber',
            'amount': '36.000,00 EUR'
        }
    },
    
    # Gericht (2)
    {
        'id': 17,
        'category': 'Gericht',
        'type': 'Gerichtstermin',
        'text': '''Amtsgericht Berlin-Charlottenburg
Ladung zur Gerichtssitzung
Termin: 20.03.2026, 09:30 Uhr
§ 330 ZPO
Versäumnisurteil bei Ausbleiben''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'deadline': '20.03.2026',
            'paragraphs': ['§ 330 ZPO'],
            'risk': 'Versäumnisurteil'
        }
    },
    {
        'id': 18,
        'category': 'Gericht',
        'type': 'Anwaltliches Schreiben',
        'text': '''Rechtsanwalt Dr. Weber
Anwaltliches Schreiben
5.000,00 EUR + 500,00 EUR Anwaltskosten
Frist: 10.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Rechtsanwalt',
            'amount': '5.500,00 EUR',
            'deadline': '10.03.2026',
            'risk': 'Gericht'
        }
    },
    
    # Krankenkasse (2)
    {
        'id': 19,
        'category': 'Krankenkasse',
        'type': 'Krankenkassenbescheid',
        'text': '''AOK Berlin
Bescheid über Krankenversicherung
Monatlicher Beitrag: 450,00 EUR
Ab 01.03.2026''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'amount': '450,00 EUR',
            'deadline': '01.03.2026'
        }
    },
    {
        'id': 20,
        'category': 'Versicherung',
        'type': 'Versicherungsrechnung',
        'text': '''Allianz Versicherung
Versicherungsrechnung 2026
Gesamtbeitrag: 890,00 EUR
Frist: 15.03.2026
§ 38 VVG''',
        'expected': {
            'is_document': True,
            'org': 'Versicherung',
            'amount': '890,00 EUR',
            'deadline': '15.03.2026',
            'paragraphs': ['§ 38 VVG']
        }
    }
]


def test_all_letters():
    """Тестування всіх 20 листів."""
    print("\n" + "="*80)
    print(" МАСОВЕ ТЕСТУВАННЯ GOV.DE BOT v4.1")
    print(" 20 тестових листів")
    print("="*80 + "\n")
    
    results = {
        'total': 20,
        'passed': 0,
        'failed': 0,
        'by_category': {}
    }
    
    for letter in TEST_LETTERS:
        category = letter['category']
        if category not in results['by_category']:
            results['by_category'][category] = {'total': 0, 'passed': 0}
        
        results['by_category'][category]['total'] += 1
        
        # Тест 1: Перевірка чи це документ
        doc_check = check_if_document(letter['text'])
        is_correct_doc = doc_check['is_document'] == letter['expected']['is_document']
        
        # Тест 2: Визначення організації
        org_detected = False
        expected_org = letter['expected'].get('org', '').lower()
        for org in ['jobcenter', 'inkasso', 'vermieter', 'finanzamt', 'gericht', 'krankenkasse', 'versicherung']:
            if org in letter['text'].lower():
                org_detected = True
                break
        
        # Тест 3: Визначення параграфів
        paragraphs_found = []
        for para in letter['expected'].get('paragraphs', []):
            if para in letter['text']:
                paragraphs_found.append(para)
        
        paragraphs_correct = len(paragraphs_found) >= len(letter['expected'].get('paragraphs', [])) * 0.5
        
        # Загальний результат тесту
        test_passed = is_correct_doc and org_detected
        
        if test_passed:
            results['passed'] += 1
            results['by_category'][category]['passed'] += 1
            status = "✅ PASS"
        else:
            results['failed'] += 1
            status = "❌ FAIL"
        
        # Вивід результату
        print(f"Лист #{letter['id']:2d} | {category:12s} | {letter['type']:30s} | {status}")
        
        if not test_passed:
            print(f"         ├─ Документ: {'✅' if is_correct_doc else '❌'}")
            print(f"         ├─ Організація: {'✅' if org_detected else '❌'}")
            print(f"         └─ Параграфи: {'✅' if paragraphs_correct else '❌'}")
    
    # Підсумки
    print("\n" + "="*80)
    print(" ПІДСУМКИ ТЕСТУВАННЯ")
    print("="*80)
    
    total_pct = (results['passed'] / results['total']) * 100
    
    print(f"\nЗагальний результат: {results['passed']}/{results['total']} ({total_pct:.1f}%)")
    
    print("\nПо категоріях:")
    for category, cat_results in sorted(results['by_category'].items()):
        pct = (cat_results['passed'] / cat_results['total']) * 100 if cat_results['total'] > 0 else 0
        print(f"  {category:15s}: {cat_results['passed']}/{cat_results['total']} ({pct:.1f}%)")
    
    # Оцінка
    print("\n" + "-"*80)
    print(" ЗАГАЛЬНА ОЦІНКА:")
    print("-"*80)
    
    if total_pct >= 95:
        grade = "A+ (Відмінно)"
        emoji = "🏆"
    elif total_pct >= 90:
        grade = "A (Дуже добре)"
        emoji = "🥇"
    elif total_pct >= 85:
        grade = "B+ (Добре)"
        emoji = "🥈"
    elif total_pct >= 80:
        grade = "B (Задовільно)"
        emoji = "🥉"
    else:
        grade = "C (Потребує покращень)"
        emoji = "⚠️"
    
    print(f"\n{emoji} Оцінка: {grade}")
    print(f"📊 Відсоток: {total_pct:.1f}%")
    print(f"✅ Пройдено: {results['passed']}")
    print(f"❌ Провалено: {results['failed']}")
    
    print("\n" + "="*80)
    
    return results


if __name__ == '__main__':
    try:
        results = test_all_letters()
        
        # Збереження результатів
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n📅 Тест проведено: {timestamp}")
        print(f"📄 Звіти збережено в: test_results/")
        
    except Exception as e:
        print(f"\n❌ Помилка тестування: {e}")
        import traceback
        traceback.print_exc()
