#!/usr/bin/env python3
"""
Fallback Templates Module v1.0
Шаблони відповідей для листів з недостатнім контекстом
"""

from typing import Dict, List, Optional
from datetime import datetime


# ============================================================================
# FALLBACK ШАБЛОНИ
# ============================================================================

FALLBACK_TEMPLATES = {
    'jobcenter': {
        'de': '''Sehr geehrte Damen und Herren,

vielen Dank für Ihr Schreiben vom {date}.

Ich nehme zur Kenntnis und werde mich fristgerecht bei Ihnen melden.

Für Rückfragen stehe ich Ihnen gerne zur Verfügung.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Дякую за Ваше повідомлення від {date}.

Приймаю до відома та зв'яжуся з Вами найближчим часом.

З повагою,
{sender_name}''',
    },
    
    'finanzamt': {
        'de': '''Sehr geehrte Damen und Herren,

vielen Dank für Ihren Steuerbescheid vom {date}.

Ich habe den Bescheid erhalten und prüfe diesen.

Bei Rückfragen melde ich mich bei Ihnen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Дякую за Ваш податковий розпис від {date}.

Отримав(ла) та перевіряю документ.

З повагою,
{sender_name}''',
    },
    
    'inkasso': {
        'de': '''Sehr geehrte Damen und Herren,

ich habe Ihre Forderung vom {date} erhalten.

Bitte senden Sie mir eine detaillierte Aufstellung der Forderung zu.

Ich prüfe den Sachverhalt und melde mich bei Ihnen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Отримав(ла) Вашу вимогу від {date}.

Прошу надати детальну розбивку боргу.

Перевіряю та зв'яжуся з Вами.

З повагою,
{sender_name}''',
    },
    
    'vermieter': {
        'de': '''Sehr geehrte(r) {recipient_name},

vielen Dank für Ihr Schreiben vom {date}.

Ich nehme zur Kenntnis und prüfe die Angelegenheit.

Ich melde mich in Kürze bei Ihnen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а) {recipient_name},

Дякую за Ваше повідомлення від {date}.

Приймаю до відома та перевіряю.

Зв'яжуся найближчим часом.

З повагою,
{sender_name}''',
    },
    
    'gericht': {
        'de': '''Sehr geehrte Damen und Herren,

ich habe Ihre Ladung vom {date} erhalten.

Ich nehme zur Kenntnis und werde erscheinen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Отримав(ла) Вашу повістку від {date}.

Підтверджую участь.

З повагою,
{sender_name}''',
    },
    
    'krankenkasse': {
        'de': '''Sehr geehrte Damen und Herren,

vielen Dank für Ihr Schreiben vom {date}.

Ich nehme zur Kenntnis.

Für Rückfragen stehe ich zur Verfügung.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Дякую за повідомлення від {date}.

Приймаю до відома.

З повагою,
{sender_name}''',
    },
    
    'versicherung': {
        'de': '''Sehr geehrte Damen und Herren,

ich habe Ihre Rechnung vom {date} erhalten.

Ich prüfe den Betrag und melde mich bei Ihnen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Отримав(ла) Ваш рахунок від {date}.

Перевіряю суму та зв'яжуся.

З повагою,
{sender_name}''',
    },
    
    'behörde': {
        'de': '''Sehr geehrte Damen und Herren,

vielen Dank für Ihr Schreiben vom {date}.

Ich nehme zur Kenntnis und werde fristgerecht reagieren.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Дякую за повідомлення від {date}.

Приймаю до відома та відреагую в термін.

З повагою,
{sender_name}''',
    },
    
    'general': {
        'de': '''Sehr geehrte Damen und Herren,

vielen Dank für Ihr Schreiben vom {date}.

Ich nehme zur Kenntnis und melde mich bei Ihnen.

Mit freundlichen Grüßen
{sender_name}''',
        
        'uk': '''Шановний(а),

Дякую за Ваше повідомлення від {date}.

Зв'яжуся з Вами найближчим часом.

З повагою,
{sender_name}''',
    },
}


# ============================================================================
# КЛЮЧОВІ СЛОВА ДЛЯ КЛАСИФІКАЦІЇ
# ============================================================================

SITUATION_KEYWORDS = {
    'einladung': [
        'einladung', 'gespräch', 'termin', 'vorsprache', 'persönlich',
        'erscheinen', 'teilnahme'
    ],
    'bescheid': [
        'bescheid', 'festsetzung', 'steuerbescheid', 'leistungsbescheid',
        'ablehnung', 'bewilligung'
    ],
    'mahnung': [
        'mahnung', 'zahlung', 'forderung', 'überweisung', 'ibаn',
        'offener betrag', 'fällig', 'zahle'
    ],
    'kuendigung': [
        'kündigung', 'beendigung', 'auflösung', 'fristlos', 'fristgerecht'
    ],
    'mieterhoehung': [
        'mieterhöhung', 'miete', 'erhöhung', 'mietspiegel', 'kaltmiete'
    ],
    'aufforderung': [
        'aufforderung', 'mitwirkung', 'unterlage', 'frist', 'einreichen'
    ],
    'rechnung': [
        'rechnung', 'beitrag', 'kosten', 'betrag', 'euro', '€'
    ],
    'ladung': [
        'ladung', 'gericht', 'verhandlung', 'saal', 'richter',
        'kläger', 'beklagte'
    ],
}


# ============================================================================
# ФУНКЦІЇ
# ============================================================================

def get_fallback_template(org_key: str, lang: str = 'de', 
                          date: str = None, sender_name: str = None,
                          recipient_name: str = None) -> str:
    """
    Отримати fallback шаблон для організації.
    
    Args:
        org_key: Ключ організації (jobcenter, finanzamt тощо)
        lang: Мова (de, uk)
        date: Дата з листа
        sender_name: Ім'я відправника
        recipient_name: Ім'я отримувача
    
    Returns:
        Текст шаблону
    """
    # Отримуємо шаблон
    templates = FALLBACK_TEMPLATES.get(org_key, FALLBACK_TEMPLATES['general'])
    template = templates.get(lang, templates['de'])
    
    # Заповнюємо змінні
    if date is None:
        date = datetime.now().strftime('%d.%m.%Y')
    
    if sender_name is None:
        sender_name = '[Ihr Name]'
    
    if recipient_name is None:
        recipient_name = '[Name]'
    
    return template.format(
        date=date,
        sender_name=sender_name,
        recipient_name=recipient_name
    )


def detect_situation_by_keywords(text: str) -> str:
    """
    Визначити ситуацію за ключовими словами.
    
    Args:
        text: Текст листа
        
    Returns:
        Ключ ситуації (einladung, mahnung тощо)
    """
    text_lower = text.lower()
    scores = {}
    
    for situation, keywords in SITUATION_KEYWORDS.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[situation] = score
    
    # Знаходимо переможця
    max_score = max(scores.values()) if scores else 0
    
    if max_score == 0:
        return 'general'
    
    # Всі ситуації з максимальним скором
    winners = [sit for sit, score in scores.items() if score == max_score]
    
    # Якщо нічия - обираємо першого
    return winners[0]


def generate_fallback_response(text: str, org_key: str, lang: str = 'de',
                               sender_name: str = None, 
                               recipient_name: str = None) -> Dict:
    """
    Згенерувати fallback відповідь.
    
    Args:
        text: Текст листа
        org_key: Ключ організації
        lang: Мова відповіді
        sender_name: Ім'я відправника
        recipient_name: Ім'я отримувача
    
    Returns:
        Dict з відповіддю та мета-даними
    """
    # Витягуємо дати
    import re
    dates = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text)
    date = dates[0] if dates else datetime.now().strftime('%d.%m.%Y')
    
    # Визначаємо ситуацію
    situation = detect_situation_by_keywords(text)
    
    # Генеруємо відповідь
    response = get_fallback_template(
        org_key=org_key,
        lang=lang,
        date=date,
        sender_name=sender_name or '[Ihr Name]',
        recipient_name=recipient_name or '[Name]'
    )
    
    return {
        'response': response,
        'situation': situation,
        'date': date,
        'template_used': True,
        'org_key': org_key,
        'lang': lang,
    }


def should_use_fallback(text: str, primary_response: str = None) -> bool:
    """
    Визначити чи потрібно використовувати fallback.
    
    Args:
        text: Текст листа
        primary_response: Відповідь від основного генератора
        
    Returns:
        True якщо потрібно fallback
    """
    # Якщо текст занадто короткий
    if len(text) < 300:
        return True
    
    # Якщо відповідь занадто коротка
    if primary_response and len(primary_response) < 150:
        return True
    
    # Якщо немає ключових слів для класифікації
    situation = detect_situation_by_keywords(text)
    if situation == 'general' and len(text) < 500:
        return True
    
    return False


if __name__ == '__main__':
    # Тестування
    test_text = '''Finanzamt München
Steuerbescheid 2025
500 EUR'''
    
    result = generate_fallback_response(
        text=test_text,
        org_key='finanzamt',
        lang='de',
        sender_name='Max Mustermann'
    )
    
    print('📝 FALLBACK ВІДПОВІДЬ:')
    print('='*60)
    print(result['response'])
    print('='*60)
    print(f'Ситуація: {result["situation"]}')
    print(f'Дата: {result["date"]}')
    print(f'Шаблон: {result["template_used"]}')
