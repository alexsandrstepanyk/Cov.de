#!/usr/bin/env python3
"""
ПОКРАЩЕНА ГЕНЕРАЦІЯ ВІДПОВІДЕЙ v2.0

Покращення:
1. Автоматичне заповнення шаблонних полів
2. Розширені шаблони (200+ символів)
3. Конкретні посилання на дані з листа
4. Детальніша структура
"""

import re
from typing import Dict, Tuple


# ============================================================================
# ВИТЯГУВАННЯ ДАНИХ З ЛИСТА
# ============================================================================

def extract_letter_data(text: str) -> Dict:
    """Витягує всі дані з листа для заповнення шаблону."""
    text_lower = text.lower()
    data = {}
    
    # Дати (формат DD.MM.YYYY)
    dates = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text)
    data['dates'] = dates[:5]  # Зберігаємо до 5 дат
    data['first_date'] = dates[0] if dates else '[ДАТА]'
    
    # Час (формат HH:MM)
    times = re.findall(r'(\d{1,2}:\d{2})', text)
    data['times'] = times[:3]
    data['first_time'] = times[0] if times else '[ЧАС]'
    
    # Грошові суми
    amounts = re.findall(r'(\d+[.,\s]?\d*)\s*(euro|EUR|€)', text_lower)
    data['amounts'] = [amt[0].replace(',', '.') for amt in amounts]
    data['first_amount'] = data['amounts'][0] if data['amounts'] else '[СУМА]'
    
    # Номери клієнта/справи
    customer_numbers = re.findall(r'(kundennummer|aktenzeichen|geschäftszeichen|forderungsnummer)[:\s]*([A-Z0-9\-/]+)', text_lower)
    data['customer_number'] = customer_numbers[0][1].upper() if customer_numbers else '[НОМЕР]'
    
    # IBAN
    ibans = re.findall(r'(DE\d{2}\s*\d{4}\s*\d{4}\s*\d{4}\s*\d{2})', text)
    data['iban'] = ibans[0].replace(' ', '') if ibans else '[IBAN]'
    
    # Імена
    name_match = re.search(r'(?:herrn|frau|sehr geehrte[r]?)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)', text, re.IGNORECASE)
    data['recipient_name'] = name_match.group(1) if name_match else '[ІМ\'Я]'
    
    sender_match = re.search(r'(?:mit freundlichen grüßen|im auftrag)\s*\n*\s*([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)', text, re.IGNORECASE)
    data['sender_name'] = sender_match.group(1) if sender_match else '[ВІДПРАВНИК]'
    
    # Адреси
    data['location'] = 'Berlin' if 'berlin' in text_lower else '[МІСТО]'
    
    # Параграфи
    paragraphs = re.findall(r'§\s*(\d+[a-z]?(?:\s*abs\.\s*\d+)?(?:\s*SGB\s*[IVX]+|\s*BGB|\s*ZPO|\s*AO)?)', text, re.IGNORECASE)
    data['paragraphs'] = ['§ ' + p.strip() for p in paragraphs[:5]]
    
    # Терміни ( Fristen)
    deadline_match = re.search(r'(?:frist|bis zum|bis|fälligkeit)[:\s]*([0-9]+\.[0-9]+\.[0-9]+)', text_lower)
    data['deadline'] = deadline_match.group(1) if deadline_match else '[ТЕРМІН]'
    
    # Суми прописом (для inkasso)
    if 'euro' in text_lower:
        total_match = re.search(r'(?:gesamt|offener betrag|summe)[:\s]*(\d+[.,\s]?\d*)\s*(?:euro|EUR|€)', text_lower)
        data['total_amount'] = total_match.group(1).replace(',', '.') if total_match else data['first_amount']
    
    return data


# ============================================================================
# ПОКРАЩЕНІ ШАБЛОНИ ВІДПОВІДЕЙ
# ============================================================================

def generate_improved_response(text: str, law_info: Dict, language: str = 'uk') -> str:
    """Генерація покращеної відповіді з автоматичним заповненням даних."""
    
    # Витягуємо дані
    data = extract_letter_data(text)
    org_key = law_info.get('organization_key', 'general')
    sit_key = law_info.get('situation_key', 'default')
    
    # Jobcenter Einladung
    if org_key == 'jobcenter' and sit_key == 'einladung':
        if language == 'uk':
            return f'''Шановний(а) {data['sender_name']},

📋 **ПІДТВЕРДЖЕННЯ ОТРИМАННЯ ЗАПРОШЕННЯ**

Отримав(ла) Ваше запрошення на співбесіду від {data['first_date']}.

✅ **ПІДТВЕРДЖУЮ УЧАСТЬ:**
📅 Дата: {data['first_date']}
⏰ Час: {data['first_time']}
📍 Місце: {data['location']}

⚖️ **ПРАВОВЕ ПІДҐРУНТЯ:**
Розумію обов'язок згідно з {data['paragraphs'][0] if data['paragraphs'] else '§ 59 SGB II'} явитися на всі запрошення Jobcenter.

📎 **ДОКУМЕНТИ ЯКІ ВІЗЬМУ:**
• Посвідчення особи / паспорт
• Свідоцтво про реєстрацію
• Резюме (CV)
• Докази заявок за останні 3 місяці

⚠️ **УСВІДОМЛЮЮ НАСЛІДКИ:**
При неявці без поважної причини виплати можуть бути зменшені на 30% (§ 31 SGB II).

З повагою,
[Ваше ім'я]
Номер клієнта: {data['customer_number']}'''

        elif language == 'de':
            return f'''Sehr geehrte(r) {data['sender_name']},

📋 **BESTÄTIGUNG DES EMPFANGS DER EINLADUNG**

Ich habe Ihre Einladung zum Gespräch vom {data['first_date']} erhalten.

✅ **ICH BESTÄTIGE MEINE TEILNAHME:**
📅 Datum: {data['first_date']}
⏰ Uhrzeit: {data['first_time']}
📍 Ort: {data['location']}

⚖️ **RECHTSGRUNDLAGE:**
Ich verstehe meine Verpflichtung gemäß {data['paragraphs'][0] if data['paragraphs'] else '§ 59 SGB II'}, zu allen Terminen des Jobcenters zu erscheinen.

📎 **UNTERLAGEN DIE ICH MITBRINGE:**
• Personalausweis / Reisepass
• Meldebescheinigung
• Lebenslauf (CV)
• Bewerbungsnachweise der letzten 3 Monate

⚠️ **MIR SIND DIE FOLGEN BEWUSST:**
Bei unentschuldigtem Fehlen können Leistungen um 30% gekürzt werden (§ 31 SGB II).

Mit freundlichen Grüßen
[Ihr Name]
Kundennummer: {data['customer_number']}'''

    # Inkasso Forderung
    elif org_key == 'inkasso' and sit_key == 'forderung':
        if language == 'uk':
            return f'''Шановний(а) {data['sender_name']},

📋 **ЩОДО ВИМОГИ {data['customer_number']} ВІД {data['first_date']}**

Отримав(ла) Вашу вимогу про сплату боргу.

💰 **ІНФОРМАЦІЯ ПРО БОРГ:**
• Сума: {data['total_amount']} EUR
• IBAN: {data['iban']}
• Термін: {data['deadline']}

⚖️ **ЗАПИТ ЗГІДНО BGB § 286:**
Прошу надати детальну розбивку боргу:
1. Основна сума
2. Відсотки (5% річних згідно BGB § 288)
3. Додаткові витрати

📋 **МОЯ ПОЗИЦІЯ:**
Я не перебуваю у простроченні оскільки:
[ВКАЖІТЬ ПРИЧИНУ - наприклад "отримав лист тільки зараз" або "оспорюю суму"]

💡 **ПРОПОЗИЦІЯ:**
Готовий(а) обговорити розстрочку платежу:
• Початковий внесок: [СУМА] EUR
• Щомісячні платежі: [СУМА] EUR
• Кількість місяців: [ЧИСЛО]

⏰ **ПРОШУ ВІДПОВІДЬ ДО:** {data['deadline']}

З повагою,
[Ваше ім'я]'''

        elif language == 'de':
            return f'''Sehr geehrte(r) {data['sender_name']},

📋 **BETREFF: FORDERUNG {data['customer_number']} VOM {data['first_date']}**

Ich habe Ihre Zahlungsaufforderung erhalten.

💰 **INFORMATIONEN ZUR FORDERUNG:**
• Betrag: {data['total_amount']} EUR
• IBAN: {data['iban']}
• Frist: {data['deadline']}

⚖️ **ANFRAGE GEMÄẞ BGB § 286:**
Bitte senden Sie mir eine detaillierte Aufstellung:
1. Hauptforderung
2. Zinsen (5% p.a. gemäß BGB § 288)
3. Zusatzkosten

📋 **MEINE POSITION:**
Ich befinde mich nicht im Verzug, weil:
[GRUND ANGEBEN - z.B. "Brief erst jetzt erhalten" oder "bestreite die Summe"]

💡 **ANGEBOT:**
Ich bin bereit, eine Ratenzahlung zu vereinbaren:
• Anzahlung: [BETRAG] EUR
• Monatliche Rate: [BETRAG] EUR
• Anzahl Monate: [ZAHL]

⏰ **BITTE ANTWORT BIS:** {data['deadline']}

Mit freundlichen Grüßen
[Ihr Name]'''

    # Vermieter Mieterhöhung
    elif org_key == 'vermieter' and sit_key == 'mieterhöhung':
        if language == 'uk':
            return f'''Шановний(а) {data['sender_name']},

📋 **ЩОДО ПІДВИЩЕННЯ ОРЕНДИ ВІД {data['first_date']}**

Отримав(ла) Ваше повідомлення про підвищення орендної плати.

🏠 **ПОТОЧНА ОРЕНДА:**
• Стара сума: {data['amounts'][0] if len(data['amounts']) > 0 else '[СУМА]'} EUR
• Нова сума: {data['amounts'][1] if len(data['amounts']) > 1 else '[СУМА]'} EUR
• Підвищення: {data['amounts'][2] if len(data['amounts']) > 2 else '[СУМА]'} EUR
• Дата набуття чинності: {data['first_date']}

⚖️ **ЗАПИТ ЗГІДНО BGB § 558:**
Прошу надати обґрунтування підвищення:
1. Порівняння з Mietspiegel Berlin 2026
2. Розрахунок 20% ліміту за 3 роки
3. Копію Mietspiegel

📋 **МОЯ ПОЗИЦІЯ:**
[ОБЕРІТЬ ВАРІАНТ]
□ Погоджуюсь з підвищенням
□ Потрібен час на розгляд (до 2 місяців згідно BGB § 558b)
□ Не погоджуюсь - прошу детальне обґрунтування

⏰ **ВІДПОВІДЬ ДО:** {data['deadline']}

З повагою,
[Ваше ім'я]'''

        elif language == 'de':
            return f'''Sehr geehrte(r) {data['sender_name']},

📋 **BETREFF: MIETERHÖHUNG VOM {data['first_date']}**

Ich habe Ihre Mitteilung zur Mieterhöhung erhalten.

🏠 **AKTUELLE MIETE:**
• Alte Miete: {data['amounts'][0] if len(data['amounts']) > 0 else '[BETRAG]'} EUR
• Neue Miete: {data['amounts'][1] if len(data['amounts']) > 1 else '[BETRAG]'} EUR
• Erhöhung: {data['amounts'][2] if len(data['amounts']) > 2 else '[BETRAG]'} EUR
• Inkrafttreten: {data['first_date']}

⚖️ **ANFRAGE GEMÄẞ BGB § 558:**
Bitte senden Sie mir eine Begründung:
1. Vergleich mit Mietspiegel Berlin 2026
2. Berechnung der 20% Grenze in 3 Jahren
3. Kopie des Mietspiegels

📋 **MEINE POSITION:**
[OPTION WÄHLEN]
□ Ich stimme der Erhöhung zu
□ Ich brauche Bedenkzeit (2 Monate gemäß BGB § 558b)
□ Ich stimme nicht zu - bitte um detaillierte Begründung

⏰ **ANTWORT BIS:** {data['deadline']}

Mit freundlichen Grüßen
[Ihr Name]'''

    # Finanzamt Steuernachzahlung
    elif org_key == 'finanzamt' and sit_key == 'steuernachzahlung':
        if language == 'uk':
            return f'''Шановний(а) {data['sender_name']},

📋 **ЩОДО ПОДАТКОВОГО РІШЕННЯ {data['customer_number']} ВІД {data['first_date']}**

Отримав(ла) податкове рішення про доплату.

💰 **ІНФОРМАЦІЯ:**
• Сума доплати: {data['total_amount']} EUR
• Податковий номер: {data['customer_number']}
• Рік: [РІК]

⚖️ **ЗАПИТ ЗГІДНО AO § 172:**
Прошу перевірити рішення та надати:
1. Детальний розрахунок доплати
2. Копію всіх використаних документів
3. Обґрунтування змін

📋 **МОЯ ПОЗИЦІЯ:**
□ Погоджуюсь з рішенням
□ Не погоджуюсь - подаю заперечення (Einspruch)
□ Потрібен час на перевірку

💡 **ПРОХАННЯ:**
Прошу відстрочку платежу згідно AO § 222 до [ДАТА].

⏰ **ЗАПЕРЕЧЕННЯ ДО:** 1 місяць з дати отримання

З повагою,
[Ваше ім'я]'''

        elif language == 'de':
            return f'''Sehr geehrte Damen und Herren,

📋 **BETREFF: STEUERBESCHEID {data['customer_number']} VOM {data['first_date']}**

Ich habe Ihren Steuerbescheid erhalten.

💰 **INFORMATIONEN:**
• Nachzahlung: {data['total_amount']} EUR
• Steuernummer: {data['customer_number']}
• Jahr: [JAHR]

⚖️ **ANFRAGE GEMÄẞ AO § 172:**
Bitte überprüfen Sie den Bescheid und senden Sie mir:
1. Detaillierte Berechnung der Nachzahlung
2. Kopie aller verwendeten Unterlagen
3. Begründung der Änderungen

📋 **MEINE POSITION:**
[OPTION WÄHLEN]
□ Ich stimme dem Bescheid zu
□ Ich lege Einspruch ein
□ Ich brauche Zeit zur Überprüfung

💡 **BITTE:**
Ich bitte um Stundung gemäß AO § 222 bis [DATUM].

⏰ **EINSPRUCH FRIST:** 1 Monat ab Erhalt

Mit freundlichen Grüßen
[Ihr Name]'''

    # Загальна відповідь (fallback)
    else:
        if language == 'uk':
            return f'''Шановний(а) {data['sender_name']},

📋 **ЩОДО ВАШОГО ЛИСТА ВІД {data['first_date']}**

Отримав(ла) Ваше повідомлення від {data['first_date']}.

📝 **ІНФОРМАЦІЯ З ЛИСТА:**
{law_info.get('situation', 'Ситуація не визначена')}

⚖️ **ЗАКОНОДАВСТВО:**
{chr(10).join('• ' + para for para in data['paragraphs'][:3]) if data['paragraphs'] else 'Параграфи не знайдені'}

📋 **ПРОХАННЯ:**
Прошу надати детальну інформацію щодо:
1. [ПИТАННЯ 1]
2. [ПИТАННЯ 2]
3. [ПИТАННЯ 3]

⏰ **ПРОШУ ВІДПОВІДЬ ДО:** [ДАТА]

З повагою,
[Ваше ім'я]'''

        elif language == 'de':
            return f'''Sehr geehrte(r) {data['sender_name']},

📋 **BETREFF: IHRE NACHRICHT VOM {data['first_date']}**

Ich habe Ihre Nachricht vom {data['first_date']} erhalten.

📝 **INFORMATIONEN AUS DEM BRIEF:**
{law_info.get('situation', 'Situation nicht bestimmt')}

⚖️ **GESETZGEBUNG:**
{chr(10).join('• ' + para for para in data['paragraphs'][:3]) if data['paragraphs'] else 'Paragraphen nicht gefunden'}

📋 **BITTE:**
Bitte senden Sie mir detaillierte Informationen zu:
1. [FRAGE 1]
2. [FRAGE 2]
3. [FRAGE 3]

⏰ **BITTE ANTWORT BIS:** [DATUM]

Mit freundlichen Grüßen
[Ihr Name]'''


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def generate_response_smart_improved(text: str, language: str = 'uk') -> Tuple[str, Dict]:
    """Покращена версія generate_response_smart."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent))
    from smart_law_reference import get_law_reference
    
    law_info = get_law_reference(text)
    response = generate_improved_response(text, law_info, language)
    
    return response, law_info


if __name__ == '__main__':
    # Тестування
    test_text = '''Jobcenter Berlin Mitte
Einladung zum persönlichen Gespräch
Termin: Montag, 12.03.2026, um 10:00 Uhr
Kundennummer: 123ABC456
Gemäß § 59 SGB II'''
    
    response, law_info = generate_response_smart_improved(test_text, 'uk')
    print("🇺🇦 УКРАЇНСЬКА ВІДПОВІДЬ:")
    print(response)
    print("\n" + "="*70 + "\n")
    
    response_de, _ = generate_response_smart_improved(test_text, 'de')
    print("🇩🇪 НІМЕЦЬКА ВІДПОВІДЬ:")
    print(response_de)
