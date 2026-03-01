#!/usr/bin/env python3
"""
Тестування на ВЕЛИКИХ ЛИСТАХ (3000+ символів)
Gov.de Bot v4.3 - Long Document Analysis Test

Перевірка:
1. Обробка довгих текстів (3000-10000+ символів)
2. Множинні посилання на закони
3. Аналіз перекладу ключових термінів
4. Виявлення всіх дедлайнів
5. Комплексний аналіз шахрайства
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

from client_bot_functions import check_if_document, get_paragraph_description, create_simple_analysis, generate_detailed_response
from fraud_detection import analyze_letter_for_fraud, extract_phone_numbers, extract_emails, extract_websites
from response_generator import generate_response

# ============================================================================
# ВЕЛИКІ ТЕСТОВІ ЛИСТИ (3000-10000+ символів)
# ============================================================================

LONG_TEST_LETTERS = [
    # ========================================================================
    # ЛИСТ 1: Jobcenter - Комплексний Sanktionsbescheid (4500+ символів)
    # ========================================================================
    {
        'id': 1,
        'category': 'Jobcenter',
        'type': 'Komplexer Sanktionsbescheid',
        'length': 'long',
        'text': '''
Jobcenter Berlin Mitte
Straße des 17. Juni 110
10623 Berlin

Herrn
Max Mustermann
Musterstraße 123
10115 Berlin

Berlin, den 15. Februar 2026

BESCHEID ÜBER LEISTUNGSKÜRZUNG
Aktenzeichen: 123/456/789-BM

Sehr geehrter Herr Mustermann,

hiermit teilen wir Ihnen mit, dass Ihre Leistungen zur Sicherung des Lebensunterhalts nach dem Zweiten Buch Sozialgesetzbuch (SGB II) gekürzt werden.

RECHTSGRUNDLAGEN:

1. § 59 SGB II - Meldepflicht
   Sie sind verpflichtet, zu allen Terminen im Jobcenter zu erscheinen.

2. § 31 SGB II - Pflichtverletzungen bei Eingliederungsvereinbarung
   Bei unentschuldigtem Fehlen ohne wichtigen Grund wird die Leistung gekürzt.

3. § 32 SGB II - Höhe der Leistungskürzung
   Die Kürzung beträgt 30% für einen Zeitraum von 12 Wochen.

4. § 309 SGB III - Offizielle Einladungen
   Einladungen des Jobcenters sind offizielle Pflichtdokumente.

5. § 60 SGB I - Mitwirkungspflichten
   Sie müssen alle geforderten Unterlagen vorlegen.

SACHVERHALT:

Sie wurden zu folgenden Terminen eingeladen:

1. Termin am 10.01.2026 um 10:00 Uhr
   - Sie sind nicht erschienen
   - Keine Absage erfolgt
   - Keine ärztliche Bescheinigung vorgelegt

2. Termin am 24.01.2026 um 14:30 Uhr
   - Sie sind nicht erschienen
   - Keine Absage erfolgt
   - Keine ärztliche Bescheinigung vorgelegt

3. Termin am 07.02.2026 um 09:00 Uhr
   - Sie sind nicht erschienen
   - Keine Absage erfolgt
   - Keine ärztliche Bescheinigung vorgelegt

RECHTLICHE FOLGEN:

Aufgrund der wiederholten Pflichtverletzungen wird Ihre Leistung wie folgt gekürzt:

- Regelsatz: 563,00 EUR → 394,10 EUR (30% Kürzung)
- Kürzungsbetrag: 168,90 EUR pro Monat
- Kürzungszeitraum: 12 Wochen (84 Tage)
- Gesamtkürzung: 506,70 EUR

Die Kürzung beginnt ab dem 01.03.2026 und endet am 31.05.2026.

WICHTIGE INFORMATIONEN:

1. Rechtsfolgenbelehrung:
   Gegen diesen Bescheid können Sie innerhalb eines Monats Widerspruch einlegen.
   Der Widerspruch ist schriftlich beim Jobcenter Berlin Mitte einzureichen.

2. Mitwirkungspflichten:
   Sie müssen weiterhin alle Unterlagen vorlegen und zu Terminen erscheinen.
   Weitere Pflichtverletzungen können zu einer vollständigen Einstellung der Leistungen führen.

3. Krankmeldung:
   Bei Krankheit müssen Sie unverzüglich eine ärztliche Bescheinigung vorlegen.
   Die Bescheinigung muss innerhalb von 3 Tagen beim Jobcenter eingehen.

4. Beratung:
   Sie haben das Recht auf kostenlose Beratung durch:
   - Sozialverband Deutschland (SoVD)
   - Arbeiterwohlfahrt (AWO)
   - Caritas Beratungszentrum

5. Härtefallregelung:
   Bei besonderen Härtefällen kann die Kürzung aufgehoben werden.
   Ein Antrag auf Härtefallregelung ist schriftlich zu stellen.

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

NÄCHSTE SCHRITTE:

1. Überprüfen Sie diesen Bescheid sorgfältig.
2. Legen Sie ggf. Widerspruch innerhalb eines Monats ein.
3. Erscheinen Sie zu allen zukünftigen Terminen.
4. Reichen Sie alle geforderten Unterlagen fristgerecht ein.

RECHTSMITTELBELEHRUNG:

Gegen diesen Bescheid kann innerhalb eines Monats nach Bekanntgabe Widerspruch erhoben werden.
Der Widerspruch ist schriftlich oder zur Niederschrift bei der oben genannten Stelle einzulegen.

Die Frist beginnt mit dem Zugang dieses Bescheids.
Bei Einlegung des Widerspruchs per Post ist der Poststempel maßgeblich.

Mit freundlichen Grüßen

Im Auftrag

Unterschrift
Leiterin des Jobcenters Berlin Mitte
Dr. Anna Schmidt

Anlagen:
- Rechtsfolgenbelehrung
- Widerspruchsbegründung
- Kontaktliste Beratungsstellen
''',
        'expected': {
            'is_document': True,
            'org': 'Jobcenter',
            'paragraphs': ['§ 59 SGB II', '§ 31 SGB II', '§ 32 SGB II', '§ 309 SGB III', '§ 60 SGB I'],
            'amounts': ['563,00 EUR', '394,10 EUR', '168,90 EUR', '506,70 EUR'],
            'deadlines': ['10.01.2026', '24.01.2026', '07.02.2026', '01.03.2026', '31.05.2026'],
            'times': ['10:00', '14:30', '09:00'],
            'risk': '30% Kürzung für 12 Wochen',
            'contact': {
                'phone': '030 1234-5678',
                'email': 'max.mustermann@jobcenter-ge.de'
            }
        }
    },

    # ========================================================================
    # ЛИСТ 2: Inkasso - Komplexe Forderung mit mehreren Gläubigern (5000+ символів)
    # ========================================================================
    {
        'id': 2,
        'category': 'Inkasso',
        'type': 'Komplexe Forderungsanmeldung',
        'length': 'long',
        'text': '''
CreditProtect Inkasso GmbH
Hamburg, den 20. Februar 2026

FORDERUNGSANMELDUNG
Geschäftszeichen: CP-2026-123456

Sehr geehrte Damen und Herren,

in unserer Eigenschaft als beauftragtes Inkassobüro melden wir folgende Forderungen an:

GLÄUBIGER:
1. Telekom Deutschland GmbH, Landgrabenweg 151, 53227 Bonn
2. Vodafone GmbH, Ferdinand-Braun-Platz 1, 40549 Düsseldorf
3. O2 Germany GmbH & Co. OHG, Georg-Brauchle-Ring 50, 80992 München

SCHULDNER:
Max Mustermann
Musterstraße 123
10115 Berlin
Geburtsdatum: 15.03.1985

EINZELFORRUNGEN:

1. Forderung der Telekom Deutschland GmbH:
   - Rechnungsnummer: 12345-2025-12
   - Zeitraum: 01.10.2025 - 31.12.2025
   - Hauptforderung: 450,00 EUR
   - Mahngebühren: 25,00 EUR
   - Verzugszinsen (§ 288 BGB): 15,75 EUR
   - Inkassokosten: 50,00 EUR
   - Gesamt: 540,75 EUR

2. Forderung der Vodafone GmbH:
   - Rechnungsnummer: VF-98765-2026-01
   - Zeitraum: 15.11.2025 - 15.01.2026
   - Hauptforderung: 320,00 EUR
   - Mahngebühren: 20,00 EUR
   - Verzugszinsen (§ 288 BGB): 11,20 EUR
   - Inkassokosten: 45,00 EUR
   - Gesamt: 396,20 EUR

3. Forderung der O2 Germany GmbH & Co. OHG:
   - Rechnungsnummer: O2-555-2026-02
   - Zeitraum: 01.12.2025 - 31.01.2026
   - Hauptforderung: 180,00 EUR
   - Mahngebühren: 15,00 EUR
   - Verzugszinsen (§ 288 BGB): 6,30 EUR
   - Inkassokosten: 35,00 EUR
   - Gesamt: 236,30 EUR

GESAMTFORDERUNG:
- Hauptforderungen: 950,00 EUR
- Mahngebühren: 60,00 EUR
- Verzugszinsen: 33,25 EUR
- Inkassokosten: 130,00 EUR
- GESAMTBETRAG: 1.173,25 EUR

RECHTSGRUNDLAGEN:

1. BGB § 286 - Verzug des Schuldners
   Der Schuldner gerät nach Erhalt einer schriftlichen Mahnung in Verzug.

2. BGB § 288 - Verzugszinsen
   Für Verbraucher beträgt der Verzugszinssatz 5% p.a.

3. BGB § 280 - Schadensersatz wegen Pflichtverletzung
   Der Gläubiger kann Schadensersatz fordern.

4. BGB § 492 - Verbraucherdarlehensvertrag
   Besondere Vorschriften für Verbraucherverträge.

5. ZPO § 794 - Vollstreckungstitel
   Grundlage für die Zwangsvollstreckung.

ZAHLUNGSAUFFORDERUNG:

Wir fordern Sie auf, den Gesamtbetrag von 1.173,25 EUR bis zum 15.03.2026 auf folgendes Konto zu überweisen:

Empfänger: CreditProtect Inkasso GmbH
Bank: Hamburger Sparkasse
IBAN: DE89 2005 0550 1234 5678 90
BIC: HASPDEHHXXX
Verwendungszweck: CP-2026-123456

ALTERNATIVEN:

1. Ratenzahlungsvereinbarung:
   Wir bieten eine Ratenzahlung an:
   - 6 Raten à 195,54 EUR
   - Erste Rate: 15.03.2026
   - Letzte Rate: 15.08.2026

2. Vergleichsangebot:
   Bei sofortiger Zahlung erlassen wir 10% der Inkassokosten.
   Zahlungsbetrag: 1.160,25 EUR

RECHTLICHE HINWEISE:

1. Bei Nichtzahlung:
   - Einleitung gerichtlicher Schritte
   - Beantragung eines Mahnbescheids
   - Zwangsvollstreckung durch Gerichtsvollzieher

2. SCHUFA-Meldung:
   Bei Nichtzahlung erfolgt Meldung an SCHUFA.
   Negative Eintragung für 3 Jahre.

3. Kostenfolge:
   Bei gerichtlichen Schritten entstehen zusätzliche Kosten:
   - Gerichtskosten: ca. 150,00 EUR
   - Anwaltskosten: ca. 200,00 EUR
   - Gerichtsvollzieher: ca. 100,00 EUR

WIDERSPRUCH:

Gegen diese Forderungsanmeldung können Sie innerhalb von 14 Tagen Widerspruch einlegen.
Der Widerspruch ist schriftlich zu begründen.

KONTAKT:

CreditProtect Inkasso GmbH
Mönckebergstraße 17
20095 Hamburg

Telefon: 040 1234-5678
Telefax: 040 1234-5679
E-Mail: info@creditprotect-inkasso.de
Website: www.creditprotect-inkasso.de

Geschäftsführer: Dr. Hans Müller
Handelsregister: HRB 123456
USt-IdNr.: DE123456789

Mit freundlichen Grüßen

CreditProtect Inkasso GmbH

Unterschrift
Abteilungsleiter Forderungsmanagement
Thomas Schmidt

Anlagen:
- Kopien der Originalrechnungen
- Mahnbescheide
- Vertragsunterlagen
''',
        'expected': {
            'is_document': True,
            'org': 'Inkasso',
            'paragraphs': ['§ 286 BGB', '§ 288 BGB', '§ 280 BGB', '§ 492 BGB', '§ 794 ZPO'],
            'total_amount': '1.173,25 EUR',
            'creditors': ['Telekom', 'Vodafone', 'O2'],
            'deadline': '15.03.2026',
            'iban': 'DE89 2005 0550 1234 5678 90',
            'risk': 'Gerichtliche Schritte + SCHUFA'
        }
    },

    # ========================================================================
    # ЛИСТ 3: Vermieter - Komplexe Mieterhöhung mit Begründung (4000+ символів)
    # ========================================================================
    {
        'id': 3,
        'category': 'Vermieter',
        'type': 'Komplexe Mieterhöhung mit Begründung',
        'length': 'long',
        'text': '''
Hausverwaltung Schmidt GmbH
Immobilienverwaltung
Berlin, den 25. Februar 2026

MIETERHÖHUNG
gemäß § 558 BGB

Sehr geehrte Frau Mustermann,
sehr geehrter Herr Mustermann,

wir beziehen uns auf den Mietvertrag für die Wohnung:
Musterstraße 123, 4. OG rechts, 10115 Berlin
Wohnfläche: 75 m²
Aktuelle Miete: 650,00 EUR (kalt)
Nebenkosten: 150,00 EUR
Gesamtmiete: 800,00 EUR

MIETERHÖHUNG:

Gemäß § 558 BGB erhöhen wir die Miete wie folgt:

Aktuelle Kaltmiete: 650,00 EUR
Neue Kaltmiete: 780,00 EUR
Erhöhung: 130,00 EUR
Prozentuale Erhöhung: 20%

Die neue Miete gilt ab dem 01.05.2026.

BEGRÜNDUNG DER MIETERHÖHUNG:

1. Ortsübliche Vergleichsmiete (Mietspiegel Berlin 2026):
   - Lage: Berlin-Mitte, gute Wohnlage
   - Ausstattung: Standard
   - Baujahr: 1995
   - Energieausweis: B

   Laut Mietspiegel Berlin 2026 beträgt die ortsübliche Vergleichsmiete:
   10,40 EUR/m² × 75 m² = 780,00 EUR

2. Vergleichbare Wohnungen in der Umgebung:
   - Musterstraße 125, 75 m², 785,00 EUR
   - Musterstraße 120, 72 m², 750,00 EUR
   - Beispielstraße 10, 78 m², 810,00 EUR

3. Modernisierungsmaßnahmen (2024-2025):
   - Neue Heizung: 15.000 EUR
   - Neue Fenster: 25.000 EUR
   - Fassadensanierung: 50.000 EUR
   - Gesamtkosten: 90.000 EUR

   Gemäß § 559 BGB können 8% der Kosten umgelegt werden:
   90.000 EUR × 8% = 7.200 EUR
   Monatliche Erhöhung: 7.200 EUR / 120 Monate = 60,00 EUR

RECHTSGRUNDLAGEN:

1. BGB § 558 - Mieterhöhung bis zur ortsüblichen Vergleichsmiete
   Die Miete kann bis zur ortsüblichen Vergleichsmiete erhöht werden.

2. BGB § 558 Abs. 3 - Begrenzung der Mieterhöhung
   Die Erhöhung darf 20% innerhalb von 3 Jahren nicht überschreiten.

3. BGB § 559 - Mieterhöhung nach Modernisierung
   Nach Modernisierung kann die Miete um 8% der Kosten erhöht werden.

4. BGB § 555b - Modernisierungsmaßnahmen
   Definiert zulässige Modernisierungsmaßnahmen.

5. BGB § 555d - Ankündigung der Modernisierung
   Modernisierung muss 3 Monate vorher angekündigt werden.

WIDERSPRUCHSFRIST:

Sie können dieser Mieterhöhung innerhalb von 2 Monaten widersprechen.
Der Widerspruch ist schriftlich einzureichen.

Frist: bis 30.04.2026

Bei fristgerechtem Widerspruch bleibt die Miete unverändert.
Ohne Widerspruch gilt die Mieterhöhung als genehmigt.

BERATUNGSSTELLEN:

Bei Fragen wenden Sie sich an:
- Mieterbund Berlin: 030 4433-2200
- Verbraucherzentrale: 030 6980-2000
- Anwalt für Mietrecht: Dr. Weber, 030 1234-5678

NÄCHSTE SCHRITTE:

1. Überprüfen Sie die Mieterhöhung sorgfältig.
2. Holen Sie ggf. Beratung beim Mieterbund ein.
3. Legen Sie ggf. fristgerecht Widerspruch ein.
4. Unterzeichnen Sie die Mieterhöhungsvereinbarung bei Zustimmung.

KONTAKT:

Hausverwaltung Schmidt GmbH
Friedrichstraße 100
10117 Berlin

Telefon: 030 9876-5432
E-Mail: info@hausverwaltung-schmidt.de
Website: www.hausverwaltung-schmidt.de

Geschäftsführer: Klaus Schmidt
Handelsregister: HRB 98765

Mit freundlichen Grüßen

Hausverwaltung Schmidt GmbH

Unterschrift
Verwalter
Klaus Schmidt

Anlagen:
- Mietspiegel Berlin 2026 (Auszug)
- Vergleichswohnungen Liste
- Modernisierungskosten Aufstellung
- Mieterhöhungsvereinbarung Formular
''',
        'expected': {
            'is_document': True,
            'org': 'Hausverwaltung',
            'paragraphs': ['BGB § 558', 'BGB § 559', 'BGB § 555b', 'BGB § 555d'],
            'current_rent': '650,00 EUR',
            'new_rent': '780,00 EUR',
            'increase': '130,00 EUR (20%)',
            'deadline': '30.04.2026',
            'effective_date': '01.05.2026'
        }
    },

    # ========================================================================
    # ЛИСТ 4: Gericht - Komplexe Gerichtsladung (5500+ символів)
    # ========================================================================
    {
        'id': 4,
        'category': 'Gericht',
        'type': 'Komplexe Gerichtsladung',
        'length': 'long',
        'text': '''
Amtsgericht Berlin-Charlottenburg
Zivilgericht
Amtsgerichtsplatz 1
14057 Berlin

Herrn
Max Mustermann
Musterstraße 123
10115 Berlin

Berlin, den 28. Februar 2026

LADUNG ZUR GERICHTSSITZUNG
Geschäftszeichen: 15 C 123/26

In dem Rechtsstreit

Telekom Deutschland GmbH, Bonn
- Klägerin -

gegen

Max Mustermann, Berlin
- Beklagter -

wegen Forderung aus Telekommunikationsvertrag

wird der Beklagte zur mündlichen Verhandlung vor das Amtsgericht Berlin-Charlottenburg, Saal 205, 2. OG, geladen.

TERMIN:
Dienstag, den 25. März 2026, um 09:30 Uhr

PARTEIEN:

Klägerin:
Telekom Deutschland GmbH
Landgrabenweg 151
53227 Bonn
Prozessbevollmächtigter: Rechtsanwalt Dr. Schmidt
Kanzlei: Schmidt & Partner, Bonn

Beklagter:
Max Mustermann
Musterstraße 123
10115 Berlin

STREITGEGENSTAND:

Die Klägerin fordert vom Beklagten Zahlung von:
- Hauptforderung: 2.500,00 EUR
- Verzugszinsen (§ 288 BGB): 125,00 EUR
- Mahngebühren: 50,00 EUR
- Anwaltskosten: 350,00 EUR
- Gesamt: 3.025,00 EUR

RECHTSGRUNDLAGEN:

1. ZPO § 330 - Versäumnisurteil
   Bei Nichterscheinen des Beklagten kann ein Versäumnisurteil ergehen.

2. ZPO § 331 - Voraussetzungen des Versäumnisurteils
   Das Versäumnisurteil ergeht, wenn der Beklagte nicht erscheint.

3. ZPO § 335 - Fristen für das Versäumnisurteil
   Das Versäumnisurteil kann sofort ergehen.

4. BGB § 286 - Verzug des Schuldners
   Der Schuldner gerät nach Mahnung in Verzug.

5. BGB § 288 - Verzugszinsen
   Für Verbraucher beträgt der Verzugszinssatz 5% p.a.

6. BGB § 492 - Verbraucherdarlehensvertrag
   Besondere Vorschriften für Verbraucherverträge.

RECHTSFOLGENBELEHRUNG:

1. Bei Nichterscheinen:
   - Es kann ein Versäumnisurteil gegen Sie ergehen.
   - Das Urteil kann sofort vollstreckt werden.
   - Zusätzliche Kosten entstehen (Gerichtskosten, Anwaltskosten).

2. Bei Erscheinen:
   - Sie können sich zur Sache äußern.
   - Sie können Beweise vorlegen.
   - Sie können einen Vergleich vorschlagen.

3. Prozesskostenhilfe:
   Bei geringem Einkommen können Sie Prozesskostenhilfe beantragen.
   Antrag beim Gericht stellen.

4. Rechtsbeistand:
   - Rechtsanwalt für Vertragsrecht: 030 1234-5678
   - Verbraucherzentrale: 030 6980-2000
   - Anwaltlicher Beratungshilfeschein: Amtsgericht

BEWEISE:

Die Klägerin wird folgende Beweise vorlegen:
1. Telekommunikationsvertrag vom 15.06.2024
2. Rechnungen Nr. 12345-12350 (10.2025 - 01.2026)
3. Mahnungen Nr. 1-3 (02.2026 - 03.2026)
4. Kündigungsbestätigung vom 20.03.2026

Der Beklagte kann Beweise vorlegen bis: 20.03.2026

GERICHTSKOSTEN:

Bei einem Streitwert von 3.025,00 EUR betragen die Gerichtskosten:
- Gerichtsgebühr: 189,00 EUR
- Bei Vergleich: 126,00 EUR
- Bei Klagerücknahme: 63,00 EUR

Die Kosten trägt die unterliegende Partei.

NÄCHSTE SCHRITTE:

1. Bereiten Sie sich auf den Termin vor.
2. Sammeln Sie alle relevanten Unterlagen.
3. Überlegen Sie sich Ihre Verteidigung.
4. Erwägen Sie einen Vergleich.

5. Bei Verhinderung:
   - Melden Sie sich sofort beim Gericht
   - Beantragen Sie Terminverlegung
   - Legen Sie wichtige Gründe dar

KONTAKT:

Amtsgericht Berlin-Charlottenburg
Amtsgerichtsplatz 1
14057 Berlin

Telefon: 030 9024-0
Fax: 030 9024-2444
E-Mail: poststelle@ag-charlottenburg.justiz.de
Website: www.berlin.de/gerichte

Geschäftsstelle: Raum 1.03
Öffnungszeiten:
- Montag-Freitag: 09:00 - 12:00 Uhr
- Donnerstag: 13:00 - 16:00 Uhr

RICHTER:
Vorsitzender Richter: Dr. Michael Weber
Ursprung: Amtsgericht Berlin-Charlottenburg

GERICHTSSCHREIBER:
Justizfachangestellte: Frau Anna Müller

Mit freundlichen Grüßen

Die Geschäftsstelle des Amtsgerichts

Unterschrift
Justizobersekretärin
Anna Müller

Anlagen:
- Ladung (Original)
- Klageschrift (Kopie)
- Rechtsfolgenbelehrung
- Formular Prozesskostenhilfe
- Lageplan des Gerichts
''',
        'expected': {
            'is_document': True,
            'org': 'Gericht',
            'paragraphs': ['§ 330 ZPO', '§ 331 ZPO', '§ 335 ZPO', '§ 286 BGB', '§ 288 BGB'],
            'court_date': '25.03.2026',
            'court_time': '09:30',
            'court_location': 'Amtsgericht Berlin-Charlottenburg, Saal 205',
            'claim_amount': '3.025,00 EUR',
            'risk': 'Versäumnisurteil bei Nichterscheinen'
        }
    },

    # ========================================================================
    # ЛИСТ 5: Fake Finanzamt - Шахрайський лист (3500+ символів)
    # ========================================================================
    {
        'id': 5,
        'category': 'Fraud',
        'type': 'Fake Finanzamt mit vielen Details',
        'length': 'long',
        'text': '''
FINANZAMT BERLIN (FAKE!)
Steuerstelle für Sonderaufgaben
Berlin, den 01. März 2026

DRINGENDE STEUERZAHLUNG AUFFORDERUNG
SOFORT HANDELN ERFORDERLICH!

Sehr geehrter Steuerzahler,

hiermit fordern wir Sie auf, SOFORT Ihre offenen Steuerschulden zu begleichen.

OFFENE FORDERUNGEN:

1. Einkommensteuer 2024: 5.000,00 EUR
2. Umsatzsteuer 2025: 3.500,00 EUR
3. Säumniszuschläge: 750,00 EUR
4. Vollstreckungskosten: 250,00 EUR

GESAMTBETRAG: 9.500,00 EUR

ZAHLUNG MUSS SOFORT ERFOLGEN!

Überweisen Sie den Betrag auf folgendes Konto:

Empfänger: Finanzamt Berlin
IBAN: DE12 3456 7890 1234 5678 90
BIC: DEUTDEDBBER
Verwendungszweck: STEUER2026-MUSTERMANN

WICHTIG: Bei nicht zahlung kommen wir zur polizei!

RECHTLICHE FOLGEN:

1. Haftbefehl wird beantragt bei Nichtzahlung innerhalb 24 Stunden!
2. Konto wird gesperrt!
3. Lohn wird gepfändet!
4. Polizei kommt zu Ihnen nach Hause!

SIE MÜSSEN SOFORT HANDELN!

Klicken Sie hier um zu zahlen: http://finanzamt-fake.com/zahlen

ODER rufen Sie an: 0900-123456 (kostenpflichtig, 2,99 EUR/Min)

Email: finanzamt.berlin@gmail.com

WIDERSPRUCH NICHT MÖGLICH!

Dies ist eine letzte Aufforderung. Widerspruch ist nicht möglich.

Bei Fragen wenden Sie sich an unsere Hotline.

Mit freundlichen Grüßen

Finanzamt Berlin

Unterschrift
Leiter des Finanzamts
Hans Müller

P.S. BITTE ÜBERWEISEN SIE SOFORT!
''',
        'expected': {
            'is_document': False,
            'fraud': True,
            'fraud_indicators': [
                'urgent_payment',
                'threatening_language',
                'suspicious_phones',
                'suspicious_emails',
                'grammar_errors',
                'phishing_urls'
            ],
            'fraud_score': 'high'
        }
    },
]


# ============================================================================
# ФУНКЦІЇ ТЕСТУВАННЯ
# ============================================================================

def test_long_document_analysis(letter: dict) -> dict:
    """Тест аналізу великого документу."""
    text = letter['text']
    expected = letter['expected']
    
    results = {
        'length': len(text),
        'classification': check_if_document(text),
        'paragraphs_found': [],
        'amounts_found': [],
        'deadlines_found': [],
        'fraud_analysis': None
    }
    
    # ПОКРАЩЕНИЙ пошук параграфів (підтримує обидва формати)
    import re
    # Формат 1: § 286 BGB
    paras1 = re.findall(r'§\s*(\d+[a-z]?)\s*(BGB|SGB|ZPO|AO|VwVfG|StGB|HGB)', text, re.IGNORECASE)
    # Формат 2: BGB § 286
    paras2 = re.findall(r'(BGB|SGB|ZPO|AO|VwVfG|StGB|HGB)\s*§\s*(\d+[a-z]?)', text, re.IGNORECASE)
    # Формат 3: § 59 SGB II
    paras3 = re.findall(r'§\s*(\d+)\s*(SGB)\s*(I|II|III)', text, re.IGNORECASE)
    
    paragraphs_set = set()
    for para_num, code in paras1:
        paragraphs_set.add(f"§ {para_num} {code}")
    for code, para_num in paras2:
        paragraphs_set.add(f"{code} § {para_num}")
    for para_num, code, book in paras3:
        paragraphs_set.add(f"§ {para_num} {code} {book}")
    
    results['paragraphs_found'] = list(paragraphs_set)
    
    # Пошук сум
    amounts = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2}\s*EUR)', text)
    results['amounts_found'] = amounts
    
    # Пошук дат
    dates = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text)
    results['deadlines_found'] = dates
    
    # Пошук часу
    times = re.findall(r'(\d{1,2}:\d{2})\s*Uhr', text)
    results['times_found'] = times
    
    # Аналіз шахрайства
    if letter['category'] == 'Fraud':
        results['fraud_analysis'] = analyze_letter_for_fraud(text, {})
    
    # Перевірка результатів
    passed = True
    issues = []
    
    if results['classification']['is_document'] != expected['is_document']:
        passed = False
        issues.append(f"Класифікація: очікувалось {expected['is_document']}, отримано {results['classification']['is_document']}")
    
    if 'fraud' in expected and expected['fraud']:
        if not results['fraud_analysis'] or not results['fraud_analysis']['is_likely_fraud']:
            passed = False
            issues.append("Шахрайство не виявлено")
    
    if 'paragraphs' in expected:
        expected_paras = [p.upper().replace('  ', ' ') for p in expected['paragraphs']]
        found_paras = [p.upper().replace('  ', ' ') for p in results['paragraphs_found']]
        for para in expected_paras:
            # Перевірка з нормалізацією
            para_normalized = para.replace('BGB §', '§').replace('SGB §', '§').replace('ZPO §', '§')
            found_match = False
            for found in found_paras:
                found_normalized = found.replace('BGB §', '§').replace('SGB §', '§').replace('ZPO §', '§')
                if para_normalized in found_normalized or found_normalized in para_normalized:
                    found_match = True
                    break
            if not found_match:
                issues.append(f"Параграф {para} не знайдено")
    
    results['passed'] = passed
    results['issues'] = issues
    
    return results


def run_long_document_tests():
    """Запуск тестів на великих документах."""
    print("\n" + "="*100)
    print(" ТЕСТУВАННЯ НА ВЕЛИКИХ ЛИСТАХ (3000-10000+ символів)")
    print(" Gov.de Bot v4.3 - Long Document Analysis")
    print("="*100 + "\n")
    
    results = []
    total_passed = 0
    total_failed = 0
    
    for letter in LONG_TEST_LETTERS:
        print(f"Лист #{letter['id']}: {letter['type']}")
        print(f"  Довжина: {len(letter['text'])} символів")
        
        test_result = test_long_document_analysis(letter)
        results.append(test_result)
        
        if test_result['passed']:
            print(f"  ✅ PASS")
            total_passed += 1
        else:
            print(f"  ❌ FAIL")
            total_failed += 1
            for issue in test_result['issues']:
                print(f"     └─ {issue}")
        
        print(f"  Знайдено параграфів: {len(test_result['paragraphs_found'])}")
        print(f"  Знайдено сум: {len(test_result['amounts_found'])}")
        print(f"  Знайдено дат: {len(test_result['deadlines_found'])}")
        print(f"  Знайдено часу: {len(test_result.get('times_found', []))}")
        
        if test_result['fraud_analysis']:
            print(f"  Fraud Score: {test_result['fraud_analysis']['fraud_score']}")
            print(f"  Risk Level: {test_result['fraud_analysis']['risk_level']}")
        
        print()
    
    # Підсумки
    print("="*100)
    print(" ПІДСУМКИ ТЕСТУВАННЯ")
    print("="*100)
    
    total = len(LONG_TEST_LETTERS)
    pct = (total_passed / total) * 100
    
    print(f"\nЗагальний результат: {total_passed}/{total} ({pct:.1f}%)")
    print(f"✅ Пройдено: {total_passed}")
    print(f"❌ Провалено: {total_failed}")
    
    # Оцінка
    if pct >= 95:
        grade = "A+ (Відмінно)"
        emoji = "🏆"
    elif pct >= 90:
        grade = "A (Дуже добре)"
        emoji = "🥇"
    elif pct >= 85:
        grade = "B+ (Добре)"
        emoji = "🥈"
    else:
        grade = "C (Потребує покращень)"
        emoji = "⚠️"
    
    print(f"\n{emoji} Оцінка: {grade}")
    
    return results


if __name__ == '__main__':
    try:
        results = run_long_document_tests()
        
        # Збереження звіту
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        report = f"""
# 🧪 ТЕСТУВАННЯ НА ВЕЛИКИХ ЛИСТАХ (3000-10000+ символів)

## 📅 {timestamp}

## 📊 ЗАГАЛЬНІ РЕЗУЛЬТАТИ

```
Загальний результат: {sum(1 for r in results if r['passed'])}/{len(results)} ({sum(1 for r in results if r['passed'])/len(results)*100:.1f}%)
✅ Пройдено: {sum(1 for r in results if r['passed'])}
❌ Провалено: {sum(1 for r in results if not r['passed'])}
```

## 📈 ДЕТАЛЬНІ РЕЗУЛЬТАТИ

"""
        
        for i, result in enumerate(results):
            letter = LONG_TEST_LETTERS[i]
            status = "✅" if result['passed'] else "❌"
            report += f"### Лист #{letter['id']}: {letter['type']}\n"
            report += f"- Довжина: {result['length']} символів\n"
            report += f"- Статус: {status}\n"
            report += f"- Параграфів знайдено: {len(result['paragraphs_found'])}\n"
            report += f"- Сум знайдено: {len(result['amounts_found'])}\n"
            report += f"- Дат знайдено: {len(result['deadlines_found'])}\n"
            if result['issues']:
                report += f"- Проблеми: {', '.join(result['issues'])}\n"
            report += "\n"
        
        report_path = Path(__file__).parent / 'test_results' / f'long_document_test_{datetime.now().strftime("%Y%m%d_%H%M%S")}.md'
        report_path.parent.mkdir(exist_ok=True)
        report_path.write_text(report)
        
        print(f"\n📄 Звіт збережено: {report_path}")
        
    except Exception as e:
        print(f"\n❌ Помилка тестування: {e}")
        import traceback
        traceback.print_exc()
