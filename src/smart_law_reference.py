#!/usr/bin/env python3
"""
Smart Law Reference System for Gov.de
Аналізує текст листа та знаходить конкретні параграфи законів для посилання
"""

import re
import logging
from typing import Dict, List, Tuple, Optional

logger = logging.getLogger(__name__)

# База законів з конкретними ситуаціями та параграфами
LAW_DATABASE = {
    'finanzamt': {
        'name': 'Finanzamt (Податкова)',
        'laws': {
            'steuernachzahlung': {
                'paragraphs': ['AO § 150', 'AO § 172', 'EStG § 25'],
                'description': 'Податкова заборгованість',
                'consequences': 'Сплата протягом 1 місяця, інакше пеня 0.5% за місяць',
                'keywords': ['steuernachzahlung', 'steuerbescheid', 'nachzahlung']
            },
            'prüfung': {
                'paragraphs': ['AO § 193', 'AO § 196', 'AO § 203'],
                'description': 'Податкова перевірка',
                'consequences': 'Обов\'язкова участь, надання документів',
                'keywords': ['prüfung', 'betriebsprüfung', 'außenprüfung']
            },
            'fristverlängerung': {
                'paragraphs': ['AO § 108', 'AO § 109'],
                'description': 'Продовження строку',
                'consequences': 'Можна подати заяву на продовження',
                'keywords': ['frist', 'verlängerung', 'aufschub']
            }
        }
    },
    'jobcenter': {
        'name': 'Jobcenter / Arbeitsagentur',
        'laws': {
            'einladung': {
                'paragraphs': ['§ 59 SGB II', '§ 309 SGB III'],
                'description': 'Запрошення на співбесіду',
                'consequences': 'Обов\'язкова явка, інакше санкції 30%',
                'keywords': ['einladung', 'termin', 'gespräch', 'vorsprache']
            },
            'sanktion': {
                'paragraphs': ['§ 31 SGB II', '§ 32 SGB II'],
                'description': 'Санкції за неявку',
                'consequences': 'Зменшення виплат на 30% на 12 тижнів',
                'keywords': ['sanktion', 'kürzung', 'minderung', 'sperre']
            },
            'leistung': {
                'paragraphs': ['§ 19 SGB II', '§ 20 SGB II', '§ 22 SGB II'],
                'description': 'Виплати та допомога',
                'consequences': 'Право на отримання допомоги',
                'keywords': ['leistung', 'geld', 'betrag', 'auszahlung']
            },
            'ablehnung': {
                'paragraphs': ['§ 33 SGB II', '§ 39 SGB X'],
                'description': 'Відмова у виплатах',
                'consequences': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['ablehnung', 'abgelehnt', 'verweigert']
            }
        }
    },
    'vermieter': {
        'name': 'Vermieter (Орендодавець)',
        'laws': {
            'mieterhöhung': {
                'paragraphs': ['BGB § 558', 'BGB § 559', 'BGB § 560'],
                'description': 'Підвищення орендної плати',
                'consequences': 'Згода потрібна, якщо підвищення > 20% за 3 роки',
                'keywords': ['mieterhöhung', 'erhöhung', 'neue miete']
            },
            'kündigung': {
                'paragraphs': ['BGB § 573', 'BGB § 573c', 'BGB § 543'],
                'description': 'Розірвання договору оренди',
                'consequences': 'Строк попередження 3 місяці',
                'keywords': ['kündigung', 'kündigen', 'frist']
            },
            'nebenkosten': {
                'paragraphs': ['BGB § 556', 'BGB § 556a'],
                'description': 'Додаткові витрати',
                'consequences': 'Потрібна детальна розбивка',
                'keywords': ['nebenkosten', 'abrechnung', 'heizkosten']
            },
            'mangel': {
                'paragraphs': ['BGB § 536', 'BGB § 536a', 'BGB § 543'],
                'description': 'Дефекти житла',
                'consequences': 'Можна зменшити оренду (Mietminderung)',
                'keywords': ['mangel', 'defekt', 'schimmel', 'reparatur']
            }
        }
    },
    'inkasso': {
        'name': 'Inkasso (Колектори)',
        'laws': {
            'mahnung': {
                'paragraphs': ['BGB § 286', 'BGB § 288'],
                'description': 'Нагадування про сплату',
                'consequences': 'Пеня 5% річних для споживачів',
                'keywords': ['mahnung', 'mahnen', 'forderung']
            },
            'forderung': {
                'paragraphs': ['BGB § 194', 'BGB § 195', 'BGB § 199'],
                'description': 'Вимога сплати боргу',
                'consequences': 'Строк позовної давності 3 роки',
                'keywords': ['forderung', 'schuld', 'betrag', 'rechnung']
            },
            'vollstreckung': {
                'paragraphs': ['BGB § 823', 'ZPO § 42', 'ZPO § 704'],
                'description': 'Примусове стягнення',
                'consequences': 'Можливе через Gerichtsvollzieher',
                'keywords': ['vollstreckung', 'gerichtsvollzieher', 'pfändung']
            },
            'betrug': {
                'paragraphs': ['StGB § 263', 'UWG § 4'],
                'description': 'Шахрайство',
                'consequences': 'Кримінальна відповідальність, не платіть!',
                'keywords': ['western union', 'bitcoin', 'paysafecard', 'geschenkkarte']
            }
        }
    },
    'gericht': {
        'name': 'Gericht (Суд)',
        'laws': {
            'beschluss': {
                'paragraphs': ['ZPO § 329', 'ZPO § 339'],
                'description': 'Судове рішення',
                'consequences': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['beschluss', 'urteil', 'entscheidung']
            },
            'ladung': {
                'paragraphs': ['ZPO § 217', 'ZPO § 220'],
                'description': 'Судова повістка',
                'consequences': 'Обов\'язкова явка в суд',
                'keywords': ['ladung', 'termin', 'verhandlung']
            },
            'mahnsache': {
                'paragraphs': ['ZPO § 688', 'ZPO § 699'],
                'description': 'Судовий наказ про сплату',
                'consequences': 'Можна подати Widerspruch протягом 2 тижнів',
                'keywords': ['mahnsache', 'mahnbescheid', 'vollstreckungsbescheid']
            }
        }
    },
    'krankenkasse': {
        'name': 'Krankenkasse (Лікарняна каса)',
        'laws': {
            'beitrag': {
                'paragraphs': ['SGB V § 249', 'SGB V § 250'],
                'description': 'Страхові внески',
                'consequences': 'Обов\'язкова сплата щомісяця',
                'keywords': ['beitrag', 'zahlung', 'monatlich']
            },
            'leistung': {
                'paragraphs': ['SGB V § 27', 'SGB V § 28'],
                'description': 'Медичні послуги',
                'consequences': 'Право на медичне обслуговування',
                'keywords': ['leistung', 'behandlung', 'arzt', 'rezept']
            },
            'antrag': {
                'paragraphs': ['SGB V § 19', 'SGB X § 16'],
                'description': 'Заява на отримання послуг',
                'consequences': 'Розгляд протягом 3 місяців',
                'keywords': ['antrag', 'beantragen', 'genehmigung']
            }
        }
    },
    'stadtwerk': {
        'name': 'Stadtwerk (Комунальні послуги)',
        'laws': {
            'rechnung': {
                'paragraphs': ['BGB § 535', 'EnWG § 36'],
                'description': 'Рахунок за послуги',
                'consequences': 'Сплата протягом 14 днів',
                'keywords': ['rechnung', 'betrag', 'strom', 'gas', 'wasser']
            },
            'sperre': {
                'paragraphs': ['BGB § 314', 'EnWG § 41'],
                'description': 'Відключення послуг',
                'consequences': 'Можливе при боргу > 100€',
                'keywords': ['sperre', 'abschaltung', 'unterbrechung']
            }
        }
    },
    'behörde': {
        'name': 'Behörde (Офіційна установа)',
        'laws': {
            'bescheid': {
                'paragraphs': ['VwVfG § 35', 'VwVfG § 37'],
                'description': 'Адміністративний акт',
                'consequences': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['bescheid', 'verwaltungsakt', 'entscheidung']
            },
            'widerspruch': {
                'paragraphs': ['VwGO § 68', 'VwGO § 70'],
                'description': 'Оскарження рішення',
                'consequences': 'Строк подання 1 місяць',
                'keywords': ['widerspruch', 'einspruch', 'klage']
            },
            'frist': {
                'paragraphs': ['VwVfG § 31', 'VwVfG § 32'],
                'description': 'Строки виконання',
                'consequences': 'Можна подати на Fristverlängerung',
                'keywords': ['frist', 'fristsetzung', 'deadline']
            }
        }
    }
}

# Шаблони відповідей німецькою
RESPONSE_TEMPLATES_DE = {
    'finanzamt': {
        'steuernachzahlung': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihren Steuerbescheid vom [DATUM].

Gemäß AO § 172 bitte ich um Überprüfung des Bescheids. 
Ich benötige eine detaillierte Aufstellung der Nachzahlung.

Bitte gewähren Sie mir eine Fristverlängerung gemäß AO § 108.

Mit freundlichen Grüßen
[Ihr Name]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihr Schreiben vom [DATUM].

Bitte um detaillierte Erklärung und Begründung.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'jobcenter': {
        'einladung': '''Sehr geehrte Damen und Herren,

hiermit bestätige ich den Termin am [DATUM] um [UHRZEIT].

Ich werde pünktlich erscheinen.

Mit freundlichen Grüßen
[Ihr Name]
Kundennummer: [NUMMER]''',
        'sanktion': '''Sehr geehrte Damen und Herren,

hiermit lege ich Widerspruch gegen die Sanktion ein.

Begründung: [GRUND]

Gemäß § 39 SGB X bitte ich um Überprüfung.

Mit freundlichen Grüßen
[Ihr Name]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihr Schreiben.

Bitte um detaillierte Information.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'vermieter': {
        'mieterhöhung': '''Sehr geehrte(r) [NAME],

ich nehme zur Kenntnis Ihre Mieterhöhung.

Gemäß BGB § 558 bitte ich um detaillierte Begründung 
und Vergleich mit der ortsüblichen Miete.

Mit freundlichen Grüßen
[Ihr Name]''',
        'kündigung': '''Sehr geehrte(r) [NAME],

ich habe Ihre Kündigung erhalten.

Ich prüfe die Rechtmäßigkeit und melde mich.

Mit freundlichen Grüßen
[Ihr Name]''',
        'default': '''Sehr geehrte(r) [NAME],

ich beziehe mich auf Ihr Schreiben.

Bitte um detaillierte Information.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'inkasso': {
        'forderung': '''Sehr geehrte Damen und Herren,

ich bestreite die Forderung in voller Höhe.

Bitte um detaillierte Aufstellung und Nachweis.

Gemäß BGB § 286 befinde ich mich nicht im Verzug.

Mit freundlichen Grüßen
[Ihr Name]''',
        'betrug': '''ACHTUNG: NICHT BEZAHLEN!
Dies ist wahrscheinlich Betrug.''',
        'default': '''Sehr geehrte Damen und Herren,

ich prüfe die Forderung und melde mich.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'gericht': {
        'beschluss': '''Sehr geehrte Damen und Herren,

ich nehme den Beschluss zur Kenntnis.

Ich prüfe meine weiteren Schritte.

Mit freundlichen Grüßen
[Ihr Name]
Aktenzeichen: [AZ]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf das Schreiben.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'krankenkasse': {
        'leistung': '''Sehr geehrte Damen und Herren,

ich beantrage die Leistung gemäß SGB V.

Bitte um Genehmigung und Information.

Mit freundlichen Grüßen
[Ihr Name]
Versichertennummer: [NUMMER]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihr Schreiben.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'stadtwerk': {
        'rechnung': '''Sehr geehrte Damen und Herren,

ich habe die Rechnung erhalten.

Bitte um Überprüfung und detaillierte Aufstellung.

Mit freundlichen Grüßen
[Ihr Name]
Kundennummer: [NUMMER]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihr Schreiben.

Mit freundlichen Grüßen
[Ihr Name]'''
    },
    'behörde': {
        'bescheid': '''Sehr geehrte Damen und Herren,

ich lege Widerspruch gegen den Bescheid ein.

Begründung: [GRUND]

Gemäß VwGO § 70 innerhalb eines Monats.

Mit freundlichen Grüßen
[Ihr Name]''',
        'default': '''Sehr geehrte Damen und Herren,

ich beziehe mich auf Ihr Schreiben.

Mit freundlichen Grüßen
[Ihr Name]'''
    }
}

# Шаблони відповідей українською
RESPONSE_TEMPLATES_UK = {
    'finanzamt': {
        'steuernachzahlung': '''Шановний(а),

Посилаючись на ваш податковий акт від [ДАТА].

Згідно з AO § 172, прошу перевірити рішення.
Мені потрібна детальна розбивка доплати.

Прошу продовжити строк згідно з AO § 108.

З повагою,
[Ваше ім'я]''',
        'default': '''Шановний(а),

Посилаючись на ваш лист від [ДАТА].

Прошу надати детальне пояснення.

З повагою,
[Ваше ім'я]'''
    },
    'jobcenter': {
        'einladung': '''Шановний(а),

Підтверджую термін [ДАТА] о [ЧАС].

Я з'явлюся вчасно.

З повагою,
[Ваше ім'я]
Номер клієнта: [НОМЕР]''',
        'sanktion': '''Шановний(а),

Подаю заперечення проти санкції.

Обґрунтування: [ПРИЧИНА]

Згідно з § 39 SGB X, прошу перевірити.

З повагою,
[Ваше ім'я]''',
        'default': '''Шановний(а),

Посилаючись на ваш лист.

Прошу надати детальну інформацію.

З повагою,
[Ваше ім'я]'''
    },
    'vermieter': {
        'mieterhöhung': '''Шановний(а) [ІМ'Я],

Приймаю до відома ваше підвищення оренди.

Згідно з BGB § 558, прошу детальне обґрунтування
та порівняння з місцевою орендою.

З повагою,
[Ваше ім'я]''',
        'default': '''Шановний(а) [ІМ'Я],

Посилаючись на ваш лист.

Прошу надати детальну інформацію.

З повагою,
[Ваше ім'я]'''
    },
    'inkasso': {
        'forderung': '''Шановний(а),

Заперечую проти вимоги сплати.

Прошу детальну розбивку та докази.

Згідно з BGB § 286, я не перебуваю у простроченні.

З повагою,
[Ваше ім'я]''',
        'default': '''Шановний(а),

Перевіряю вимогу та зв'яжуся з вами.

З повагою,
[Ваше ім'я]'''
    },
    'general': {
        'default': '''Шановний(а),

Дякую за ваше повідомлення.

Прошу надати детальну інформацію.

З повагою,
[Ваше ім'я]'''
    }
}


def detect_organization(text: str) -> str:
    """
    Визначення організації за текстом листа.
    
    Args:
        text: Текст листа
    
    Returns:
        Ключ організації (finanzamt, jobcenter тощо)
    """
    text_lower = text.lower()
    
    # Пріоритетні ключові слова для кожної організації
    org_keywords = {
        'finanzamt': ['finanzamt', 'steuer', 'bescheid', 'sternummer', 'einkommensteuer'],
        'jobcenter': ['jobcenter', 'arbeitsagentur', 'arbeitslos', 'hartz', 'sgb ii', 'kundennummer'],
        'vermieter': ['mieter', 'vermieter', 'wohnung', 'miete', 'mietvertrag'],
        'inkasso': ['inkasso', 'forderung', 'schuld', 'mahnung', 'zahlung'],
        'gericht': ['gericht', 'urteil', 'beschluss', 'aktenzeichen', 'verhandlung'],
        'krankenkasse': ['krankenkasse', 'aok', 'tk', 'barmer', 'versicherung', 'versichert'],
        'stadtwerk': ['stadtwerk', 'strom', 'gas', 'wasser', 'energie', 'zähler'],
        'behörde': ['behörde', 'amt', 'antrag', 'genehmigung', 'satzung']
    }
    
    # Підрахунок балів для кожної організації
    scores = {}
    for org, keywords in org_keywords.items():
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[org] = score
    
    # Визначаємо переможця
    max_score = max(scores.values())
    if max_score == 0:
        return 'general'
    
    winners = [org for org, score in scores.items() if score == max_score]
    return winners[0]


def detect_situation(text: str, organization: str) -> str:
    """
    Визначення ситуації за текстом листа.
    
    Args:
        text: Текст листа
        organization: Організація
    
    Returns:
        Ключ ситуації (einladung, mahnung тощо)
    """
    text_lower = text.lower()
    
    if organization not in LAW_DATABASE:
        return 'default'
    
    org_laws = LAW_DATABASE[organization]['laws']
    
    # Підрахунок балів для кожної ситуації
    scores = {}
    for situation, data in org_laws.items():
        score = sum(1 for kw in data['keywords'] if kw in text_lower)
        scores[situation] = score
    
    # Визначаємо переможця
    max_score = max(scores.values())
    if max_score == 0:
        return 'default'
    
    winners = [sit for sit, score in scores.items() if score == max_score]
    return winners[0]


def get_law_reference(text: str) -> Dict:
    """
    Отримання посилання на закон на основі аналізу тексту.
    
    Args:
        text: Текст листа
    
    Returns:
        Dict з інформацією про закон
    """
    # Визначаємо організацію
    organization = detect_organization(text)
    
    # Визначаємо ситуацію
    situation = detect_situation(text, organization)
    
    # Отримуємо інформацію про закон
    if organization in LAW_DATABASE:
        org_data = LAW_DATABASE[organization]
        if situation in org_data['laws']:
            law_data = org_data['laws'][situation]
            return {
                'organization': org_data['name'],
                'organization_key': organization,
                'situation': law_data['description'],
                'situation_key': situation,
                'paragraphs': law_data['paragraphs'],
                'consequences': law_data['consequences'],
                'keywords': law_data['keywords']
            }
    
    # Default для general
    return {
        'organization': 'Загальний лист',
        'organization_key': 'general',
        'situation': 'Не визначено',
        'situation_key': 'default',
        'paragraphs': ['BGB § 241', 'BGB § 242'],
        'consequences': 'Залежить від контексту листа',
        'keywords': []
    }


def generate_response_smart(text: str, language: str = 'uk') -> str:
    """
    Генерація розумної відповіді на основі аналізу тексту.
    
    Args:
        text: Текст листа
        language: Мова відповіді ('uk' або 'de')
    
    Returns:
        Текст відповіді
    """
    # Отримуємо інформацію про закон
    law_info = get_law_reference(text)
    
    org_key = law_info['organization_key']
    sit_key = law_info['situation_key']
    
    # Вибираємо шаблон
    if language == 'de':
        templates = RESPONSE_TEMPLATES_DE.get(org_key, RESPONSE_TEMPLATES_DE['general'])
    else:
        templates = RESPONSE_TEMPLATES_UK.get(org_key, RESPONSE_TEMPLATES_UK['general'])
    
    response = templates.get(sit_key, templates.get('default', ''))
    
    return response, law_info


def is_personal_letter(text: str) -> bool:
    """
    Визначення чи лист є особистим (не потребує законів).
    
    Args:
        text: Текст листа
    
    Returns:
        True якщо лист особистий
    """
    text_lower = text.lower()
    
    # Ознаки особистого листа
    personal_indicators = [
        'sohn', 'tochter', 'kind', 'junge', 'mädchen',  # діти
        'erfolg', 'leistung', 'note', 'zeugnis',  # успіхи
        'geburtstag', 'feier', 'einladung',  # свята
        'familie', 'eltern', 'oma', 'opa',  # сім'я
        'freuen', 'gratulieren', 'toll', 'super', 'klasse',  # емоції
        'liebe', 'lieber', 'herzliche', 'beste grüße',  # звертання
        'urlaub', 'ferien', 'reise',  # відпустка
        'gesund', 'besserung', 'gute besserung',  # здоров'я
    ]
    
    # Ознаки офіційного листа
    official_indicators = [
        'hiermit', 'gemäß', 'aufgrund', 'betreffend',  # офіційний стиль
        'frist', 'termin', 'zahlung', 'rechnung',  # терміни/оплата
        'mahnung', 'forderung', 'bescheid',  # офіційні документи
        'gesetz', 'paragraf', '§',  # закони
        'konto', 'iban', 'betrag', 'euro',  # гроші
        'unterschrift', 'stempel',  # підписи
    ]
    
    # Підрахунок балів
    personal_score = sum(1 for word in personal_indicators if word in text_lower)
    official_score = sum(1 for word in official_indicators if word in text_lower)
    
    # Якщо особистих слів більше і немає офіційних - це особистий лист
    return personal_score > 2 and official_score == 0


def analyze_letter_smart(text: str, language: str = 'uk') -> Dict:
    """
    Повний розумний аналіз листа.
    
    Args:
        text: Текст листа
        language: Мова користувача
    
    Returns:
        Dict з повною інформацією
    """
    # Перевіряємо чи лист особистий
    if is_personal_letter(text):
        return analyze_personal_letter(text, language)
    
    # Офіційний лист - глибокий аналіз
    return analyze_official_letter(text, language)


def analyze_personal_letter(text: str, language: str = 'uk') -> Dict:
    """
    Аналіз особистого листа (без законів).
    """
    # Проста відповідь без законів
    if language == 'de':
        response = '''Vielen Dank für Ihre Nachricht!

Das sind wunderbare Neuigkeiten. Ich freue mich sehr darüber!

Mit herzlichen Grüßen
[Ihr Name]'''
    else:
        response = '''Дякую за ваше повідомлення!

Це чудові новини! Я дуже радий(а) за вас!

З найкращими побажаннями,
[Ваше ім'я]'''
    
    return {
        'law_info': {
            'organization': 'Особисте листування',
            'organization_key': 'personal',
            'situation': 'Особисте повідомлення',
            'situation_key': 'personal',
            'paragraphs': [],
            'consequences': 'Не застосовується'
        },
        'response_de': response if language == 'de' else '''Vielen Dank für Ihre Nachricht!
Das sind wunderbare Neuigkeiten!
Mit herzlichen Grüßen
[Ihr Name]''',
        'response_uk': response if language == 'uk' else '''Дякую за ваше повідомлення!
Це чудові новини!
З найкращими побажаннями,
[Ваше ім'я]''',
        'tips': [
            '📌 Збережіть лист як пам\'ять',
            '🎉 Поділіться радістю з близькими',
            '👏 Заохочуйте дитину/рідних'
        ],
        'is_personal': True
    }


def analyze_official_letter(text: str, language: str = 'uk') -> Dict:
    """
    Аналіз офіційного листа (з законами).
    """
    # Отримуємо посилання на закон
    law_info = get_law_reference(text)
    
    # Генеруємо відповідь
    response_de, _ = generate_response_smart(text, 'de')
    response_uk, _ = generate_response_smart(text, 'uk')
    
    # Формуємо поради на основі ситуації
    tips = []
    situation = law_info.get('situation_key', '')
    
    if situation == 'einladung':
        tips = [
            '📅 Прийдіть на 10 хвилин раніше',
            '📄 Візьміть всі необхідні документи',
            '📝 Робіть нотатки під час зустрічі'
        ]
    elif situation == 'mahnung':
        tips = [
            '⏰ Не ігноруйте лист',
            '📞 Зв\'яжіться з кредитором',
            '💰 Домовтеся про розстрочку'
        ]
    elif situation == 'kündigung':
        tips = [
            '📋 Перевірте законність',
            '⏰ Строк на пошук нового житла',
            '⚖️ Зверніться до Mieterbund'
        ]
    elif situation == 'steuerbescheid':
        tips = [
            '📋 Перевірте всі суми',
            '⏰ Строк на оскарження 1 місяць',
            '💰 Зверніться до податкового консультанта'
        ]
    else:
        tips = [
            '📋 Збережіть копію листа',
            '📞 Перевірте контактні дані',
            '⏰ Дотримуйтесь строків'
        ]
    
    return {
        'law_info': law_info,
        'response_de': response_de,
        'response_uk': response_uk,
        'tips': tips,
        'paragraphs': law_info['paragraphs'],
        'consequences': law_info['consequences'],
        'is_personal': False
    }
