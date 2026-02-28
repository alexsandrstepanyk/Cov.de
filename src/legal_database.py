#!/usr/bin/env python3
"""
Legal Database Module - SQLite implementation
Локальна база даних німецьких законів для швидкого пошуку.
"""

import sqlite3
import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger(__name__)

# Шлях до бази даних
DB_PATH = Path(__file__).parent.parent / "data" / "legal_database.db"

# Початкові дані з legal_db.py
LEGAL_DATA = {
    'de': {
        'debt_collection': {
            'laws': [
                {'name': 'BGB § 241', 'description': 'Обов\'язки зі зобов\'язання: Кожна сторона зобов\'язана виконувати умови договору добросовісно.'},
                {'name': 'BGB § 286', 'description': 'Прострочення боржника: Боржник перебуває у простроченні після отримання письмового нагадування (Mahnung).'},
                {'name': 'BGB § 288', 'description': 'Проценти у простроченні: 5% річних для споживачів, 9% для бізнес-позик.'},
                {'name': 'BGB § 433', 'description': 'Купівля-продаж: Продавець зобов\'язаний передати товар, покупець — сплатити ціну.'},
                {'name': 'BGB § 488', 'description': 'Кредитний договір: Кредитор надає гроші, боржник повертає з процентами.'},
                {'name': 'BGB § 823', 'description': 'Відшкодування збитків: Хто заподіяв шкоду іншому, зобов\'язаний її відшкодувати.'}
            ],
            'consequences': '⚠️ При несплаті боргу:\n• Нараховується пеня 5% річних (§ 288 BGB)\n• Можливі судові витрати (Gerichtskosten)\n• Примусове стягнення через судового виконавця (Gerichtsvollzieher)\n• Заборона на виїзд з країни при боргу > €2000\n• Від\'ємна кредитна історія (Schufa)',
            'keywords': ['mahnung', 'zahlung', 'forderung', 'schuld', 'inkasso']
        },
        'tenancy': {
            'laws': [
                {'name': 'BGB § 535', 'description': 'Обов\'язки орендодавця: Утримувати житло в придатному для проживання стані.'},
                {'name': 'BGB § 536', 'description': 'Зниження оренди: При дефектах житла орендна плата може бути зменшена.'},
                {'name': 'BGB § 543', 'description': 'Позачергове розірвання: Можливе при серйозних порушеннях (наприклад, несплата 2+ місяці).'},
                {'name': 'BGB § 558', 'description': 'Підвищення оренди: Тільки до місцевого рівня, максимум 20% за 3 роки.'},
                {'name': 'BGB § 573', 'description': 'Розірвання орендодавцем: Тільки за обґрунтованих причин (власні потреби, порушення орендаря).'}
            ],
            'consequences': '⚠️ При порушенні умов оренди:\n• Можливе підвищення оренди до 20% за 3 роки (§ 558 BGB)\n• При несплаті 2+ місяців — виселення (§ 543 BGB)\n• Орендодавець може розірвати договір (§ 573 BGB)\n• При дефектах житла — зниження оренди (§ 536 BGB)',
            'keywords': ['miete', 'wohnung', 'nebenkosten', 'kaution', 'vermieter']
        },
        'employment': {
            'laws': [
                {'name': '§ 59 SGB II', 'description': 'Обов\'язок явки: Отримувачі допомоги зобов\'язані з\'являтися на всі запрошення Jobcenter.'},
                {'name': '§ 31 SGB II', 'description': 'Наслідки неявки: Зменшення виплат на 30% протягом 12 тижнів.'},
                {'name': '§ 32 SGB II', 'description': 'Повторне порушення: Повне припинення виплат при систематичних порушеннях.'},
                {'name': '§ 309 SGB III', 'description': 'Офіційні запрошення: Запрошення біржі праці є офіційними обов\'язковими документами.'},
                {'name': 'KSchG § 1', 'description': 'Захист від звільнення: Звільнення тільки за соціально обґрунтованих причин.'},
                {'name': 'BGB § 611', 'description': 'Трудовий договір: Роботодавець платить зарплату, працівник виконує роботу.'},
                {'name': 'BGB § 620', 'description': 'Припинення трудових відносин: Можливе за згодою сторін або з дотриманням строку попередження.'}
            ],
            'consequences': '⚠️ При неявці на Jobcenter без поважної причини:\n• Зменшення виплат на 30% на 12 тижнів (§ 31 SGB II)\n• Повне припинення виплат при повторному порушенні (§ 32 SGB II)\n• Хворобу потрібно підтвердити лікарською довідкою протягом 3 днів\n• Запрошення є офіційним обов\'язковим документом (§ 309 SGB III)',
            'keywords': ['jobcenter', 'einladung', 'termin', 'bewerbung', 'hartz']
        },
        'administrative': {
            'laws': [
                {'name': 'VwVfG § 35', 'description': 'Адміністративний акт: Повинен бути письмовим, обґрунтованим та містити правове підґрунтя.'},
                {'name': 'VwGO § 42', 'description': 'Право на оскарження: Кожен може оскаржити адміністративне рішення до адміністративного суду.'},
                {'name': 'VwVfG § 28', 'description': 'Право на вислуховування: Перед виданням акту сторона має право бути вислуханою.'},
                {'name': 'VwVfG § 29', 'description': 'Доступ до файлів: Сторони мають право на ознайомлення з документами.'}
            ],
            'consequences': '⚠️ Адміністративні наслідки:\n• Строк оскарження — 1 місяць з моменту отримання (§ 42 VwGO)\n• Після строку рішення стає остаточним (Bestandskraft)\n• Можливе примусове виконання (Vollstreckung)\n• Судові витрати при програші справи',
            'keywords': ['bescheid', 'antrag', 'behörde', 'frist', 'verwaltung']
        },
        'general': {
            'laws': [
                {'name': 'BGB § 241', 'description': 'Обов\'язки зі зобов\'язання: Кожна сторона зобов\'язана виконувати умови договору добросовісно.'},
                {'name': 'BGB § 242', 'description': 'Добросовісність: Виконання зобов\'язань має відбуватися з урахуванням звичаїв та добросовісності.'},
                {'name': 'BGB § 308', 'description': 'Неприпустимі умови договору: Загальні умови використання не можуть необґрунтовано обмежувати права.'}
            ],
            'consequences': '📋 Залежно від типу листа можливі різні наслідки.\nРекомендується звернутися до фахівця для детального розбору вашої ситуації.\n\n📞 Безкоштовна правова допомога:\n• Telefonseelsorge: 0800 111 0 111\n• Rechtsantragsstelle: безкоштовна консультація',
            'keywords': ['allgemein', 'general', 'sonstiges']
        }
    }
}

# Дані з smart_law_reference.py
ORGANIZATION_DATA = {
    'finanzamt': {
        'name_de': 'Finanzamt',
        'name_uk': 'Податкова',
        'situations': {
            'steuernachzahlung': {
                'paragraphs': ['AO § 150', 'AO § 172', 'EStG § 25'],
                'description_de': 'Steuerforderung',
                'description_uk': 'Податкова заборгованість',
                'consequences_de': 'Zahlung innerhalb von 1 Monat, sonst Säumniszuschlag 0.5% pro Monat',
                'consequences_uk': 'Сплата протягом 1 місяця, інакше пеня 0.5% за місяць',
                'keywords': ['steuernachzahlung', 'steuerbescheid', 'nachzahlung']
            },
            'prüfung': {
                'paragraphs': ['AO § 193', 'AO § 196', 'AO § 203'],
                'description_de': 'Steuerprüfung',
                'description_uk': 'Податкова перевірка',
                'consequences_de': 'Teilnahmepflicht, Dokumentenvorlage',
                'consequences_uk': 'Обов\'язкова участь, надання документів',
                'keywords': ['prüfung', 'betriebsprüfung', 'außenprüfung']
            },
            'fristverlängerung': {
                'paragraphs': ['AO § 108', 'AO § 109'],
                'description_de': 'Fristverlängerung',
                'description_uk': 'Продовження строку',
                'consequences_de': 'Antrag auf Fristverlängerung möglich',
                'consequences_uk': 'Можна подати заяву на продовження',
                'keywords': ['frist', 'verlängerung', 'aufschub']
            }
        }
    },
    'jobcenter': {
        'name_de': 'Jobcenter / Arbeitsagentur',
        'name_uk': 'Jobcenter / Біржа праці',
        'situations': {
            'einladung': {
                'paragraphs': ['§ 59 SGB II', '§ 309 SGB III'],
                'description_de': 'Einladung zum Gespräch',
                'description_uk': 'Запрошення на співбесіду',
                'consequences_de': 'Teilnahmepflicht, sonst Sanktion 30%',
                'consequences_uk': 'Обов\'язкова явка, інакше санкції 30%',
                'keywords': ['einladung', 'termin', 'gespräch', 'vorsprache']
            },
            'sanktion': {
                'paragraphs': ['§ 31 SGB II', '§ 32 SGB II'],
                'description_de': 'Sanktion bei Nichtteilnahme',
                'description_uk': 'Санкції за неявку',
                'consequences_de': 'Leistungskürzung um 30% für 12 Wochen',
                'consequences_uk': 'Зменшення виплат на 30% на 12 тижнів',
                'keywords': ['sanktion', 'kürzung', 'minderung', 'sperre']
            },
            'leistung': {
                'paragraphs': ['§ 19 SGB II', '§ 20 SGB II', '§ 22 SGB II'],
                'description_de': 'Leistungen und Hilfe',
                'description_uk': 'Виплати та допомога',
                'consequences_de': 'Anspruch auf Leistungen',
                'consequences_uk': 'Право на отримання допомоги',
                'keywords': ['leistung', 'geld', 'betrag', 'auszahlung']
            },
            'ablehnung': {
                'paragraphs': ['§ 33 SGB II', '§ 39 SGB X'],
                'description_de': 'Ablehnung von Leistungen',
                'description_uk': 'Відмова у виплатах',
                'consequences_de': 'Widerspruch innerhalb von 1 Monat möglich',
                'consequences_uk': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['ablehnung', 'abgelehnt', 'verweigert']
            }
        }
    },
    'vermieter': {
        'name_de': 'Vermieter',
        'name_uk': 'Орендодавець',
        'situations': {
            'mieterhöhung': {
                'paragraphs': ['BGB § 558', 'BGB § 559', 'BGB § 560'],
                'description_de': 'Erhöhung der Miete',
                'description_uk': 'Підвищення орендної плати',
                'consequences_de': 'Zustimmung erforderlich bei >20% in 3 Jahren',
                'consequences_uk': 'Згода потрібна, якщо підвищення > 20% за 3 роки',
                'keywords': ['mieterhöhung', 'erhöhung', 'neue miete']
            },
            'kündigung': {
                'paragraphs': ['BGB § 573', 'BGB § 573c', 'BGB § 543'],
                'description_de': 'Kündigung des Mietvertrags',
                'description_uk': 'Розірвання договору оренди',
                'consequences_de': 'Kündigungsfrist 3 Monate',
                'consequences_uk': 'Строк попередження 3 місяці',
                'keywords': ['kündigung', 'kündigen', 'frist']
            },
            'nebenkosten': {
                'paragraphs': ['BGB § 556', 'BGB § 556a'],
                'description_de': 'Nebenkosten',
                'description_uk': 'Додаткові витрати',
                'consequences_de': 'Detaillierte Aufstellung erforderlich',
                'consequences_uk': 'Потрібна детальна розбивка',
                'keywords': ['nebenkosten', 'abrechnung', 'heizkosten']
            },
            'mangel': {
                'paragraphs': ['BGB § 536', 'BGB § 536a', 'BGB § 543'],
                'description_de': 'Mängel der Wohnung',
                'description_uk': 'Дефекти житла',
                'consequences_de': 'Mietminderung möglich',
                'consequences_uk': 'Можна зменшити оренду (Mietminderung)',
                'keywords': ['mangel', 'defekt', 'schimmel', 'reparatur']
            }
        }
    },
    'inkasso': {
        'name_de': 'Inkasso',
        'name_uk': 'Колектори',
        'situations': {
            'mahnung': {
                'paragraphs': ['BGB § 286', 'BGB § 288'],
                'description_de': 'Mahnung zur Zahlung',
                'description_uk': 'Нагадування про сплату',
                'consequences_de': 'Säumniszuschlag 5% p.a. für Verbraucher',
                'consequences_uk': 'Пеня 5% річних для споживачів',
                'keywords': ['mahnung', 'mahnen', 'forderung']
            },
            'forderung': {
                'paragraphs': ['BGB § 194', 'BGB § 195', 'BGB § 199'],
                'description_de': 'Forderung zur Zahlung',
                'description_uk': 'Вимога сплати боргу',
                'consequences_de': 'Verjährungsfrist 3 Jahre',
                'consequences_uk': 'Строк позовної давності 3 роки',
                'keywords': ['forderung', 'schuld', 'betrag', 'rechnung']
            },
            'vollstreckung': {
                'paragraphs': ['BGB § 823', 'ZPO § 42', 'ZPO § 704'],
                'description_de': 'Zwangsvollstreckung',
                'description_uk': 'Примусове стягнення',
                'consequences_de': 'Möglich durch Gerichtsvollzieher',
                'consequences_uk': 'Можливе через Gerichtsvollzieher',
                'keywords': ['vollstreckung', 'gerichtsvollzieher', 'pfändung']
            },
            'betrug': {
                'paragraphs': ['StGB § 263', 'UWG § 4'],
                'description_de': 'Betrugsversuch',
                'description_uk': 'Шахрайство',
                'consequences_de': 'Strafrechtliche Verfolgung, nicht zahlen!',
                'consequences_uk': 'Кримінальна відповідальність, не платіть!',
                'keywords': ['western union', 'bitcoin', 'paysafecard', 'geschenkkarte']
            }
        }
    },
    'gericht': {
        'name_de': 'Gericht',
        'name_uk': 'Суд',
        'situations': {
            'beschluss': {
                'paragraphs': ['ZPO § 329', 'ZPO § 339'],
                'description_de': 'Gerichtliche Entscheidung',
                'description_uk': 'Судове рішення',
                'consequences_de': 'Widerspruch innerhalb von 1 Monat möglich',
                'consequences_uk': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['beschluss', 'urteil', 'entscheidung']
            },
            'ladung': {
                'paragraphs': ['ZPO § 217', 'ZPO § 220'],
                'description_de': 'Gerichtliche Vorladung',
                'description_uk': 'Судова повістка',
                'consequences_de': 'Teilnahmepflicht vor Gericht',
                'consequences_uk': 'Обов\'язкова явка в суд',
                'keywords': ['ladung', 'termin', 'verhandlung']
            },
            'mahnsache': {
                'paragraphs': ['ZPO § 688', 'ZPO § 699'],
                'description_de': 'Gerichtlicher Mahnbescheid',
                'description_uk': 'Судовий наказ про сплату',
                'consequences_de': 'Widerspruch innerhalb von 2 Wochen möglich',
                'consequences_uk': 'Можна подати Widerspruch протягом 2 тижнів',
                'keywords': ['mahnsache', 'mahnbescheid', 'vollstreckungsbescheid']
            }
        }
    },
    'krankenkasse': {
        'name_de': 'Krankenkasse',
        'name_uk': 'Лікарняна каса',
        'situations': {
            'beitrag': {
                'paragraphs': ['SGB V § 249', 'SGB V § 250'],
                'description_de': 'Krankenversicherungsbeitrag',
                'description_uk': 'Страхові внески',
                'consequences_de': 'Monatliche Zahlungspflicht',
                'consequences_uk': 'Обов\'язкова сплата щомісяця',
                'keywords': ['beitrag', 'zahlung', 'monatlich']
            },
            'leistung': {
                'paragraphs': ['SGB V § 27', 'SGB V § 28'],
                'description_de': 'Medizinische Leistungen',
                'description_uk': 'Медичні послуги',
                'consequences_de': 'Anspruch auf medizinische Versorgung',
                'consequences_uk': 'Право на медичне обслуговування',
                'keywords': ['leistung', 'behandlung', 'arzt', 'rezept']
            },
            'antrag': {
                'paragraphs': ['SGB V § 19', 'SGB X § 16'],
                'description_de': 'Antrag auf Leistungen',
                'description_uk': 'Заява на отримання послуг',
                'consequences_de': 'Bearbeitung innerhalb von 3 Monaten',
                'consequences_uk': 'Розгляд протягом 3 місяців',
                'keywords': ['antrag', 'beantragen', 'genehmigung']
            }
        }
    },
    'stadtwerk': {
        'name_de': 'Stadtwerk',
        'name_uk': 'Комунальні послуги',
        'situations': {
            'rechnung': {
                'paragraphs': ['BGB § 535', 'EnWG § 36'],
                'description_de': 'Rechnung für Versorgungsleistungen',
                'description_uk': 'Рахунок за послуги',
                'consequences_de': 'Zahlung innerhalb von 14 Tagen',
                'consequences_uk': 'Сплата протягом 14 днів',
                'keywords': ['rechnung', 'betrag', 'strom', 'gas', 'wasser']
            },
            'sperre': {
                'paragraphs': ['BGB § 314', 'EnWG § 41'],
                'description_de': 'Sperrung der Versorgung',
                'description_uk': 'Відключення послуг',
                'consequences_de': 'Möglich bei Schuld > 100€',
                'consequences_uk': 'Можливе при боргу > 100€',
                'keywords': ['sperre', 'abschaltung', 'unterbrechung']
            }
        }
    },
    'behörde': {
        'name_de': 'Behörde',
        'name_uk': 'Офіційна установа',
        'situations': {
            'bescheid': {
                'paragraphs': ['VwVfG § 35', 'VwVfG § 37'],
                'description_de': 'Verwaltungsakt',
                'description_uk': 'Адміністративний акт',
                'consequences_de': 'Widerspruch innerhalb von 1 Monat möglich',
                'consequences_uk': 'Можна подати Widerspruch протягом 1 місяця',
                'keywords': ['bescheid', 'verwaltungsakt', 'entscheidung']
            },
            'widerspruch': {
                'paragraphs': ['VwGO § 68', 'VwGO § 70'],
                'description_de': 'Widerspruch gegen Entscheidung',
                'description_uk': 'Оскарження рішення',
                'consequences_de': 'Einspruchsfrist 1 Monat',
                'consequences_uk': 'Строк подання 1 місяць',
                'keywords': ['widerspruch', 'einspruch', 'klage']
            },
            'frist': {
                'paragraphs': ['VwVfG § 31', 'VwVfG § 32'],
                'description_de': 'Fristen zur Erfüllung',
                'description_uk': 'Строки виконання',
                'consequences_de': 'Antrag auf Fristverlängerung möglich',
                'consequences_uk': 'Можна подати на Fristverlängerung',
                'keywords': ['frist', 'fristsetzung', 'deadline']
            }
        }
    }
}


def init_db():
    """
    Ініціалізація бази даних та заповнення початковими даними.
    """
    # Створюємо директорію data якщо не існує
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблиця законів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS laws (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT NOT NULL,
            category TEXT NOT NULL,
            law_name TEXT NOT NULL,
            description TEXT,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця організацій
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_key TEXT UNIQUE NOT NULL,
            name_de TEXT NOT NULL,
            name_uk TEXT NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця ситуацій
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS situations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            org_id INTEGER NOT NULL,
            situation_key TEXT NOT NULL,
            paragraphs TEXT,
            description_de TEXT,
            description_uk TEXT,
            consequences_de TEXT,
            consequences_uk TEXT,
            keywords TEXT,
            FOREIGN KEY (org_id) REFERENCES organizations(id),
            UNIQUE(org_id, situation_key)
        )
    ''')
    
    # Таблиця наслідків для категорій
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS consequences (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            country_code TEXT NOT NULL,
            category TEXT NOT NULL,
            consequences_de TEXT,
            consequences_uk TEXT,
            FOREIGN KEY (country_code, category) REFERENCES laws(country_code, category)
        )
    ''')
    
    # Індекс для швидкого пошуку
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_laws_search ON laws(law_name, description)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_situations_keywords ON situations(keywords)')
    
    conn.commit()
    
    # Перевіряємо чи база вже заповнена
    cursor.execute('SELECT COUNT(*) FROM laws')
    if cursor.fetchone()[0] == 0:
        logger.info("Заповнення бази даних початковими даними...")
        populate_db(cursor)
        conn.commit()
        logger.info(f"База даних створена: {DB_PATH}")
    else:
        logger.info(f"База даних вже існує: {DB_PATH}")
    
    conn.close()


def populate_db(cursor):
    """
    Заповнення бази даних початковими даними.
    """
    # Додаємо закони з LEGAL_DATA
    for country_code, categories in LEGAL_DATA.items():
        for category, data in categories.items():
            keywords_json = json.dumps(data.get('keywords', []))
            
            for law in data.get('laws', []):
                cursor.execute('''
                    INSERT INTO laws (country_code, category, law_name, description, keywords)
                    VALUES (?, ?, ?, ?, ?)
                ''', (country_code, category, law['name'], law['description'], keywords_json))
            
            # Додаємо наслідки
            if 'consequences' in data:
                cursor.execute('''
                    INSERT INTO consequences (country_code, category, consequences_de, consequences_uk)
                    VALUES (?, ?, ?, ?)
                ''', (country_code, category, data['consequences'], data['consequences']))
    
    # Додаємо організації з ORGANIZATION_DATA
    for org_key, org_data in ORGANIZATION_DATA.items():
        cursor.execute('''
            INSERT INTO organizations (org_key, name_de, name_uk)
            VALUES (?, ?, ?)
        ''', (org_key, org_data['name_de'], org_data['name_uk']))
        
        org_id = cursor.lastrowid
        
        # Додаємо ситуації
        for situation_key, situation_data in org_data['situations'].items():
            paragraphs_json = json.dumps(situation_data.get('paragraphs', []))
            keywords_json = json.dumps(situation_data.get('keywords', []))
            
            cursor.execute('''
                INSERT INTO situations (org_id, situation_key, paragraphs, description_de, 
                                       description_uk, consequences_de, consequences_uk, keywords)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (org_id, situation_key, paragraphs_json, 
                  situation_data.get('description_de', ''),
                  situation_data.get('description_uk', ''),
                  situation_data.get('consequences_de', ''),
                  situation_data.get('consequences_uk', ''),
                  keywords_json))


def search_laws(query: str, country: str = 'de') -> List[Dict]:
    """
    Пошук законів за текстовим запитом.
    
    Args:
        query: Текст запиту
        country: Код країни
        
    Returns:
        Список знайдених законів
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Пошук по назві та опису
    search_query = f"%{query.lower()}%"
    cursor.execute('''
        SELECT law_name, description, category, keywords
        FROM laws
        WHERE country_code = ?
        AND (LOWER(law_name) LIKE ? OR LOWER(description) LIKE ?)
        ORDER BY law_name
    ''', (country, search_query, search_query))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'law_name': row['law_name'],
            'description': row['description'],
            'category': row['category'],
            'keywords': json.loads(row['keywords']) if row['keywords'] else []
        })
    
    conn.close()
    return results


def search_by_keywords(keywords: List[str], country: str = 'de') -> List[Dict]:
    """
    Пошук законів за списком ключових слів.
    
    Args:
        keywords: Список ключових слів
        country: Код країни
        
    Returns:
        Список знайдених законів
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    results = []
    for keyword in keywords:
        search_query = f"%{keyword.lower()}%"
        cursor.execute('''
            SELECT DISTINCT law_name, description, category, keywords
            FROM laws
            WHERE country_code = ?
            AND (LOWER(law_name) LIKE ? OR LOWER(description) LIKE ? OR keywords LIKE ?)
        ''', (country, search_query, search_query, search_query))
        
        for row in cursor.fetchall():
            law_dict = {
                'law_name': row['law_name'],
                'description': row['description'],
                'category': row['category'],
                'keywords': json.loads(row['keywords']) if row['keywords'] else []
            }
            if law_dict not in results:
                results.append(law_dict)
    
    conn.close()
    return results


def get_laws_by_category(category: str, country: str = 'de') -> List[Dict]:
    """
    Отримати всі закони для категорії.
    
    Args:
        category: Категорія (debt_collection, tenancy тощо)
        country: Код країни
        
    Returns:
        Список законів
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT law_name, description, keywords
        FROM laws
        WHERE country_code = ? AND category = ?
        ORDER BY law_name
    ''', (country, category))
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'law_name': row['law_name'],
            'description': row['description'],
            'keywords': json.loads(row['keywords']) if row['keywords'] else []
        })
    
    conn.close()
    return results


def get_consequences(category: str, country: str = 'de') -> Optional[str]:
    """
    Отримати наслідки для категорії.
    
    Args:
        category: Категорія
        country: Код країни
        
    Returns:
        Текст з наслідками або None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT consequences_uk
        FROM consequences
        WHERE country_code = ? AND category = ?
    ''', (country, category))
    
    row = cursor.fetchone()
    conn.close()
    
    return row['consequences_uk'] if row else None


def detect_organization(text: str) -> Optional[Dict]:
    """
    Визначити організацію за текстом листа.
    
    Args:
        text: Текст листа
        
    Returns:
        Інформація про організацію або None
    """
    text_lower = text.lower()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Рахуємо бали для кожної організації
    cursor.execute('SELECT id, org_key, name_de, name_uk FROM organizations')
    orgs = cursor.fetchall()
    
    scores = {}
    for org in orgs:
        org_id = org['id']
        
        # Отримуємо всі ключові слова для цієї організації
        cursor.execute('SELECT keywords FROM situations WHERE org_id = ?', (org_id,))
        situation_keywords = []
        for row in cursor.fetchall():
            if row['keywords']:
                situation_keywords.extend(json.loads(row['keywords']))
        
        # Рахуємо співпадіння
        score = sum(1 for kw in situation_keywords if kw in text_lower)
        scores[org['org_key']] = {
            'score': score,
            'name_de': org['name_de'],
            'name_uk': org['name_uk']
        }
    
    conn.close()
    
    # Знаходимо переможця
    if not scores:
        return None
    
    max_score = max(s['score'] for s in scores.values())
    if max_score == 0:
        return None
    
    winners = [k for k, v in scores.items() if v['score'] == max_score]
    winner_key = winners[0]
    winner_data = scores[winner_key]
    
    return {
        'org_key': winner_key,
        'name_de': winner_data['name_de'],
        'name_uk': winner_data['name_uk'],
        'score': winner_data['score']
    }


def detect_situation(org_key: str, text: str) -> Optional[Dict]:
    """
    Визначити ситуацію за текстом листа для організації.
    
    Args:
        org_key: Ключ організації
        text: Текст листа
        
    Returns:
        Інформація про ситуацію або None
    """
    text_lower = text.lower()
    
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    # Отримуємо org_id
    cursor.execute('SELECT id FROM organizations WHERE org_key = ?', (org_key,))
    org_row = cursor.fetchone()
    
    if not org_row:
        conn.close()
        return None
    
    org_id = org_row['id']
    
    # Рахуємо бали для кожної ситуації
    cursor.execute('''
        SELECT situation_key, paragraphs, description_de, description_uk,
               consequences_de, consequences_uk, keywords
        FROM situations
        WHERE org_id = ?
    ''', (org_id,))
    
    scores = {}
    situation_data = {}
    
    for row in cursor.fetchall():
        situation_key = row['situation_key']
        keywords = json.loads(row['keywords']) if row['keywords'] else []
        
        score = sum(1 for kw in keywords if kw in text_lower)
        scores[situation_key] = score
        situation_data[situation_key] = {
            'paragraphs': json.loads(row['paragraphs']) if row['paragraphs'] else [],
            'description_de': row['description_de'],
            'description_uk': row['description_uk'],
            'consequences_de': row['consequences_de'],
            'consequences_uk': row['consequences_uk']
        }
    
    conn.close()

    if not scores:
        return None

    max_score = max(scores.values())
    if max_score == 0:
        return None

    winners = [k for k, v in scores.items() if v == max_score]
    winner_key = winners[0]

    return {
        'situation_key': winner_key,
        'score': scores[winner_key],
        **situation_data[winner_key]
    }


def analyze_letter(text: str) -> Dict:
    """
    Повний аналіз листа з використанням бази даних.
    
    Args:
        text: Текст листа
        
    Returns:
        Dict з результатами аналізу
    """
    # Визначаємо організацію
    org_info = detect_organization(text)
    
    if not org_info:
        return {
            'organization': 'Загальний лист',
            'organization_key': 'general',
            'situation': 'Не визначено',
            'paragraphs': [],
            'consequences': 'Залежить від контексту листа'
        }
    
    # Визначаємо ситуацію
    situation_info = detect_situation(org_info['org_key'], text)
    
    if not situation_info:
        return {
            'organization': org_info['name_uk'],
            'organization_key': org_info['org_key'],
            'situation': 'Не визначено',
            'paragraphs': [],
            'consequences': 'Залежить від контексту листа'
        }
    
    return {
        'organization': org_info['name_uk'],
        'organization_key': org_info['org_key'],
        'situation': situation_info['description_uk'],
        'situation_key': situation_info['situation_key'],
        'paragraphs': situation_info['paragraphs'],
        'consequences': situation_info['consequences_uk']
    }


def get_all_organizations() -> List[Dict]:
    """
    Отримати список всіх організацій.
    
    Returns:
        Список організацій
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT org_key, name_de, name_uk FROM organizations')
    
    results = []
    for row in cursor.fetchall():
        results.append({
            'org_key': row['org_key'],
            'name_de': row['name_de'],
            'name_uk': row['name_uk']
        })
    
    conn.close()
    return results


def get_all_categories(country: str = 'de') -> List[str]:
    """
    Отримати список всіх категорій.
    
    Returns:
        Список категорій
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT DISTINCT category
        FROM laws
        WHERE country_code = ?
    ''', (country,))
    
    results = [row[0] for row in cursor.fetchall()]
    conn.close()
    
    return results


# Ініціалізація при імпорті
init_db()


if __name__ == '__main__':
    # Тестування
    print("Тестування бази даних законів...\n")
    
    # Пошук законів
    print("🔍 Пошук законів за запитом 'mahnung':")
    results = search_laws('mahnung')
    for law in results:
        print(f"  • {law['law_name']}: {law['description']}")
    
    print("\n🔍 Пошук за ключовими словами ['mahnung', 'zahlung']:")
    results = search_by_keywords(['mahnung', 'zahlung'])
    for law in results:
        print(f"  • {law['law_name']}: {law['description']}")
    
    print("\n📋 Закони категорії 'debt_collection':")
    results = get_laws_by_category('debt_collection')
    for law in results:
        print(f"  • {law['law_name']}: {law['description']}")
    
    print("\n⚠️ Наслідки для 'debt_collection':")
    consequences = get_consequences('debt_collection')
    print(f"  {consequences}")
    
    print("\n🏢 Визначення організації:")
    test_text = "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung der offenen Forderung..."
    org = detect_organization(test_text)
    print(f"  Текст: {test_text[:50]}...")
    print(f"  Організація: {org}")
    
    print("\n📊 Аналіз листа:")
    analysis = analyze_letter(test_text)
    print(f"  Організація: {analysis['organization']}")
    print(f"  Ситуація: {analysis['situation']}")
    print(f"  Параграфи: {analysis['paragraphs']}")
    
    print("\n✅ База даних працює коректно!")
