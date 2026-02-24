#!/usr/bin/env python3
"""
NLP Analysis Module
Використовує spaCy для аналізу німецьких текстів, витягування сутностей та класифікації.
"""

import spacy
import logging
from typing import Dict, List, Tuple

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Завантаження німецької моделі
try:
    nlp = spacy.load("de_core_news_sm")
    logger.info("spaCy модель de_core_news_sm завантажена")
except OSError:
    logger.error("Модель de_core_news_sm не знайдено!")
    logger.error("Встановіть командою: python3 -m spacy download de_core_news_sm")
    raise

# Ключові слова для класифікації
KEYWORDS = {
    'debt_collection': [
        'schuld', 'forderung', 'zahlung', 'rechnung', 'mahnung', 'verzug',
        'überweisung', 'betrag', 'offen', 'bezahlen', 'konto', 'bank',
        'gläubiger', 'schulden', 'mahnen', 'frist', 'zahlen'
    ],
    'tenancy': [
        'miete', 'wohnung', 'mietvertrag', 'kündigung', 'nebenkosten',
        'hausmeister', 'vermieter', 'mieter', 'kaution', 'abrechnung',
        'heizkosten', 'warmwasser', 'renovierung', 'mangel', 'defekt'
    ],
    'employment': [
        'jobcenter', 'einladung', 'termin', 'bewerbung', 'gespräch',
        'interview', 'arbeitsamt', 'leistungen', 'hartz', 'arbeitsvertrag',
        'kündigung', 'gehalt', 'lohn', 'arbeitgeber', 'arbeitnehmer',
        'urlaub', 'krankheit', 'rente', 'sozial', 'beratung'
    ],
    'administrative': [
        'behörde', 'amt', 'bescheid', 'antrag', 'genehmigung',
        'steuer', 'finanzamt', 'ausländerbehörde', 'anmeldung',
        'dokument', 'unterlage', 'frist', 'einspruch', 'bescheid'
    ]
}

def analyze_text(text: str) -> Dict:
    """
    Аналіз тексту для витягування юридичних сутностей та ключових слів.
    
    Args:
        text: Текст для аналізу
    
    Returns:
        Словник з результатами аналізу
    """
    doc = nlp(text)
    
    # Витягування іменованих сутностей
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Витягування ключових слів (іменники та дієслова)
    keywords = [
        token.lemma_.lower() 
        for token in doc 
        if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop
    ][:15]  # Обмежуємо до 15
    
    # Витягування дат
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    
    # Витягування грошових сум
    money = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
    
    # Витягування організацій
    organizations = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    
    logger.info(f"Аналіз завершено: {len(entities)} сутностей, {len(keywords)} ключових слів")
    
    return {
        'entities': entities,
        'keywords': keywords,
        'dates': dates,
        'money': money,
        'organizations': organizations,
        'text_length': len(text),
        'sentence_count': len(list(doc.sents))
    }

def classify_letter_type(text: str) -> str:
    """
    Класифікація типу листа на основі ключових слів.
    
    Args:
        text: Текст листа
    
    Returns:
        Тип листа: 'debt_collection', 'tenancy', 'employment', 'administrative', 'general'
    """
    text_lower = text.lower()
    
    # Підрахунок збігів для кожної категорії
    scores = {}
    
    for category, keywords in KEYWORDS.items():
        score = sum(1 for keyword in keywords if keyword in text_lower)
        scores[category] = score
    
    logger.info(f"Класифікація: {scores}")
    
    # Вибір категорії з найвищим score
    max_score = max(scores.values())
    
    if max_score == 0:
        logger.info("Не знайдено збігів, повертаємо 'general'")
        return 'general'
    
    # Отримуємо всі категорії з максимальним score
    top_categories = [cat for cat, score in scores.items() if score == max_score]
    
    # Пріоритетність категорій
    priority = ['employment', 'debt_collection', 'tenancy', 'administrative']
    
    for cat in priority:
        if cat in top_categories:
            logger.info(f"Обрано категорію: {cat}")
            return cat
    
    return top_categories[0]

def extract_important_info(text: str) -> Dict:
    """
    Витягування важливої інформації з тексту.
    
    Args:
        text: Текст листа
    
    Returns:
        Словник з важливою інформацією
    """
    doc = nlp(text)
    
    info = {
        'dates': [],
        'money': [],
        'organizations': [],
        'locations': [],
        'persons': [],
        'reference_numbers': []
    }
    
    for ent in doc.ents:
        if ent.label_ == 'DATE':
            info['dates'].append(ent.text)
        elif ent.label_ == 'MONEY':
            info['money'].append(ent.text)
        elif ent.label_ == 'ORG':
            info['organizations'].append(ent.text)
        elif ent.label_ == 'LOC':
            info['locations'].append(ent.text)
        elif ent.label_ == 'PERSON':
            info['persons'].append(ent.text)
    
    # Пошук номерів справ/посилань (наприклад, AZ: 123/2024)
    import re
    ref_patterns = [
        r'[A-Z]{1,3}\s*[:.]?\s*\d+/\d+',  # AZ: 123/2024
        r'Nr\.\s*\d+',  # Nr. 12345
        r'Aktenzeichen\s*[:.]?\s*\S+',  # Aktenzeichen: ...
        r'Az\.\s*\S+'  # Az. ...
    ]
    
    for pattern in ref_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        info['reference_numbers'].extend(matches)
    
    logger.info(f"Витягнуто інформацію: {info}")
    return info
