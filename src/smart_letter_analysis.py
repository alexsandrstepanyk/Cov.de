#!/usr/bin/env python3
"""
Smart Letter Analysis v8.1
Точний аналіз німецьких юридичних листів

Витягує:
- Організацію (Jobcenter, Finanzamt, Inkasso...)
- Тип листа (Einladung, Mahnung, Bescheid...)
- Параграфи (§ 59 SGB II, § 286 BGB...)
- Дати, суми, номери
- Наслідки невиконання
"""

import re
from typing import Dict, List, Optional


# База даних організацій
ORGANIZATIONS = {
    'jobcenter': {
        'name': 'Jobcenter / Arbeitsagentur',
        'keywords': ['jobcenter', 'arbeitsagentur', 'arbeitslos', 'hartz', 'sgb ii', 'kundennummer', 'vermittlung'],
        'paragraphs': ['§ 59 SGB II', '§ 31 SGB II', '§ 309 SGB III'],
        'consequences': 'При неявці без поважної причини виплати можуть бути зменшені на 30% (§ 31 SGB II). При повторному порушенні виплати можуть бути повністю припинені (§ 32 SGB II).',
    },
    'finanzamt': {
        'name': 'Finanzamt (Податкова)',
        'keywords': ['finanzamt', 'steuer', 'steuerbescheid', 'steuernummer', 'einkommensteuer', 'nachzahlung'],
        'paragraphs': ['§ 150 AO', '§ 172 AO', '§ 355 AO'],
        'consequences': 'При несплаті податків можуть бути нараховані пені (§ 240 AO), а також примусове стягнення через судового виконавця.',
    },
    'inkasso': {
        'name': 'Inkasso (Колекторська служба)',
        'keywords': ['inkasso', 'forderung', 'mahnung', 'zahlung', 'schuld', 'gläubiger', 'ibаn'],
        'paragraphs': ['§ 286 BGB', '§ 288 BGB', '§ 194 BGB'],
        'consequences': 'При несплаті боргу нараховується пеня 5% річних (§ 288 BGB). Можливі судові витрати та примусове стягнення через Gerichtsvollzieher.',
    },
    'vermieter': {
        'name': 'Vermieter (Орендодавець)',
        'keywords': ['mieter', 'vermieter', 'miete', 'wohnung', 'mieterhöhung', 'kündigung', 'kaution'],
        'paragraphs': ['§ 558 BGB', '§ 573 BGB', '§ 543 BGB'],
        'consequences': 'При несплаті оренди 2+ місяці можливе виселення (§ 543 BGB). Орендодавець може розірвати договір (§ 573 BGB).',
    },
    'gericht': {
        'name': 'Gericht (Суд)',
        'keywords': ['gericht', 'urteil', 'beschluss', 'ladung', 'verhandlung', 'aktenzeichen', 'richter'],
        'paragraphs': ['§ 330 ZPO', '§ 217 ZPO', '§ 688 ZPO'],
        'consequences': 'При неявці в суд може бути винесено заочне рішення (§ 330 ZPO). Можливі судові витрати та примусове виконання.',
    },
    'krankenkasse': {
        'name': 'Krankenkasse (Лікарняна каса)',
        'keywords': ['krankenkasse', 'aok', 'tk', 'barmer', 'versicherung', 'versichert', 'beitrag'],
        'paragraphs': ['§ 249 SGB V', '§ 250 SGB V', '§ 19 SGB V'],
        'consequences': 'При несплаті внесків можливе припинення страхування. Медичне обслуговування може бути обмежене.',
    },
    'versicherung': {
        'name': 'Versicherung (Страхова)',
        'keywords': ['versicherung', 'allianz', 'axa', 'beitrag', 'police', 'versichert'],
        'paragraphs': ['§ 38 VVG', '§ 1 VVG'],
        'consequences': 'При несплаті внесків страховий договір може бути розірваний (§ 38 VVG). Страхові виплати можуть бути відхилені.',
    },
}

# Типи листів
LETTER_TYPES = {
    'einladung': {
        'name': 'Einladung (Запрошення)',
        'keywords': ['einladung', 'termin', 'gespräch', 'vorsprache', 'erscheinen'],
    },
    'mahnung': {
        'name': 'Mahnung (Нагадування)',
        'keywords': ['mahnung', 'zahlung', 'fällig', 'überweisung', 'verzug'],
    },
    'bescheid': {
        'name': 'Bescheid (Рішення)',
        'keywords': ['bescheid', 'festsetzung', 'steuerbescheid', 'leistungsbescheid'],
    },
    'kundigung': {
        'name': 'Kündigung (Розірвання)',
        'keywords': ['kündigung', 'fristlos', 'fristgerecht', 'beendigung'],
    },
    'aufforderung': {
        'name': 'Aufforderung (Вимога)',
        'keywords': ['aufforderung', 'mitwirkung', 'unterlage', 'frist'],
    },
}


def analyze_letter_smart(text: str, lang: str = 'uk') -> Dict:
    """
    Розумний аналіз німецького юридичного листа.
    
    Args:
        text: Текст листа
        lang: Мова користувача
        
    Returns:
        Dict з повним аналізом
    """
    text_lower = text.lower()
    
    # 1. Визначення організації
    org_key, org_data = detect_organization(text_lower)
    
    # 2. Визначення типу листа
    type_key, type_data = detect_letter_type(text_lower)
    
    # 3. Витягування параграфів
    paragraphs = extract_paragraphs(text)
    
    # 4. Витягування дат
    dates = extract_dates(text)
    
    # 5. Витягування сум
    amounts = extract_amounts(text)
    
    # 6. Витягування номерів
    customer_number = extract_customer_number(text)
    
    # 7. Витягування імен
    recipient_name, sender_name = extract_names(text)
    
    # 8. Витягування адрес
    recipient_address, sender_address = extract_addresses(text)
    
    # Формування результату
    result = {
        'organization': org_data['name'] if org_data else 'Невизначено',
        'organization_key': org_key,
        'letter_type': type_data['name'] if type_data else 'Загальний лист',
        'letter_type_key': type_key,
        'paragraphs': paragraphs if paragraphs else org_data.get('paragraphs', []),
        'consequences': org_data.get('consequences', 'Наслідки не визначено'),
        'dates': dates,
        'amounts': amounts,
        'customer_number': customer_number,
        'recipient_name': recipient_name,
        'sender_name': sender_name,
        'recipient_address': recipient_address,
        'sender_address': sender_address,
        'is_legal': org_key is not None,
        'confidence': 0.9 if org_key else 0.5,
    }
    
    return result


def detect_organization(text_lower: str) -> tuple:
    """Визначення організації за ключовими словами."""
    scores = {}
    
    for org_key, org_data in ORGANIZATIONS.items():
        score = sum(1 for kw in org_data['keywords'] if kw in text_lower)
        scores[org_key] = score
    
    if not scores or max(scores.values()) == 0:
        return None, None
    
    best_org = max(scores, key=scores.get)
    return best_org, ORGANIZATIONS[best_org]


def detect_letter_type(text_lower: str) -> tuple:
    """Визначення типу листа за ключовими словами."""
    scores = {}
    
    for type_key, type_data in LETTER_TYPES.items():
        score = sum(1 for kw in type_data['keywords'] if kw in text_lower)
        scores[type_key] = score
    
    if not scores or max(scores.values()) == 0:
        return None, None
    
    best_type = max(scores, key=scores.get)
    return best_type, LETTER_TYPES[best_type]


def extract_paragraphs(text: str) -> List[str]:
    """Витягування параграфів з тексту."""
    paragraphs = []
    
    # Формат: § 59 SGB II
    pattern1 = re.findall(r'§\s*(\d+[a-z]?)\s*(SGB\s*[IVX]+|BGB|AO|ZPO|VVG)', text, re.IGNORECASE)
    for match in pattern1:
        paragraphs.append(f'§ {match[0]} {match[1]}')
    
    # Формат: BGB § 286
    pattern2 = re.findall(r'(SGB\s*[IVX]+|BGB|AO|ZPO|VVG)\s*§\s*(\d+[a-z]?)', text, re.IGNORECASE)
    for match in pattern2:
        para = f'§ {match[1]} {match[0]}'
        if para not in paragraphs:
            paragraphs.append(para)
    
    return paragraphs if paragraphs else None


def extract_dates(text: str) -> List[str]:
    """Витягування дат з тексту."""
    pattern = r'(\d{1,2}\.\d{1,2}\.\d{2,4})'
    return re.findall(pattern, text)


def extract_amounts(text: str) -> List[str]:
    """Витягування сум з тексту."""
    pattern = r'(\d+[.,\s]?\d*)\s*(EUR|€|euro)'
    matches = re.findall(pattern, text, re.IGNORECASE)
    return [f'{m[0]} {m[1]}' for m in matches]


def extract_customer_number(text: str) -> str:
    """Витягування номера клієнта/справи."""
    patterns = [
        r'(?:kundennummer|kunden-nr)[\s:]*([A-Z0-9]+)',
        r'(?:aktenzeichen|az\.?)[\s:]*([A-Z0-9/\-]+)',
        r'(?:forderungsnummer|forderung-nr)[\s:]*([A-Z0-9/]+)',
        r'(?:steuernummer|st-nr\.?)[\s:]*([A-Z0-9/\-]+)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return match.group(1)
    
    return ''


def extract_names(text: str) -> tuple:
    """Витягування імен отримувача та відправника."""
    recipient_name = ''
    sender_name = ''
    
    # Отримувач (після Herrn/Frau)
    recipient_match = re.search(r'(?:Herrn|Frau)\s*\n([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
    if recipient_match:
        recipient_name = recipient_match.group(1)
    
    # Відправник (з підпису)
    sender_match = re.search(r'Mit freundlichen Grüßen\s*\n([A-Z][a-z]+\s+[A-Z][a-z]+)', text)
    if sender_match:
        sender_name = sender_match.group(1)
    
    return recipient_name, sender_name


def extract_addresses(text: str) -> tuple:
    """Витягування адрес отримувача та відправника."""
    recipient_address = ''
    sender_address = ''
    
    lines = text.split('\n')
    
    # Отримувач (після Herrn/Frau)
    for i, line in enumerate(lines):
        if 'Herrn' in line or 'Frau' in line:
            if i + 2 < len(lines):
                recipient_address = f"{lines[i+1].strip()}, {lines[i+2].strip()}"
            break
    
    # Відправник (перші рядки)
    for i, line in enumerate(lines[:5]):
        if re.search(r'\d{4,5}\s+[A-Z]', line):  # ZIP + місто
            if i > 0:
                sender_address = f"{lines[i-1].strip()}, {line.strip()}"
            break
    
    return recipient_address, sender_address


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  🧠 ТЕСТУВАННЯ АНАЛІЗУ ЛИСТІВ v8.1")
    print("="*80)
    
    test_letter = """Jobcenter Berlin Mitte
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

Gemäß § 59 SGB II sind Sie verpflichtet...

Mit freundlichen Grüßen
Maria Schmidt
Beraterin

Kundennummer: 123ABC456"""
    
    result = analyze_letter_smart(test_letter, 'uk')
    
    print("\n📊 РЕЗУЛЬТАТИ АНАЛІЗУ:")
    print(f"  Організація: {result['organization']}")
    print(f"  Тип листа: {result['letter_type']}")
    print(f"  Параграфи: {', '.join(result['paragraphs'])}")
    print(f"  Дати: {', '.join(result['dates'])}")
    print(f"  Суми: {', '.join(result['amounts'])}")
    print(f"  Номер: {result['customer_number']}")
    print(f"  Отримувач: {result['recipient_name']}")
    print(f"  Відправник: {result['sender_name']}")
    print(f"  Впевненість: {result['confidence']*100:.0f}%")
    
    print(f"\n⚠️ НАСЛІДКИ:")
    print(f"  {result['consequences']}")
