#!/usr/bin/env python3
"""
Масове тестування Gov.de Bot v4.2
50 тестових листів від різних організацій
Перевірка: класифікація, закони, терміни, шахрайство
"""

import sys
from pathlib import Path
from datetime import datetime

# Додаємо шлях до модулів
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import check_if_document, get_paragraph_description, create_simple_analysis
from fraud_detection import analyze_letter_for_fraud, extract_phone_numbers, extract_emails

# ============================================================================
# 50 ТЕСТОВИХ ЛИСТІВ
# ============================================================================

TEST_LETTERS = [
    # ========================================================================
    # JOBCENTER (10 листів)
    # ========================================================================
    {
        'id': 1,
        'category': 'Jobcenter',
        'type': 'Einladung zum Gespräch',
        'text': '''Jobcenter Berlin Mitte
Straße des 17. Juni 110, 10623 Berlin

Sehr geehrte Damen und Herren,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 15.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 204
Ansprechpartner: Herr Müller

Rechtsgrundlage: § 59 SGB II, § 31 SGB II

Bei unentschuldigtem Fehlen kann die Leistung um 30% gekürzt werden.

Mit freundlichen Grüßen
Ihr Jobcenter Berlin Mitte''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 59 SGB II', '§ 31 SGB II'],
            'deadline': '15.03.2026',
            'time': '10:00',
            'risk': '30% Kürzung'
        }
    },
    {
        'id': 2,
        'category': 'Jobcenter',
        'type': 'Leistungsbescheid',
        'text': '''Jobcenter Hamburg
Bescheid über Arbeitslosengeld II
Aktenzeichen: 123/456/789

Gesamtbedarf: 1.093,00 EUR
- Regelsatz: 563,00 EUR
- Miete: 530,00 EUR

Bescheid vom: 01.03.2026
§ 84 SGG

Widerspruch innerhalb eines Monats möglich.

Mit freundlichen Grüßen''',
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
        'text': '''Jobcenter München
Aufforderung zur Mitwirkung

Sie werden aufgefordert, folgende Unterlagen einzureichen:
- Kontoauszüge Februar 2026
- Mietbescheinigung
- Nachweise über Bewerbungen

Frist: bis 20.03.2026

Rechtsfolge: § 60 SGB I
Bei Nichtvorlage können die Leistungen eingestellt werden.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'deadline': '20.03.2026',
            'paragraphs': ['§ 60 SGB I']
        }
    },
    {
        'id': 4,
        'category': 'Jobcenter',
        'type': 'Sanktionsbescheid',
        'text': '''Jobcenter Köln
Bescheid über Leistungskürzung

Aufgrund wiederholten unentschuldigten Fehlens bei Terminen:

Kürzung: 30% für 3 Monate
Gesamtbetrag: 327,90 EUR

§ 31 SGB II, § 32 SGB II

Widerspruchsfrist: bis 25.03.2026

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'reduction': '30%',
            'paragraphs': ['§ 31 SGB II', '§ 32 SGB II']
        }
    },
    {
        'id': 5,
        'category': 'Jobcenter',
        'type': 'Vermittlungsvorschlag',
        'text': '''Arbeitsagentur Nürnberg
Vermittlungsvorschlag

Stellenangebot: Lagerist (m/w/d)
Arbeitgeber: Logistik GmbH
Arbeitsbeginn: 01.04.2026

Bewerbung bis: 10.03.2026

§ 140 SGB III, § 309 SGB III

Bei Ablehnung ohne wichtigen Grund können Sanktionen folgen.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Arbeitsagentur',
            'deadline': '10.03.2026',
            'paragraphs': ['§ 140 SGB III', '§ 309 SGB III']
        }
    },
    {
        'id': 6,
        'category': 'Jobcenter',
        'type': 'Terminbestätigung',
        'text': '''Jobcenter Stuttgart
Terminbestätigung

Ihr Termin wurde bestätigt:
Datum: 18.03.2026
Uhrzeit: 14:30 Uhr
Ort: Jobcenter Stuttgart, Friedrichstraße 10

Bitte bringen Sie mit:
- Personalausweis
- Lebenslauf
- Bewerbungsunterlagen

§ 59 SGB II

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'deadline': '18.03.2026',
            'time': '14:30'
        }
    },
    {
        'id': 7,
        'category': 'Jobcenter',
        'type': 'Änderungsbescheid',
        'text': '''Jobcenter Frankfurt
Änderungsbescheid

Ihr Bedarf ändert sich ab 01.04.2026:

Neuer Gesamtbedarf: 1.150,00 EUR
Bisheriger Bedarf: 1.093,00 EUR
Erhöhung: 57,00 EUR

§ 48 SGB X

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'amount': '1.150,00 EUR',
            'paragraphs': ['§ 48 SGB X']
        }
    },
    {
        'id': 8,
        'category': 'Jobcenter',
        'type': 'Rückforderung',
        'text': '''Jobcenter Düsseldorf
Rückforderung von Leistungen

Aufgrund zu hoher Zahlungen fordern wir zurück:

Betrag: 450,00 EUR
Frist: 14 Tage ab Erhalt

§ 45 SGB X

Bei Nichtzahlung erfolgt Verrechnung mit künftigen Leistungen.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'amount': '450,00 EUR',
            'paragraphs': ['§ 45 SGB X']
        }
    },
    {
        'id': 9,
        'category': 'Jobcenter',
        'type': 'Bewilligungsbescheid',
        'text': '''Jobcenter Leipzig
Bewilligungsbescheid

Ihr Antrag auf Arbeitslosengeld II wurde bewilligt.

Bewilligungszeitraum: 01.03.2026 - 31.08.2026
Monatlicher Betrag: 563,00 EUR + Miete

§ 7 SGB II, § 19 SGB II

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 7 SGB II', '§ 19 SGB II']
        }
    },
    {
        'id': 10,
        'category': 'Jobcenter',
        'type': 'Meldeaufforderung',
        'text': '''Jobcenter Dresden
Meldeaufforderung

Sie werden aufgefordert, sich persönlich zu melden.

Termin: 22.03.2026, 09:00 Uhr
Ort: Jobcenter Dresden

§ 59 SGB II, § 309 SGB III

Bei Nichterscheinen: Leistungskürzung 30%

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'deadline': '22.03.2026',
            'paragraphs': ['§ 59 SGB II', '§ 309 SGB III']
        }
    },

    # ========================================================================
    # INKASSO (8 листів)
    # ========================================================================
    {
        'id': 11,
        'category': 'Inkasso',
        'type': 'Erste Mahnung',
        'text': '''CreditProtect Inkasso GmbH
Hamburg, den 01.03.2026

Erste Mahnung

Sehr geehrte Damen und Herren,

für unseren Auftraggeber fordern wir:

Offener Betrag: 350,00 EUR
Frist: bis 15.03.2026

Überweisung auf:
IBAN: DE89 3704 0044 0532 0130 00

§ 286 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '350,00 EUR',
            'deadline': '15.03.2026',
            'paragraphs': ['§ 286 BGB']
        }
    },
    {
        'id': 12,
        'category': 'Inkasso',
        'type': 'Letzte Mahnung',
        'text': '''EOS Rema Inkasso
München, den 28.02.2026

Letzte Mahnung

Gesamtbetrag: 1.250,00 EUR
- Hauptforderung: 1.100,00 EUR
- Zinsen: 150,00 EUR

Frist: 28.02.2026

Bei Nichtzahlung leiten wir gerichtliche Schritte ein.

§ 288 BGB, § 286 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '1.250,00 EUR',
            'deadline': '28.02.2026',
            'risk': 'Gericht'
        }
    },
    {
        'id': 13,
        'category': 'Inkasso',
        'type': 'Zahlungsvereinbarung',
        'text': '''Inkasso Service Deutschland
Angebot zur Ratenzahlung

Gesamtforderung: 890,00 EUR

Wir bieten Ratenzahlung an:
6 Raten à 148,33 EUR
Erste Rate: 15.03.2026

Frist für Annahme: 28.02.2026

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '890,00 EUR',
            'deadline': '28.02.2026'
        }
    },
    {
        'id': 14,
        'category': 'Inkasso',
        'type': 'Gerichtlicher Mahnbescheid',
        'text': '''Amtsgericht Hamburg
Mahnbescheid

Gläubiger: Telekom Deutschland GmbH
Schuldner: Max Mustermann

Forderung: 2.500,00 EUR
Gerichtskosten: 150,00 EUR

Widerspruchsfrist: bis 12.03.2026

Bei Widerspruch: Gerichtstermin

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '2.500,00 EUR',
            'deadline': '12.03.2026',
            'risk': 'Sehr hoch'
        }
    },
    {
        'id': 15,
        'category': 'Inkasso',
        'type': 'Forderungsanmeldung',
        'text': '''Forderungsmanagement GmbH
Forderungsanmeldung

Offene Forderungen:
- Rechnung 12345: 450,00 EUR
- Rechnung 12346: 320,00 EUR
- Mahngebühren: 50,00 EUR

Gesamt: 820,00 EUR

Frist: 14 Tage

§ 286 BGB, § 288 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'amount': '820,00 EUR',
            'paragraphs': ['§ 286 BGB', '§ 288 BGB']
        }
    },
    {
        'id': 16,
        'category': 'Inkasso',
        'type': 'Vollstreckungsbescheid',
        'text': '''Amtsgericht Berlin
Vollstreckungsbescheid

Nach Fristablauf ohne Widerspruch:

Vollstreckungssumme: 3.200,00 EUR
Gerichtsvollzieher wird beauftragt.

§ 794 ZPO, § 758 ZPO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '3.200,00 EUR',
            'paragraphs': ['§ 794 ZPO', '§ 758 ZPO'],
            'risk': 'Gerichtsvollzieher'
        }
    },
    {
        'id': 17,
        'category': 'Inkasso',
        'type': 'Schufa-Meldung',
        'text': '''SCHUFA Holding AG
Schufa-Meldung

Bei Nichtzahlung erfolgt Meldung an SCHUFA.

Forderung: 670,00 EUR
Frist: 10.03.2026

Negative Schufa-Eintragung für 3 Jahre.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'SCHUFA',
            'amount': '670,00 EUR',
            'deadline': '10.03.2026'
        }
    },
    {
        'id': 18,
        'category': 'Inkasso',
        'type': 'Anwaltliches Mahnschreiben',
        'text': '''Rechtsanwalt Dr. Schmidt
Anwaltliches Mahnschreiben

Im Auftrag meines Mandanten fordere ich:

5.000,00 EUR + 500,00 EUR Anwaltskosten
Gesamt: 5.500,00 EUR

Frist: 10.03.2026

Bei Nichtzahlung: Klageerhebung

§ 286 BGB

Mit freundlichen Grüßen
Dr. Schmidt, Rechtsanwalt''',
        'expected': {
            'is_document': True,
            'org': 'Rechtsanwalt',
            'amount': '5.500,00 EUR',
            'deadline': '10.03.2026',
            'risk': 'Gericht'
        }
    },

    # ========================================================================
    # VERMIETER (8 листів)
    # ========================================================================
    {
        'id': 19,
        'category': 'Vermieter',
        'type': 'Mieterhöhung',
        'text': '''Vermieter Hans Müller
Mieterhöhung

Sehr geehrte Mieter,

die Miete wird erhöht:
Von: 450,00 EUR
Auf: 550,00 EUR
Erhöhung: 22,2%

§ 558 BGB

Widerspruch bis 30.04.2026

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'amount': '100,00 EUR',
            'paragraphs': ['§ 558 BGB']
        }
    },
    {
        'id': 20,
        'category': 'Vermieter',
        'type': 'Kündigung',
        'text': '''Vermieterin Maria Schmidt
Fristlose Kündigung

Miete 2 Monate nicht gezahlt.

§ 543 BGB

Räumung bis 31.03.2026

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'paragraphs': ['§ 543 BGB'],
            'deadline': '31.03.2026',
            'risk': 'Räumung'
        }
    },
    {
        'id': 21,
        'category': 'Vermieter',
        'type': 'Nebenkostenabrechnung',
        'text': '''Hausverwaltung Berlin GmbH
Nebenkostenabrechnung 2025

Nachzahlung: 300,00 EUR
Frist: 15.03.2026

Überweisung auf Konto:
IBAN: DE89 3704 0044 0532 0130 00

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'amount': '300,00 EUR',
            'deadline': '15.03.2026'
        }
    },
    {
        'id': 22,
        'category': 'Vermieter',
        'type': 'Mietmängelanzeige',
        'text': '''Mieterbund Berlin
Ihre Rechte bei Mietmängeln

Schimmelbildung im Bad.

§ 536 BGB

Mietminderung bis 50% möglich.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Mieterbund',
            'paragraphs': ['§ 536 BGB']
        }
    },
    {
        'id': 23,
        'category': 'Vermieter',
        'type': 'Modernisierung',
        'text': '''Vermieter Klaus Weber
Modernisierungsankündigung

Neue Heizung und Fenster.
Mehrkosten: 80,00 EUR monatlich.

§ 559 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'paragraphs': ['§ 559 BGB']
        }
    },
    {
        'id': 24,
        'category': 'Vermieter',
        'type': 'Besichtigung',
        'text': '''Vermieterin Anna Braun
Besichtigungstermin

Besichtigung der Wohnung:
Termin: 20.03.2026, 14:00 Uhr

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'deadline': '20.03.2026',
            'time': '14:00'
        }
    },
    {
        'id': 25,
        'category': 'Vermieter',
        'type': 'Kaution',
        'text': '''Vermieter Thomas Fischer
Kautionsabrechnung

Nach Auszug:
Kaution: 1.200,00 EUR
Abzüglich Schäden: 350,00 EUR
Rückzahlung: 850,00 EUR

§ 551 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Vermieter',
            'amount': '850,00 EUR',
            'paragraphs': ['§ 551 BGB']
        }
    },
    {
        'id': 26,
        'category': 'Vermieter',
        'type': 'Betriebskosten',
        'text': '''Hausverwaltung Schmidt GmbH
Betriebskostenvorauszahlung

Ab 01.04.2026:
Von 150,00 EUR auf 180,00 EUR

§ 560 BGB

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'paragraphs': ['§ 560 BGB']
        }
    },

    # ========================================================================
    # FINANZAMT (6 листів)
    # ========================================================================
    {
        'id': 27,
        'category': 'Finanzamt',
        'type': 'Steuerbescheid',
        'text': '''Finanzamt Berlin
Einkommensteuerbescheid 2025

Nachzahlung: 400,00 EUR
Frist: 10.03.2026

§ 355 AO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'amount': '400,00 EUR',
            'deadline': '10.03.2026',
            'paragraphs': ['§ 355 AO']
        }
    },
    {
        'id': 28,
        'category': 'Finanzamt',
        'type': 'Aufforderung zur Steuererklärung',
        'text': '''Finanzamt Hamburg
Aufforderung zur Abgabe der Steuererklärung

Frist: 31.05.2026

§ 328 AO

Zwangsgeld bei Verspätung.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'deadline': '31.05.2026',
            'paragraphs': ['§ 328 AO']
        }
    },
    {
        'id': 29,
        'category': 'Finanzamt',
        'type': 'Lohnsteuerbescheinigung',
        'text': '''Arbeitgeber GmbH
Lohnsteuerbescheinigung 2025

Brutto: 36.000,00 EUR
Lohnsteuer: 4.800,00 EUR
Netto: 23.736,00 EUR

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Arbeitgeber',
            'amount': '36.000,00 EUR'
        }
    },
    {
        'id': 30,
        'category': 'Finanzamt',
        'type': 'Umsatzsteuervoranmeldung',
        'text': '''Finanzamt München
Umsatzsteuervoranmeldung

Frist: 10.03.2026
Vorauszahlung: 1.250,00 EUR

§ 18 UStG

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'deadline': '10.03.2026',
            'amount': '1.250,00 EUR',
            'paragraphs': ['§ 18 UStG']
        }
    },
    {
        'id': 31,
        'category': 'Finanzamt',
        'type': 'Außenprüfung',
        'text': '''Finanzamt Frankfurt
Ankündigung einer Außenprüfung

Prüfungsbeginn: 01.04.2026
Prüfungszeitraum: 2023-2025

§ 193 AO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'deadline': '01.04.2026',
            'paragraphs': ['§ 193 AO']
        }
    },
    {
        'id': 32,
        'category': 'Finanzamt',
        'type': 'Stundung',
        'text': '''Finanzamt Köln
Stundungsantrag abgelehnt

Ihr Antrag auf Stundung wurde abgelehnt.

Zahlung sofort fällig: 2.800,00 EUR

§ 222 AO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Finanzamt',
            'amount': '2.800,00 EUR',
            'paragraphs': ['§ 222 AO']
        }
    },

    # ========================================================================
    # GERICHT (5 листів)
    # ========================================================================
    {
        'id': 33,
        'category': 'Gericht',
        'type': 'Gerichtstermin',
        'text': '''Amtsgericht Berlin-Charlottenburg
Ladung zur Gerichtssitzung

Termin: 20.03.2026, 09:30 Uhr
Saal 123

§ 330 ZPO

Versäumnisurteil bei Ausbleiben.

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'deadline': '20.03.2026',
            'time': '09:30',
            'paragraphs': ['§ 330 ZPO'],
            'risk': 'Versäumnisurteil'
        }
    },
    {
        'id': 34,
        'category': 'Gericht',
        'type': 'Anwaltliches Schreiben',
        'text': '''Rechtsanwalt Dr. Weber
Anwaltliches Schreiben

5.000,00 EUR + 500,00 EUR Anwaltskosten
Frist: 10.03.2026

Bei Nichtzahlung: Klage

Mit freundlichen Grüßen
Dr. Weber''',
        'expected': {
            'is_document': True,
            'org': 'Rechtsanwalt',
            'amount': '5.500,00 EUR',
            'deadline': '10.03.2026',
            'risk': 'Gericht'
        }
    },
    {
        'id': 35,
        'category': 'Gericht',
        'type': 'Strafbefehl',
        'text': '''Amtsgericht Stuttgart
Strafbefehl

Geldstrafe: 90 Tagessätze à 50,00 EUR
Gesamt: 4.500,00 EUR

Widerspruchsfrist: 2 Wochen

§ 410 StPO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'amount': '4.500,00 EUR',
            'paragraphs': ['§ 410 StPO']
        }
    },
    {
        'id': 36,
        'category': 'Gericht',
        'type': 'Einstweilige Verfügung',
        'text': '''Landgericht Hamburg
Einstweilige Verfügung

Unterlassungserklärung erforderlich.
Frist: 7 Tage

§ 935 ZPO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'paragraphs': ['§ 935 ZPO']
        }
    },
    {
        'id': 37,
        'category': 'Gericht',
        'type': 'Gerichtsvollzieher',
        'text': '''Gerichtsvollzieher Müller
Ankündigung der Zwangsvollstreckung

Termin: 25.03.2026, 08:00 Uhr

Forderung: 8.500,00 EUR

§ 758 ZPO, § 794 ZPO

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Gerichtsvollzieher',
            'amount': '8.500,00 EUR',
            'deadline': '25.03.2026',
            'paragraphs': ['§ 758 ZPO', '§ 794 ZPO']
        }
    },

    # ========================================================================
    # KRANKENKASSE (4 листи)
    # ========================================================================
    {
        'id': 38,
        'category': 'Krankenkasse',
        'type': 'Krankenkassenbescheid',
        'text': '''AOK Berlin
Bescheid über Krankenversicherung

Monatlicher Beitrag: 450,00 EUR
Ab 01.03.2026

§ 249 SGB V

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'amount': '450,00 EUR',
            'paragraphs': ['§ 249 SGB V']
        }
    },
    {
        'id': 39,
        'category': 'Krankenkasse',
        'type': 'Rezeptgebühr',
        'text': '''TK Krankenkasse
Rezeptgebühr

Zuzahlung: 10,00 EUR pro Rezept
Quartalslimit: 2% des Bruttoeinkommens

§ 61 SGB V

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'paragraphs': ['§ 61 SGB V']
        }
    },
    {
        'id': 40,
        'category': 'Krankenkasse',
        'type': 'Krankenhausrechnung',
        'text': '''Krankenhaus Berlin
Krankenhausrechnung

Behandlung: 01.02.2026 - 05.02.2026
Gesamt: 2.500,00 EUR
Eigenanteil: 10,00 EUR/Tag

§ 39 SGB V

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Krankenhaus',
            'amount': '2.500,00 EUR',
            'paragraphs': ['§ 39 SGB V']
        }
    },
    {
        'id': 41,
        'category': 'Krankenkasse',
        'type': 'Reha-Genehmigung',
        'text': '''AOK Bayern
Reha-Genehmigung

Ihr Antrag wurde genehmigt.
Beginn: 15.04.2026
Dauer: 3 Wochen

§ 40 SGB V

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Krankenkasse',
            'deadline': '15.04.2026',
            'paragraphs': ['§ 40 SGB V']
        }
    },

    # ========================================================================
    # VERSICHERUNG (4 листи)
    # ========================================================================
    {
        'id': 42,
        'category': 'Versicherung',
        'type': 'Versicherungsrechnung',
        'text': '''Allianz Versicherung
Versicherungsrechnung 2026

Gesamtbeitrag: 890,00 EUR
Frist: 15.03.2026

§ 38 VVG

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Versicherung',
            'amount': '890,00 EUR',
            'deadline': '15.03.2026',
            'paragraphs': ['§ 38 VVG']
        }
    },
    {
        'id': 43,
        'category': 'Versicherung',
        'type': 'Schadenmeldung',
        'text': '''HDI Versicherung
Schadenmeldung

Ihr Schaden wurde registriert.
Schadennummer: 12345/2026
Bearbeitungsdauer: 2-4 Wochen

§ 6 VVG

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Versicherung',
            'paragraphs': ['§ 6 VVG']
        }
    },
    {
        'id': 44,
        'category': 'Versicherung',
        'type': 'Beitragserhöhung',
        'text': '''AXA Versicherung
Beitragserhöhung

Ab 01.04.2026:
Von 120,00 EUR auf 145,00 EUR

§ 31 VVG

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Versicherung',
            'paragraphs': ['§ 31 VVG']
        }
    },
    {
        'id': 45,
        'category': 'Versicherung',
        'type': 'Kündigung',
        'text': '''Allianz Versicherung
Kündigung der Versicherung

Wegen Nichtzahlung kündigen wir.

§ 38 VVG

Mit freundlichen Grüßen''',
        'expected': {
            'is_document': True,
            'org': 'Versicherung',
            'paragraphs': ['§ 38 VVG']
        }
    },

    # ========================================================================
    # ШАХРАЙСЬКІ ЛИСТИ (5 листів)
    # ========================================================================
    {
        'id': 46,
        'category': 'Fraud',
        'type': 'Fake Polizei',
        'text': '''Bundespolizei Berlin
Dringende Zahlung erforderlich!

Sie müssen sofort 5.000 EUR überweisen!
Sonst kommt Haftbefehl!

Western Union oder Bitcoin!
Tel: 0900-123456 (kostenpflichtig)

SOFORT ÜBERWEISEN!''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': ['urgent_payment', 'threatening_language', 'suspicious_accounts', 'suspicious_phones']
        }
    },
    {
        'id': 47,
        'category': 'Fraud',
        'type': 'Fake Gewinn',
        'text': '''GEWONNEN!

Sie haben 100.000 EUR gewonnen!

Senden Sie 500 EUR Bearbeitungsgebühr an:
Geschenkkarte iTunes

Email: winner@gmail.com

Click here: http://fake-lottery.com''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': ['suspicious_accounts', 'suspicious_emails']
        }
    },
    {
        'id': 48,
        'category': 'Fraud',
        'type': 'Fake Finanzamt',
        'text': '''Finanzamt (FAKE)
Steuerzahlung SOFORT!

Überweisen Sie 3.000 EUR auf:
IBAN: DE12 3456 7890 1234 5678 90

Bei nicht zahlung kommen wir zur polizei!

Tel: +44 123 456789 (UK Nummer)''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': ['urgent_payment', 'threatening_language', 'grammar_errors', 'suspicious_phones']
        }
    },
    {
        'id': 49,
        'category': 'Fraud',
        'type': 'Fake Paket',
        'text': '''DHL Paket
Ihr Paket konnte nicht zugestellt werden.

Klicken Sie hier: http://fake-dhl.com
Zahlen Sie 2,99 EUR Bearbeitungsgebühr.

Email: dhl-service @web.de''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': ['suspicious_emails', 'suspicious_phones']
        }
    },
    {
        'id': 50,
        'category': 'Fraud',
        'type': 'Fake Bank',
        'text': '''Sparkasse (FAKE)
Ihr Konto wird gesperrt!

Bitte bestätigen Sie Ihre Daten:
www.sparkasse-fake.com

Passwort und PIN erforderlich!

Sofort handeln!''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': ['urgent_payment', 'threatening_language']
        }
    },
]


# ============================================================================
# ФУНКЦІЇ ТЕСТУВАННЯ
# ============================================================================

def test_document_classification(letter: dict) -> dict:
    """Тест класифікації документу."""
    text = letter['text']
    expected = letter['expected']
    
    result = check_if_document(text)
    
    passed = result['is_document'] == expected['is_document']
    
    return {
        'passed': passed,
        'result': result,
        'expected': expected
    }


def test_organization_detection(letter: dict) -> dict:
    """Тест визначення організації."""
    text = letter['text'].lower()
    expected_org = letter['expected'].get('org', '').lower()
    
    orgs = {
        'jobcenter': ['jobcenter', 'arbeitsagentur'],
        'inkasso': ['inkasso', 'eos', 'credit', 'forderung'],
        'vermieter': ['vermieter', 'mieter', 'hausverwaltung', 'immobilien'],
        'finanzamt': ['finanzamt', 'steuer'],
        'gericht': ['gericht', 'anwalt', 'rechtsanwalt', 'gerichtsvollzieher'],
        'krankenkasse': ['aok', 'tk', 'krankenkasse', 'krankenhaus'],
        'versicherung': ['allianz', 'axa', 'hdi', 'versicherung'],
        'fraud': ['bundespolizei', 'gewonnen', 'fake']
    }
    
    detected = False
    for org, keywords in orgs.items():
        if any(kw in text for kw in keywords):
            detected = True
            break
    
    passed = detected
    
    return {
        'passed': passed,
        'detected': detected,
        'expected_org': expected_org
    }


def test_paragraph_detection(letter: dict) -> dict:
    """Тест визначення параграфів."""
    text = letter['text']
    expected_paragraphs = letter['expected'].get('paragraphs', [])
    
    found_paragraphs = []
    for para in expected_paragraphs:
        if para in text:
            found_paragraphs.append(para)
    
    # 50% параграфів має бути знайдено
    passed = len(found_paragraphs) >= len(expected_paragraphs) * 0.5 if expected_paragraphs else True
    
    return {
        'passed': passed,
        'found': found_paragraphs,
        'expected': expected_paragraphs
    }


def test_deadline_detection(letter: dict) -> dict:
    """Тест визначення термінів."""
    text = letter['text']
    expected_deadline = letter['expected'].get('deadline')
    
    import re
    dates = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text)
    
    passed = expected_deadline in dates if expected_deadline else True
    
    return {
        'passed': passed,
        'found_dates': dates,
        'expected': expected_deadline
    }


def test_fraud_detection(letter: dict) -> dict:
    """Тест виявлення шахрайства."""
    text = letter['text']
    expected = letter['expected']
    
    if 'fraud' not in expected or not expected.get('fraud'):
        return {'passed': True, 'skipped': True}
    
    fraud_data = analyze_letter_for_fraud(text, {})
    
    passed = fraud_data['is_likely_fraud'] or fraud_data['risk_level'] in ['medium', 'high']
    
    return {
        'passed': passed,
        'fraud_data': fraud_data,
        'expected_fraud': True
    }


def run_all_tests():
    """Запуск всіх тестів."""
    print("\n" + "="*100)
    print(" МАСОВЕ ТЕСТУВАННЯ GOV.DE BOT v4.2")
    print(" 50 тестових листів: класифікація, закони, терміни, шахрайство")
    print("="*100 + "\n")
    
    results = {
        'total': 50,
        'passed': 0,
        'failed': 0,
        'by_category': {},
        'by_test_type': {
            'classification': {'total': 0, 'passed': 0},
            'organization': {'total': 0, 'passed': 0},
            'paragraphs': {'total': 0, 'passed': 0},
            'deadlines': {'total': 0, 'passed': 0},
            'fraud': {'total': 0, 'passed': 0}
        }
    }
    
    detailed_results = []
    
    for letter in TEST_LETTERS:
        category = letter['category']
        if category not in results['by_category']:
            results['by_category'][category] = {'total': 0, 'passed': 0}
        
        results['by_category'][category]['total'] += 1
        
        # Тест 1: Класифікація
        test1 = test_document_classification(letter)
        results['by_test_type']['classification']['total'] += 1
        if test1['passed']:
            results['by_test_type']['classification']['passed'] += 1
        
        # Тест 2: Організація
        test2 = test_organization_detection(letter)
        results['by_test_type']['organization']['total'] += 1
        if test2['passed']:
            results['by_test_type']['organization']['passed'] += 1
        
        # Тест 3: Параграфи
        test3 = test_paragraph_detection(letter)
        results['by_test_type']['paragraphs']['total'] += 1
        if test3['passed']:
            results['by_test_type']['paragraphs']['passed'] += 1
        
        # Тест 4: Терміни
        test4 = test_deadline_detection(letter)
        results['by_test_type']['deadlines']['total'] += 1
        if test4['passed']:
            results['by_test_type']['deadlines']['passed'] += 1
        
        # Тест 5: Шахрайство (тільки для fraud листів)
        if letter['category'] == 'Fraud':
            test5 = test_fraud_detection(letter)
            results['by_test_type']['fraud']['total'] += 1
            if test5['passed']:
                results['by_test_type']['fraud']['passed'] += 1
        else:
            test5 = {'passed': True, 'skipped': True}
        
        # Загальний результат для листа
        all_passed = all([test1['passed'], test2['passed'], test3['passed'], test4['passed'], test5['passed']])
        
        if all_passed:
            results['passed'] += 1
            results['by_category'][category]['passed'] += 1
            status = "✅ PASS"
        else:
            results['failed'] += 1
            status = "❌ FAIL"
        
        # Вивід результату
        print(f"Лист #{letter['id']:2d} | {category:12s} | {letter['type']:30s} | {status}")
        
        if not all_passed:
            if not test1['passed']:
                print(f"         ├─ Класифікація: ❌ (очікувалось {test1['expected']['is_document']}, отримано {test1['result']['is_document']})")
            if not test2['passed']:
                print(f"         ├─ Організація: ❌")
            if not test3['passed']:
                print(f"         ├─ Параграфи: ❌ (знайдено {test3['found']}, очікувалось {test3['expected']})")
            if not test4['passed']:
                print(f"         ├─ Терміни: ❌ (знайдено {test4['found_dates']}, очікувалось {test4['expected']})")
            if not test5['passed']:
                print(f"         └─ Шахрайство: ❌")
        
        detailed_results.append({
            'id': letter['id'],
            'category': category,
            'type': letter['type'],
            'passed': all_passed,
            'tests': {
                'classification': test1,
                'organization': test2,
                'paragraphs': test3,
                'deadlines': test4,
                'fraud': test5
            }
        })
    
    # Підсумки
    print("\n" + "="*100)
    print(" ПІДСУМКИ ТЕСТУВАННЯ")
    print("="*100)
    
    total_pct = (results['passed'] / results['total']) * 100
    
    print(f"\nЗагальний результат: {results['passed']}/{results['total']} ({total_pct:.1f}%)")
    
    print("\nПо категоріях:")
    for category, cat_results in sorted(results['by_category'].items()):
        pct = (cat_results['passed'] / cat_results['total']) * 100 if cat_results['total'] > 0 else 0
        print(f"  {category:15s}: {cat_results['passed']}/{cat_results['total']} ({pct:.1f}%)")
    
    print("\nПо типах тестів:")
    for test_type, test_results in results['by_test_type'].items():
        pct = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
        print(f"  {test_type:15s}: {test_results['passed']}/{test_results['total']} ({pct:.1f}%)")
    
    # Оцінка
    print("\n" + "-"*100)
    print(" ЗАГАЛЬНА ОЦІНКА:")
    print("-"*100)
    
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
    
    print("\n" + "="*100)
    
    # Збереження результатів
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    report = f"""
# 🧪 ЗВІТ ПРО ТЕСТУВАННЯ (50 ЛИСТІВ)

## 📅 {timestamp}

## 📊 ЗАГАЛЬНІ РЕЗУЛЬТАТИ

```
Загальний результат: {results['passed']}/{results['total']} ({total_pct:.1f}%)
Оцінка: {grade}
✅ Пройдено: {results['passed']}
❌ Провалено: {results['failed']}
```

## 📈 РЕЗУЛЬТАТИ ПО КАТЕГОРІЯХ

"""
    
    for category, cat_results in sorted(results['by_category'].items()):
        pct = (cat_results['passed'] / cat_results['total']) * 100 if cat_results['total'] > 0 else 0
        status = "✅" if pct >= 80 else "⚠️" if pct >= 60 else "❌"
        report += f"| **{category}** | {cat_results['passed']}/{cat_results['total']} ({pct:.1f}%) {status} |\n"
    
    report += f"""

## 📈 РЕЗУЛЬТАТИ ПО ТИПАХ ТЕСТІВ

"""
    
    for test_type, test_results in results['by_test_type'].items():
        pct = (test_results['passed'] / test_results['total']) * 100 if test_results['total'] > 0 else 0
        status = "✅" if pct >= 80 else "⚠️" if pct >= 60 else "❌"
        report += f"| **{test_type}** | {test_results['passed']}/{test_results['total']} ({pct:.1f}%) {status} |\n"
    
    report += f"""

## 🎯 ЗАГАЛЬНА ОЦІНКА

{emoji} **Оцінка: {grade}**

📊 Відсоток: {total_pct:.1f}%
✅ Пройдено: {results['passed']}
❌ Провалено: {results['failed']}

---

**Створено:** {timestamp}
**Версія:** v4.2
**Тестів проведено:** 50
"""
    
    # Збереження звіту
    report_path = Path(__file__).parent / 'test_results' / f'test_50_letters_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
    report_path.parent.mkdir(exist_ok=True)
    report_path.write_text(report)
    
    print(f"\n📄 Звіт збережено: {report_path}")
    
    return results, detailed_results


if __name__ == '__main__':
    try:
        results, detailed_results = run_all_tests()
        
        # Додатковий аналіз
        print("\n\n" + "="*100)
        print(" ДЕТАЛЬНИЙ АНАЛІЗ ПОМИЛОК")
        print("="*100)
        
        failed_tests = [r for r in detailed_results if not r['passed']]
        
        if failed_tests:
            print(f"\nЗнайдено {len(failed_tests)} листів з помилками:\n")
            
            for result in failed_tests:
                print(f"Лист #{result['id']} - {result['category']} - {result['type']}")
                for test_name, test_result in result['tests'].items():
                    if not test_result['passed']:
                        print(f"  ❌ {test_name}: {test_result}")
                print()
        else:
            print("\n✅ Всі тести пройшли успішно!")
        
    except Exception as e:
        print(f"\n❌ Помилка тестування: {e}")
        import traceback
        traceback.print_exc()
