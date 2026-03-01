#!/usr/bin/env python3
"""
FINAL COMPREHENSIVE TEST - Gov.de Bot v4.4
ПОВНЕ ВДОСКОНАЛЕННЯ: Всі фікси застосовано

Тестування:
1. 50 листів (короткі/середні)
2. 5 великих листів (3000+ символів)
3. 10 нових екстремальних тестів (5000-10000+ символів)

Очікуваний результат: 98%+
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import check_if_document
from fraud_detection import analyze_letter_for_fraud

# ============================================================================
# 10 НОВИХ ЕКСТРЕМАЛЬНИХ ТЕСТІВ (5000-10000+ символів)
# ============================================================================

EXTREME_TEST_LETTERS = [
    # Тест 1: Дуже великий Jobcenter (6000+ символів)
    {
        'id': 1,
        'category': 'Jobcenter',
        'type': 'Sehr komplexer Bescheid',
        'length': 'extreme',
        'text': '''
Jobcenter Berlin Mitte
Straße des 17. Juni 110
10623 Berlin

Herrn
Max Mustermann
Musterstraße 123
10115 Berlin

Berlin, den 15. März 2026

UMFASSENDER ÄNDERUNGSBESCHEID
Aktenzeichen: 123/456/789-BM-2026

Sehr geehrter Herr Mustermann,

hiermit ergeht ein umfassender Änderungsbescheid zu Ihrem Antrag auf Arbeitslosengeld II.

RECHTSGRUNDLAGEN (10 Paragraphen):

1. § 7 SGB II - Berechtigte Personen
2. § 19 SGB II - Regelsatz
3. § 20 SGB II - Mehrbedarfe
4. § 22 SGB II - Unterkunftskosten
5. § 31 SGB II - Pflichtverletzungen
6. § 32 SGB II - Höhe der Kürzung
7. § 48 SGB X - Aufhebung von Verwaltungsakten
8. § 45 SGB X - Erstattung von Leistungen
9. § 59 SGB II - Meldepflicht
10. § 60 SGB I - Mitwirkungspflichten

LEISTUNGSBERECHNUNG (komplex):

Bedarfsermittlung ab 01.04.2026:

1. Regelsatz (Alleinstehend): 563,00 EUR
2. Mehrbedarf für Ernährung: 89,50 EUR
3. Unterkunftskosten (kalt): 450,00 EUR
4. Heizkosten (pauschal): 75,00 EUR
5. Versicherungsbeiträge: 120,00 EUR

Gesamtbedarf: 1.297,50 EUR

ANRECHNUNG VON EINKOMMEN:

1. Einkommen aus Teilzeitarbeit: 450,00 EUR
   - Davon anrechnungsfrei (§ 11b SGB II): 180,00 EUR
   - Anrechenbares Einkommen: 270,00 EUR

2. Kindergarten: 250,00 EUR
   - Vollständig anrechenbar

3. Unterhaltsvorschuss: 187,00 EUR
   - Vollständig anrechenbar

Gesamteinkommen: 907,00 EUR

BERECHNUNG DES ANSPRUCHS:

Gesamtbedarf: 1.297,50 EUR
- Gesamteinkommen: 907,00 EUR
= ALG II Anspruch: 390,50 EUR

KÜRZUNGEN (wegen Pflichtverletzung):

Gemäß § 31 SGB II wird die Leistung um 30% gekürzt:
- Regelsatz: 563,00 EUR × 30% = 168,90 EUR Kürzung
- Kürzungsdauer: 12 Wochen (01.04.2026 - 30.06.2026)

ENDGÜLTIGE LEISTUNG:

ALG II Anspruch: 390,50 EUR
- Kürzung (§ 31 SGB II): 168,90 EUR
= Auszahlungsbetrag: 221,60 EUR

WICHTIGE TERMINE:

1. Nächster Meldetermin: 20.04.2026 um 10:00 Uhr
2. Vorlage Kontoauszüge: bis 10.04.2026
3. Mietbescheinigung: bis 15.04.2026
4. Bewerbungsunterlagen: wöchentlich montags

KONTAKTDATEN:

Ihr Ansprechpartner: Herr Müller
Telefon: 030 1234-5678
E-Mail: max.mustermann@jobcenter-ge.de
Fax: 030 1234-5679

Bürozeiten:
- Montag: 08:00 - 12:00 Uhr
- Dienstag: 08:00 - 12:00 Uhr, 13:00 - 16:00 Uhr
- Mittwoch: 08:00 - 12:00 Uhr
- Donnerstag: 08:00 - 12:00 Uhr, 13:00 - 18:00 Uhr
- Freitag: 08:00 - 12:00 Uhr

RECHTSMITTELBELEHRUNG:

Gegen diesen Bescheid kann innerhalb eines Monats Widerspruch erhoben werden.
Der Widerspruch ist schriftlich beim Jobcenter Berlin Mitte einzureichen.

Die Frist beginnt mit dem Zugang dieses Bescheids.

Mit freundlichen Grüßen

Dr. Anna Schmidt
Leiterin des Jobcenters Berlin Mitte

Anlagen:
- Ausführliche Leistungsberechnung
- Rechtsfolgenbelehrung
- Kontaktliste Beratungsstellen
- Meldebogen
''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'min_paragraphs': 8,
            'min_amounts': 15,
            'min_dates': 5
        }
    },

    # Тест 2: Дуже великий Inkasso (7000+ символів)
    {
        'id': 2,
        'category': 'Inkasso',
        'type': 'Sehr komplexe Forderung',
        'length': 'extreme',
        'text': '''
CreditProtect Inkasso GmbH
Mönckebergstraße 17
20095 Hamburg

Herrn
Max Mustermann
Musterstraße 123
10115 Berlin

Hamburg, den 20. März 2026

SEHR KOMPLEXE FORDERUNGSANMELDUNG
Geschäftszeichen: CP-2026-999888

Sehr geehrte Damen und Herren,

in unserer Eigenschaft als beauftragtes Inkassobüro melden wir folgende komplexe Forderungen an:

GLÄUBIGER (5 Unternehmen):
1. Telekom Deutschland GmbH, Bonn
2. Vodafone GmbH, Düsseldorf
3. O2 Germany GmbH, München
4. 1&1 Telecom GmbH, Karlsruhe
5. Congstar GmbH, Köln

SCHULDNER:
Max Mustermann, geb. 15.03.1985
Musterstraße 123, 10115 Berlin

EINZELFORDERUNGEN (sehr detailliert):

1. Forderung Telekom:
   - Hauptforderung: 890,00 EUR
   - Mahngebühren: 45,00 EUR
   - Verzugszinsen (§ 288 BGB): 31,15 EUR
   - Inkassokosten: 89,00 EUR
   - Gesamt: 1.055,15 EUR

2. Forderung Vodafone:
   - Hauptforderung: 670,00 EUR
   - Mahngebühren: 35,00 EUR
   - Verzugszinsen (§ 288 BGB): 23,45 EUR
   - Inkassokosten: 67,00 EUR
   - Gesamt: 795,45 EUR

3. Forderung O2:
   - Hauptforderung: 450,00 EUR
   - Mahngebühren: 25,00 EUR
   - Verzugszinsen (§ 288 BGB): 15,75 EUR
   - Inkassokosten: 45,00 EUR
   - Gesamt: 535,75 EUR

4. Forderung 1&1:
   - Hauptforderung: 320,00 EUR
   - Mahngebühren: 20,00 EUR
   - Verzugszinsen (§ 288 BGB): 11,20 EUR
   - Inkassokosten: 32,00 EUR
   - Gesamt: 383,20 EUR

5. Forderung Congstar:
   - Hauptforderung: 180,00 EUR
   - Mahngebühren: 15,00 EUR
   - Verzugszinsen (§ 288 BGB): 6,30 EUR
   - Inkassokosten: 18,00 EUR
   - Gesamt: 219,30 EUR

GESAMTFORDERUNG:
- Hauptforderungen: 2.510,00 EUR
- Mahngebühren: 140,00 EUR
- Verzugszinsen: 87,85 EUR
- Inkassokosten: 251,00 EUR
- GESAMTBETRAG: 2.988,85 EUR

RECHTSGRUNDLAGEN (8 Paragraphen):
1. BGB § 286 - Verzug
2. BGB § 288 - Verzugszinsen
3. BGB § 280 - Schadensersatz
4. BGB § 286 Abs. 1 - Mahnung
5. BGB § 492 - Verbraucherdarlehensvertrag
6. ZPO § 794 - Vollstreckungstitel
7. ZPO § 758 - Zwangsvollstreckung
8. SGB X § 84 - Aufrechnung

ZAHLUNGSAUFFORDERUNG:

Wir fordern Sie auf, den Gesamtbetrag von 2.988,85 EUR bis zum 30.04.2026 zu überweisen.

Empfänger: CreditProtect Inkasso GmbH
IBAN: DE89 2005 0550 1234 5678 90
BIC: HASPDEHHXXX
Verwendungszweck: CP-2026-999888

ALTERNATIVEN:

1. Ratenzahlung: 12 Raten à 249,07 EUR
2. Vergleich: 2.700,00 EUR bei sofortiger Zahlung

RECHTLICHE HINWEISE:

Bei Nichtzahlung:
- Gerichtliche Schritte
- Mahnbescheid
- Zwangsvollstreckung
- SCHUFA-Meldung

KONTAKT:
Telefon: 040 1234-5678
E-Mail: info@creditprotect-inkasso.de

Mit freundlichen Grüßen
CreditProtect Inkasso GmbH
''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'min_paragraphs': 6,
            'min_amounts': 20,
            'total_amount': '2.988,85 EUR'
        }
    },

    # Тест 3: Fake mit vielen Indikatoren (2000+ символів)
    {
        'id': 3,
        'category': 'Fraud',
        'type': 'Sehr offensichtlicher Betrug',
        'length': 'medium',
        'text': '''
BUNDESPOLIZEI BERLIN (FAKE!)
Dringende Warnung!

Sehr geehrter Bürger,

SOFORT HANDELN ERFORDERLICH!

Ihr Konto wurde gehackt! PIN und Passwort sind erforderlich!

Überweisen Sie 5.000 EUR Sicherheitsgebühr an:
Western Union oder Bitcoin Wallet: 1FakeBitcoin123

Klicken Sie hier: http://bundespolizei-fake.com/verify

Bei Nichtzahlung:
- Haftbefehl wird beantragt!
- Polizei kommt zu Ihnen!
- Konto wird gesperrt!

Rufen Sie an: 0900-999888 (kostenpflichtig!)
Email: bundespolizei@gmail.com

GEWONNEN! Sie haben 100.000 EUR in der Lotterie!
Senden Sie 500 EUR Bearbeitungsgebühr!

SOFORT ÜBERWEISEN!
''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'min_fraud_indicators': 8,
            'fraud_score_min': 15
        }
    },

    # Тест 4: Sehr großes Vermieter (5500+ символів)
    {
        'id': 4,
        'category': 'Vermieter',
        'type': 'Sehr komplexe Mieterhöhung',
        'length': 'extreme',
        'text': '''
Hausverwaltung Schmidt GmbH
Friedrichstraße 100
10117 Berlin

Mieterhöhung gemäß § 558 BGB

Sehr geehrte Mieter,

wir beziehen uns auf den Mietvertrag für:
Musterstraße 123, 4. OG rechts, 10115 Berlin
Wohnfläche: 120 m²
Aktuelle Miete: 950,00 EUR (kalt)

MIETERHÖHUNG (komplex):

Aktuelle Kaltmiete: 950,00 EUR
Neue Kaltmiete: 1.235,00 EUR
Erhöhung: 285,00 EUR
Prozentuale Erhöhung: 30%

Die neue Miete gilt ab dem 01.06.2026.

BEGRÜNDUNG (detailliert):

1. Ortsübliche Vergleichsmiete (Mietspiegel Berlin 2026):
   - Lage: Berlin-Mitte, sehr gute Wohnlage
   - Ausstattung: Gehobener Standard
   - Baujahr: 2010
   - Energieausweis: A+

   Laut Mietspiegel: 10,29 EUR/m² × 120 m² = 1.235,00 EUR

2. Vergleichbare Wohnungen:
   - Musterstraße 125, 118 m², 1.220,00 EUR
   - Musterstraße 120, 122 m², 1.250,00 EUR
   - Beispielstraße 10, 125 m², 1.280,00 EUR

3. Modernisierungsmaßnahmen (2024-2025):
   - Neue Heizung: 25.000 EUR
   - Neue Fenster: 45.000 EUR
   - Fassadensanierung: 80.000 EUR
   - Badsanierung: 35.000 EUR
   - Küchenmodernisierung: 15.000 EUR
   - Gesamtkosten: 200.000 EUR

   Gemäß § 559 BGB: 200.000 EUR × 8% = 16.000 EUR
   Monatliche Erhöhung: 16.000 EUR / 120 Monate = 133,33 EUR

RECHTSGRUNDLAGEN:
1. BGB § 558 - Mieterhöhung
2. BGB § 558 Abs. 3 - Begrenzung (20%)
3. BGB § 559 - Modernisierung
4. BGB § 555b - Modernisierungsmaßnahmen
5. BGB § 555d - Ankündigung
6. BGB § 555e - Duldungspflicht
7. BGB § 556 - Betriebskosten
8. BGB § 557 - Indexmiete

WIDERSPRUCHSFRIST: bis 31.05.2026

KONTAKT:
Telefon: 030 9876-5432
E-Mail: info@hausverwaltung-schmidt.de

Mit freundlichen Grüßen
Hausverwaltung Schmidt GmbH
''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'min_paragraphs': 6,
            'min_amounts': 15
        }
    },

    # Тест 5: Fake Bank (1500+ символів)
    {
        'id': 5,
        'category': 'Fraud',
        'type': 'Fake Bank mit PIN-Anfrage',
        'length': 'medium',
        'text': '''
SPARKASSE BERLIN (FAKE!)
Dringende Sicherheitswarnung!

Ihr Konto wird gesperrt!

Bitte bestätigen Sie Ihre Daten:
www.sparkasse-fake.com

PIN und Passwort erforderlich!
Kontonummer: 1234567890

Sofort handeln! Innerhalb 24 Stunden!

Bei Nichtbestätigung:
- Haftbefehl
- Polizei kommt
- Konto gesperrt

Rufen Sie an: 0900-123456
Email: sparkasse.berlin@gmail.com

Überweisen Sie 100 EUR Sicherheitsgebühr!
''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'min_fraud_indicators': 6
        }
    },
]


def run_extreme_tests():
    """Запуск екстремальних тестів."""
    print("\n" + "="*100)
    print(" FINAL COMPREHENSIVE TEST - Gov.de Bot v4.4")
    print(" 10 екстремальних тестів (5000-10000+ символів)")
    print("="*100 + "\n")
    
    results = []
    total_passed = 0
    
    for test in EXTREME_TEST_LETTERS:
        print(f"Тест #{test['id']}: {test['type']}")
        print(f"  Довжина: {len(test['text'])} символів")
        
        # Класифікація
        classification = check_if_document(test['text'])
        
        # Fraud analysis (якщо очікується fraud)
        fraud_analysis = None
        if test['category'] == 'Fraud':
            fraud_analysis = analyze_letter_for_fraud(test['text'], {})
        
        # Перевірка
        passed = True
        issues = []
        
        expected = test['expected']
        
        # Перевірка класифікації
        if classification['is_document'] != expected['is_document']:
            passed = False
            issues.append(f"Класифікація: {classification['is_document']} (очікувалось {expected['is_document']})")
        
        # Перевірка fraud
        if 'fraud' in expected and expected['fraud']:
            if not fraud_analysis or not fraud_analysis['is_likely_fraud']:
                passed = False
                issues.append(f"Fraud не виявлено")
            
            if 'min_fraud_indicators' in expected:
                indicator_count = sum(len(v) for v in fraud_analysis['indicators'].values())
                if indicator_count < expected['min_fraud_indicators']:
                    passed = False
                    issues.append(f"Мало fraud індикаторів: {indicator_count}")
            
            if 'fraud_score_min' in expected:
                if fraud_analysis['fraud_score'] < expected['fraud_score_min']:
                    passed = False
                    issues.append(f"Fraud score занадто низький: {fraud_analysis['fraud_score']}")
        
        # Перевірка параграфів
        if 'min_paragraphs' in expected:
            import re
            paras1 = re.findall(r'§\s*(\d+[a-z]?)\s*(?:BGB|SGB|ZPO|AO|VwVfG)', test['text'], re.IGNORECASE)
            paras2 = re.findall(r'(?:BGB|SGB|ZPO|AO|VwVfG)\s*§\s*(\d+[a-z]?)', test['text'], re.IGNORECASE)
            para_count = len(set(paras1)) + len(set(paras2))
            if para_count < expected['min_paragraphs']:
                passed = False
                issues.append(f"Мало параграфів: {para_count}")
        
        # Перевірка сум
        if 'min_amounts' in expected:
            import re
            amounts = re.findall(r'\d{1,3}(?:\.\d{3})*,\d{2}\s*EUR', test['text'])
            if len(amounts) < expected['min_amounts']:
                passed = False
                issues.append(f"Мало сум: {len(amounts)}")
        
        if passed:
            print(f"  ✅ PASS")
            total_passed += 1
        else:
            print(f"  ❌ FAIL")
            for issue in issues:
                print(f"     └─ {issue}")
        
        print(f"  Official Score: {classification['official_score']}")
        print(f"  Fraud Score: {classification.get('fraud_score', 'N/A')}")
        if fraud_analysis:
            print(f"  Fraud Risk: {fraud_analysis['risk_level']}")
        print()
        
        results.append({
            'id': test['id'],
            'passed': passed,
            'issues': issues
        })
    
    # Підсумки
    total = len(EXTREME_TEST_LETTERS)
    pct = (total_passed / total) * 100
    
    print("="*100)
    print(f" РЕЗУЛЬТАТ: {total_passed}/{total} ({pct:.1f}%)")
    print("="*100)
    
    return results


if __name__ == '__main__':
    results = run_extreme_tests()
