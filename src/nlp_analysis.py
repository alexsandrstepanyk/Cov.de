#!/usr/bin/env python3
"""
Advanced NLP Analysis Module for Gov.de
Використовує контекстний аналіз для точної класифікації листів
Інтегрований з SQLite базою даних законів.
"""

import spacy
import logging
from typing import Dict, List, Tuple
from collections import Counter

logger = logging.getLogger(__name__)

# Завантаження німецької моделі
try:
    nlp = spacy.load("de_core_news_sm")
    logger.info("spaCy модель de_core_news_sm завантажена")
except OSError:
    logger.error("Модель de_core_news_sm не знайдено!")
    raise

# Імпорт SQLite бази даних законів
try:
    from legal_database import (
        analyze_letter,
        search_laws,
        search_by_keywords,
        get_laws_by_category,
        get_consequences,
        detect_organization,
        detect_situation
    )
    DB_AVAILABLE = True
    logger.info("SQLite база даних законів підключена")
except Exception as e:
    logger.warning(f"SQLite база даних недоступна: {e}")
    DB_AVAILABLE = False

# Розширені ключові слова з контекстом
KEYWORDSWithContext = {
    'debt_collection': {
        'strong': [
            'mahnung', 'forderung', 'zahlung', 'schuld', 'rechnung',
            'überweisung', 'betrag', 'konto', 'bank', 'gläubiger',
            'inkasso', 'vollstreckung', 'pfändung', 'mahnen'
        ],
        'medium': [
            'offen', 'bezahlen', 'frist', 'zahlen', 'kredit',
            'darlehen', 'zinsen', 'säumnis', 'verzug'
        ],
        'context': [
            'sie schulden', 'zahlen sie', 'überweisen sie',
            'innerhalb von', 'tagen', 'euro', '€'
        ]
    },
    'tenancy': {
        'strong': [
            'miete', 'wohnung', 'mieter', 'vermieter', 'mietvertrag',
            'kündigung', 'nebenkosten', 'kaution', 'hausmeister',
            'mietzins', 'wohnraum'
        ],
        'medium': [
            'abrechnung', 'heizkosten', 'warmwasser', 'renovierung',
            'mangel', 'defekt', 'reparatur', 'mieterhöhung'
        ],
        'context': [
            'mieter', 'vermieter', 'wohnung', 'haus', 'zimmer',
            'quadratmeter', 'm²'
        ]
    },
    'employment': {
        'strong': [
            'jobcenter', 'arbeitsagentur', 'arbeitslos', 'bewerbung',
            'kündigung', 'arbeitsvertrag', 'gehalt', 'lohn',
            'arbeitgeber', 'arbeitnehmer', 'hartz'
        ],
        'medium': [
            'einladung', 'termin', 'gespräch', 'interview',
            'leistungen', 'arbeitsamt', 'vermittlung', 'beratung',
            'urlaub', 'krankheit', 'rente', 'sozial'
        ],
        'context': [
            'sgb', '§ 59', '§ 31', '§ 32', 'kundennummer',
            'vermittlungs', 'arbeitslosengeld'
        ]
    },
    'administrative': {
        'strong': [
            'behörde', 'amt', 'bescheid', 'antrag', 'genehmigung',
            'steuer', 'finanzamt', 'ausländerbehörde', 'anmeldung',
            'gericht', 'urteil', 'beschluss', 'anwalt'
        ],
        'medium': [
            'dokument', 'unterlage', 'frist', 'einspruch',
            'aktenzeichen', 'geschäftszeichen', 'satzung', 'verordnung'
        ],
        'context': [
            'vg', 'vwvfg', 'sbg', 'ao', 'gg', 'lvwvfg',
            'rechtsmittel', 'einspruchs'
        ]
    },
    'personal': {
        'strong': [
            'sohn', 'tochter', 'kind', 'familie', 'eltern',
            'schule', 'lehrer', 'zeugnis', 'note', 'klasse',
            'geburtstag', 'feier', 'einladung', 'gratulation'
        ],
        'medium': [
            'erfolg', 'leistung', 'fortschritt', 'entwicklung',
            'teilnahme', 'projekt', 'veranstaltung', 'aktivität',
            'brief', 'nachricht', 'persönlich'
        ],
        'context': [
            'ihr kind', 'mein sohn', 'meine tochter', 'wir freuen',
            'herzlichen glückwunsch', 'liebe', 'beste grüße'
        ]
    },
    'insurance': {
        'strong': [
            'versicherung', 'kasse', 'beitrag', 'leistung', 'tarif',
            'aok', 'tk', 'barmer', 'dak', 'krankenkasse'
        ],
        'medium': [
            'versichert', 'abrechnung', 'rezept', 'behandlung',
            'arzt', 'klinik', 'spital', 'gesund'
        ],
        'context': [
            'versichertennummer', 'kassennummer', 'sgb v', 'bema',
            'gebührenordnung'
        ]
    },
    'utility': {
        'strong': [
            'strom', 'gas', 'wasser', 'heizung', 'energie',
            'stadtwerk', 'versorger', 'zähler', 'verbrauch'
        ],
        'medium': [
            'rechnung', 'abschlag', 'nachzahlung', 'guthaben',
            'tarif', 'vertrag', 'lieferant'
        ],
        'context': [
            'kilowattstunde', 'kwh', 'zählerstand', 'grundversorgung'
        ]
    }
}

# Закони та коди для кожного типу
LAWS_BY_TYPE = {
    'debt_collection': {
        'primary': [
            'BGB § 286 (Прострочення боржника)',
            'BGB § 288 (Проценти у простроченні)',
            'BGB § 241 (Обов\'язки зі зобов\'язання)'
        ],
        'secondary': [
            'BGB § 433 (Купівля-продаж)',
            'BGB § 488 (Кредитний договір)',
            'BGB § 823 (Відшкодування збитків)',
            'ZPO § 42 (Судовий процес)'
        ]
    },
    'tenancy': {
        'primary': [
            'BGB § 535 (Обов\'язки орендодавця)',
            'BGB § 536 (Зниження оренди при дефектах)',
            'BGB § 558 (Підвищення оренди)'
        ],
        'secondary': [
            'BGB § 543 (Позачергове розірвання)',
            'BGB § 573 (Розірвання орендодавцем)',
            'BGB § 555 (Модернізація)',
            'WoHG § 1 (Закон про житлове господарство)'
        ]
    },
    'employment': {
        'primary': [
            '§ 59 SGB II (Обов\'язок явки на Jobcenter)',
            '§ 31 SGB II (Наслідки неявки)',
            'BGB § 611 (Трудовий договір)'
        ],
        'secondary': [
            'KSchG § 1 (Захист від звільнення)',
            'BGB § 620 (Припинення трудових відносин)',
            '§ 309 SGB III (Офіційні запрошення)',
            'SGB III § 130 (Арbeitslosengeld)'
        ]
    },
    'administrative': {
        'primary': [
            'VwVfG § 35 (Адміністративний акт)',
            'VwGO § 42 (Право на оскарження)',
            'VwVfG § 28 (Право на вислуховування)'
        ],
        'secondary': [
            'VwVfG § 29 (Доступ до файлів)',
            'VwVfG § 44 (Недійсність акту)',
            'GG § 19 (Основне право на звернення)',
            'SGB X (Соціальний кодекс)'
        ]
    },
    'personal': {
        'primary': [
            'Не застосовується (особисте листування)'
        ],
        'secondary': [
            'BGB § 823 (Загальні права особистості)',
            'GG § 1 (Гідність людини)',
            'GG § 2 (Вільний розвиток особистості)'
        ]
    },
    'insurance': {
        'primary': [
            'SGB V § 1 (Обов\'язкове страхування)',
            'SGB V § 19 (Реєстрація)',
            'BGB § 779 (Договір страхування)'
        ],
        'secondary': [
            'VVG § 1 (Закон про страхування)',
            'SGB V § 25 (Медичне обслуговування)',
            'BGB § 611 (Договір про надання послуг)'
        ],
        'consequences': '⚠️ При несплаті внесків:\n• Можливе припинення покриття\n• Вимога сплати заборгованості\n• Розірвання договору'
    },
    'utility': {
        'primary': [
            'BGB § 535 (Постачання енергії)',
            'EnWG § 1 (Закон про енергетику)',
            'BGB § 433 (Договір постачання)'
        ],
        'secondary': [
            'StromGVV § 1 (Постачання електроенергії)',
            'GasGVV § 1 (Постачання газу)',
            'BGB § 241 (Зобов\'язання з договору)'
        ],
        'consequences': '⚠️ При несплаті рахунків:\n• Можливе відключення послуг\n• Нарахування пені\n• Примусове стягнення боргу'
    },
    'general': {
        'primary': [
            'BGB § 241 (Обов\'язки зі зобов\'язання)',
            'BGB § 242 (Добросовісність)',
            'BGB § 308 (Неприпустимі умови договору)'
        ],
        'secondary': [
            'BGB § 133 (Тлумачення заяв)',
            'BGB § 157 (Тлумачення договорів)',
            'GG § 2 (Загальні права громадян)'
        ],
        'consequences': '📋 Залежно від типу листа можливі різні наслідки.\nРекомендується звернутися до фахівця для детального розбору вашої ситуації.\n\n📞 Безкоштовна правова допомога:\n• Telefonseelsorge: 0800 111 0 111\n• Rechtsantragsstelle: безкоштовна консультація'
    }
}

def analyze_context(doc) -> Dict[str, float]:
    """
    Аналіз контексту документа.
    
    Returns:
        Dict з оцінками для кожного типу листа
    """
    scores = {}
    
    # Отримуємо частини мови
    nouns = [token.lemma_.lower() for token in doc if token.pos_ == 'NOUN']
    verbs = [token.lemma_.lower() for token in doc if token.pos_ == 'VERB']
    adjectives = [token.lemma_.lower() for token in doc if token.pos_ == 'ADJ']
    
    # Аналіз іменованих сутностей
    entities = {ent.label_: ent.text for ent in doc.ents}
    
    # Перевірка на особисті звертання
    has_personal_address = any(
        word in ' '.join(adjectives + nouns)
        for word in ['liebe', 'lieber', 'herzliche', 'persönlich', 'familie']
    )
    
    # Перевірка на офіційний стиль
    has_formal_style = any(
        word in ' '.join(doc.text.lower().split())
        for word in ['hiermit', 'gemäß', 'aufgrund', 'betreffend', 'bezugnehmend']
    )
    
    # Перевірка на емоційне забарвлення
    emotional_words = ['freuen', 'glückwunsch', 'erfolg', 'toll', 'super', 'klasse']
    has_emotional = any(word in ' '.join(verbs + adjectives) for word in emotional_words)
    
    return {
        'personal': 0.8 if (has_personal_address or has_emotional) else 0.1,
        'formal': 0.8 if has_formal_style else 0.2,
        'entities': entities,
        'nouns': nouns,
        'verbs': verbs,
    }

def classify_letter_type_advanced(text: str) -> Tuple[str, Dict]:
    """
    Розширена класифікація типу листа з контекстним аналізом.
    
    Args:
        text: Текст листа
    
    Returns:
        (тип листа, детальна інформація)
    """
    doc = nlp(text)
    text_lower = text.lower()
    
    # Контекстний аналіз
    context = analyze_context(doc)
    
    # Підрахунок балів для кожного типу
    type_scores = {}
    
    for letter_type, keywords in KEYWORDSWithContext.items():
        score = 0
        details = {
            'strong_matches': [],
            'medium_matches': [],
            'context_matches': [],
            'context_bonus': 0
        }
        
        # Strong keywords (3 бали кожен)
        for keyword in keywords['strong']:
            if keyword in text_lower:
                score += 3
                details['strong_matches'].append(keyword)
        
        # Medium keywords (1 бал кожен)
        for keyword in keywords['medium']:
            if keyword in text_lower:
                score += 1
                details['medium_matches'].append(keyword)
        
        # Context keywords (2 бали кожен)
        for keyword in keywords['context']:
            if keyword in text_lower:
                score += 2
                details['context_matches'].append(keyword)
        
        # Context bonus
        if letter_type == 'personal' and context['personal'] > 0.5:
            score += 5
            details['context_bonus'] = 5
        elif letter_type != 'personal' and context['formal'] > 0.5:
            score += 2
        
        # Penalize personal for formal documents
        if letter_type == 'personal' and context['formal'] > 0.5:
            score -= 10
        
        type_scores[letter_type] = score
        details['total_score'] = score
    
    # Визначаємо переможця
    max_score = max(type_scores.values())
    
    if max_score == 0:
        return 'general', {'scores': type_scores, 'details': {}}
    
    # Отримуємо всі типи з максимальним score
    top_types = [t for t, s in type_scores.items() if s == max_score]
    
    # Пріоритетність при однакових балах
    priority = ['personal', 'employment', 'administrative', 'tenancy', 'debt_collection', 'insurance', 'utility']
    
    winner = None
    for ptype in priority:
        if ptype in top_types:
            winner = ptype
            break
    
    if not winner:
        winner = top_types[0]
    
    logger.info(f"Класифікація: {type_scores}")
    logger.info(f"Обрано категорію: {winner}")
    
    return winner, {
        'scores': type_scores,
        'details': type_scores,
        'context': context,
        'winner_details': KEYWORDSWithContext.get(winner, {})
    }

def get_laws_for_letter(letter_type: str, text: str) -> Dict:
    """
    Отримання релевантних законів для типу листа.
    Використовує SQLite базу даних якщо доступна.

    Args:
        letter_type: Тип листа
        text: Текст листа (для додаткового аналізу)

    Returns:
        Dict з законами
    """
    # Спробуємо використати SQLite базу даних
    if DB_AVAILABLE:
        try:
            # Аналізуємо лист через базу даних
            db_analysis = analyze_letter(text)
            
            if db_analysis and db_analysis.get('paragraphs'):
                return {
                    'primary': db_analysis['paragraphs'],
                    'secondary': [],
                    'organization': db_analysis.get('organization', ''),
                    'situation': db_analysis.get('situation', ''),
                    'consequences': db_analysis.get('consequences', '')
                }
        except Exception as e:
            logger.warning(f"Помилка використання SQLite бази: {e}")
    
    # Fallback на стару логіку
    laws = LAWS_BY_TYPE.get(letter_type, LAWS_BY_TYPE['general'])

    # Додатковий аналіз для уточнення законів
    text_lower = text.lower()

    specific_laws = {
        'jobcenter': '§ 59 SGB II',
        'arbeitsagentur': 'SGB III',
        'finanzamt': 'AO (Abgabenordnung)',
        'gericht': 'ZPO / StPO',
        'miete': 'BGB Mietrecht',
        'strom': 'EnWG',
        'versicherung': 'SGB V / VVG',
    }

    for key, law in specific_laws.items():
        if key in text_lower:
            laws['specific'] = law
            break

    return laws


def get_laws_from_database(keywords: List[str]) -> List[Dict]:
    """
    Пошук законів у базі даних за ключовими словами.
    
    Args:
        keywords: Список ключових слів
        
    Returns:
        Список знайдених законів
    """
    if not DB_AVAILABLE:
        return []
    
    try:
        return search_by_keywords(keywords)
    except Exception as e:
        logger.error(f"Помилка пошуку законів: {e}")
        return []


def analyze_letter_with_db(text: str) -> Dict:
    """
    Аналіз листа з використанням SQLite бази даних.
    
    Args:
        text: Текст листа
        
    Returns:
        Dict з результатами аналізу
    """
    if not DB_AVAILABLE:
        return None
    
    try:
        return analyze_letter(text)
    except Exception as e:
        logger.error(f"Помилка аналізу через базу даних: {e}")
        return None

def analyze_text_advanced(text: str) -> Dict:
    """
    Розширений аналіз тексту.
    
    Args:
        text: Текст листа
    
    Returns:
        Dict з результатами аналізу
    """
    doc = nlp(text)
    
    # Витягування іменованих сутностей
    entities = [(ent.text, ent.label_) for ent in doc.ents]
    
    # Витягування ключових слів (іменники та дієслова)
    keywords = [
        token.lemma_.lower()
        for token in doc
        if token.pos_ in ['NOUN', 'VERB'] and not token.is_stop
    ][:20]
    
    # Витягування дат
    dates = [ent.text for ent in doc.ents if ent.label_ == 'DATE']
    
    # Витягування грошових сум
    money = [ent.text for ent in doc.ents if ent.label_ == 'MONEY']
    
    # Витягування організацій
    organizations = [ent.text for ent in doc.ents if ent.label_ == 'ORG']
    
    # Витягування осіб
    persons = [ent.text for ent in doc.ents if ent.label_ == 'PERSON']
    
    # Аналіз тону (простий)
    formal_indicators = ['hiermit', 'gemäß', 'aufgrund', 'sehr geehrte']
    is_formal = any(ind in text.lower() for ind in formal_indicators)
    
    return {
        'entities': entities,
        'keywords': keywords,
        'dates': dates,
        'money': money,
        'organizations': organizations,
        'persons': persons,
        'text_length': len(text),
        'sentence_count': len(list(doc.sents)),
        'is_formal': is_formal,
        'language': 'de'  # Припускаємо німецьку
    }
