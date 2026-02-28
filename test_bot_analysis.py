#!/usr/bin/env python3
"""
Тестування аналізу тестових листів
Перевірка якості відповідей бота
"""

import sys
from pathlib import Path

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import (
    check_if_document,
    get_paragraph_description,
    create_simple_analysis,
    generate_detailed_response
)

# Тестові листи
TEST_LETTERS = {
    'jobcenter': '''
Jobcenter Berlin Mitte
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

Termin: Montag, 25.02.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12
Ansprechpartner: Frau Schmidt

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)
- Zeugnisse und Qualifikationsnachweise
- Nachweise über Bewerbungen der letzten 3 Monate

Wichtiger Hinweis:
Gemäß § 59 SGB II sind Sie verpflichtet, zu allen Einladungen des Jobcenters zu erscheinen. Bei unentschuldigtem Fehlen kann Ihre Leistung um 30% gekürzt werden (§ 31 SGB II).

Bei Krankheit müssen Sie uns unverzüglich eine ärztliche Bescheinigung vorlegen.

Mit freundlichen Grüßen

Im Auftrag

Maria Schmidt
Beraterin

Kundennummer: 123ABC456
Telefon: 030 1234 5678
E-Mail: kontakt@jobcenter-berlin-mitte.de
''',
    
    'inkasso': '''
CreditProtect Inkasso GmbH
Forderungsstraße 789
20095 Hamburg

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Hamburg, 20.02.2026

LETZTE MAHNUNG
Forderungsnummer: 2026/12345

Sehr geehrter Herr Shevchenko,

leider mussten wir feststellen, dass Sie Ihrer Zahlungsverpflichtung trotz unserer bisherigen Schreiben nicht nachgekommen sind.

Wir fordern Sie daher letztmalig auf, den offenen Betrag in Höhe von

1.250,00 EUR

bis zum 05.03.2026 auf unser Konto zu überweisen.

Bankverbindung:
IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Commerzbank Hamburg

Verwendungszweck: 2026/12345

Rechtliche Hinweise:
Gemäß § 286 BGB befinden Sie sich im Verzug. Nach § 288 BGB berechnen wir Verzugszinsen in Höhe von 5% p.a.

Sollte die Frist fruchtlos verstreichen, werden wir gerichtliche Schritte einleiten. Dies würde zusätzliche Kosten verursachen.

Bei Fragen stehen wir Ihnen unter 040 9876 5432 zur Verfügung.

Mit freundlichen Grüßen

CreditProtect Inkasso GmbH

Thomas Weber
Geschäftsführer

Telefon: 040 9876 5432
E-Mail: info@creditprotect-inkasso.de
Website: www.creditprotect-inkasso.de
IBAN: DE89 3704 0044 0532 0130 00
''',
    
    'vermieter': '''
Vermieter Hans Müller
Wohnungsstraße 12
13351 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 18.02.2026

Mieterhöhung bis zur ortsüblichen Vergleichsmiete

Sehr geehrter Herr Shevchenko,

die Miete für Ihre Wohnung in der Müllerstraße 45, Apt. 12, beträgt derzeit 450,00 EUR kalt.

Nach Überprüfung der ortsüblichen Vergleichsmiete müssen wir die Miete anpassen. Der aktuelle Mietspiegel Berlin 2026 zeigt, dass vergleichbare Wohnungen in Ihrer Lage durchschnittlich 550,00 EUR kosten.

Wir erhöhen daher die Miete wie folgt:

Aktuelle Miete: 450,00 EUR
Neue Miete: 550,00 EUR
Erhöhung: 100,00 EUR (22,2%)

Die Mieterhöhung tritt ab dem 01.05.2026 in Kraft.

Rechtliche Hinweise:
Gemäß § 558 BGB kann die Miete bis zur ortsüblichen Vergleichsmiete erhöht werden. Die Erhöhung beträgt maximal 20% innerhalb von 3 Jahren (§ 558 Abs. 3 BGB).

Sie haben ein Widerspruchsrecht bis zum 30.04.2026.

Bei Fragen stehe ich Ihnen unter 0171 234 5678 zur Verfügung.

Mit freundlichen Grüßen

Hans Müller
Vermieter

Telefon: 0171 234 5678
E-Mail: h.mueller@email.de
'''
}


def test_document_check():
    """Тест 1: Перевірка чи це офіційний документ."""
    print("\n" + "="*70)
    print("ТЕСТ 1: Перевірка чи це офіційний документ")
    print("="*70)
    
    for letter_type, text in TEST_LETTERS.items():
        result = check_if_document(text)
        print(f"\n📄 {letter_type.upper()}:")
        print(f"  is_document: {result['is_document']}")
        print(f"  official_score: {result['official_score']}")
        print(f"  is_personal: {result['is_personal']}")
        print(f"  text_length: {result['text_length']}")
        
        # Оцінка
        if result['is_document'] and result['official_score'] >= 3:
            print(f"  ✅ ПРАВИЛЬНО: Визначено як офіційний документ")
        else:
            print(f"  ❌ ПОМИЛКА: Не визначено як офіційний документ")


def test_paragraph_descriptions():
    """Тест 2: Описи параграфів."""
    print("\n" + "="*70)
    print("ТЕСТ 2: Описи параграфів")
    print("="*70)
    
    paragraphs = [
        ('§ 59 SGB II', 'uk'),
        ('§ 31 SGB II', 'uk'),
        ('BGB § 286', 'uk'),
        ('BGB § 288', 'uk'),
        ('BGB § 558', 'uk'),
        ('§ 59 SGB II', 'de'),
    ]
    
    for para, lang in paragraphs:
        desc = get_paragraph_description(para, lang)
        print(f"\n📖 {para} ({lang}):")
        print(f"  {desc}")


def test_simple_analysis():
    """Тест 3: Простий аналіз."""
    print("\n" + "="*70)
    print("ТЕСТ 3: Простий аналіз з законами та наслідками")
    print("="*70)
    
    # Симуляція law_info для Jobcenter
    law_info_jobcenter = {
        'organization': 'Jobcenter Berlin Mitte',
        'situation': 'Запрошення на співбесіду',
        'paragraphs': ['§ 59 SGB II', '§ 31 SGB II'],
        'consequences': 'Зменшення виплат на 30% при неявці'
    }
    
    # Симуляція law_info для Inkasso
    law_info_inkasso = {
        'organization': 'CreditProtect Inkasso GmbH',
        'situation': 'Вимога сплати боргу',
        'paragraphs': ['BGB § 286', 'BGB § 288'],
        'consequences': 'Судові кроки, додаткові витрати'
    }
    
    for letter_type, text in TEST_LETTERS.items():
        if letter_type == 'jobcenter':
            law_info = law_info_jobcenter
        elif letter_type == 'inkasso':
            law_info = law_info_inkasso
        else:
            continue
        
        print(f"\n📄 {letter_type.upper()}:")
        print("-"*50)
        
        analysis = create_simple_analysis(text, law_info, 'uk')
        print(analysis[:1000] + "..." if len(analysis) > 1000 else analysis)


def test_detailed_response():
    """Тест 4: Розгорнута відповідь."""
    print("\n" + "="*70)
    print("ТЕСТ 4: Розгорнута відповідь")
    print("="*70)
    
    law_info_jobcenter = {
        'organization': 'Jobcenter Berlin Mitte',
        'situation': 'Запрошення на співбесіду',
        'paragraphs': ['§ 59 SGB II', '§ 31 SGB II'],
        'consequences': 'Зменшення виплат на 30% при неявці'
    }
    
    law_info_inkasso = {
        'organization': 'CreditProtect Inkasso GmbH',
        'situation': 'Вимога сплати боргу',
        'paragraphs': ['BGB § 286', 'BGB § 288'],
        'consequences': 'Судові кроки, додаткові витрати'
    }
    
    for letter_type, text in TEST_LETTERS.items():
        if letter_type == 'jobcenter':
            law_info = law_info_jobcenter
        elif letter_type == 'inkasso':
            law_info = law_info_inkasso
        else:
            continue
        
        print(f"\n📄 {letter_type.upper()}:")
        print("-"*50)
        
        response = generate_detailed_response(text, law_info, 'uk')
        print(response[:1500] + "..." if len(response) > 1500 else response)


def evaluate_responses():
    """Оцінка якості відповідей."""
    print("\n" + "="*70)
    print("ОЦІНКА ЯКОСТІ ВІДПОВІДЕЙ")
    print("="*70)
    
    criteria = [
        ("Професійний тон", 0),
        ("Наявність законів", 0),
        ("Наявність наслідків", 0),
        ("Двомовність (UA+DE)", 0),
        ("Контактні дані", 0),
        ("Поради користувачу", 0),
    ]
    
    print("\nКритерії оцінки:")
    for criterion, _ in criteria:
        print(f"  □ {criterion}")
    
    print("\n" + "-"*70)
    print("ЗАГАЛЬНА ОЦІНКА: __ / 6")
    print("-"*70)


if __name__ == '__main__':
    print("\n" + "="*70)
    print("ТЕСТУВАННЯ БОТА v4.0")
    print("Аналіз тестових німецьких юридичних листів")
    print("="*70)
    
    try:
        test_document_check()
        test_paragraph_descriptions()
        test_simple_analysis()
        test_detailed_response()
        evaluate_responses()
        
        print("\n" + "="*70)
        print("✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ ПОМИЛКА: {e}")
        import traceback
        traceback.print_exc()
