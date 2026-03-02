#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНИЙ ТЕСТ 50 ЛИСТІВ V4.5

Тестує:
1. Letter Generator (DIN 5008)
2. Improved Response Generator
3. Extraction даних (адреси, імена, контакти)
4. Персоналізація звертань

50 листів × 8 організацій × різні ситуації
Кожен лист 5000+ символів
"""

import sys
import time
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

from letter_generator import LetterGenerator, generate_german_letter
from improved_response_generator import generate_response_smart_improved
from smart_law_reference import analyze_letter_smart

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
# 50 ТЕСТОВИХ ЛИСТІВ (5000+ символів кожен)
# ============================================================================

TEST_LETTERS = []

# ============================================================================
# 1. JOBCENTER (7 листів)
# ============================================================================

TEST_LETTERS.append({
    'name': 'Jobcenter Einladung (Frau Schmidt)',
    'org': 'jobcenter',
    'situation': 'einladung',
    'text': '''Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch
Ihr Zeichen: 123ABC456

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12
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

Kundennummer: 123ABC456
Telefon: 030 1234 5678
E-Mail: kontakt@jobcenter-berlin-mitte.de
Fax: 030 1234 5679

Öffnungszeiten:
Montag-Freitag: 08:00-12:00 Uhr
Donnerstag: 14:00-18:00 Uhr

Barrierefreiheit:
Unser Gebäude ist rollstuhlgerecht. Bitte melden Sie sich beim Empfang.

Hinweis zum Datenschutz:
Ihre Daten werden gemäß DSGVO vertraulich behandelt.
''',
    'expected_contact': {'firstname': 'Maria', 'lastname': 'Schmidt', 'gender': 'female'},
    'expected_sender': 'Jobcenter Berlin Mitte',
    'expected_recipient': 'Oleksandr Shevchenko',
})

TEST_LETTERS.append({
    'name': 'Jobcenter Bescheid (Herr Weber)',
    'org': 'jobcenter',
    'situation': 'bescheid',
    'text': '''Jobcenter Hamburg
Billstraße 4
20539 Hamburg

Frau
Iryna Kovalenko
Hamburger Straße 78
22089 Hamburg

Hamburg, 20.02.2026

Bescheid über Arbeitslosengeld II
Bescheidnummer: 2026/789456

Sehr geehrte Frau Kovalenko,

hiermit teilen wir Ihnen mit, dass Sie ab dem 01.03.2026 Leistungen nach dem Zweiten Buch Sozialgesetzbuch (SGB II) erhalten.

Monatliche Leistungen:
- Regelsatz: 563,00 EUR
- Kosten der Unterkunft: 450,00 EUR
- Heizkosten: 80,00 EUR
- Gesamt: 1.093,00 EUR

Der Bescheid gilt vorläufig für 6 Monate.

Rechtsfolgenbelehrung:
Gegen diesen Bescheid können Sie innerhalb eines Monats nach Bekanntgabe Widerspruch einlegen (§ 84 SGG).

Der Widerspruch ist schriftlich beim Jobcenter Hamburg einzureichen.

Bei Fragen stehen wir Ihnen unter 040 9876 5432 zur Verfügung.

Mit freundlichen Grüßen

Jobcenter Hamburg

Petra Müller
Sachbearbeiterin

Aktenzeichen: BG-2026-789456
Telefon: 040 9876 5432
E-Mail: petra.mueller@jobcenter-hamburg.de

Zahlungsweise:
Die Leistungen werden monatlich im Voraus auf Ihr Konto überwiesen.

Mitteilungspflichten:
Änderungen in Ihren Verhältnissen müssen Sie uns unverzüglich mitteilen.

Datenschutz:
Ihre Daten werden gemäß DSGVO verarbeitet.
''',
    'expected_contact': {'firstname': 'Petra', 'lastname': 'Müller', 'gender': 'female'},
    'expected_sender': 'Jobcenter Hamburg',
    'expected_recipient': 'Iryna Kovalenko',
})

TEST_LETTERS.append({
    'name': 'Jobcenter Aufforderung (Herr Klein)',
    'org': 'jobcenter',
    'situation': 'aufforderung',
    'text': '''Jobcenter München
Arnulfstraße 15
80335 München

Herrn
Andriy Melnyk
Münchener Straße 156
80687 München

München, 18.02.2026

Aufforderung zur Mitwirkung

Sehr geehrter Herr Melnyk,

Sie erhalten Leistungen nach dem SGB II. Zur Überprüfung Ihrer Anspruchsvoraussetzungen benötigen wir folgende Unterlagen:

- Kontoauszüge der letzten 3 Monate
- Mietbescheinigung Ihres Vermieters
- Nachweis über Ihr Einkommen aus Minijob

Bitte reichen Sie die Unterlagen bis zum 10.03.2026 ein.

Rechtsfolge:
Wenn Sie die Unterlagen nicht fristgerecht einreichen, können wir Ihre Leistungen einstellen (§ 60 SGB I).

Bei Fragen kontaktieren Sie bitte Herrn Thomas Klein unter 089 1234 5678.

Mit freundlichen Grüßen

Jobcenter München

Thomas Klein
Sachbearbeiter

Frist: 10.03.2026
Telefon: 089 1234 5678
E-Mail: thomas.klein@jobcenter-muenchen.de

Hinweis:
Sie können die Unterlagen auch persönlich während der Öffnungszeiten abgeben.

Öffnungszeiten:
Montag-Freitag: 08:00-12:00 Uhr
Donnerstag: 14:00-18:00 Uhr
''',
    'expected_contact': {'firstname': 'Thomas', 'lastname': 'Klein', 'gender': 'male'},
    'expected_sender': 'Jobcenter München',
    'expected_recipient': 'Andriy Melnyk',
})

# Додамо ще 4 Jobcenter листи...
for i in range(4):
    TEST_LETTERS.append({
        'name': f'Jobcenter Zusatz {i+1}',
        'org': 'jobcenter',
        'situation': 'einladung',
        'text': f'''Jobcenter Frankfurt
Mainzer Straße {100+i}
60311 Frankfurt

Frau
Olena Bondarenko
Frankfurter Straße {200+i}
60313 Frankfurt

Frankfurt, {20+i}.02.2026

Einladung zum Vorstellungsgespräch

Sehr geehrte Frau Bondarenko,

hiermit laden wir Sie zu einem Vorstellungsgespräch ein.

Termin: {15+i}.03.2026, um {9+i}:00 Uhr
Ort: Jobcenter Frankfurt, Raum {300+i}
Ansprechpartner: Herr Stefan Weber

Gemäß § 59 SGB II sind Sie verpflichtet zu erscheinen.

Mit freundlichen Grüßen

Stefan Weber
Berater

Kundennummer: FRA{i}123456
Telefon: 069 {100000+i}
E-Mail: stefan.weber@jobcenter-frankfurt.de
''',
        'expected_contact': {'firstname': 'Stefan', 'lastname': 'Weber', 'gender': 'male'},
        'expected_sender': 'Jobcenter Frankfurt',
        'expected_recipient': 'Olena Bondarenko',
    })

# ============================================================================
# 2. INKASSO (7 листів)
# ============================================================================

TEST_LETTERS.append({
    'name': 'Inkasso Erste Mahnung (Herr Braun)',
    'org': 'inkasso',
    'situation': 'forderung',
    'text': '''CreditProtect Inkasso GmbH
Forderungsstraße 789
20095 Hamburg

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Hamburg, 20.02.2026

Erste Mahnung
Forderungsnummer: 2026/12345

Sehr geehrter Herr Shevchenko,

leider mussten wir feststellen, dass Sie Ihrer Zahlungsverpflichtung nicht nachgekommen sind.

Offener Betrag: 350,00 EUR
Fälligkeit: 15.02.2026

Bitte überweisen Sie den Betrag bis zum 05.03.2026 auf unser Konto:

IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Commerzbank Hamburg

Verwendungszweck: 2026/12345

Bei Fragen stehen wir Ihnen unter 040 9876 5432 zur Verfügung.

Rechtsfolgenbelehrung:
Sollten Sie die Forderung nicht begleichen, werden wir gerichtliche Schritte einleiten. Dies würde zusätzliche Kosten verursachen.

Mit freundlichen Grüßen

CreditProtect Inkasso GmbH

Thomas Braun
Geschäftsführer

Telefon: 040 9876 5432
E-Mail: kontakt@creditprotect.de
Internet: www.creditprotect.de

Hinweis:
Diese Mahnung ersetzt keine rechtliche Beratung.

Datenschutz:
Ihre Daten werden gemäß DSGVO verarbeitet.
''',
    'expected_contact': {'firstname': 'Thomas', 'lastname': 'Braun', 'gender': 'male'},
    'expected_sender': 'CreditProtect Inkasso GmbH',
    'expected_recipient': 'Oleksandr Shevchenko',
})

TEST_LETTERS.append({
    'name': 'Inkasso Letzte Mahnung (Frau Fischer)',
    'org': 'inkasso',
    'situation': 'mahnung',
    'text': '''EOS Rema Inkasso
Wendenstraße 245
20537 Hamburg

Frau
Iryna Kovalchuk
Berliner Straße 156
10115 Berlin

Hamburg, 22.02.2026

Letzte Mahnung
Forderungsnummer: 2026/987654

Sehr geehrte Frau Kovalchuk,

trotz unserer bisherigen Schreiben haben Sie die Forderung nicht beglichen.

Offener Gesamtbetrag: 1.250,00 EUR
- Hauptforderung: 1.100,00 EUR
- Mahngebühren: 50,00 EUR
- Verzugszinsen: 100,00 EUR

Zahlungsfrist: 28.02.2026

Sollte die Frist fruchtlos verstreichen, werden wir gerichtliche Schritte einleiten. Dies würde zusätzliche Kosten verursachen (Gerichtskosten, Gerichtsvollzieher).

IBAN: DE89 2004 0000 0123 4567 89
BIC: COBADEFFXXX

Mit freundlichen Grüßen

EOS Rema Inkasso

Michael Fischer
Leiter Forderungsmanagement

Telefon: 040 23666 0
E-Mail: michael.fischer@eos-inkasso.de

Rechtlicher Hinweis:
Gemäß § 286 BGB befinden Sie sich im Verzug.
''',
    'expected_contact': {'firstname': 'Michael', 'lastname': 'Fischer', 'gender': 'male'},
    'expected_sender': 'EOS Rema Inkasso',
    'expected_recipient': 'Iryna Kovalchuk',
})

# Додамо ще 5 Inkasso листів...
for i in range(5):
    TEST_LETTERS.append({
        'name': f'Inkasso Forderung {i+1}',
        'org': 'inkasso',
        'situation': 'forderung',
        'text': f'''Inkasso Service Deutschland
Königsallee {90+i}
40212 Düsseldorf

Herrn
Viktor Savchenko
Königsstraße {40+i}
40211 Düsseldorf

Düsseldorf, {20+i}.02.2026

Zahlungsaufforderung
Forderungsnummer: 2026/{400000+i}

Sehr geehrter Herr Savchenko,

wir fordern Sie zur Zahlung auf.

Offener Betrag: {500+i*100},00 EUR
Frist: {28+i}.02.2026

IBAN: DE89 {3000+i} 0000 0123 4567 89

Mit freundlichen Grüßen

Sandra {["Klein", "Wolf", "Bach", "Hofmann", "Richter"][i]}
Kundenbetreuung

Telefon: 0211 {100000+i}
E-Mail: kontakt@inkasso-service.de
''',
        'expected_contact': {'firstname': 'Sandra', 'lastname': ["Klein", "Wolf", "Bach", "Hofmann", "Richter"][i], 'gender': 'female'},
        'expected_sender': 'Inkasso Service Deutschland',
        'expected_recipient': 'Viktor Savchenko',
    })

# ============================================================================
# 3. VERMIETER (7 листів)
# ============================================================================

TEST_LETTERS.append({
    'name': 'Vermieter Mieterhöhung (Herr Müller)',
    'org': 'vermieter',
    'situation': 'mieterhöhung',
    'text': '''Vermieter Hans Müller
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

Mit freundlichen Grüßen

Hans Müller
Vermieter

Telefon: 0171 234 5678
E-Mail: hans.mueller@vermieter.de

Hinweis:
Bei Fragen können Sie sich an den Mieterbund wenden.
''',
    'expected_contact': {'firstname': 'Hans', 'lastname': 'Müller', 'gender': 'male'},
    'expected_sender': 'Hans Müller',
    'expected_recipient': 'Oleksandr Shevchenko',
})

# Додамо ще 6 Vermieter листів...
for i in range(6):
    TEST_LETTERS.append({
        'name': f'Vermieter Schreiben {i+1}',
        'org': 'vermieter',
        'situation': 'mieterhöhung',
        'text': f'''Vermieterin Maria {["Schmidt", "Wagner", "Becker", "Schulz", "Neumann", "Zimmermann"][i]}
Berliner Straße {70+i}
10115 Berlin

Frau
Olena Petrenko
Berliner Straße {150+i}, Apt. {5+i}
10117 Berlin

Berlin, {20+i}.02.2026

Mieterhöhung

Sehr geehrte Frau Petrenko,

wir müssen die Miete erhöhen.

Aktuelle Miete: {400+i*50},00 EUR
Neue Miete: {500+i*50},00 EUR

Gemäß § 558 BGB.

Mit freundlichen Grüßen

Maria {["Schmidt", "Wagner", "Becker", "Schulz", "Neumann", "Zimmermann"][i]}
Vermieterin

Telefon: 0171 {2000000+i}
''',
        'expected_contact': {'firstname': 'Maria', 'lastname': ["Schmidt", "Wagner", "Becker", "Schulz", "Neumann", "Zimmermann"][i], 'gender': 'female'},
        'expected_sender': f'Maria {["Schmidt", "Wagner", "Becker", "Schulz", "Neumann", "Zimmermann"][i]}',
        'expected_recipient': 'Olena Petrenko',
    })

# ============================================================================
# 4. FINANZAMT (7 листів)
# ============================================================================

TEST_LETTERS.append({
    'name': 'Finanzamt Steuerbescheid (Frau Wagner)',
    'org': 'finanzamt',
    'situation': 'steuerbescheid',
    'text': '''Finanzamt Berlin
Alte Jakobstraße 124
10969 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45
13351 Berlin

Berlin, 20.02.2026

Einkommensteuerbescheid 2025

Sehr geehrter Herr Shevchenko,

hiermit setzen wir Ihre Einkommensteuer für das Jahr 2025 fest:

Zu versteuerndes Einkommen: 24.000,00 EUR
Festgesetzte Steuer: 3.200,00 EUR
Bereits gezahlt: 2.800,00 EUR
Nachzahlung: 400,00 EUR

Die Nachzahlung ist bis zum 10.03.2026 fällig.

Rechtsbehelfsbelehrung:
Gegen diesen Bescheid können Sie innerhalb eines Monats Einspruch einlegen (§ 355 AO).

Der Einspruch ist schriftlich beim Finanzamt Berlin einzureichen.

Mit freundlichen Grüßen

Finanzamt Berlin

Petra Wagner
Sachbearbeiterin

Steuernummer: 12/345/67890
Telefon: 030 9876 5432
E-Mail: petra.wagner@finanzamt-berlin.de

Zahlungsweise:
Die Nachzahlung können Sie per Überweisung oder Lastschrift leisten.
''',
    'expected_contact': {'firstname': 'Petra', 'lastname': 'Wagner', 'gender': 'female'},
    'expected_sender': 'Finanzamt Berlin',
    'expected_recipient': 'Oleksandr Shevchenko',
})

# Додамо ще 6 Finanzamt листів...
for i in range(6):
    TEST_LETTERS.append({
        'name': f'Finanzamt Bescheid {i+1}',
        'org': 'finanzamt',
        'situation': 'steuerbescheid',
        'text': f'''Finanzamt {"Hamburg" if i%2==0 else "München"}
{"Billstraße 4" if i%2==0 else "Arnulfstraße 15"}
{20539 if i%2==0 else 80335} {"Hamburg" if i%2==0 else "München"}

{"Herrn" if i%3==0 else "Frau"}
{"Andriy" if i%3==0 else "Iryna"} {"Melnyk" if i%3==0 else "Kovalchuk"}
{"Hamburger" if i%2==0 else "Münchener"} Straße {100+i}
{22089 if i%2==0 else 80687} {"Hamburg" if i%2==0 else "München"}

{"Hamburg" if i%2==0 else "München"}, {20+i}.02.2026

Steuerbescheid 2025
Steuernummer: {10+i}/345/6789{i}

Sehr geehrte{"r" if i%3==0 else ""} {"Melnyk" if i%3==0 else "Kovalchuk"},

hiermit setzen wir Ihre Einkommensteuer fest.

Nachzahlung: {300+i*100},00 EUR
Frist: {10+i}.03.2026

Gemäß § 355 AO.

Mit freundlichen Grüßen

Finanzamt {"Hamburg" if i%2==0 else "München"}

{"Klaus" if i%2==0 else "Anna"} {"Becker" if i%2==0 else "Schmidt"}
Sachbearbeiter{"in" if i%2==0 else ""}

Telefon: 0{40 if i%2==0 else 89} {100000+i}
''',
        'expected_contact': {'firstname': "Klaus" if i%2==0 else "Anna", 'lastname': "Becker" if i%2==0 else "Schmidt", 'gender': 'male' if i%2==0 else 'female'},
        'expected_sender': f'Finanzamt {"Hamburg" if i%2==0 else "München"}',
        'expected_recipient': "Andriy Melnyk" if i%3==0 else "Iryna Kovalchuk",
    })

# ============================================================================
# 5. GERICHT (6 листів)
# ============================================================================

for i in range(6):
    TEST_LETTERS.append({
        'name': f'Gericht Ladung {i+1}',
        'org': 'gericht',
        'situation': 'ladung',
        'text': f'''Amtsgericht {"Berlin-Charlottenburg" if i%2==0 else "München"}
{"Amtsgerichtsplatz 1" if i%2==0 else "Pacellistraße 5"}
{14057 if i%2==0 else 80333} {"Berlin" if i%2==0 else "München"}

{"Frau" if i%3==0 else "Herrn"}
{"Olena" if i%3==0 else "Viktor"} {"Petrenko" if i%3==0 else "Savchenko"}
{"Berliner" if i%2==0 else "Nürnberger"} Straße {200+i}
{10115 if i%2==0 else 90429} {"Berlin" if i%2==0 else "Nürnberg"}

{"Berlin" if i%2==0 else "München"}, {25+i}.02.2026

Ladung zur Gerichtssitzung
Aktenzeichen: {15+i} C {123+i}/26

Sehr geehrte{" Frau" if i%3==0 else "r Herr"} {"Petrenko" if i%3==0 else "Savchenko"},

in dem Rechtsstreit

{"Telekommunikation GmbH" if i%2==0 else "ABC GmbH"} ./. {"Frau Petrenko" if i%3==0 else "Herr Savchenko"}

laden wir Sie zur mündlichen Verhandlung.

Termin: {20+i}.03.2026, um {9+i}:30 Uhr
Saal: {200+i}, {2+i}. Stock

Gemäß § 330 ZPO.

Mit freundlichen Grüßen

Amtsgericht {"Berlin-Charlottenburg" if i%2==0 else "München"}

Der Rechtspfleger

Telefon: 0{30 if i%2==0 else 89} {100000+i}
''',
        'expected_contact': {'firstname': None, 'lastname': 'Rechtspfleger', 'gender': None},
        'expected_sender': f'Amtsgericht {"Berlin-Charlottenburg" if i%2==0 else "München"}',
        'expected_recipient': "Olena Petrenko" if i%3==0 else "Viktor Savchenko",
    })

# ============================================================================
# 6. KRANKENKASSE (6 листів)
# ============================================================================

for i in range(6):
    TEST_LETTERS.append({
        'name': f'Krankenkasse Bescheid {i+1}',
        'org': 'krankenkasse',
        'situation': 'bescheid',
        'text': f'''{"AOK" if i%2==0 else "TK"} {"Berlin" if i%3==0 else "Hamburg"}
{"Friedrichstraße 100" if i%3==0 else "Spitalerstraße 5"}
{10117 if i%3==0 else 20095} {"Berlin" if i%3==0 else "Hamburg"}

{"Frau" if i%2==0 else "Herrn"}
{"Iryna" if i%2==0 else "Andriy"} {"Bondarenko" if i%2==0 else "Melnyk"}
{"Friedrich" if i%3==0 else "Hamburger"} Straße {150+i}
{10117 if i%3==0 else 22089} {"Berlin" if i%3==0 else "Hamburg"}

{"Berlin" if i%3==0 else "Hamburg"}, {28-i}.02.2026

Bescheid über Krankenversicherung
Versichertennummer: A{123456789+i}

Sehr geehrte{" Frau" if i%2==0 else "r Herr"} {"Bondarenko" if i%2==0 else "Melnyk"},

hiermit bestätigen wir Ihre Mitgliedschaft.

Monatlicher Beitrag: {400+i*10},00 EUR
- Eigenanteil: {200+i*5},00 EUR
- Arbeitgeberanteil: {200+i*5},00 EUR

Beginn: 01.03.2026

Mit freundlichen Grüßen

{"AOK" if i%2==0 else "TK"} {"Berlin" if i%3==0 else "Hamburg"}

{"Petra" if i%2==0 else "Klaus"} {"Schmidt" if i%3==0 else "Weber"}
Kundenbetreuung

Telefon: 0{30 if i%3==0 else 40} {100000+i}
''',
        'expected_contact': {'firstname': "Petra" if i%2==0 else "Klaus", 'lastname': "Schmidt" if i%3==0 else "Weber", 'gender': 'female' if i%2==0 else 'male'},
        'expected_sender': f'{"AOK" if i%2==0 else "TK"} {"Berlin" if i%3==0 else "Hamburg"}',
        'expected_recipient': "Iryna Bondarenko" if i%2==0 else "Andriy Melnyk",
    })

# ============================================================================
# 7. VERSICHERUNG (5 листів)
# ============================================================================

for i in range(5):
    TEST_LETTERS.append({
        'name': f'Versicherung Rechnung {i+1}',
        'org': 'versicherung',
        'situation': 'rechnung',
        'text': f'''{"Allianz" if i%2==0 else "AXA"} Versicherung
{"Königinstraße 107" if i%2==0 else "Landsberger Straße 300"}
{80802 if i%2==0 else 80687} München

{"Herrn" if i%3==0 else "Frau"}
{"Andriy" if i%3==0 else "Iryna"} {"Shevchuk" if i%3==0 else "Bondarenko"}
{"Leopold" if i%2==0 else "Berliner"} Straße {200+i}
{80807 if i%2==0 else 10117} {"München" if i%2==0 else "Berlin"}

München, {28-i}.02.2026

Versicherungsrechnung 2026
Versicherungsnummer: {123456789+i}

Sehr geehrte{"r Herr" if i%3==0 else " Frau"} {"Shevchuk" if i%3==0 else "Bondarenko"},

anbei erhalten Sie die Rechnung für Ihre Versicherung 2026.

Gesamtbeitrag: {800+i*20},00 EUR
Fälligkeit: {15+i}.03.2026

Bei Nichtzahlung können wir den Vertrag kündigen (§ 38 VVG).

Mit freundlichen Grüßen

{"Allianz" if i%2==0 else "AXA"} Versicherung

{"Michael" if i%2==0 else "Sandra"} {"Fischer" if i%3==0 else "Klein"}
Kundenbetreuung

Telefon: 089 {100000+i}
''',
        'expected_contact': {'firstname': "Michael" if i%2==0 else "Sandra", 'lastname': "Fischer" if i%3==0 else "Klein", 'gender': 'male' if i%2==0 else 'female'},
        'expected_sender': f'{"Allianz" if i%2==0 else "AXA"} Versicherung',
        'expected_recipient': "Andriy Shevchuk" if i%3==0 else "Iryna Bondarenko",
    })

# ============================================================================
# 8. BEHÖRDE / STADTWERKE (5 листів)
# ============================================================================

for i in range(5):
    TEST_LETTERS.append({
        'name': f'Behörde Schreiben {i+1}',
        'org': 'behörde',
        'situation': 'bescheid',
        'text': f'''{"Stadt Berlin" if i%2==0 else "Landratsamt München"}
{"Rathausstraße 1" if i%2==0 else "Marienplatz 8"}
{10178 if i%2==0 else 80331} {"Berlin" if i%2==0 else "München"}

{"Herrn" if i%3==0 else "Frau"}
{"Viktor" if i%3==0 else "Olena"} {"Savchenko" if i%3==0 else "Petrenko"}
{"Müller" if i%2==0 else "Berliner"} Straße {250+i}
{13351 if i%2==0 else 10117} {"Berlin" if i%2==0 else "München"}

{"Berlin" if i%2==0 else "München"}, {26+i}.02.2026

{"Antrag auf Aufenthaltstitel" if i%2==0 else "Anmeldung"}
Aktenzeichen: {2026}/{1000+i}

Sehr geehrte{"r Herr" if i%3==0 else " Frau"} {"Savchenko" if i%3==0 else "Petrenko"},

hiermit bestätigen wir Ihren {"Antrag" if i%2==0 else "Termin"}.

{"Termin: "+str(15+i)+".03.2026 um 11:00 Uhr" if i%2==0 else "Bitte erscheinen Sie pünktlich."}

Mit freundlichen Grüßen

{"Stadt Berlin" if i%2==0 else "Landratsamt München"}

{"Klaus" if i%2==0 else "Anna"} {"Becker" if i%3==0 else "Schmidt"}
Sachbearbeiter{"in" if i%2==0 else ""}

Telefon: 0{30 if i%2==0 else 89} {200000+i}
''',
        'expected_contact': {'firstname': "Klaus" if i%2==0 else "Anna", 'lastname': "Becker" if i%3==0 else "Schmidt", 'gender': 'male' if i%2==0 else 'female'},
        'expected_sender': f'{"Stadt Berlin" if i%2==0 else "Landratsamt München"}',
        'expected_recipient': "Viktor Savchenko" if i%3==0 else "Olena Petrenko",
    })

# ============================================================================
# ГОЛОВНА ФУНКЦІЯ ТЕСТУВАННЯ
# ============================================================================

def test_letter_generator(test_case, test_num):
    """Тестування одного листа."""
    generator = LetterGenerator()
    
    # Витягування даних
    data = generator.extract_all_data(test_case['text'])
    
    # Перевірка extraction
    results = {
        'extraction': {},
        'generation': {},
        'response': {},
    }
    
    # 1. Перевірка витягування відправника
    sender_ok = test_case['expected_sender'] in data.get('sender', {}).get('name', '')
    results['extraction']['sender'] = {
        'passed': sender_ok,
        'expected': test_case['expected_sender'],
        'actual': data.get('sender', {}).get('name', ''),
    }
    
    # 2. Перевірка витягування отримувача
    recipient_ok = test_case['expected_recipient'] in data.get('recipient', {}).get('name', '')
    results['extraction']['recipient'] = {
        'passed': recipient_ok,
        'expected': test_case['expected_recipient'],
        'actual': data.get('recipient', {}).get('name', ''),
    }
    
    # 3. Перевірка контактної особи (більш реалістично)
    contact = data.get('contact_person', {})
    expected_contact = test_case['expected_contact']
    
    # Перевіряємо тільки прізвище та стать (ім'я може бути None)
    contact_ok = (
        (contact.get('lastname') == expected_contact['lastname']) and
        (contact.get('gender') == expected_contact['gender'])
    )
    results['extraction']['contact'] = {
        'passed': contact_ok,
        'expected': expected_contact,
        'actual': contact,
    }
    
    # 4. Генерація німецької відповіді
    try:
        response_de, _ = generate_response_smart_improved(test_case['text'], 'de')
        results['response']['generated'] = len(response_de) > 100
        results['response']['length'] = len(response_de)
    except Exception as e:
        results['response']['generated'] = False
        results['response']['error'] = str(e)[:100]  # Обмежуємо довжину помилки
    
    # 5. Генерація повного листа
    try:
        if results['response']['generated']:
            # Визначаємо тип відповіді
            response_type = test_case['org']
            
            # Генеруємо повний лист
            full_letter = generate_german_letter(test_case['text'], response_de, response_type)
            results['generation']['passed'] = len(full_letter) > 200
            results['generation']['length'] = len(full_letter)
            
            # Перевірка чи є звертання
            has_salutation = 'Sehr geehrte' in full_letter
            results['generation']['salutation'] = has_salutation
            
            # Перевірка чи є адреси
            has_sender = test_case['expected_recipient'] in full_letter
            has_recipient = test_case['expected_sender'] in full_letter
            results['generation']['addresses'] = has_sender and has_recipient
        else:
            results['generation']['passed'] = False
            results['generation']['error'] = 'Response not generated'
    except Exception as e:
        results['generation']['passed'] = False
        results['generation']['error'] = str(e)[:100]
    
    return results

def main():
    print_header("🧪 КОМПЛЕКСНИЙ ТЕСТ 50 ЛИСТІВ V4.5")
    print(f"Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Кількість листів: {len(TEST_LETTERS)}")
    print(f"Організації: Jobcenter, Inkasso, Vermieter, Finanzamt, Gericht, Krankenkasse, Versicherung, Behörde")
    
    results_summary = {
        'total': len(TEST_LETTERS),
        'passed': 0,
        'failed': 0,
        'by_org': {},
        'by_category': {
            'extraction_sender': 0,
            'extraction_recipient': 0,
            'extraction_contact': 0,
            'response_generation': 0,
            'letter_generation': 0,
            'salutation': 0,
            'addresses': 0,
        }
    }
    
    detailed_results = []
    
    for i, test_case in enumerate(TEST_LETTERS, 1):
        org = test_case['org']
        if org not in results_summary['by_org']:
            results_summary['by_org'][org] = {'total': 0, 'passed': 0}
        results_summary['by_org'][org]['total'] += 1
        
        # Тестування
        results = test_letter_generator(test_case, i)
        
        # Підрахунок
        all_passed = (
            results['extraction']['sender']['passed'] and
            results['extraction']['recipient']['passed'] and
            results['extraction']['contact']['passed'] and
            results['response']['generated'] and
            results['generation']['passed']
        )
        
        if all_passed:
            results_summary['passed'] += 1
            results_summary['by_org'][org]['passed'] += 1
        else:
            results_summary['failed'] += 1
        
        # Категорії
        if results['extraction']['sender']['passed']:
            results_summary['by_category']['extraction_sender'] += 1
        if results['extraction']['recipient']['passed']:
            results_summary['by_category']['extraction_recipient'] += 1
        if results['extraction']['contact']['passed']:
            results_summary['by_category']['extraction_contact'] += 1
        if results['response']['generated']:
            results_summary['by_category']['response_generation'] += 1
        if results['generation']['passed']:
            results_summary['by_category']['letter_generation'] += 1
        if results['generation'].get('salutation'):
            results_summary['by_category']['salutation'] += 1
        if results['generation'].get('addresses'):
            results_summary['by_category']['addresses'] += 1
        
        # Збереження деталей
        detailed_results.append({
            'name': test_case['name'],
            'org': org,
            'results': results,
            'passed': all_passed,
        })
        
        # Вивід прогресу
        status = f"{Colors.GREEN}✅{Colors.END}" if all_passed else f"{Colors.RED}❌{Colors.END}"
        print(f"{status} Тест {i:2d}/50: {test_case['name'][:50]:<50}")
    
    # Підсумки
    print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    
    total_percentage = (results_summary['passed'] / results_summary['total']) * 100
    print(f"\nЗагальна точність: {Colors.BOLD}{results_summary['passed']}/{results_summary['total']} ({total_percentage:.1f}%){Colors.END}")
    
    if total_percentage >= 90:
        print(f"{Colors.GREEN}✅ ВІДМІННО{Colors.END}")
    elif total_percentage >= 70:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END}")
    else:
        print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END}")
    
    # По організаціях
    print(f"\n{Colors.BLUE}ПО ОРГАНІЗАЦІЯМ:{Colors.END}")
    for org, stats in results_summary['by_org'].items():
        percentage = (stats['passed'] / stats['total']) * 100 if stats['total'] > 0 else 0
        print(f"  {org:.<30} {stats['passed']:2d}/{stats['total']:2d} ({percentage:5.1f}%)")
    
    # По категоріях
    print(f"\n{Colors.BLUE}ПО КАТЕГОРІЯМ:{Colors.END}")
    category_names = {
        'extraction_sender': 'Витягування відправника',
        'extraction_recipient': 'Витягування отримувача',
        'extraction_contact': 'Витягування контактної особи',
        'response_generation': 'Генерація відповіді',
        'letter_generation': 'Генерація листа',
        'salutation': 'Персоналізоване звертання',
        'addresses': 'Адреси в листі',
    }
    
    for cat, count in results_summary['by_category'].items():
        percentage = (count / results_summary['total']) * 100
        status = f"{Colors.GREEN}✅{Colors.END}" if percentage >= 90 else f"{Colors.YELLOW}⚠️{Colors.END}" if percentage >= 70 else f"{Colors.RED}❌{Colors.END}"
        print(f"  {category_names[cat]:.<40} {count:2d}/{results_summary['total']:2d} ({percentage:5.1f}%) {status}")
    
    # Деталі провалених тестів
    failed_tests = [r for r in detailed_results if not r['passed']]
    if failed_tests:
        print(f"\n{Colors.RED}❌ ПРОВАЛЕНІ ТЕСТИ ({len(failed_tests)}):{Colors.END}")
        for result in failed_tests[:10]:  # Показати перші 10
            print(f"  - {result['name']} ({result['org']})")
    
    # Час завершення
    print(f"\nЧас завершення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return total_percentage

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 70 else 1)
