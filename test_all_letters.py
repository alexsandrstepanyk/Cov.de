#!/usr/bin/env python3
"""
Test Script for Gov.de Bot
Тестування 10 листів від різних організацій
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from nlp_analysis import classify_letter_type, analyze_text
from legal_db import get_relevant_laws
from fraud_detection import (
    extract_phone_numbers, extract_emails, extract_websites,
    analyze_letter_for_fraud, generate_fraud_warning
)

# Тестові листи
TEST_LETTERS = {
    'Jobcenter': """
Bundesagentur für Arbeit
Jobcenter Berlin-Mitte

Sehr geehrte Frau Müller,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: 15.03.2024 um 10:00 Uhr
Ort: Jobcenter Berlin-Mitte, Straße der Migration 45, 10115 Berlin
Ansprechpartner: Herr Schmidt, Raum 3.12

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktueller Lebenslauf
- Bewerbungsnachweise

Gemäß § 59 SGB II sind Sie verpflichtet, zu dem Termin zu erscheinen.
Bei unentschuldigtem Fehlen können Leistungen nach § 31 SGB II gekürzt werden.

Mit freundlichen Grüßen
Ihr Jobcenter Team
Kundennummer: 123BG456
Tel: 030 123456-0
Email: jobcenter-berlin@arbeitsagentur.de
""",

    'FAKE Inkasso': """
FAKE Inkasso GmbH
Forderungsmanagement

Sehr geehrte Dame und Herren,

letzte Mahnung!

Sie schulden uns sofort 2.500 Euro!

Überweisen Sie das Geld innerhalb 24 Stunden auf:
Western Union MTCN: 1234567890

Bei nicht Zahlung kommt Polizei und macht Haftbefehl!
Sie müssen ins Gefängnis für 3 Jahre!

Bitcoin Wallet: 1A2B3C4D5E6F7G8H9I

Rufen Sie an: 0900-999888 (2€/Minute)
Email: scammer@gmail.com

Dringend! Sofort!
Mit freundlichen Grüßen
Inkasso Team
""",

    'Finanzamt': """
Finanzamt München
Steuerabteilung

Sehr geehrter Herr Kowalenko,

wir beziehen uns auf Ihre Einkommensteuererklärung 2023.

Nach Prüfung ergibt sich eine Steuernachzahlung in Höhe von 450,00 Euro.

Bitte überweisen Sie den Betrag bis zum 30.04.2024 auf folgendes Konto:

Finanzamt München
IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Verwendungszweck: Steuernummer 123/456/7890

Bei Fragen stehen wir Ihnen gerne zur Verfügung.

Telefon: 089 123456-0
Email: poststelle@finanzamt-muenchen.de

Mit freundlichen Grüßen
Ihr Finanzamt
""",

    'Vermieter': """
Herrn Wolfgang Müller
Vermieter

Sehr geehrte Familie Kowalenko,

hiermit kündige ich eine Mieterhöhung gemäß § 558 BGB an.

Die neue Miete beträgt ab 01.05.2024:
- Kaltmiete: 650 Euro (vorher 550 Euro)
- Nebenkosten: 150 Euro
- Gesamtmiete: 800 Euro

Begründung: Die ortsübliche Vergleichsmiete liegt bei 12 Euro/qm.

Sie haben der Erhöhung bis zum 30.04.2024 zuzustimmen.

Mit freundlichen Grüßen
Wolfgang Müller
Telefon: 0171 1234567
Email: w.mueller@web.de
""",

    'Falsche Polizei': """
BUNDESPOLIZEI ZENTRALE
Kriminalpolizei

SEHR GEEHRTE DAME UND HERREN,

SIE MÜSSEN SOFORT 5000 EURO ÜBERWEISEN!

Gegen Sie läuft ein Strafverfahren wegen Geldwäsche.

Bei nicht Zahlung:
- Haftbefehl wird ausgestellt
- Sie werden verhaftet
- Abschiebung in die Ukraine

Überweisen Sie auf:
Kontonummer: 1234567890
BLZ: 10020030

Oder Paysafecard Code: 1234-5678-9012-3456

Rufen Sie an: +44 20 1234567 (UK Nummer!)
Email: polizei.bundes@gmail.com

DRINGEND! 24 STUNDEN!
Mit freundlichen Grüßen
Kommissar Müller
""",

    'Gericht': """
Amtsgericht Berlin-Charlottenburg
Gerichtstraße 123
10585 Berlin

Beschluss

In dem Verfahren betreffend die Mietsache
Kowalenko ./. Müller

hat das Gericht am 20.02.2024 entschieden:

Der Mietvertrag wird zum 31.05.2024 gekündigt.

Rechtsmittelbelehrung:
Gegen diesen Beschluss kann innerhalb eines Monats
Widerspruch eingelegt werden.

Geschäftszeichen: 12 C 345/24

Telefon: 030 9018-0
Email: poststelle@agch-gericht-berlin.de
Internet: www.gericht-berlin.de
""",

    'Stadtwerke': """
Stadtwerke Berlin GmbH
Energieversorgung

Sehr geehrter Kunde,

hiermit mahnen wir Sie zur Zahlung der offenen Stromrechnung.

Rechnungsnummer: SW-2024-12345
Offener Betrag: 234,56 Euro
Fälligkeitsdatum: 01.02.2024

Bitte überweisen Sie den Betrag innerhalb 14 Tagen auf:

Stadtwerke Berlin GmbH
IBAN: DE12 1005 0000 0123 4567 89
BIC: BELADEBEXXX

Bei Nichtzahlung müssen wir leider eine Mahngebühr von 5 Euro berechnen.

Kundenservice: 030 123456-0
Email: kundenservice@stadtwerke-berlin.de

Mit freundlichen Grüßen
Ihre Stadtwerke Berlin
""",

    'Krankenkasse': """
AOK Berlin-Brandenburg
Gesundheitskasse

Sehr geehrte Frau Kowalenko,

wir bestätigen den Eingang Ihrer Unterlagen vom 15.02.2024.

Ihre Versichertennummer: A123456789

Wir haben Ihre Daten geprüft. Alles ist in Ordnung.

Ihre Beiträge werden weiterhin monatlich abgebucht.

Bei Fragen:
Telefon: 030 39002-0
Email: service@bb.aok.de
Internet: www.aok.de/bb

Mit freundlichen Grüßen
Ihre AOK Berlin-Brandenburg
""",

    'Falsches Paketamt': """
Deutsche Post DHL
Paketzentrum

Sehr geehrte Kundin,

Ihr Paket kann nicht zugestellt werden!

Es fallen Zollgebühren in Höhe von 45,90 Euro an.

Bitte bezahlen Sie online:
www.dhl-paket-zoll.com/track123

Oder überweisen Sie:
Deutsche Post Bank
IBAN: DE89 1001 0010 0123 4567 89

Bei nicht Zahlung wird das Paket zurückgeschickt.

Rufen Sie an: 0180-5-123456 (14 Cent/Minute)

Mit freundlichen Grüßen
DHL Team
""",

    'Arbeitgeber': """
Musterfirma GmbH
Personalabteilung

Sehr geehrter Herr Kowalenko,

hiermit kündigen wir das Arbeitsverhältnis fristgerecht zum 31.03.2024.

Begründung: Betriebliche Gründe erfordern den Abbau von Arbeitsplätzen.

Sie haben Anspruch auf Arbeitslosengeld I.

Bitte melden Sie sich innerhalb 3 Monaten bei der Arbeitsagentur.

Ihr Arbeitszeugnis erhalten Sie separat.

Bei Fragen:
Telefon: 089 987654-0
Email: personal@musterfirma.de

Mit freundlichen Grüßen
Geschäftsführung
Musterfirma GmbH
HRB 123456
""",
}

# Очікувані результати
EXPECTED_RESULTS = {
    'Jobcenter': {'type': 'employment', 'risk': 'LOW'},
    'FAKE Inkasso': {'type': 'debt_collection', 'risk': 'HIGH'},
    'Finanzamt': {'type': 'administrative', 'risk': 'LOW'},
    'Vermieter': {'type': 'tenancy', 'risk': 'LOW'},
    'Falsche Polizei': {'type': 'administrative', 'risk': 'HIGH'},
    'Gericht': {'type': 'administrative', 'risk': 'LOW'},
    'Stadtwerke': {'type': 'debt_collection', 'risk': 'LOW'},
    'Krankenkasse': {'type': 'general', 'risk': 'LOW'},
    'Falsches Paketamt': {'type': 'debt_collection', 'risk': 'MEDIUM'},
    'Arbeitgeber': {'type': 'employment', 'risk': 'LOW'},
}

def test_letter(name: str, text: str, expected: dict):
    """Тестування одного листа."""
    print(f"\n{'='*60}")
    print(f"📄 {name}")
    print(f"{'='*60}")
    
    # Класифікація
    letter_type = classify_letter_type(text)
    type_match = "✅" if letter_type == expected['type'] else "❌"
    
    # Аналіз
    analysis = analyze_text(text)
    
    # Anti-Fraud
    fraud_analysis = analyze_letter_for_fraud(text, {})
    fraud_warning = generate_fraud_warning(fraud_analysis)
    
    # Ризик
    risk = fraud_analysis['risk_level'].upper()
    risk_match = "✅" if risk == expected['risk'] else "⚠️" if risk == 'MEDIUM' and expected['risk'] in ['LOW', 'HIGH'] else "❌"
    
    # Контактні дані
    phones = extract_phone_numbers(text)
    emails = extract_emails(text)
    websites = extract_websites(text)
    
    # Вивід результатів
    print(f"\n📌 Тип листа: {letter_type} {type_match} (очікувався: {expected['type']})")
    print(f"⚠️  Рівень ризику: {risk} {risk_match} (очікувався: {expected['risk']})")
    
    if phones:
        print(f"\n📞 Телефони: {', '.join(phones)}")
    if emails:
        print(f"📧 Email: {', '.join(emails)}")
    if websites:
        print(f"🌐 Сайти: {', '.join(websites)}")
    
    print(f"\n🔍 Ключові слова: {', '.join(analysis['keywords'][:5])}")
    
    # Ознаки шахрайства
    has_fraud = any(v for v in fraud_analysis['indicators'].values() if v)
    if has_fraud:
        print(f"\n🚨 Ознаки шахрайства:")
        for category, indicators in fraud_analysis['indicators'].items():
            if indicators:
                print(f"  • {category.replace('_', ' ').title()}: {', '.join(indicators)}")
    
    print(f"\n📊 Fraud Score: {fraud_analysis['fraud_score']}")
    
    # Рекомендації
    print(f"\n💡 Рекомендації:")
    for rec in fraud_analysis['recommendations'][:3]:
        print(f"  {rec}")
    
    return {
        'name': name,
        'type': letter_type,
        'type_match': letter_type == expected['type'],
        'risk': risk,
        'risk_match': risk == expected['risk'],
        'fraud_score': fraud_analysis['fraud_score'],
    }

def main():
    """Запуск всіх тестів."""
    print("="*60)
    print("🧪 ТЕСТУВАННЯ ЛИСТІВ Gov.de Bot")
    print("="*60)
    
    results = []
    
    for name, text in TEST_LETTERS.items():
        expected = EXPECTED_RESULTS.get(name, {'type': 'general', 'risk': 'LOW'})
        result = test_letter(name, text, expected)
        results.append(result)
    
    # Підсумки
    print(f"\n{'='*60}")
    print("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    print(f"{'='*60}")
    
    type_correct = sum(1 for r in results if r['type_match'])
    risk_correct = sum(1 for r in results if r['risk_match'])
    
    print(f"\n✅ Тип листа визначено правильно: {type_correct}/{len(results)}")
    print(f"✅ Рівень ризику визначено правильно: {risk_correct}/{len(results)}")
    
    # Детальна таблиця
    print(f"\n{'='*60}")
    print("📋 ДЕТАЛЬНІ РЕЗУЛЬТАТИ")
    print(f"{'='*60}")
    print(f"{'Організація':<25} {'Тип':<20} {'Ризик':<10} {'Score':<5}")
    print(f"{'-'*60}")
    
    for r in results:
        type_icon = "✅" if r['type_match'] else "❌"
        risk_icon = "✅" if r['risk_match'] else "⚠️" if r['risk'] == 'MEDIUM' else "❌"
        print(f"{r['name']:<25} {r['type']:<20} {r['risk']:<10} {r['fraud_score']:<5}")
    
    # Висновки
    print(f"\n{'='*60}")
    print("📝 ВИСНОВКИ")
    print(f"{'='*60}")
    
    high_risk = [r for r in results if r['risk'] == 'HIGH']
    medium_risk = [r for r in results if r['risk'] == 'MEDIUM']
    low_risk = [r for r in results if r['risk'] == 'LOW']
    
    print(f"\n🔴 HIGH ризик (шахрайство): {len(high_risk)}")
    for r in high_risk:
        print(f"  • {r['name']}")
    
    print(f"\n🟡 MEDIUM ризик (підозріло): {len(medium_risk)}")
    for r in medium_risk:
        print(f"  • {r['name']}")
    
    print(f"\n🟢 LOW ризик (легітимно): {len(low_risk)}")
    for r in low_risk:
        print(f"  • {r['name']}")
    
    print(f"\n{'='*60}")
    print("✅ Тестування завершено!")
    print(f"{'='*60}")

if __name__ == '__main__':
    main()
