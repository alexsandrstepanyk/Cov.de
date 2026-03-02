#!/usr/bin/env python3
"""
Advanced Classification Module v1.0
Розширена класифікація листів з комбінованим аналізом
"""

import re
from typing import Dict, Tuple, List


# ============================================================================
# РОЗШИРЕНІ КЛЮЧОВІ СЛОВА
# ============================================================================

ORG_KEYWORDS = {
    'jobcenter': {
        'weight': 3,  # Вага організації
        'keywords': [
            'jobcenter', 'arbeitsagentur', 'arbeitslos', 'hartz', 'sgb ii',
            'kundennummer', 'vermittlung', 'bewerbung', 'arbeitgeber',
            'leistung', 'sanktion', 'kürzung', 'bescheid', 'einladung',
            'gespräch', 'termin', 'vorsprache', 'berater', 'vermittler'
        ]
    },
    'finanzamt': {
        'weight': 3,
        'keywords': [
            'finanzamt', 'steuer', 'bescheid', 'steuernummer', 'einkommensteuer',
            'umsatzsteuer', 'nachzahlung', 'erstattung', 'steuererklärung',
            'elster', 'steuerbescheid', 'vorsteuer', 'meldung'
        ]
    },
    'inkasso': {
        'weight': 3,
        'keywords': [
            'inkasso', 'forderung', 'schuld', 'mahnung', 'zahlung',
            'gläubiger', 'schuldner', 'überweisung', 'ibаn', 'bic',
            'konto', 'betrag', 'fällig', 'verzug', 'zins'
        ]
    },
    'vermieter': {
        'weight': 3,
        'keywords': [
            'mieter', 'vermieter', 'wohnung', 'miete', 'mietvertrag',
            'mieterhöhung', 'kündigung', 'kaution', 'nebenkosten',
            'hausverwaltung', 'mieterbund', 'mietspiegel'
        ]
    },
    'gericht': {
        'weight': 3,
        'keywords': [
            'gericht', 'urteil', 'beschluss', 'aktenzeichen', 'verhandlung',
            'ladung', 'richter', 'anwalt', 'kläger', 'beklagte',
            'staatsanwaltschaft', 'prozess', 'klage'
        ]
    },
    'krankenkasse': {
        'weight': 3,
        'keywords': [
            'krankenkasse', 'aok', 'tk', 'barmer', 'versicherung',
            'versichert', 'beitrag', 'leistung', 'arzt', 'rezept',
            'krankenversicherung', 'pflegestufe', 'gesundheitszeugnis'
        ]
    },
    'versicherung': {
        'weight': 2,
        'keywords': [
            'versicherung', 'allianz', 'axa', 'hdi', 'police',
            'beitrag', 'leistung', 'schaden', 'vertrag', 'laufzeit',
            'kündigung', 'tarif'
        ]
    },
    'behörde': {
        'weight': 2,
        'keywords': [
            'behörde', 'amt', 'antrag', 'genehmigung', 'satzung',
            'stadt', 'gemeinde', 'landratsamt', 'rathaus', 'verwaltung',
            'aufenthalt', 'ausländerbehörde', 'anmeldung'
        ]
    },
}

SITUATION_KEYWORDS = {
    'einladung': {
        'weight': 2,
        'keywords': [
            'einladung', 'gespräch', 'termin', 'vorsprache', 'persönlich',
            'erscheinen', 'teilnahme', 'einladen'
        ]
    },
    'bescheid': {
        'weight': 2,
        'keywords': [
            'bescheid', 'festsetzung', 'steuerbescheid', 'leistungsbescheid',
            'ablehnung', 'bewilligung', 'feststellen', 'festsetzen'
        ]
    },
    'mahnung': {
        'weight': 2,
        'keywords': [
            'mahnung', 'zahlung', 'forderung', 'überweisung', 'iban',
            'offener betrag', 'fällig', 'zahle', 'begleichen',
            'erste mahnung', 'letzte mahnung'
        ]
    },
    'kuendigung': {
        'weight': 2,
        'keywords': [
            'kündigung', 'beendigung', 'auflösung', 'fristlos', 'fristgerecht',
            'kündigen', 'beenden'
        ]
    },
    'mieterhoehung': {
        'weight': 2,
        'keywords': [
            'mieterhöhung', 'miete', 'erhöhung', 'mietspiegel', 'kaltmiete',
            'warmmiete', 'anpassen'
        ]
    },
    'aufforderung': {
        'weight': 2,
        'keywords': [
            'aufforderung', 'mitwirkung', 'unterlage', 'frist', 'einreichen',
            'vorlegen', 'nachweis', 'beleg'
        ]
    },
    'rechnung': {
        'weight': 1,
        'keywords': [
            'rechnung', 'beitrag', 'kosten', 'betrag', 'euro', '€',
            'zahlen', 'bezahlen'
        ]
    },
    'ladung': {
        'weight': 2,
        'keywords': [
            'ladung', 'gericht', 'verhandlung', 'saal', 'richter',
            'kläger', 'beklagte', 'termin', 'erscheinen'
        ]
    },
}


# ============================================================================
# ФУНКЦІЇ КЛАСИФІКАЦІЇ
# ============================================================================

def classify_organization(text: str) -> Tuple[str, float]:
    """
    Класифікація організації за ключовими словами.
    
    Args:
        text: Текст листа
        
    Returns:
        (org_key, confidence)
    """
    text_lower = text.lower()
    scores = {}
    
    for org, data in ORG_KEYWORDS.items():
        score = 0
        for keyword in data['keywords']:
            if keyword in text_lower:
                score += data['weight']
        scores[org] = score
    
    # Знаходимо переможця
    max_score = max(scores.values()) if scores else 0
    
    if max_score == 0:
        return 'general', 0.0
    
    winners = [org for org, score in scores.items() if score == max_score]
    
    # Обчислюємо впевненість
    confidence = min(1.0, max_score / 10.0)  # Нормалізація до 1.0
    
    return winners[0], confidence


def classify_situation(text: str) -> Tuple[str, float]:
    """
    Класифікація ситуації за ключовими словами.
    
    Args:
        text: Текст листа
        
    Returns:
        (situation_key, confidence)
    """
    text_lower = text.lower()
    scores = {}
    
    for situation, data in SITUATION_KEYWORDS.items():
        score = 0
        for keyword in data['keywords']:
            if keyword in text_lower:
                score += data['weight']
        scores[situation] = score
    
    # Знаходимо переможця
    max_score = max(scores.values()) if scores else 0
    
    if max_score == 0:
        return 'general', 0.0
    
    winners = [sit for sit, score in scores.items() if score == max_score]
    
    # Обчислюємо впевненість
    confidence = min(1.0, max_score / 8.0)  # Нормалізація до 1.0
    
    return winners[0], confidence


def classify_letter_combined(text: str) -> Dict:
    """
    Комбінована класифікація листа.
    
    Args:
        text: Текст листа
        
    Returns:
        Dict з результатами класифікації
    """
    # Класифікація організації
    org_key, org_confidence = classify_organization(text)
    
    # Класифікація ситуації
    situation_key, situation_confidence = classify_situation(text)
    
    # Загальна впевненість
    overall_confidence = (org_confidence + situation_confidence) / 2
    
    return {
        'organization': org_key,
        'organization_confidence': org_confidence,
        'situation': situation_key,
        'situation_confidence': situation_confidence,
        'overall_confidence': overall_confidence,
        'is_confident': overall_confidence >= 0.6,
    }


def get_classification_description(result: Dict) -> str:
    """
    Отримати опис класифікації.
    
    Args:
        result: Результат класифікації
        
    Returns:
        Опис українською
    """
    org_names = {
        'jobcenter': 'Jobcenter / Arbeitsagentur',
        'finanzamt': 'Finanzamt',
        'inkasso': 'Inkasso / Forderung',
        'vermieter': 'Vermieter / Miete',
        'gericht': 'Gericht / Recht',
        'krankenkasse': 'Krankenkasse',
        'versicherung': 'Versicherung',
        'behörde': 'Behörde / Amt',
        'general': 'Загальний лист',
    }
    
    situation_names = {
        'einladung': 'Запрошення',
        'bescheid': 'Рішення / Bescheid',
        'mahnung': 'Нагадування / Mahnung',
        'kuendigung': 'Розірвання / Kündigung',
        'mieterhoehung': 'Підвищення оренди',
        'aufforderung': 'Вимога надати документи',
        'rechnung': 'Рахунок / Rechnung',
        'ladung': 'Судова повістка',
        'general': 'Загальне',
    }
    
    org_name = org_names.get(result['organization'], result['organization'])
    sit_name = situation_names.get(result['situation'], result['situation'])
    
    confidence_emoji = '✅' if result['is_confident'] else '⚠️'
    
    return (
        f"{confidence_emoji} **Організація:** {org_name} "
        f"({result['organization_confidence']:.0%})\n"
        f"{confidence_emoji} **Ситуація:** {sit_name} "
        f"({result['situation_confidence']:.0%})\n"
        f"📊 **Впевненість:** {result['overall_confidence']:.0%}"
    )


if __name__ == '__main__':
    # Тестування
    test_texts = [
        ('Jobcenter Einladung', '''Jobcenter Berlin Mitte
Einladung zum persönlichen Gespräch
Termin: 12.03.2026, 10:00 Uhr
Kundennummer: 123ABC'''),
        
        ('Finanzamt Steuerbescheid', '''Finanzamt München
Steuerbescheid 2025
Steuernummer: 12/345/67890
Nachzahlung: 500 EUR'''),
        
        ('Inkasso Mahnung', '''Inkasso Service
Mahnung
Offener Betrag: 350 EUR
IBAN: DE89...'''),
        
        ('Короткий лист', '''Finanzamt
Steuerbescheid
500 EUR'''),
    ]
    
    print_header = lambda t: print(f"\n{'='*60}\n{t}\n{'='*60}\n")
    
    for name, text in test_texts:
        print_header(f"ТЕСТ: {name}")
        
        result = classify_letter_combined(text)
        
        print(get_classification_description(result))
        print(f"\nДеталі:")
        print(f"  Org: {result['organization']} ({result['organization_confidence']:.2f})")
        print(f"  Sit: {result['situation']} ({result['situation_confidence']:.2f})")
        print(f"  Overall: {result['overall_confidence']:.2f}")
        print(f"  Is Confident: {result['is_confident']}")
