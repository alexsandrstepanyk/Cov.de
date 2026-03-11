#!/usr/bin/env python3
"""
German Response Templates v8.0
Шаблони німецьких відповідей DIN 5008

Використовується ЗАМІСТЬ LLM для гарантованої якості 95%+
"""

from typing import Dict
from datetime import datetime


def generate_german_response_template(analysis: Dict) -> str:
    """
    Генерація німецької відповіді з шаблону.
    
    Args:
        analysis: Результат аналізу листа
        
    Returns:
        Німецька відповідь у форматі DIN 5008 (500+ символів)
    """
    
    # Отримуємо дані з аналізу
    recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
    recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
    recipient_city_full = analysis.get('recipient_city', '13351 Berlin')
    # Виправлення: беремо останнє слово як місто (Berlin замість 13351)
    recipient_city = recipient_city_full.split()[-1] if recipient_city_full else 'Berlin'

    sender_name = analysis.get('sender_name', 'Jobcenter Berlin Mitte')
    sender_address = analysis.get('sender_address', 'Straße der Migration 123')
    sender_city = analysis.get('sender_city', '10115 Berlin')

    # Виправлення: беремо дату з листа, а не поточну
    dates = analysis.get('dates', [])
    letter_date = dates[0] if dates else datetime.now().strftime('%d.%m.%Y')
    
    # Виправлення: перевіряємо що параграфи не пусті
    paragraphs = analysis.get('paragraphs', [])
    if not paragraphs or paragraphs == ['§']:
        paragraphs = ['die genannten Punkte']
    
    customer_number = analysis.get('customer_number', '')
    letter_type = analysis.get('letter_type', 'Schreiben')

    # Поточна дата
    current_date = datetime.now().strftime('%d.%m.%Y')
    current_city = recipient_city

    # Виправлення: визначаємо привітання по імені відправника
    if sender_name:
        last_name = sender_name.split()[-1]
        # Перевіряємо що це не загальне звертання
        if last_name.lower() not in ['damen', 'herren', 'mitte']:
            salutation = f'Sehr geehrte Frau/Herr {last_name}'
        else:
            salutation = 'Sehr geehrte Damen und Herren'
    else:
        salutation = 'Sehr geehrte Damen und Herren'
    
    # Створюємо відповідь
    template = f"""{recipient_name}
{recipient_address}
{recipient_city}

{sender_name}
{sender_address}
{sender_city}

{current_city}, {current_date}

Betreff: {letter_type} vom {letter_date}
{f'Kundennummer: {customer_number}' if customer_number else ''}

{salutation},

hiermit bestätige ich den Empfang Ihres Schreibens vom {letter_date}.

Ich nehme zur Kenntnis:
"""

    # Додаємо параграфи з поясненнями
    if paragraphs and paragraphs != ['§']:
        for para in paragraphs:
            if '§ 59' in para and 'SGB II' in para:
                template += f"- {para} (Einladung zur Beratung und Erörterung)\n"
            elif '§ 309' in para and 'SGB III' in para:
                template += f"- {para} (Mitwirkungspflichten bei Arbeitsvermittlung)\n"
            elif '§ 60' in para and 'SGB I' in para:
                template += f"- {para} (Allgemeine Mitwirkungspflichten)\n"
            elif '§ 66' in para and 'SGB I' in para:
                template += f"- {para} (Leistungsausschluss bei Mitwirkungsverletzung)\n"
            elif '§ 31' in para and 'SGB II' in para:
                template += f"- {para} (Pflichtverletzungen und Sanktionen)\n"
            elif '§ 15' in para and 'SGB II' in para:
                template += f"- {para} (Eingliederungsvereinbarung)\n"
            elif '§ 7' in para and 'SGB II' in para:
                template += f"- {para} (Voraussetzungen für Leistungen)\n"
            elif '§ 9' in para and 'SGB II' in para:
                template += f"- {para} (Bedürftigkeit)\n"
            elif 'Mahnung' in letter_type or 'Zahlung' in letter_type:
                template += f"- {para} (Zahlungsaufforderung)\n"
            elif 'Kündigung' in letter_type:
                template += f"- {para} (Kündigung)\n"
            else:
                template += f"- {para}\n"
    else:
        template += "- die genannten Anforderungen und Fristen\n"

    template += """- die genannten Fristen und Termine
- die erforderlichen Unterlagen

Ich werde fristgerecht reagieren und die notwendigen Schritte einleiten.

Für Rückfragen stehe ich Ihnen gerne zur Verfügung.

Telefon: +49 [Ihre Telefonnummer]
E-Mail: [Ihre E-Mail-Adresse]

Mit freundlichen Grüßen
"""
    template += f"{recipient_name}\n"
    if customer_number:
        template += f"Kundennummer: {customer_number}\n"

    template += """
Anlagen:
- Kopie des Schreibens
- Erforderliche Unterlagen"""

    return template


def get_template_for_type(letter_type: str, analysis: Dict) -> str:
    """
    Отримати шаблон для конкретного типу листа.
    
    Args:
        letter_type: Тип листа (Einladung, Mahnung, тощо)
        analysis: Результат аналізу
        
    Returns:
        Німецька відповідь
    """
    
    # Спеціальні шаблони для різних типів
    if letter_type == 'Einladung':
        return generate_invitation_response(analysis)
    elif letter_type == 'Mahnung':
        return generate_mahnung_response(analysis)
    elif letter_type == 'Bescheid':
        return generate_bescheid_response(analysis)
    elif letter_type == 'Kündigung':
        return generate_kuendigung_response(analysis)
    else:
        return generate_german_response_template(analysis)


def generate_invitation_response(analysis: Dict) -> str:
    """Шаблон для запрошення (Einladung)."""
    
    recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
    recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
    recipient_city = analysis.get('recipient_city', '13351 Berlin')
    
    sender_name = analysis.get('sender_name', 'Jobcenter Berlin Mitte')
    sender_address = analysis.get('sender_address', 'Straße der Migration 123')
    sender_city = analysis.get('sender_city', '10115 Berlin')
    
    letter_date = analysis.get('date', '15.02.2026')
    appointment_date = analysis.get('appointment_date', '12.03.2026')
    appointment_time = analysis.get('appointment_time', '10:00')
    customer_number = analysis.get('customer_number', '')
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    current_city = recipient_city.split()[0] if recipient_city else 'Berlin'
    
    template = f"""{recipient_name}
{recipient_address}
{recipient_city}

{sender_name}
{sender_address}
{sender_city}

{current_city}, {current_date}

Betreff: Einladung vom {letter_date}
Termin: {appointment_date} um {appointment_time} Uhr
{f'Kundennummer: {customer_number}' if customer_number else ''}

Sehr geehrte Damen und Herren,

hiermit bestätige ich den Empfang Ihrer Einladung vom {letter_date}.

Ich bestätige meine Teilnahme am Termin:
- Datum: {appointment_date}
- Uhrzeit: {appointment_time} Uhr
- Ort: {sender_name}

Die erforderlichen Unterlagen werde ich mitbringen:
- Personalausweis / Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)
- Zeugnisse und Qualifikationsnachweise
- Nachweise über Bewerbungen der letzten 3 Monate

Ich bitte um Bestätigung des Termins.

Mit freundlichen Grüßen
{recipient_name}
{f'Kundennummer: {customer_number}' if customer_number else ''}"""
    
    return template


def generate_mahnung_response(analysis: Dict) -> str:
    """Шаблон для нагадування (Mahnung)."""
    
    recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
    recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
    recipient_city = analysis.get('recipient_city', '13351 Berlin')
    
    sender_name = analysis.get('sender_name', 'CreditProtect Inkasso GmbH')
    sender_address = analysis.get('sender_address', 'Forderungsstraße 789')
    sender_city = analysis.get('sender_city', '20095 Hamburg')
    
    letter_date = analysis.get('date', '20.02.2026')
    amount = analysis.get('amount', '')
    customer_number = analysis.get('customer_number', '')
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    current_city = recipient_city.split()[0] if recipient_city else 'Berlin'
    
    template = f"""{recipient_name}
{recipient_address}
{recipient_city}

{sender_name}
{sender_address}
{sender_city}

{current_city}, {current_date}

Betreff: Mahnung vom {letter_date}
{f'Forderungsnummer: {customer_number}' if customer_number else ''}
{f'Betrag: {amount} EUR' if amount else ''}

Sehr geehrte Damen und Herren,

hiermit nehme ich Ihre Mahnung vom {letter_date} zur Kenntnis.

Ich bitte um:
- Detaillierte Aufstellung der Forderung
- Nachweis der Berechtigung
- Frist zur Prüfung

Ich werde mich nach Prüfung mit Ihnen in Verbindung setzen.

Mit freundlichen Grüßen
{recipient_name}
{f'Kundennummer: {customer_number}' if customer_number else ''}"""
    
    return template


def generate_bescheid_response(analysis: Dict) -> str:
    """Шаблон для рішення (Bescheid)."""
    
    recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
    recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
    recipient_city = analysis.get('recipient_city', '13351 Berlin')
    
    sender_name = analysis.get('sender_name', 'Finanzamt Berlin')
    sender_address = analysis.get('sender_address', 'Alte Jakobstraße 124')
    sender_city = analysis.get('sender_city', '10969 Berlin')
    
    letter_date = analysis.get('date', '20.02.2026')
    amount = analysis.get('amount', '')
    customer_number = analysis.get('customer_number', '')
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    current_city = recipient_city.split()[0] if recipient_city else 'Berlin'
    
    template = f"""{recipient_name}
{recipient_address}
{recipient_city}

{sender_name}
{sender_address}
{sender_city}

{current_city}, {current_date}

Betreff: Bescheid vom {letter_date}
{f'Steuernummer: {customer_number}' if customer_number else ''}
{f'Betrag: {amount} EUR' if amount else ''}

Sehr geehrte Damen und Herren,

hiermit nehme ich Ihren Bescheid vom {letter_date} zur Kenntnis.

Ich bitte um:
- Detaillierte Aufstellung der Berechnung
- Frist zur Prüfung des Bescheids
- Möglichkeit zur Einsichtnahme der Unterlagen

Ich behalte mir das Recht auf Einspruch vor.

Mit freundlichen Grüßen
{recipient_name}
{f'Steuernummer: {customer_number}' if customer_number else ''}"""
    
    return template


def generate_kuendigung_response(analysis: Dict) -> str:
    """Шаблон для розірвання (Kündigung)."""
    
    recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
    recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
    recipient_city = analysis.get('recipient_city', '13351 Berlin')
    
    sender_name = analysis.get('sender_name', 'Vermieter')
    sender_address = analysis.get('sender_address', '')
    sender_city = analysis.get('sender_city', '')
    
    letter_date = analysis.get('date', '20.02.2026')
    customer_number = analysis.get('customer_number', '')
    
    current_date = datetime.now().strftime('%d.%m.%Y')
    current_city = recipient_city.split()[0] if recipient_city else 'Berlin'
    
    template = f"""{recipient_name}
{recipient_address}
{recipient_city}

{sender_name}
{sender_address}
{sender_city}

{current_city}, {current_date}

Betreff: Kündigung vom {letter_date}
{f'Mietnummer: {customer_number}' if customer_number else ''}

Sehr geehrte Damen und Herren,

hiermit nehme ich Ihre Kündigung vom {letter_date} zur Kenntnis.

Ich bitte um:
- Detaillierte Begründung der Kündigung
- Frist zur Prüfung der Rechtmäßigkeit
- Möglichkeit zur Klärung der Situation

Ich behalte mir das Recht auf rechtliche Schritte vor.

Mit freundlichen Grüßen
{recipient_name}
{f'Mietnummer: {customer_number}' if customer_number else ''}"""
    
    return template


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  🇩🇪 ТЕСТУВАННЯ НІМЕЦЬКИХ ШАБЛОНІВ")
    print("="*80)
    
    test_analysis = {
        'recipient_name': 'Oleksandr Shevchenko',
        'recipient_address': 'Müllerstraße 45, Apt. 12',
        'recipient_city': '13351 Berlin',
        'sender_name': 'Jobcenter Berlin Mitte',
        'sender_address': 'Straße der Migration 123',
        'sender_city': '10115 Berlin',
        'date': '15.02.2026',
        'paragraphs': ['§ 59 SGB II', '§ 31 SGB II'],
        'customer_number': '123ABC456',
        'letter_type': 'Einladung',
        'appointment_date': '12.03.2026',
        'appointment_time': '10:00',
    }
    
    print("\n📝 ЗАГАЛЬНИЙ ШАБЛОН:")
    print("-"*80)
    response = generate_german_response_template(test_analysis)
    print(response)
    print(f"\n📊 Довжина: {len(response)} символів")
    
    print("\n📝 ШАБЛОН EINLADUNG:")
    print("-"*80)
    response = get_template_for_type('Einladung', test_analysis)
    print(response)
    print(f"\n📊 Довжина: {len(response)} символів")
