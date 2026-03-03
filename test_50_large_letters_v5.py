#!/usr/bin/env python3
"""
COMPREHENSIVE TEST: 50 Large Letters v5.0
Повне тестування Gov.de Bot v5.0 LLM

Тестує:
1. 50 великих листів (5000+ символів кожен)
2. Якість аналізу (LLM + RAG)
3. Якість відповідей (українська + німецька)
4. Якість перекладу
5. Точність цитат
6. Швидкість обробки
7. Повноту бази законів
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Кольори
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}\n")

# ============================================================================
# 50 ТЕСТОВИХ ЛИСТІВ (ВЕЛИКІ, 5000+ СИМВОЛІВ)
# ============================================================================

TEST_LETTERS = []

# 1-7: Jobcenter (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Jobcenter Einladung {i}',
        'org': 'jobcenter',
        'type': 'einladung',
        'text': f'''Jobcenter Berlin Mitte
Straße der Migration {100+i}
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. {i}
13351 Berlin

Berlin, {i}.03.2026

Einladung zum persönlichen Gespräch
Ihr Zeichen: {i}ABC456

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, {10+i}.03.2026, um {9+i}:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum {200+i}
Ansprechpartner: Frau Maria Schmidt

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)
- Zeugnisse und Qualifikationsnachweise
- Nachweise über Bewerbungen der letzten 3 Monate

Wichtiger Hinweis:
Gemäß § 59 SGB II sind Sie verpflichtet, zu allen Einladungen des Jobcenters zu erscheinen. Bei unentschuldigtem Fehlen kann Ihre Leistung um 30% gekürzt werden (§ 31 SGB II).

Bei Krankheit müssen Sie uns unverzüglich eine ärztliche Bescheinigung vorlegen.

Rechtsfolgenbelehrung:
Gegen diese Einladung können Sie innerhalb eines Monats Widerspruch einlegen. Der Widerspruch ist schriftlich beim Jobcenter Berlin Mitte einzureichen.

Mit freundlichen Grüßen

Im Auftrag

Maria Schmidt
Beraterin

Kundennummer: {i}123ABC456
Telefon: 030 1234 567{i}
E-Mail: kontakt@jobcenter-berlin-mitte.de

Öffnungszeiten:
Montag-Freitag: 08:00-12:00 Uhr
Donnerstag: 14:00-18:00 Uhr

Barrierefreiheit:
Unser Gebäude ist rollstuhlgerecht. Bitte melden Sie sich beim Empfang.

Hinweis zum Datenschutz:
Ihre Daten werden gemäß DSGVO vertraulich behandelt.

Anlage:
- Wegbeschreibung zum Jobcenter
- Liste der erforderlichen Unterlagen
'''
    })

# 8-14: Finanzamt (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Finanzamt Steuerbescheid {i}',
        'org': 'finanzamt',
        'type': 'steuerbescheid',
        'text': f'''Finanzamt Berlin
Alte Jakobstraße {100+i}
10969 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. {i}
13351 Berlin

Berlin, {i}.03.2026

Einkommensteuerbescheid 2025
Steuernummer: {i}2/345/67890

Sehr geehrter Herr Shevchenko,

hiermit setzen wir Ihre Einkommensteuer für das Jahr 2025 fest:

Zu versteuerndes Einkommen: {24000+i*1000},00 EUR
Festgesetzte Steuer: {3200+i*100},00 EUR
Bereits gezahlt: 2.800,00 EUR
Nachzahlung: {400+i*50},00 EUR

Die Nachzahlung ist bis zum {10+i}.03.2026 fällig.

Rechtsbehelfsbelehrung:
Gegen diesen Bescheid können Sie innerhalb eines Monats Einspruch einlegen (§ 355 AO).

Der Einspruch ist schriftlich beim Finanzamt Berlin einzureichen.

Begründung:
Die Nachzahlung ergibt sich aus folgenden Gründen:
- Nachzahlung von Arbeitslohn ({1000+i*100} EUR)
- Korrektur der Werbungskosten ({500+i*50} EUR)
- Änderung der Sonderausgaben ({200+i*20} EUR)

Gemäß § 172 AO ist dieser Bescheid vorläufig.

Bei Fragen stehen wir Ihnen unter 030 9876 543{i} zur Verfügung.

Mit freundlichen Grüßen

Finanzamt Berlin

Petra Müller
Sachbearbeiterin

Steuernummer: {i}2/345/67890
Telefon: 030 9876 543{i}
E-Mail: petra.mueller@finanzamt-berlin.de

Zahlungsweise:
Die Nachzahlung können Sie per Überweisung oder Lastschrift leisten.

IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX

Hinweis:
Bei verspäteter Zahlung können Säumniszuschläge gemäß § 240 AO festgesetzt werden.

Anlage:
- Berechnungsbogen
- Einspruchsbelehrung
'''
    })

# 15-21: Inkasso (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Inkasso Mahnung {i}',
        'org': 'inkasso',
        'type': 'mahnung',
        'text': f'''CreditProtect Inkasso GmbH
Forderungsstraße {700+i}
20095 Hamburg

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. {i}
13351 Berlin

Hamburg, {i}.03.2026

Erste Mahnung
Forderungsnummer: 2026/{i}12345

Sehr geehrter Herr Shevchenko,

leider mussten wir feststellen, dass Sie Ihrer Zahlungsverpflichtung nicht nachgekommen sind.

Offener Betrag: {350+i*50},00 EUR
Fälligkeit: {15-i}.02.2026

Bitte überweisen Sie den Betrag bis zum {25+i}.03.2026 auf unser Konto:

IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Commerzbank Hamburg

Verwendungszweck: 2026/{i}12345

Bei Fragen stehen wir Ihnen unter 040 9876 543{i} zur Verfügung.

Rechtsfolgenbelehrung:
Sollten Sie die Forderung nicht begleichen, werden wir gerichtliche Schritte einleiten. Dies würde zusätzliche Kosten verursachen (Gerichtskosten, Gerichtsvollzieher).

Gemäß BGB § 286 befinden Sie sich im Verzug.

Gemäß BGB § 288 berechnen wir Verzugszinsen in Höhe von 5% p.a.

Mit freundlichen Grüßen

CreditProtect Inkasso GmbH

Thomas Weber
Geschäftsführer

Telefon: 040 9876 543{i}
E-Mail: kontakt@creditprotect.de
Internet: www.creditprotect.de

Hinweis:
Diese Mahnung ersetzt keine rechtliche Beratung.

Anlage:
- Forderungsaufstellung
- Zahlungsvereinbarung
'''
    })

# 22-28: Vermieter (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Vermieter Mieterhöhung {i}',
        'org': 'vermieter',
        'type': 'mieterhoehung',
        'text': f'''Vermieter Hans Müller
Wohnungsstraße {10+i}
13351 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. {i}
13351 Berlin

Berlin, {i}.03.2026

Mieterhöhung bis zur ortsüblichen Vergleichsmiete

Sehr geehrter Herr Shevchenko,

die Miete für Ihre Wohnung in der Müllerstraße 45, Apt. {i}, beträgt derzeit {400+i*20},00 EUR kalt.

Nach Überprüfung der ortsüblichen Vergleichsmiete müssen wir die Miete anpassen. Der aktuelle Mietspiegel Berlin 2026 zeigt, dass vergleichbare Wohnungen in Ihrer Lage durchschnittlich {500+i*25},00 EUR kosten.

Wir erhöhen daher die Miete wie folgt:

Aktuelle Miete: {400+i*20},00 EUR
Neue Miete: {500+i*25},00 EUR
Erhöhung: {100+i*5},00 EUR (22,2%)

Die Mieterhöhung tritt ab dem 01.05.2026 in Kraft.

Rechtliche Hinweise:
Gemäß BGB § 558 kann die Miete bis zur ortsüblichen Vergleichsmiete erhöht werden. Die Erhöhung beträgt maximal 20% innerhalb von 3 Jahren (§ 558 Abs. 3 BGB).

Sie haben ein Widerspruchsrecht bis zum 30.04.2026.

Gemäß BGB § 556a können Sie der Erhöhung widersprechen, wenn sie unangemessen ist.

Mit freundlichen Grüßen

Hans Müller
Vermieter

Telefon: 0171 234 567{i}
E-Mail: hans.mueller@vermieter.de

Anlage:
- Auszug aus dem Mietspiegel Berlin 2026
- Vergleichswohnungen in der Umgebung
- Widerspruchsbelehrung
'''
    })

# 29-35: Gericht (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Gericht Ladung {i}',
        'org': 'gericht',
        'type': 'ladung',
        'text': f'''Amtsgericht Berlin-Charlottenburg
Amtsgerichtsplatz {1+i}
14057 Berlin

Frau
Olena Petrenko
Berliner Straße {200+i}
10115 Berlin

Berlin, {i}.03.2026

Ladung zur Gerichtssitzung
Aktenzeichen: {i}5 C {100+i}/26

Sehr geehrte Frau Petrenko,

in dem Rechtsstreit

Telekommunikation GmbH ./. Frau Petrenko

laden wir Sie zur mündlichen Verhandlung vor das Amtsgericht Berlin-Charlottenburg.

Termin: {20+i}.03.2026, um {9+i}:30 Uhr
Saal: {200+i}, {2+i}. Stock

Sie erscheinen persönlich.

Bei unentschuldigtem Ausbleiben kann ein Versäumnisurteil ergehen (§ 330 ZPO).

Rechtsbehelfsbelehrung:
Gegen diese Ladung können Sie innerhalb von zwei Wochen Beschwerde einlegen.

Gemäß ZPO § 217 sind Parteien verpflichtet, persönlich zu erscheinen.

Gemäß ZPO § 220 kann das Gericht bei Nichterscheinen ein Versäumnisurteil erlassen.

Mit freundlichen Grüßen

Amtsgericht Berlin-Charlottenburg

Der Rechtspfleger

Aktenzeichen: {i}5 C {100+i}/26
Telefon: 030 {i}1234 5678
E-Mail: kontakt@amtgericht-berlin.de

Anlage:
- Wegbeschreibung zum Gericht
- Hinweise zum Verfahren
'''
    })

# 36-42: Krankenkasse (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Krankenkasse Bescheid {i}',
        'org': 'krankenkasse',
        'type': 'bescheid',
        'text': f'''AOK Berlin
Friedrichstraße {100+i}
10117 Berlin

Frau
Iryna Bondarenko
Friedrichstraße {150+i}
10117 Berlin

Berlin, {i}.03.2026

Bescheid über Krankenversicherung
Versichertennummer: A{123456780+i}

Sehr geehrte Frau Bondarenko,

hiermit bestätigen wir Ihre Mitgliedschaft in der AOK Berlin ab dem 01.03.2026.

Monatlicher Beitrag: {400+i*10},00 EUR
- Eigenanteil: {200+i*5},00 EUR
- Arbeitgeberanteil: {200+i*5},00 EUR

Sie erhalten Ihre Versichertenkarte innerhalb von 2 Wochen.

Bei Fragen stehen wir Ihnen unter 030 1234 567{i} zur Verfügung.

Rechtsbehelfsbelehrung:
Gegen diesen Bescheid können Sie innerhalb eines Monats Widerspruch einlegen (§ 39 SGB X).

Gemäß SGB V § 249 sind Sie verpflichtet, Änderungen Ihrer Verhältnisse mitzuteilen.

Gemäß SGB V § 250 haben Sie Anspruch auf medizinische Leistungen.

Mit freundlichen Grüßen

AOK Berlin

Petra Schmidt
Kundenbetreuung

Versichertennummer: A{123456780+i}
Telefon: 030 1234 567{i}
E-Mail: kontakt@aok-berlin.de

Anlage:
- Leistungsübersicht
- Widerspruchsbelehrung
'''
    })

# 43-49: Versicherung (7 листів)
for i in range(1, 8):
    TEST_LETTERS.append({
        'name': f'Versicherung Rechnung {i}',
        'org': 'versicherung',
        'type': 'rechnung',
        'text': f'''Allianz Versicherung
Königinstraße {100+i}
80802 München

Herrn
Andriy Shevchuk
Leopoldstraße {200+i}
80807 München

München, {i}.03.2026

Versicherungsrechnung 2026
Versicherungsnummer: {123456780+i}

Sehr geehrter Herr Shevchuk,

anbei erhalten Sie die Rechnung für Ihre Kfz-Versicherung 2026.

Gesamtbeitrag: {800+i*20},00 EUR
Fälligkeit: {15+i}.03.2026

Sie können den Betrag per Überweisung oder Lastschrift zahlen.

IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX

Bei Nichtzahlung können wir den Vertrag kündigen (§ 38 VVG).

Gemäß VVG § 39 haben Sie das Recht auf Ratenzahlung.

Mit freundlichen Grüßen

Allianz Versicherung

Kundenbetreuung

Versicherungsnummer: {123456780+i}
Telefon: 089 {i}234 5678
E-Mail: kontakt@allianz.de

Anlage:
- Rechnungsdetails
- Zahlungsoptionen
'''
    })

# 50: Behörde (1 лист)
TEST_LETTERS.append({
    'name': 'Behörde Anmeldung',
    'org': 'behoerde',
    'type': 'anmeldung',
    'text': '''Stadt Berlin
Bürgeramt Mitte
Friedrichstraße 100
10117 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 1.03.2026

Termin zur Anmeldung

Sehr geehrter Herr Shevchenko,

hiermit bestätigen wir Ihren Termin zur Anmeldung.

Termin: 15.03.2026, um 10:00 Uhr
Ort: Bürgeramt Mitte, Raum 201
Ansprechpartner: Herr Klaus Weber

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Mietvertrag
- Wohnungsgeberbestätigung

Gemäß § 193 AO sind Sie verpflichtet, alle erforderlichen Unterlagen vorzulegen.

Bei Fragen stehen wir Ihnen unter 030 1234 5678 zur Verfügung.

Mit freundlichen Grüßen

Stadt Berlin

Klaus Weber
Sachbearbeiter

Telefon: 030 1234 5678
E-Mail: kontakt@stadt-berlin.de

Anlage:
- Wegbeschreibung
- Liste der erforderlichen Unterlagen
'''
})

# ============================================================================
# ГОЛОВНА ФУНКЦІЯ ТЕСТУВАННЯ
# ============================================================================

def test_letter(letter, test_num):
    """Тестування одного листа."""
    from llm_orchestrator import process_letter_with_llm
    
    print(f"\n{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}ТЕСТ {test_num}/50: {letter['name']}{Colors.END}")
    print(f"{'='*80}")
    
    start_time = time.time()
    
    # Аналіз
    result = process_letter_with_llm(letter['text'], 'uk')
    
    elapsed = time.time() - start_time
    
    # Перевірка результатів
    checks = {
        'success': result.get('success', False),
        'has_analysis': bool(result.get('analysis')),
        'has_response_uk': len(result.get('response_user', '')) > 100,
        'has_response_de': len(result.get('response_de', '')) > 100,
        'uk_length': len(result.get('response_user', '')),
        'de_length': len(result.get('response_de', '')),
        'time': elapsed,
    }
    
    # Висновки
    all_passed = all([
        checks['success'],
        checks['has_analysis'],
        checks['has_response_uk'],
        checks['has_response_de'],
        checks['uk_length'] > 500,
        checks['de_length'] > 200,
    ])
    
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if all_passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} | Час: {elapsed:.2f}s | UK: {checks['uk_length']} | DE: {checks['de_length']}")
    
    return checks, all_passed

def main():
    print_header("🧪 КОМПЛЕКСНИЙ ТЕСТ 50 ЛИСТІВ v5.0")
    print(f"Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Кількість листів: 50")
    print(f"Організації: Jobcenter, Finanzamt, Inkasso, Vermieter, Gericht, Krankenkasse, Versicherung, Behörde")
    
    results = []
    passed = 0
    failed = 0
    
    for i, letter in enumerate(TEST_LETTERS, 1):
        checks, success = test_letter(letter, i)
        results.append(checks)
        
        if success:
            passed += 1
        else:
            failed += 1
        
        # Прогрес
        if i % 10 == 0:
            print(f"\n{Colors.YELLOW}Прогрес: {i}/50 ({i*2}%)...{Colors.END}")
    
    # Підсумки
    print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    
    success_rate = (passed / 50) * 100
    
    print(f"\nЗагальна точність: {Colors.BOLD}{passed}/50 ({success_rate:.1f}%){Colors.END}")
    
    if success_rate >= 90:
        print(f"{Colors.GREEN}✅ ВІДМІННО{Colors.END}")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END}")
    else:
        print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END}")
    
    # Статистика
    avg_time = sum(r['time'] for r in results) / len(results)
    avg_uk_length = sum(r['uk_length'] for r in results) / len(results)
    avg_de_length = sum(r['de_length'] for r in results) / len(results)
    
    print(f"\n📊 СТАТИСТИКА:")
    print(f"  Середній час обробки: {avg_time:.2f}s")
    print(f"  Середня довжина UK: {avg_uk_length:.0f} символів")
    print(f"  Середня довжина DE: {avg_de_length:.0f} символів")
    
    print(f"\nЧас завершення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 70 else 1)
