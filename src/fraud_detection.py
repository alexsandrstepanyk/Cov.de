#!/usr/bin/env python3
"""
Fraud Detection Module for Gov.de
Перевірка організацій на шахрайство:
- Перевірка телефонів
- Перевірка сайтів
- Перевірка адрес
- Перевірка реєстраційних номерів
"""

import re
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# База даних офіційних організацій Німеччини
OFFICIAL_ORGANIZATIONS = {
    'jobcenter': {
        'names': ['Jobcenter', 'Arbeitsagentur', 'Bundesagentur für Arbeit'],
        'phone_prefixes': ['+49', '0049', '0'],
        'domains': ['jobcenter-ge.de', 'arbeitsagentur.de', 'bund.de'],
        'address_patterns': ['Straße', 'Str.', 'Platz', 'Str.'],
    },
    'finanzamt': {
        'names': ['Finanzamt', 'Steuer'],
        'phone_prefixes': ['+49', '0049', '0'],
        'domains': ['finanzamt.de', 'bund.de'],
        'address_patterns': ['Straße', 'Str.'],
    },
    'stadt': {
        'names': ['Stadt', 'Gemeinde', 'Bürgeramt', 'Einwohnermeldeamt'],
        'phone_prefixes': ['+49', '0049', '0'],
        'domains': ['.de'],
        'address_patterns': ['Rathaus', 'Platz'],
    },
    'gericht': {
        'names': ['Gericht', 'Amtsgericht', 'Landgericht', 'Verwaltungsgericht'],
        'phone_prefixes': ['+49', '0049', '0'],
        'domains': ['justiz.de', 'bund.de'],
        'address_patterns': ['Gericht', 'Str.'],
    },
    'inkasso': {
        'names': ['Inkasso', 'Forderung', 'Zahlung'],
        'phone_prefixes': ['+49', '0049', '0'],
        'domains': [],  # Inkasso часто не мають офіційних сайтів
        'address_patterns': [],
        'warning': True,  # Потрібна додаткова перевірка
    },
}

# Ознаки шахрайства (РОЗШИРЕНО)
FRAUD_INDICATORS = {
    'urgent_payment': [
        'sofort', 'umgehend', 'innerhalb 24 Stunden', 'dringend',
        'sofortige Zahlung', 'letzte Mahnung', 'sofort handeln',
        'sofort überweisen', 'zahlung sofort', 'innerhalb 24 stunden'
    ],
    'threatening_language': [
        'Gerichtsvollzieher', 'Haftbefehl', 'Polizei', 'Strafanzeige',
        'Verhaftung', 'Abschiebung', 'deport', 'konto wird gesperrt',
        'wir kommen zur polizei', 'anordnung der haft', 'polizei kommt',
        'zur polizei kommen'
    ],
    'suspicious_accounts': [
        'Western Union', 'MoneyGram', 'Kryptowährung', 'Bitcoin',
        'Geschenkkarte', 'Gutscheinkarte', 'Paysafecard', 'iTunes',
        'Amazon Gutscheinkarte', 'Steam Wallet', 'bitcoin', 'western union'
    ],
    'fake_official': [
        'Bundespolizei', 'Ausländerbehörde', 'Finanzamt',
        'Kreditanstalt', 'Bundesbank', 'fake'
    ],
    'grammar_errors': [
        'bei nicht zahlung',  # Правильно: bei Nichtzahlung
        'kommen sie zur polizei',  # Дивний вираз
        'überweißen sie',  # Правильно: überweisen Sie
        'sie müssen sofort',  # Занадто агресивно
        'sofort handeln',
    ],
    'suspicious_phones': [
        r'^0900',  # Платні номери
        r'^0180',  # Сервісні номери
        r'^\+44',  # UK номери (не Німеччина)
        r'^\+1',   # US номери
        r'^\+234', # Нігерія
        r'^\+254', # Кенія
    ],
    'suspicious_emails': [
        '@gmail.com',
        '@yahoo.com',
        '@hotmail.com',
        '@web.de',
        '@gmx.de',
        '@t-online.de',
        '@aol.com',
    ],
    # НОВІ: Banking fraud індикатори
    'banking_fraud': [
        'pin erforderlich', 'passwort bestätigen', 'konto wird gesperrt',
        'daten bestätigen', 'tan eingeben', 'online-banking aktualisieren',
        'sicherheitssperre', 'konto entsperren', 'zugangsdaten aktualisieren',
        'pin und passwort'
    ],
    # НОВІ: Phishing URL індикатори
    'phishing_urls': [
        'klicken sie hier', 'link aktualisieren', 'seite öffnen',
        'hier klicken', 'jetzt öffnen', 'daten eingeben',
        'paket konnte nicht zugestellt werden'
    ],
    # НОВІ: Lottery fraud індикатори
    'lottery_fraud': [
        'gewonnen', 'lotterie', 'eurojackpot', 'millionen',
        '100.000 euro', 'hauptgewinn', 'glücksspiel',
        'kostenlos gewonnen', 'zufallsgenerator'
    ]
}


def extract_phone_numbers(text: str) -> List[str]:
    """Витягнути всі номери телефонів з тексту."""
    patterns = [
        r'\+?\d[\d\s\-\(\)]{8,}\d',  # Міжнародний формат
        r'0\d{3,}\s?\d{3,}\s?\d{2,}',  # Німецький формат
        r'Tel\.?\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{8,}\d)',
        r'Telefon\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{8,}\d)',
        r'Fax\s*[:\-]?\s*(\+?\d[\d\s\-\(\)]{8,}\d)',
    ]
    
    phones = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        phones.extend(matches if matches else re.findall(pattern, text))
    
    return list(set(phones))


def extract_emails(text: str) -> List[str]:
    """Витягнути всі email адреси з тексту."""
    pattern = r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}'
    return list(set(re.findall(pattern, text)))


def extract_websites(text: str) -> List[str]:
    """Витягнути всі вебсайти з тексту."""
    patterns = [
        r'https?://[^\s<>"{}|\\^`\[\]]+',
        r'www\.[^\s<>"{}|\\^`\[\]]+',
        r'[a-zA-Z0-9-]+\.(de|com|org|net|eu|info)[^\s<>"{}|\\^`\[\]]*',
    ]
    
    websites = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        websites.extend(matches)
    
    return list(set(websites))


def extract_account_numbers(text: str) -> List[str]:
    """Витягнути номери рахунків/IBAN."""
    patterns = [
        r'DE\d{2}\s?\d{8,}',  # IBAN Німеччина
        r'IBAN\s*[:\-]?\s*DE\d{2}\s?\d{8,}',
        r'Kontonummer\s*[:\-]?\s*\d{4,}',
        r'BLZ\s*[:\-]?\s*\d{8}',
    ]
    
    accounts = []
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        accounts.extend(matches)
    
    return list(set(accounts))


def check_phone_legitimacy(phone: str, organization_type: str) -> Tuple[bool, str]:
    """
    Перевірка легітимності телефону.
    
    Returns:
        (is_legitimate, reason)
    """
    # Перевірка на платні номери
    for pattern in FRAUD_INDICATORS['suspicious_phones']:
        if re.match(pattern, phone):
            return False, f"Підозрілий номер (платний/сервісний): {phone}"
    
    # Перевірка префіксу для Німеччини
    org_data = OFFICIAL_ORGANIZATIONS.get(organization_type, {})
    prefixes = org_data.get('phone_prefixes', ['+49', '0049', '0'])
    
    has_valid_prefix = any(phone.strip().startswith(p) for p in prefixes)
    if not has_valid_prefix:
        return False, f"Номер не німецький: {phone}"
    
    return True, "Номер валідний"


def check_email_legitimacy(email: str) -> Tuple[bool, str]:
    """
    Перевірка легітимності email.
    
    Returns:
        (is_legitimate, reason)
    """
    # Перевірка на підозрілі домени
    for suspicious in FRAUD_INDICATORS['suspicious_emails']:
        if suspicious in email.lower():
            return False, f"Підозрілий email домен: {email}"
    
    # Офіційні організації повинні мати .de або .bund.de
    if '.de' not in email and '.bund.de' not in email:
        return False, f"Email не німецький: {email}"
    
    return True, "Email валідний"


def check_website_legitimacy(website: str, organization_type: str) -> Tuple[bool, str]:
    """
    Перевірка легітимності вебсайту.
    
    Returns:
        (is_legitimate, reason)
    """
    org_data = OFFICIAL_ORGANIZATIONS.get(organization_type, {})
    official_domains = org_data.get('domains', [])
    
    # Перевірка на офіційні домени
    for official in official_domains:
        if official in website.lower():
            return True, f"Офіційний домен: {website}"
    
    # Для офіційних організацій перевіряємо .de
    if organization_type in ['jobcenter', 'finanzamt', 'gericht', 'stadt']:
        if '.de' not in website:
            return False, f"Офіційна організація має мати .de: {website}"
    
    return True, f"Домен прийнятний: {website}"


def detect_fraud_indicators(text: str) -> Dict:
    """
    Виявлення ознак шахрайства в тексті.
    
    Returns:
        Dict з ознаками шахрайства
    """
    text_lower = text.lower()
    
    fraud_score = 0
    indicators = {
        'urgent_payment': [],
        'threatening_language': [],
        'suspicious_accounts': [],
        'fake_official': [],
        'grammar_errors': [],
        'suspicious_phones': [],
        'suspicious_emails': [],
    }
    
    # Перевірка на терміновість платежу
    for indicator in FRAUD_INDICATORS['urgent_payment']:
        if indicator.lower() in text_lower:
            indicators['urgent_payment'].append(indicator)
            fraud_score += 1
    
    # Перевірка на загрозливий тон (тільки якщо є погрози)
    for indicator in FRAUD_INDICATORS['threatening_language']:
        if indicator.lower() in text_lower:
            # Не рахувати якщо це офіційний контекст
            if 'gerichtsvollzieher' in indicator.lower() and 'kommt' not in text_lower:
                continue
            indicators['threatening_language'].append(indicator)
            fraud_score += 2  # Більша вага
    
    # Перевірка на підозрілі методи оплати
    for indicator in FRAUD_INDICATORS['suspicious_accounts']:
        if indicator.lower() in text_lower:
            indicators['suspicious_accounts'].append(indicator)
            fraud_score += 3  # Дуже підозріло
    
    # Перевірка на підроблені офіційні назви
    for indicator in FRAUD_INDICATORS['fake_official']:
        if indicator.lower() in text_lower:
            # Не рахувати якщо це справжній Finanzamt або офіційний контекст
            if 'finanzamt' in indicator.lower() and '.de' in text_lower:
                continue
            indicators['fake_official'].append(indicator)
            fraud_score += 1
    
    # Перевірка на граматичні помилки (тільки явні)
    for indicator in FRAUD_INDICATORS['grammar_errors']:
        if indicator.lower() in text_lower:
            # "hiermit mahnen wir sie" - це нормальний вираз, не помилка
            if 'hiermit mahnen wir sie' in indicator.lower():
                continue
            indicators['grammar_errors'].append(indicator)
            fraud_score += 2
    
    return {
        'fraud_score': fraud_score,
        'indicators': indicators,
        'is_likely_fraud': fraud_score >= 5,
        'risk_level': 'high' if fraud_score >= 5 else 'medium' if fraud_score >= 2 else 'low'
    }


def analyze_letter_for_fraud(text: str, extracted_data: Dict) -> Dict:
    """
    Повний аналіз листа на шахрайство.
    
    Args:
        text: Текст листа
        extracted_data: Витягнуті дані (телефони, email, сайти тощо)
    
    Returns:
        Результати аналізу
    """
    # Витягуємо дані якщо не передано
    if not extracted_data:
        extracted_data = {
            'phones': extract_phone_numbers(text),
            'emails': extract_emails(text),
            'websites': extract_websites(text),
            'accounts': extract_account_numbers(text),
        }
    
    # Перевірка на ознаки шахрайства
    fraud_analysis = detect_fraud_indicators(text)
    
    # Перевірка телефонів
    phone_checks = []
    for phone in extracted_data.get('phones', []):
        is_legit, reason = check_phone_legitimacy(phone, 'inkasso')
        phone_checks.append({
            'phone': phone,
            'is_legitimate': is_legit,
            'reason': reason
        })
        if not is_legit:
            fraud_analysis['fraud_score'] += 2
    
    # Перевірка email
    email_checks = []
    for email in extracted_data.get('emails', []):
        is_legit, reason = check_email_legitimacy(email)
        email_checks.append({
            'email': email,
            'is_legitimate': is_legit,
            'reason': reason
        })
        if not is_legit:
            fraud_analysis['fraud_score'] += 2
    
    # Перевірка сайтів
    website_checks = []
    for website in extracted_data.get('websites', []):
        is_legit, reason = check_website_legitimacy(website, 'inkasso')
        website_checks.append({
            'website': website,
            'is_legitimate': is_legit,
            'reason': reason
        })
        if not is_legit:
            fraud_analysis['fraud_score'] += 1
    
    # Оновлюємо рівень ризику
    fraud_analysis['is_likely_fraud'] = fraud_analysis['fraud_score'] >= 5
    fraud_analysis['risk_level'] = (
        'high' if fraud_analysis['fraud_score'] >= 5 else
        'medium' if fraud_analysis['fraud_score'] >= 2 else
        'low'
    )
    
    # Додаємо перевірки контактних даних
    fraud_analysis['phone_checks'] = phone_checks
    fraud_analysis['email_checks'] = email_checks
    fraud_analysis['website_checks'] = website_checks
    
    # Рекомендації
    recommendations = []
    if fraud_analysis['is_likely_fraud']:
        recommendations = [
            "⚠️ НЕ ПЕРЕРАХОВУЙТЕ ГРОШІ!",
            "📞 Перевірте організацію на офіційному сайті",
            "🏦 Зверніться до банку для перевірки рахунку",
            "👮 Повідомте поліцію про шахрайство",
            "📧 Не відповідайте на цей лист",
        ]
    elif fraud_analysis['risk_level'] == 'medium':
        recommendations = [
            "⚠️ Будьте обережні",
            "📞 Перевірте телефон організації на офіційному сайті",
            "📧 Надішліть запит на офіційний email",
            "💡 Зверніться до адвоката для консультації",
        ]
    else:
        recommendations = [
            "✅ Лист виглядає легітимним",
            "📞 Все одно перевірте контактні дані",
            "📋 Збережіть копію листа",
        ]
    
    fraud_analysis['recommendations'] = recommendations
    
    return fraud_analysis


def generate_fraud_warning(fraud_analysis: Dict) -> str:
    """
    Генерація попередження про шахрайство.
    
    Args:
        fraud_analysis: Результати аналізу на шахрайство
    
    Returns:
        Текст попередження
    """
    risk_level = fraud_analysis['risk_level']
    
    if risk_level == 'high':
        warning = """
🚨 **УВАГА! ВИСОКИЙ РИЗИК ШАФРАЙСТВА!** 🚨

Цей лист має ознаки шахрайства:

"""
        for category, indicators in fraud_analysis['indicators'].items():
            if indicators:
                warning += f"• {category.replace('_', ' ').title()}: {', '.join(indicators)}\n"
        
        warning += "\n" + "\n".join(fraud_analysis['recommendations'])
        
    elif risk_level == 'medium':
        warning = """
⚠️ **УВАГА! СЕРЕДНІЙ РИЗИК**

Цей лист має підозрілі елементи:

"""
        for category, indicators in fraud_analysis['indicators'].items():
            if indicators:
                warning += f"• {category.replace('_', ' ').title()}: {', '.join(indicators)}\n"
        
        warning += "\n" + "\n".join(fraud_analysis['recommendations'])
        
    else:
        warning = """
✅ **НИЗЬКИЙ РИЗИК**

Лист виглядає легітимним, але все одно перевірте:

""" + "\n".join(fraud_analysis['recommendations'])
    
    return warning
