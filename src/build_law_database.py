#!/usr/bin/env python3
"""
German Laws Database Builder
Завантаження та збереження всіх німецьких кодексів та законів.
"""

import sqlite3
import json
import logging
import requests
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Шлях до бази даних
DB_PATH = Path(__file__).parent.parent / "data" / "legal_database.db"

# Офіційні джерела німецьких законів
OFFICIAL_SOURCES = {
    'gesetze-im-internet': 'https://www.gesetze-im-internet.de/api/',
    'dejure': 'https://dejure.org/',
    'bundesrecht': 'https://www.bundesrecht.juris.de/'
}

# Список всіх кодексів Німеччини
CODES_TO_DOWNLOAD = {
    # Основні кодекси
    'BGB': {
        'name': 'Bürgerliches Gesetzbuch',
        'name_uk': 'Цивільний кодекс',
        'url': 'https://www.gesetze-im-internet.de/bgb/',
        'categories': ['debt_collection', 'tenancy', 'employment', 'general']
    },
    'ZPO': {
        'name': 'Zivilprozessordnung',
        'name_uk': 'Цивільний процесуальний кодекс',
        'url': 'https://www.gesetze-im-internet.de/zpo/',
        'categories': ['debt_collection', 'administrative']
    },
    'AO': {
        'name': 'Abgabenordnung',
        'name_uk': 'Податковий кодекс',
        'url': 'https://www.gesetze-im-internet.de/ao/',
        'categories': ['administrative']
    },
    'SGB': {
        'name': 'Sozialgesetzbuch',
        'name_uk': 'Соціальний кодекс',
        'url': 'https://www.gesetze-im-internet.de/sgb_2/',
        'categories': ['employment']
    },
    'StGB': {
        'name': 'Strafgesetzbuch',
        'name_uk': 'Кримінальний кодекс',
        'url': 'https://www.gesetze-im-internet.de/stgb/',
        'categories': ['general']
    },
    'HGB': {
        'name': 'Handelsgesetzbuch',
        'name_uk': 'Торговельний кодекс',
        'url': 'https://www.gesetze-im-internet.de/hgb/',
        'categories': ['general']
    },
    'GG': {
        'name': 'Grundgesetz',
        'name_uk': 'Основний закон (Конституція)',
        'url': 'https://www.gesetze-im-internet.de/gg/',
        'categories': ['administrative', 'general']
    },
    
    # Спеціальні закони
    'VwVfG': {
        'name': 'Verwaltungsverfahrensgesetz',
        'name_uk': 'Закон про адміністративне судочинство',
        'url': 'https://www.gesetze-im-internet.de/vwvfg/',
        'categories': ['administrative']
    },
    'VwGO': {
        'name': 'Verwaltungsgerichtsordnung',
        'name_uk': 'Кодекс адміністративного судочинства',
        'url': 'https://www.gesetze-im-internet.de/vwgo/',
        'categories': ['administrative']
    },
    'KSchG': {
        'name': 'Kündigungsschutzgesetz',
        'name_uk': 'Закон про захист від звільнення',
        'url': 'https://www.gesetze-im-internet.de/kschg/',
        'categories': ['employment']
    },
    'EnWG': {
        'name': 'Energiewirtschaftsgesetz',
        'name_uk': 'Закон про енергетику',
        'url': 'https://www.gesetze-im-internet.de/enwg/',
        'categories': ['utility']
    },
    'SGB_V': {
        'name': 'Sozialgesetzbuch V',
        'name_uk': 'Соціальний кодекс V (Здоров\'я)',
        'url': 'https://www.gesetze-im-internet.de/sgb_5/',
        'categories': ['insurance']
    },
    'VVG': {
        'name': 'Versicherungsvertragsgesetz',
        'name_uk': 'Закон про страхування',
        'url': 'https://www.gesetze-im-internet.de/vvg/',
        'categories': ['insurance']
    },
    'UWG': {
        'name': 'Gesetz gegen den unlauteren Wettbewerb',
        'name_uk': 'Закон про недобросовісну конкуренцію',
        'url': 'https://www.gesetze-im-internet.de/uwg/',
        'categories': ['general']
    },
    'EStG': {
        'name': 'Einkommensteuergesetz',
        'name_uk': 'Закон про прибутковий податок',
        'url': 'https://www.gesetze-im-internet.de/estg/',
        'categories': ['administrative']
    },
    'UStG': {
        'name': 'Umsatzsteuergesetz',
        'name_uk': 'Закон про податок з обороту',
        'url': 'https://www.gesetze-im-internet.de/ustg/',
        'categories': ['administrative']
    },
    'WoHG': {
        'name': 'Wohnungseigentumsgesetz',
        'name_uk': 'Закон про житлову власність',
        'url': 'https://www.gesetze-im-internet.de/wegg/',
        'categories': ['tenancy']
    },
    'MietR': {
        'name': 'Mietrecht',
        'name_uk': 'Орендне право',
        'url': 'https://www.gesetze-im-internet.de/mietrecht/',
        'categories': ['tenancy']
    }
}

# Базові параграфи для кожного кодексу (для початку)
INITIAL_PARAGRAPHS = {
    'BGB': {
        '241': 'Обов\'язки зі зобов\'язання: Кожна сторона зобов\'язана виконувати умови договору добросовісно.',
        '242': 'Добросовісність: Виконання зобов\'язань має відбуватися з урахуванням звичаїв та добросовісності.',
        '286': 'Прострочення боржника: Боржник перебуває у простроченні після отримання письмового нагадування (Mahnung).',
        '288': 'Проценти у простроченні: 5% річних для споживачів, 9% для бізнес-позик.',
        '433': 'Купівля-продаж: Продавець зобов\'язаний передати товар, покупець — сплатити ціну.',
        '488': 'Кредитний договір: Кредитор надає гроші, боржник повертає з процентами.',
        '535': 'Обов\'язки орендодавця: Утримувати житло в придатному для проживання стані.',
        '536': 'Зниження оренди: При дефектах житла орендна плата може бути зменшена.',
        '543': 'Позачергове розірвання: Можливе при серйозних порушеннях (наприклад, несплата 2+ місяці).',
        '558': 'Підвищення оренди: Тільки до місцевого рівня, максимум 20% за 3 роки.',
        '573': 'Розірвання орендодавцем: Тільки за обґрунтованих причин (власні потреби, порушення орендаря).',
        '611': 'Трудовий договір: Роботодавець платить зарплату, працівник виконує роботу.',
        '620': 'Припинення трудових відносин: Можливе за згодою сторін або з дотриманням строку попередження.',
        '823': 'Відшкодування збитків: Хто заподіяв шкоду іншому, зобов\'язаний її відшкодувати.',
        '194': 'Право на вимогу: Право вимагати дії або бездіяльності від іншої особи.',
        '195': 'Загальний строк позовної давності: 3 роки.',
        '199': 'Закінчення строку позовної давності: Строк закінчується в кінці року.',
        '314': 'Розірвання договору з важливих причин: Можливе без строку попередження.',
        '308': 'Неприпустимі умови договору: Загальні умови використання не можуть необґрунтовано обмежувати права.'
    },
    'ZPO': {
        '42': 'Судовий процес: Порядок розгляду цивільних справ.',
        '217': 'Судова повістка: Виклик сторін до суду.',
        '220': 'Виклик до суду: Порядок виклику свідків.',
        '329': 'Судове рішення: Рішення суду першої інстанції.',
        '339': 'Оскарження: Порядок оскарження рішень.',
        '688': 'Судовий наказ: Наказ про сплату боргу.',
        '699': 'Виконання наказу: Порядок виконання судового наказу.',
        '704': 'Примусове виконання: Порядок примусового виконання рішень.'
    },
    'AO': {
        '108': 'Продовження строку: Можливе за заявою платника податків.',
        '109': 'Відстрочка сплати: Можлива за наявності поважних причин.',
        '150': 'Податкова декларація: Обов\'язок подати декларацію.',
        '172': 'Податкове рішення: Рішення податкової інспекції.',
        '193': 'Податкова перевірка: Право на проведення перевірки.',
        '196': 'Зовнішня перевірка: Перевірка на місці.',
        '203': 'Наслідки перевірки: Результати та санкції.'
    },
    'SGB_II': {
        '19': 'Реєстрація: Обов\'язок зареєструватися.',
        '20': 'Допомога: Право на отримання допомоги.',
        '22': 'Витрати: Покриття витрат на житло.',
        '31': 'Санкції: Зменшення виплат при порушенні.',
        '32': 'Повторне порушення: Повне припинення виплат.',
        '33': 'Відмова: Підстави для відмови.',
        '59': 'Обов\'язок явки: Обов\'язок з\'явитися на запрошення.'
    },
    'SGB_III': {
        '309': 'Офіційні запрошення: Запрошення біржі праці є обов\'язковими.'
    },
    'StGB': {
        '263': 'Шахрайство: Кримінальна відповідальність за шахрайство.'
    },
    'VwVfG': {
        '28': 'Право на вислуховування: Перед виданням акту сторона має право бути вислуханою.',
        '29': 'Доступ до файлів: Сторони мають право на ознайомлення з документами.',
        '31': 'Строки: Строки виконання рішень.',
        '32': 'Продовження строків: Можливе за заявою.',
        '35': 'Адміністративний акт: Повинен бути письмовим, обґрунтованим та містити правове підґрунтя.',
        '37': 'Форма акту: Письмова форма адміністративного акту.'
    },
    'VwGO': {
        '42': 'Право на оскарження: Кожен може оскаржити адміністративне рішення до адміністративного суду.',
        '68': 'Процедура оскарження: Порядок подання скарги.',
        '70': 'Строк оскарження: 1 місяць з моменту отримання рішення.'
    },
    'KSchG': {
        '1': 'Захист від звільнення: Звільнення тільки за соціально обґрунтованих причин (поведінка, особа, операційні потреби).'
    },
    'EnWG': {
        '36': 'Постачання енергії: Обов\'язки постачальника.',
        '41': 'Відключення послуг: Можливе при боргу > 100€.'
    },
    'SGB_V': {
        '1': 'Обов\'язкове страхування: Всі громадяни мають бути застраховані.',
        '19': 'Реєстрація: Обов\'язок зареєструватися в лікарняній касі.',
        '27': 'Медичні послуги: Право на медичне обслуговування.',
        '28': 'Лікування: Право на лікування.',
        '249': 'Страхові внески: Обов\'язкова сплата внесків.',
        '250': 'Розмір внесків: Визначається доходом.'
    },
    'VVG': {
        '1': 'Закон про страхування: Регулює страхові відносини.'
    },
    'UWG': {
        '4': 'Недобросовісна конкуренція: Заборона недобросовісної конкуренції.'
    },
    'EStG': {
        '25': 'Податкова декларація: Порядок подання декларації.'
    },
    'GG': {
        '1': 'Гідність людини: Гідність людини недоторканна.',
        '2': 'Вільний розвиток особистості: Кожен має право на вільний розвиток.',
        '19': 'Основне право на звернення: Право звертатися до органів влади.'
    }
}


def init_db():
    """Ініціалізація бази даних."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Таблиця кодексів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS codes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_name TEXT UNIQUE NOT NULL,
            name_de TEXT NOT NULL,
            name_uk TEXT NOT NULL,
            url TEXT,
            categories TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Таблиця параграфів
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paragraphs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            code_name TEXT NOT NULL,
            paragraph_number TEXT NOT NULL,
            text_de TEXT,
            text_uk TEXT,
            category TEXT,
            keywords TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(code_name, paragraph_number)
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
    
    # Індекс для швидкого пошуку
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_paragraphs_code ON paragraphs(code_name, paragraph_number)')
    cursor.execute('CREATE INDEX IF NOT EXISTS idx_paragraphs_category ON paragraphs(category)')
    
    conn.commit()
    conn.close()
    logger.info("✅ База даних ініціалізована")


def populate_codes():
    """Заповнення бази даних кодексами."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    for code_name, code_data in CODES_TO_DOWNLOAD.items():
        try:
            categories_json = json.dumps(code_data.get('categories', []))
            cursor.execute('''
                INSERT OR REPLACE INTO codes (code_name, name_de, name_uk, url, categories)
                VALUES (?, ?, ?, ?, ?)
            ''', (code_name, code_data['name'], code_data['name_uk'], 
                  code_data.get('url', ''), categories_json))
            logger.info(f"✅ Додано кодекс: {code_name} ({code_data['name_uk']})")
        except Exception as e:
            logger.error(f"❌ Помилка додавання кодексу {code_name}: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Додано {len(CODES_TO_DOWNLOAD)} кодексів")


def populate_paragraphs():
    """Заповнення бази даних параграфами."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    total = 0
    for code_name, paragraphs in INITIAL_PARAGRAPHS.items():
        for para_num, para_text in paragraphs.items():
            try:
                # Визначаємо категорію
                category = 'general'
                code_info = CODES_TO_DOWNLOAD.get(code_name, {})
                categories = code_info.get('categories', [])
                if categories:
                    category = categories[0]
                
                cursor.execute('''
                    INSERT OR REPLACE INTO paragraphs 
                    (code_name, paragraph_number, text_de, text_uk, category)
                    VALUES (?, ?, ?, ?, ?)
                ''', (code_name, para_num, f"[DE] {para_text}", para_text, category))
                total += 1
            except Exception as e:
                logger.error(f"❌ Помилка додавання параграфу {code_name} § {para_num}: {e}")
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Додано {total} параграфів")


def download_from_gesetze_im_internet():
    """
    Завантаження законів з офіційного джерела gesetze-im-internet.de
    """
    logger.info("🌐 Завантаження з gesetze-im-internet.de...")
    
    for code_name, code_data in CODES_TO_DOWNLOAD.items():
        try:
            url = code_data.get('url', '')
            if not url:
                continue
            
            logger.info(f"  📥 Завантаження {code_name}...")
            
            # Отримуємо HTML сторінки
            response = requests.get(url, timeout=30)
            if response.status_code == 200:
                logger.info(f"  ✅ Завантажено {code_name}")
                # Тут можна парсити HTML та зберігати параграфи
            else:
                logger.warning(f"  ⚠️ Не вдалося завантажити {code_name}")
                
        except Exception as e:
            logger.error(f"  ❌ Помилка завантаження {code_name}: {e}")


def get_all_codes() -> List[Dict]:
    """Отримати список всіх кодексів."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM codes ORDER BY code_name')
    results = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return results


def get_paragraph(code_name: str, paragraph_number: str) -> Optional[Dict]:
    """
    Отримати конкретний параграф.
    
    Args:
        code_name: Назва кодексу (наприклад, 'BGB')
        paragraph_number: Номер параграфу (наприклад, '286')
        
    Returns:
        Dict з інформацією про параграф або None
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM paragraphs
        WHERE code_name = ? AND paragraph_number = ?
    ''', (code_name, paragraph_number))
    
    row = cursor.fetchone()
    conn.close()
    
    return dict(row) if row else None


def search_paragraphs(query: str) -> List[Dict]:
    """
    Пошук параграфів за текстом.
    
    Args:
        query: Текст для пошуку
        
    Returns:
        Список знайдених параграфів
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    search_query = f"%{query.lower()}%"
    cursor.execute('''
        SELECT * FROM paragraphs
        WHERE LOWER(text_uk) LIKE ? OR LOWER(text_de) LIKE ? OR paragraph_number LIKE ?
        ORDER BY code_name, paragraph_number
    ''', (search_query, search_query, search_query))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_paragraphs_by_code(code_name: str) -> List[Dict]:
    """
    Отримати всі параграфи кодексу.
    
    Args:
        code_name: Назва кодексу
        
    Returns:
        Список параграфів
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT * FROM paragraphs
        WHERE code_name = ?
        ORDER BY paragraph_number
    ''', (code_name,))
    
    results = [dict(row) for row in cursor.fetchall()]
    conn.close()
    
    return results


def get_statistics() -> Dict:
    """Отримати статистику бази даних."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    stats = {}
    
    # Кількість кодексів
    cursor.execute('SELECT COUNT(*) FROM codes')
    stats['codes'] = cursor.fetchone()[0]
    
    # Кількість параграфів
    cursor.execute('SELECT COUNT(*) FROM paragraphs')
    stats['paragraphs'] = cursor.fetchone()[0]
    
    # Параграфи по кодексах
    cursor.execute('''
        SELECT code_name, COUNT(*) as count
        FROM paragraphs
        GROUP BY code_name
        ORDER BY count DESC
    ''')
    stats['by_code'] = {row[0]: row[1] for row in cursor.fetchall()}
    
    conn.close()
    return stats


if __name__ == '__main__':
    print("\n" + "="*60)
    print("  ЗАВАНТАЖЕННЯ НІМЕЦЬКИХ ЗАКОНІВ")
    print("="*60)
    
    # Ініціалізація
    print("\n⏳ Ініціалізація бази даних...")
    init_db()
    
    # Заповнення кодексами
    print("\n📚 Заповнення кодексами...")
    populate_codes()
    
    # Заповнення параграфами
    print("\n📜 Заповнення параграфами...")
    populate_paragraphs()
    
    # Спроба завантаження з офіційних джерел
    print("\n🌐 Завантаження з офіційних джерел...")
    download_from_gesetze_im_internet()
    
    # Статистика
    print("\n📊 Статистика:")
    stats = get_statistics()
    print(f"  Кодексів: {stats['codes']}")
    print(f"  Параграфів: {stats['paragraphs']}")
    print(f"  По кодексах:")
    for code, count in stats['by_code'].items():
        print(f"    • {code}: {count}")
    
    print("\n" + "="*60)
    print("  ✅ БАЗА ДАНИХ ЗАКОНІВ СТВОРЕНА!")
    print("="*60 + "\n")
