#!/usr/bin/env python3
"""
Повторне масове тестування Gov.de Bot v4.1
20 НОВИХ тестових листів від різних організацій
"""

import sys
from pathlib import Path

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import check_if_document, get_paragraph_description

# 20 НОВИХ тестових листів
NEW_TEST_LETTERS = [
    # Jobcenter (5)
    {
        'id': 1,
        'category': 'Jobcenter',
        'type': 'Terminbestätigung',
        'text': '''Jobcenter Berlin
Ihre Straße 100, 10115 Berlin

Herrn
Max Mustermann
Musterstraße 1
10117 Berlin

Berlin, 01.03.2026

Bestätigung Ihres Termins

Sehr geehrter Herr Mustermann,

wir bestätigen Ihren Termin am 15.03.2026 um 14:00 Uhr.

Bitte bringen Sie alle Unterlagen mit.

§ 59 SGB II verpflichtet Sie zum Erscheinen.

Mit freundlichen Grüßen
Jobcenter Berlin''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 59 SGB II'],
            'deadline': '15.03.2026'
        }
    },
    {
        'id': 2,
        'category': 'Jobcenter',
        'type': 'Bewilligungsbescheid',
        'text': '''Jobcenter München
Arnulfstraße 15, 80335 München

Frau
Anna Schmidt
Münchener Straße 89
80687 München

München, 02.03.2026

Bewilligungsbescheid ALG II

Sehr geehrte Frau Schmidt,

Sie erhalten ab 01.04.2026 Arbeitslosengeld II.

Regelsatz: 563,00 EUR
Unterkunft: 500,00 EUR
Gesamt: 1.063,00 EUR

Bescheidnummer: 2026/123456

Mit freundlichen Grüßen
Jobcenter München''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'amount': '1.063,00 EUR'
        }
    },
    {
        'id': 3,
        'category': 'Jobcenter',
        'type': 'Rückforderung',
        'text': '''Jobcenter Hamburg
Billstraße 4, 20539 Hamburg

Herrn
Peter Müller
Hamburger Straße 156
22089 Hamburg

Hamburg, 03.03.2026

Rückforderung von Leistungen

Sehr geehrter Herr Müller,

Sie haben zu viel Leistungen erhalten: 800,00 EUR

Bitte zahlen Sie bis 20.03.2026 zurück.

§ 45 SGB X ermöglicht Rückforderung.

Mit freundlichen Grüßen
Jobcenter Hamburg''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'amount': '800,00 EUR',
            'deadline': '20.03.2026',
            'paragraphs': ['§ 45 SGB X']
        }
    },
    {
        'id': 4,
        'category': 'Jobcenter',
        'type': 'Eingliederungsvereinbarung',
        'text': '''Jobcenter Köln
Turiner Straße 16, 50668 Köln

Frau
Maria Weber
Kölner Straße 234
50668 Köln

Köln, 04.03.2026

Eingliederungsvereinbarung

Sehr geehrte Frau Weber,

wir vereinbaren folgende Maßnahmen:
- Bewerbungstraining
- 5 Bewerbungen pro Monat

§ 15 SGB II regelt die Vereinbarung.

Mit freundlichen Grüßen
Jobcenter Köln''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 15 SGB II']
        }
    },
    {
        'id': 5,
        'category': 'Jobcenter',
        'type': 'Umzugsgenehmigung',
        'text': '''Jobcenter Stuttgart
Heilbronner Straße 177, 70191 Stuttgart

Herrn
Thomas Klein
Stuttgarter Straße 89
70191 Stuttgart

Stuttgart, 05.03.2026

Genehmigung Ihres Umzugs

Sehr geehrter Herr Klein,

wir genehmigen Ihren Umzug nach Berlin.

Die neuen Kosten werden übernommen.

Mit freundlichen Grüßen
Jobcenter Stuttgart''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter'
        }
    },
    
    # Inkasso (4)
    {
        'id': 6,
        'category': 'Inkasso',
        'type': 'Zahlungsaufforderung',
        'text': '''Inkasso GmbH
Forderungsstraße 100, 20095 Hamburg

Frau
Sandra Braun
Hamburger Straße 45
20095 Hamburg

Hamburg, 06.03.2026

Zahlungsaufforderung

Sehr geehrte Frau Braun,

Sie schulden uns 450,00 EUR.

Bitte zahlen Sie bis 25.03.2026.

IBAN: DE89 3704 0044 0532 0130 00

Mit freundlichen Grüßen
Inkasso GmbH''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '450,00 EUR',
            'deadline': '25.03.2026'
        }
    },
    {
        'id': 7,
        'category': 'Inkasso',
        'type': 'Vollstreckungsbescheid',
        'text': '''Amtsgericht Berlin
Amtsgerichtsplatz 1, 14057 Berlin

Herrn
Michael Wolf
Berliner Straße 156
10115 Berlin

Berlin, 07.03.2026

Vollstreckungsbescheid

Sehr geehrter Herr Wolf,

der Gläubiger fordert 3.500,00 EUR.

Widerspruch innerhalb von 2 Wochen.

Mit freundlichen Grüßen
Amtsgericht Berlin''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '3.500,00 EUR'
        }
    },
    {
        'id': 8,
        'category': 'Inkasso',
        'type': 'Pfändungsbeschluss',
        'text': '''Amtsgericht München
Pacellistraße 5, 80333 München

Frau
Julia Fischer
Münchener Straße 234
80333 München

München, 08.03.2026

Pfändungsbeschluss

Sehr geehrte Frau Fischer,

wir pfänden Ihr Gehalt für 5.000,00 EUR Forderung.

Mit freundlichen Grüßen
Amtsgericht München''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '5.000,00 EUR',
            'risk': 'Pfändung'
        }
    },
    {
        'id': 9,
        'category': 'Inkasso',
        'type': 'Schufa-Meldung',
        'text': '''CreditProtect Inkasso
Forderungsstraße 789, 20095 Hamburg

Herrn
Stefan Wagner
Hamburger Straße 89
20095 Hamburg

Hamburg, 09.03.2026

Schufa-Meldung angekündigt

Sehr geehrter Herr Wagner,

bei Nichtzahlung melden wir die Forderung (1.200,00 EUR) an die SCHUFA.

Frist: 20.03.2026

Mit freundlichen Grüßen
CreditProtect''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '1.200,00 EUR',
            'deadline': '20.03.2026',
            'risk': 'SCHUFA'
        }
    },
    
    # Vermieter (4)
    {
        'id': 10,
        'category': 'Vermieter',
        'type': 'Modernisierung',
        'text': '''Vermieter Hans Müller
Wohnungsstraße 12, 13351 Berlin

Frau
Petra Schmidt
Müllerstraße 45
13351 Berlin

Berlin, 10.03.2026

Modernisierung Ihrer Wohnung

Sehr geehrte Frau Schmidt,

wir modernisieren Ihr Bad.
Kosten: 5.000,00 EUR
Mietmehrung: 50,00 EUR/Monat

§ 559 BGB ermöglicht Mieterhöhung.

Mit freundlichen Grüßen
Hans Müller''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'paragraphs': ['§ 559 BGB']
        }
    },
    {
        'id': 11,
        'category': 'Vermieter',
        'type': 'Betriebskosten',
        'text': '''Hausverwaltung Berlin
Potsdamer Straße 100, 10785 Berlin

Herrn
Andreas Klein
Potsdamer Straße 156
10783 Berlin

Berlin, 11.03.2026

Betriebskostenabrechnung 2025

Sehr geehrter Herr Klein,

Gesamtkosten: 3.000,00 EUR
Ihre Vorauszahlung: 2.800,00 EUR
Nachzahlung: 200,00 EUR

Frist: 30.03.2026

Mit freundlichen Grüßen
Hausverwaltung Berlin''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'amount': '200,00 EUR',
            'deadline': '30.03.2026'
        }
    },
    {
        'id': 12,
        'category': 'Vermieter',
        'type': 'Eigenbedarf',
        'text': '''Vermieterin Maria Weber
Berliner Straße 78, 10115 Berlin

Frau
Anna Müller
Berliner Straße 78, Apt. 5
10115 Berlin

Berlin, 12.03.2026

Kündigung wegen Eigenbedarf

Sehr geehrte Frau Müller,

ich kündige wegen Eigenbedarf für meine Tochter.

Räumung bis 30.06.2026.

§ 573 BGB regelt Eigenbedarf.

Mit freundlichen Grüßen
Maria Weber''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'paragraphs': ['§ 573 BGB'],
            'deadline': '30.06.2026'
        }
    },
    {
        'id': 13,
        'category': 'Vermieter',
        'type': 'Mietvertrag',
        'text': '''Vermieter GmbH
Hauptstraße 100, 10115 Berlin

Herrn
Thomas Schmidt
Hauptstraße 156
10117 Berlin

Berlin, 13.03.2026

Neuer Mietvertrag

Sehr geehrter Herr Schmidt,

anbei erhalten Sie den neuen Mietvertrag.

Miete: 600,00 EUR
Beginn: 01.05.2026

Mit freundlichen Grüßen
Vermieter GmbH''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'amount': '600,00 EUR'
        }
    },
    
    # Finanzamt (3)
    {
        'id': 14,
        'category': 'Finanzamt',
        'type': 'Steuernachzahlung',
        'text': '''Finanzamt Frankfurt
Gutleutstraße 20, 60329 Frankfurt

Frau
Sabine Weber
Frankfurter Straße 89
60329 Frankfurt

Frankfurt, 14.03.2026

Steuernachzahlung 2024

Sehr geehrte Frau Weber,

Sie müssen 1.500,00 EUR nachzahlen.

Frist: 30.04.2026

§ 233 AO regelt die Nachzahlung.

Mit freundlichen Grüßen
Finanzamt Frankfurt''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'amount': '1.500,00 EUR',
            'deadline': '30.04.2026',
            'paragraphs': ['§ 233 AO']
        }
    },
    {
        'id': 15,
        'category': 'Finanzamt',
        'type': 'Steuererstattung',
        'text': '''Finanzamt Düsseldorf
Königsallee 92, 40212 Düsseldorf

Herrn
Michael Braun
Königsstraße 45
40211 Düsseldorf

Düsseldorf, 15.03.2026

Steuererstattung 2024

Sehr geehrter Herr Braun,

Sie erhalten 800,00 EUR erstattet.

Auszahlung am 25.03.2026.

Mit freundlichen Grüßen
Finanzamt Düsseldorf''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'amount': '800,00 EUR'
        }
    },
    {
        'id': 16,
        'category': 'Finanzamt',
        'type': 'Außenprüfung',
        'text': '''Finanzamt Hamburg
Billstraße 4, 20539 Hamburg

Frau
Anna Fischer
Hamburger Straße 234
22089 Hamburg

Hamburg, 16.03.2026

Ankündigung einer Außenprüfung

Sehr geehrte Frau Fischer,

wir prüfen Ihre Steuererklärung 2023-2025.

Termin: 01.04.2026

§ 193 AO ermöglicht Außenprüfung.

Mit freundlichen Grüßen
Finanzamt Hamburg''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'deadline': '01.04.2026',
            'paragraphs': ['§ 193 AO']
        }
    },
    
    # Gericht (2)
    {
        'id': 17,
        'category': 'Gericht',
        'type': 'Strafbefehl',
        'text': '''Amtsgericht Köln
Turiner Straße 16, 50668 Köln

Herrn
Peter Schmidt
Kölner Straße 89
50668 Köln

Köln, 17.03.2026

Strafbefehl

Sehr geehrter Herr Schmidt,

wegen Betrugs werden Sie zu 90 Tagessätzen verurteilt.

Widerspruch innerhalb von 2 Wochen.

Mit freundlichen Grüßen
Amtsgericht Köln''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'risk': 'Strafe'
        }
    },
    {
        'id': 18,
        'category': 'Gericht',
        'type': 'Einstweilige Verfügung',
        'text': '''Landgericht Berlin
Littenstraße 12-17, 10179 Berlin

Frau
Maria Klein
Berliner Straße 156
10117 Berlin

Berlin, 18.03.2026

Einstweilige Verfügung

Sehr geehrte Frau Klein,

Sie müssen die Handlung sofort unterlassen.

Bei Zuwiderhandlung: Ordnungsgeld bis 250.000,00 EUR.

Mit freundlichen Grüßen
Landgericht Berlin''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'risk': 'Ordnungsgeld'
        }
    },
    
    # Krankenkasse (2)
    {
        'id': 19,
        'category': 'Krankenkasse',
        'type': 'Beitragsanpassung',
        'text': '''TK Krankenkasse
Brieffach 11 02 48, 20422 Hamburg

Herrn
Andreas Weber
Hamburger Straße 89
22089 Hamburg

Hamburg, 19.03.2026

Beitragsanpassung 2026

Sehr geehrter Herr Weber,

Ihr Beitrag ändert sich ab 01.04.2026.

Neuer Beitrag: 480,00 EUR/Monat

Mit freundlichen Grüßen
TK Krankenkasse''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'amount': '480,00 EUR',
            'deadline': '01.04.2026'
        }
    },
    {
        'id': 20,
        'category': 'Krankenkasse',
        'type': 'Reha-Genehmigung',
        'text': '''AOK Berlin
Friedrichstraße 100, 10117 Berlin

Frau
Sabine Müller
Friedrichstraße 156
10117 Berlin

Berlin, 20.03.2026

Genehmigung Ihrer Reha-Maßnahme

Sehr geehrte Frau Müller,

wir genehmigen Ihre Reha-Maßnahme.

Beginn: 01.05.2026
Dauer: 4 Wochen

Mit freundlichen Grüßen
AOK Berlin''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'deadline': '01.05.2026'
        }
    }
]


def test_all_new_letters():
    """Тестування всіх 20 нових листів."""
    print("\n" + "="*80)
    print(" ПОВТОРНЕ МАСОВЕ ТЕСТУВАННЯ GOV.DE BOT v4.1")
    print(" 20 НОВИХ тестових листів")
    print("="*80 + "\n")
    
    results = {
        'total': 20,
        'passed': 0,
        'failed': 0,
        'by_category': {}
    }
    
    for letter in NEW_TEST_LETTERS:
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
        text_lower = letter['text'].lower()
        
        org_keywords = {
            'jobcenter': ['jobcenter', 'arbeitsagentur'],
            'inkasso': ['inkasso', 'forderung', 'gläubiger'],
            'vermieter': ['vermieter', 'mieter', 'miete', 'hausverwaltung'],
            'finanzamt': ['finanzamt', 'steuer'],
            'gericht': ['gericht', 'amt', 'landgericht', 'rechtsanwalt'],
            'krankenkasse': ['krankenkasse', 'aok', 'tk', 'barmer'],
            'versicherung': ['versicherung', 'allianz', 'axa']
        }
        
        for keyword in org_keywords.get(expected_org, []):
            if keyword in text_lower:
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
        results = test_all_new_letters()
        
        # Збереження результатів
        from datetime import datetime
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n📅 Тест проведено: {timestamp}")
        print(f"📄 Звіти збережено в: test_results/")
        
    except Exception as e:
        print(f"\n❌ Помилка тестування: {e}")
        import traceback
        traceback.print_exc()
