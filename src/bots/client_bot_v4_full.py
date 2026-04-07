#!/usr/bin/env python3
"""
Client Bot v4.0 for Gov.de - Повна Інтеграція
Реєстрація користувачів, завантаження листів, меню з підтримкою багатосторінкових документів.
Інтегровано: Advanced OCR, Advanced Translator, Legal Database, Multi-page Handler, Fraud Detection
"""

import os
import logging
import sqlite3
import asyncio
from pathlib import Path
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
import pytesseract
from PIL import Image
from telegram import Update, ReplyKeyboardMarkup, InlineKeyboardMarkup, InlineKeyboardButton
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ContextTypes,
    ConversationHandler,
    CallbackQueryHandler
)

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger('client_bot')

# Імпорт всіх модулів
ADVANCED_TRANSLATOR = False
ADVANCED_OCR = False
LEGAL_DATABASE = False
MULTI_PAGE_HANDLER = False
FRAUD_DETECTION = False
SMART_LAW_REFERENCE = False
IMPROVED_RESPONSES = False
LETTER_GENERATOR = False
ADVANCED_CLASSIFICATION = False
LLM_ORCHESTRATOR = False
PDF_GENERATOR = False
STATS_AVAILABLE = False

# Імпортуємо модулі по черзі з обробкою помилок
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from advanced_translator import translate_text_async
    ADVANCED_TRANSLATOR = True
    logger.info("✅ Advanced Translator підключено")
except Exception as e:
    logger.warning(f"⚠️ Advanced Translator недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from advanced_ocr import recognize_image
    ADVANCED_OCR = True
    logger.info("✅ Advanced OCR підключено")
except Exception as e:
    logger.warning(f"⚠️ Advanced OCR недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from legal_database import analyze_letter
    LEGAL_DATABASE = True
    logger.info("✅ Legal Database підключено")
except Exception as e:
    logger.warning(f"⚠️ Legal Database недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from multi_page_handler import handle_multi_page_photo, get_multi_page_keyboard, ask_for_more_pages, finalize_multi_page
    MULTI_PAGE_HANDLER = True
    logger.info("✅ Multi-page Handler підключено")
except Exception as e:
    logger.warning(f"⚠️ Multi-page Handler недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from fraud_detection import analyze_letter_for_fraud, generate_fraud_warning, extract_phone_numbers, extract_emails, extract_websites
    FRAUD_DETECTION = True
    logger.info("✅ Fraud Detection підключено")
except Exception as e:
    logger.warning(f"⚠️ Fraud Detection недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from smart_law_reference import analyze_letter_smart, get_law_reference
    SMART_LAW_REFERENCE = True
    logger.info("✅ Smart Law Reference підключено")
except Exception as e:
    logger.warning(f"⚠️ Smart Law Reference недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from improved_response_generator import generate_response_smart_improved
    IMPROVED_RESPONSES = True
    logger.info("✅ Improved Response Generator підключено (v4.5)")
except Exception as e:
    logger.warning(f"⚠️ Improved Response Generator недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from letter_generator import generate_german_letter_with_fallback
    LETTER_GENERATOR = True
    logger.info("✅ Letter Generator підключено (DIN 5008 + Fallback)")
except Exception as e:
    logger.warning(f"⚠️ Letter Generator недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from advanced_classification import classify_letter_combined, get_classification_description
    ADVANCED_CLASSIFICATION = True
    logger.info("✅ Advanced Classification підключено")
except Exception as e:
    logger.warning(f"⚠️ Advanced Classification недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from llm_orchestrator import process_letter_with_llm
    LLM_ORCHESTRATOR = True
    logger.info("✅ LLM Orchestrator підключено (v5.0 - мозок бота)")
except Exception as e:
    logger.warning(f"⚠️ LLM Orchestrator недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from pdf_generator import generate_letter_pdf
    PDF_GENERATOR = True
    logger.info("✅ PDF Generator підключено (v8.4)")
except Exception as e:
    logger.warning(f"⚠️ PDF Generator недоступний: {e}")

try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from bot_statistics import (
        log_event, get_daily_stats, get_weekly_stats, get_user_stats,
        create_reminder, get_due_reminders, mark_reminder_sent, get_user_reminders,
        rate_response, get_response_stats,
        check_organization, get_all_verified_organizations
    )
    STATS_AVAILABLE = True
    logger.info("✅ Модуль статистики підключено")
except Exception as e:
    logger.warning(f"⚠️ Модуль статистики недоступний: {e}")

# Імпорт розширеного юридичного словника
LEGAL_TRANSLATION_FIXES = {}
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from legal_dictionary import LEGAL_TRANSLATION_FIXES_EXTENDED
    LEGAL_TRANSLATION_FIXES = LEGAL_TRANSLATION_FIXES_EXTENDED
    logger.info(f"✅ Юридичний словник підключено ({len(LEGAL_TRANSLATION_FIXES)} термінів)")
except Exception as e:
    logger.warning(f"⚠️ Юридичний словник недоступний: {e}")

# Імпорт з client_bot_functions.py
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent))
    from client_bot_functions import (
        check_if_document,
        get_paragraph_description,
        create_simple_analysis,
        generate_detailed_response
    )
    logger.info("✅ Client Bot Functions підключено")
except Exception as e:
    logger.warning(f"⚠️ Client Bot Functions недоступні: {e}")
    # Створюємо заглушки
    def check_if_document(text): return {'is_document': False}
    def get_paragraph_description(para, lang='uk'): return para
    def create_simple_analysis(text, law_info, lang): return "Аналіз недоступний"
    def generate_detailed_response(text, law_info, lang): return ""

# Токен бота
BOT_TOKEN = "8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0"

# Стани діалогу
WAITING_FOR_USERNAME = 1
WAITING_FOR_LANGUAGE = 2
WAITING_FOR_COUNTRY = 3
WAITING_FOR_STATUS = 4
WAITING_FOR_LETTER = 5
WAITING_FOR_SETTINGS_LANGUAGE = 6
WAITING_FOR_MORE_PAGES = 7  # Багатосторінкові документи

# Доступні мови
AVAILABLE_LANGUAGES = {
    '🇺🇦 Українська': 'uk',
    '🇷🇺 Русский': 'ru',
    '🇩🇪 Deutsch': 'de',
    '🇬🇧 English': 'en'
}

# Переклади інтерфейсу
INTERFACE_TRANSLATIONS = {
    'uk': {
        'welcome': 'Вітаємо! Оберіть дію:',
        'not_registered': 'Спочатку зареєструйтесь (/start)',
        'menu': {
            'register': '📝 Реєстрація',
            'upload': '📤 Завантажити лист',
            'history': '📋 Історія листів',
            'lawyer': '⚖️ Замовити перевірку адвоката',
            'help': '❓ Допомога',
            'settings': '⚙️ Налаштування'
        },
        'settings': {
            'title': '⚙️ Налаштування',
            'language': '🌐 Мова / Language',
            'back': '🔙 Назад',
            'language_selected': '✅ Мову змінено на: {}'
        },
        'registration': {
            'start': '📝 **Реєстрація**\n\nВведіть ваше ім\'я:',
            'username_saved': '✅ Ім\'я: {}\n\nОберіть мову спілкування:',
            'language_saved': '✅ Мова: {}\n\nОберіть країну проживання:',
            'country_saved': '✅ Країна: Німеччина\n\nОберіть ваш статус:',
            'status_saved': '✅ **Реєстрація успішна!**',
            'complete': 'Тепер ви можете завантажити лист для аналізу.'
        },
        'upload': {
            'title': '📤 **Завантаження листа**\n\nНадішліть:\n• 📷 Фото листа (якісне, рівне освітлення)\n• 📄 Текст листа\n• 📎 PDF файл\n\n*Порада:* Для кращого розпізнавання фото має бути чітким.',
            'processing_photo': '⏳ Обробка фото, зачекайте...',
            'processing_pdf': '⏳ Обробка PDF, зачекайте...',
            'processing_translation': '⏳ Переклад тексту...',
            'processing_analysis': '⏳ Аналіз листа, зачекайте...',
            'error_not_recognized': '❌ Не вдалося розпізнати текст.\nСпробуйте надіслати інше фото або текст вручну.',
            'error_no_text': '❌ Не вдалося отримати текст. Спробуйте ще раз.',
            'error_analysis': '❌ Помилка аналізу: {}'
        }
    },
    'ru': {
        'welcome': 'Приветствуем! Выберите действие:',
        'not_registered': 'Сначала зарегистрируйтесь (/start)',
        'menu': {
            'register': '📝 Регистрация',
            'upload': '📤 Загрузить письмо',
            'history': '📋 История писем',
            'lawyer': '⚖️ Заказать проверку адвоката',
            'help': '❓ Помощь',
            'settings': '⚙️ Настройки'
        },
        'settings': {
            'title': '⚙️ Настройки',
            'language': '🌐 Язык / Language',
            'back': '🔙 Назад',
            'language_selected': '✅ Язык изменён на: {}'
        },
        'registration': {
            'start': '📝 **Регистрация**\n\nВведите ваше имя:',
            'username_saved': '✅ Имя: {}\n\nВыберите язык общения:',
            'language_saved': '✅ Язык: {}\n\nВыберите страну проживания:',
            'country_saved': '✅ Страна: Германия\n\nВыберите ваш статус:',
            'status_saved': '✅ **Регистрация успешна!**',
            'complete': 'Теперь вы можете загрузить письмо для анализа.'
        },
        'upload': {
            'title': '📤 **Загрузка письма**\n\nОтправьте:\n• 📷 Фото письма (качественное, ровное освещение)\n• 📄 Текст письма\n• 📎 PDF файл\n\n*Совет:* Для лучшего распознавания фото должно быть четким.',
            'processing_photo': '⏳ Обработка фото, подождите...',
            'processing_pdf': '⏳ Обработка PDF, подождите...',
            'processing_translation': '⏳ Перевод текста...',
            'processing_analysis': '⏳ Анализ письма, подождите...',
            'error_not_recognized': '❌ Не удалось распознать текст.\nПопробуйте отправить другое фото или текст вручную.',
            'error_no_text': '❌ Не удалось получить текст. Попробуйте еще раз.',
            'error_analysis': '❌ Ошибка анализа: {}'
        }
    },
    'de': {
        'welcome': 'Willkommen! Wählen Sie eine Aktion:',
        'not_registered': 'Bitte registrieren Sie sich zuerst (/start)',
        'menu': {
            'register': '📝 Registrierung',
            'upload': '📤 Brief hochladen',
            'history': '📋 Briefverlauf',
            'lawyer': '⚖️ Anwalt prüfen',
            'help': '❓ Hilfe',
            'settings': '⚙️ Einstellungen'
        },
        'settings': {
            'title': '⚙️ Einstellungen',
            'language': '🌐 Sprache / Language',
            'back': '🔙 Zurück',
            'language_selected': '✅ Sprache geändert zu: {}'
        },
        'registration': {
            'start': '📝 **Registrierung**\n\nGeben Sie Ihren Namen ein:',
            'username_saved': '✅ Name: {}\n\nWählen Sie die Sprache:',
            'language_saved': '✅ Sprache: {}\n\nWählen Sie das Land:',
            'country_saved': '✅ Land: Deutschland\n\nWählen Sie Ihren Status:',
            'status_saved': '✅ **Registrierung erfolgreich!**',
            'complete': 'Sie können jetzt einen Brief hochladen.'
        }
    },
    'en': {
        'welcome': 'Welcome! Choose an action:',
        'not_registered': 'Please register first (/start)',
        'menu': {
            'register': '📝 Registration',
            'upload': '📤 Upload letter',
            'history': '📋 Letter history',
            'lawyer': '⚖️ Lawyer review',
            'help': '❓ Help',
            'settings': '⚙️ Settings'
        },
        'settings': {
            'title': '⚙️ Settings',
            'language': '🌐 Language',
            'back': '🔙 Back',
            'language_selected': '✅ Language changed to: {}'
        },
        'registration': {
            'start': '📝 **Registration**\n\nEnter your name:',
            'username_saved': '✅ Name: {}\n\nChoose language:',
            'language_saved': '✅ Language: {}\n\nChoose country:',
            'country_saved': '✅ Country: Germany\n\nChoose your status:',
            'status_saved': '✅ **Registration successful!**',
            'complete': 'You can now upload a letter for analysis.'
        }
    }
}

# Database setup
def init_db():
    """Ініціалізація бази даних."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Таблиця користувачів
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE,
            username TEXT,
            language TEXT DEFAULT 'uk',
            country TEXT DEFAULT 'de',
            status TEXT DEFAULT 'resident',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Таблиця листів
    c.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER,
            text TEXT,
            letter_type TEXT,
            analysis TEXT,
            response TEXT,
            lawyer_review TEXT,
            photo_path TEXT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    # Додаємо photo_path якщо колонки немає
    try:
        c.execute('ALTER TABLE letters ADD COLUMN photo_path TEXT')
        logger.info("Додано колонку photo_path")
    except sqlite3.OperationalError:
        pass  # Колонка вже існує

    conn.commit()
    conn.close()
    logger.info("База даних ініціалізована")

# Ensure upload folder
Path('uploads').mkdir(exist_ok=True)

def get_user(chat_id: int) -> dict:
    """Отримати дані користувача."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    row = c.fetchone()
    conn.close()

    if row:
        return {
            'id': row[0],
            'chat_id': row[1],
            'username': row[2],
            'language': row[3],
            'country': row[4],
            'status': row[5]
        }
    return None

def post_process_translation(text: str) -> str:
    """Пост-обробка перекладу з виправленням юридичних термінів."""
    if not text:
        return text

    result = text
    # Сортуємо за довжиною - спочатку найдовші заміни
    for wrong, correct in sorted(LEGAL_TRANSLATION_FIXES.items(), key=lambda x: -len(x[0])):
        result = result.replace(wrong, correct)

    return result

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Головне меню."""
    chat_id = update.effective_chat.id

    # Перевірка реєстрації
    user = get_user(chat_id)

    # Отримуємо мову користувача або за замовчуванням українська
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    if user:
        # Зареєстрований користувач
        keyboard = [
            [t['menu']['upload']],
            [t['menu']['history']],
            [t['menu']['lawyer']],
            [t['menu']['settings'], t['menu']['help']]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        lang_names = {'uk': 'Українська', 'ru': 'Русский', 'de': 'Deutsch', 'en': 'English'}
        await update.message.reply_text(
            f"{t['welcome']}\n\n"
            f"👤 {user['username']}\n"
            f"🌐 Мова: {lang_names.get(user['language'], 'Українська')}\n"
            f"🏳️ Статус: {user['status']}",
            reply_markup=reply_markup
        )
    else:
        # Новий користувач
        keyboard = [[t['menu']['register']]]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"{t['welcome']}\n\n"
            "🇺🇦 Мультикраїновий Аналізатор Юридичних Листів\n\n"
            "Я допоможу зрозуміти листи від:\n"
            "• Jobcenter\n"
            "• Орендодавця\n"
            "• Кредиторів\n"
            "• Інших установ\n\n"
            "Підтримувані мови: 🇺🇦🇷🇺🇩🇪🇬🇧",
            reply_markup=reply_markup
        )

    return ConversationHandler.END

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок реєстрації."""
    await update.message.reply_text(
        "📝 **Реєстрація**\n\n"
        "Введіть ваше ім'я:"
    )
    return WAITING_FOR_USERNAME

async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Збереження username."""
    context.user_data['username'] = update.message.text.strip()

    keyboard = [['🇺🇦 Українська'], ['🇩🇪 Deutsch']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"✅ Ім'я: {context.user_data['username']}\n\n"
        "Оберіть мову спілкування:",
        reply_markup=reply_markup
    )
    return WAITING_FOR_LANGUAGE

async def register_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вибір мови."""
    context.user_data['language'] = 'uk' if 'Українська' in update.message.text else 'de'

    keyboard = [['🇩🇪 Німеччина']]  # Можна додати більше країн
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        f"✅ Мова: {'Українська' if context.user_data['language'] == 'uk' else 'Deutsch'}\n\n"
        "Оберіть країну проживання:",
        reply_markup=reply_markup
    )
    return WAITING_FOR_COUNTRY

async def register_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вибір країни."""
    context.user_data['country'] = 'de'  # Поки тільки Німеччина

    keyboard = [['🏠 Резидент'], ['🇩🇪 Громадянин']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "✅ Країна: Німеччина\n\n"
        "Оберіть ваш статус:",
        reply_markup=reply_markup
    )
    return WAITING_FOR_STATUS

async def register_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Завершення реєстрації."""
    context.user_data['status'] = 'resident' if 'Резидент' in update.message.text else 'citizen'

    chat_id = update.effective_chat.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    try:
        c.execute("""
            INSERT INTO users (chat_id, username, language, country, status)
            VALUES (?, ?, ?, ?, ?)
        """, (
            chat_id,
            context.user_data['username'],
            context.user_data['language'],
            context.user_data['country'],
            context.user_data['status']
        ))
        conn.commit()

        keyboard = [
            ['📤 Завантажити лист'],
            ['📋 Історія листів'],
            ['⚖️ Замовити перевірку адвоката'],
            ['❓ Допомога']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        await update.message.reply_text(
            "✅ **Реєстрація успішна!**\n\n"
            f"Ваші дані:\n"
            f"• Ім'я: {context.user_data['username']}\n"
            f"• Мова: {'Українська' if context.user_data['language'] == 'uk' else 'Deutsch'}\n"
            f"• Країна: Німеччина\n"
            f"• Статус: {context.user_data['status']}\n\n"
            "Тепер ви можете завантажити лист для аналізу.",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        logger.info(f"Новий користувач зареєстрований: chat_id={chat_id}")

    except sqlite3.IntegrityError:
        await update.message.reply_text("❌ Користувач вже існує.")
    finally:
        conn.close()

    return ConversationHandler.END

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Початок завантаження листа."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)

    # Отримуємо мову користувача
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    if not user:
        await update.message.reply_text(t['not_registered'])
        return ConversationHandler.END

    # Очищаємо тимчасове сховище
    context.user_data['letter_photos'] = []
    context.user_data['letter_text'] = ''

    await update.message.reply_text(
        t['upload']['title'] + "\n\n"
        "📌 **УВАГА: Багатосторінкові документи**\n\n"
        "Якщо ваш лист має **кілька сторінок**:\n"
        "1️⃣ Надішліть перше фото\n"
        "2️⃣ Я запитаю чи є ще сторінки\n"
        "3️⃣ Надсилайте фото по черзі\n"
        "4️⃣ Коли всі фото надіслані - натисніть \"✅ Все, аналізуй\"\n\n"
        "📄 **Поради для якісного фото:**\n"
        "• Робіть фото при хорошому освітленні\n"
        "• Тримайте камеру рівно\n"
        "• Уникайте тіней та відблисків",
        parse_mode='Markdown'
    )
    return WAITING_FOR_LETTER

async def handle_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка завантаженого листа з підтримкою багатосторінкових документів."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)

    # Отримуємо мову користувача
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    if not user:
        await update.message.reply_text(t['not_registered'])
        return ConversationHandler.END

    text = ""
    file_path = None

    # Отримання тексту з різних джерел
    if update.message.photo:
        # Обробка фото
        await update.message.reply_text(t['upload']['processing_photo'])

        photo = update.message.photo[-1]  # Найкраща якість
        file = await photo.get_file()

        # Завантаження фото
        file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        await file.download_to_drive(file_path)

        # OCR з використанням advanced_ocr якщо доступний
        if ADVANCED_OCR:
            try:
                ocr_result = recognize_image(file_path, lang='deu+eng')
                text = ocr_result.get('text', '')
                logger.info(f"OCR (advanced_ocr): витягнуто {len(text)} символів")
            except Exception as e:
                logger.warning(f"advanced_ocr не доступний: {e}")
                text = ""
        else:
            # Fallback на pytesseract
            try:
                img = Image.open(file_path)
                text = pytesseract.image_to_string(img, lang='deu+eng')
                logger.info(f"OCR (pytesseract): витягнуто {len(text)} символів")
            except Exception as e:
                logger.error(f"OCR помилка: {e}")
                text = ""

        if not text.strip():
            await update.message.reply_text(t['upload']['error_not_recognized'])
            return ConversationHandler.END

        # Зберігаємо фото для багатосторінкової обробки
        if 'letter_photos' not in context.user_data:
            context.user_data['letter_photos'] = []
            context.user_data['letter_text'] = ''

        context.user_data['letter_photos'].append(file_path)
        page_num = len(context.user_data['letter_photos'])
        context.user_data['letter_text'] += f"\n\n--- СТОРІНКА {page_num} ---\n\n{text}"

        # Запитуємо чи є ще сторінки
        keyboard = get_multi_page_keyboard()
        await update.message.reply_text(
            f"✅ **Сторінка {page_num} оброблена**\n\n"
            f"Розпізнано {len(text)} символів.\n\n"
            f"Чи є ще сторінки?",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return WAITING_FOR_MORE_PAGES

    elif update.message.document:
        # Обробка документа (PDF)
        await update.message.reply_text(t['upload']['processing_pdf'])

        doc = update.message.document
        file = await doc.get_file()
        file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
        await file.download_to_drive(file_path)

        # Спроба витягнути текст з PDF
        try:
            from pdfminer.high_level import extract_text as pdf_extract
            text = pdf_extract(file_path)
        except Exception as e:
            logger.error(f"PDF помилка: {e}")
            text = ""

    elif update.message.text:
        # Текстовий лист
        text = update.message.text

        # Запитуємо чи це все (multi-page support для тексту)
        if 'letter_photos' not in context.user_data:
            context.user_data['letter_photos'] = []
            context.user_data['letter_text'] = ''

        context.user_data['letter_text'] += text

        # Запитуємо чи це все
        keyboard = get_multi_page_keyboard()
        await update.message.reply_text(
            f"✅ **Текст отримано**\n\n"
            f"Розпізнано {len(text)} символів.\n\n"
            f"Чи є ще сторінки для додавання?",
            reply_markup=keyboard,
            parse_mode='Markdown'
        )
        return WAITING_FOR_MORE_PAGES

    if not text.strip():
        await update.message.reply_text(t['upload']['error_no_text'])
        return ConversationHandler.END

    logger.info(f"Отримано текст: {len(text)} символів")

    # Використовуємо накопичений текст якщо це багатосторінковий документ
    if context.user_data.get('letter_text'):
        text = context.user_data['letter_text']
        logger.info(f"Багатосторінковий текст: {len(text)} символів")

    # Переклад тексту на рідну мову користувача
    translated_text = None
    if user['language'] in ['uk', 'ru'] and text.strip():
        try:
            await update.message.reply_text(t['upload']['processing_translation'])
            dest_lang = user['language']
            
            if ADVANCED_TRANSLATOR:
                clean_text = text[:3000].replace('[', '').replace(']', '')
                result = await translate_text_async(clean_text, 'de', dest_lang)
                translated_text = result.get('text', '') if isinstance(result, dict) else str(result)
                # Пост-обробка з юридичним словником
                translated_text = post_process_translation(translated_text)
                logger.info(f"Переклад через advanced_translator: {len(translated_text)} символів")
            else:
                # Fallback на googletrans
                from googletrans import Translator
                translator = Translator()
                clean_text = text[:3000].replace('[', '').replace(']', '')
                translation = await translator.translate(clean_text, src='de', dest=dest_lang)
                translated_text = translation.text
                logger.info(f"Переклад через googletrans: {len(translated_text)} символів")
        except Exception as e:
            logger.warning(f"Переклад не вдався: {e}")
            translated_text = "[Переклад тимчасово недоступний]"

    # Відправка тексту на обробку
    await update.message.reply_text(t['upload']['processing_analysis'])

    # АНАЛІЗ ЛИСТА
    try:
        # 1. Перевірка чи це документ
        doc_check = check_if_document(text)
        
        # 2. Analiz z Legal Database
        law_info = {}
        if LEGAL_DATABASE:
            law_info = analyze_letter(text)
            logger.info(f"Legal Database аналіз: {law_info.get('organization', 'N/A')}")
        
        # 3. Fraud detection
        fraud_warning = ""
        if FRAUD_DETECTION and doc_check.get('is_fraud', False):
            fraud_analysis = analyze_letter_for_fraud(text, {})
            fraud_warning = generate_fraud_warning(fraud_analysis)
        
        # 4. Отримуємо відповідь
        user_response = ""
        german_response = ""
        
        if LLM_ORCHESTRATOR:
            # Використовуємо LLM Orchestrator
            llm_result = process_letter_with_llm(text, lang)
            if llm_result.get('success'):
                user_response = llm_result.get('response_user', '')
                german_response = llm_result.get('response_de', '')
                logger.info("✅ LLM аналіз успішний")
            else:
                logger.warning("⚠️ LLM аналіз не вдався, fallback")
        
        if not user_response and IMPROVED_RESPONSES:
            # Fallback на improved_response_generator
            user_response, german_response = generate_response_smart_improved(text, lang)
            logger.info("✅ Використано Improved Response Generator")
        
        if not user_response:
            # Fallback на smart_law_reference
            if SMART_LAW_REFERENCE:
                smart_analysis = analyze_letter_smart(text, lang)
                user_response = smart_analysis.get('response_uk' if lang == 'uk' else 'response_de', '')
                german_response = smart_analysis.get('response_de', '')
                law_info.update(smart_analysis.get('law_info', {}))
                logger.info("✅ Використано Smart Law Reference")
        
        # 5. Контактні дані
        contacts_info = ""
        if FRAUD_DETECTION:
            phones = extract_phone_numbers(text)
            emails = extract_emails(text)
            websites = extract_websites(text)
            
            if phones:
                contacts_info += f"📞 **Телефони:** {', '.join(phones)}\n"
            if emails:
                contacts_info += f"📧 **Email:** {', '.join(emails)}\n"
            if websites:
                contacts_info += f"🌐 **Сайти:** {', '.join(websites)}\n"
            
            if contacts_info:
                contacts_info = f"🔍 **Контактні дані:**\n{contacts_info}\n"
        
        # 6. Формуємо результат
        result = f"""✅ **Аналіз завершено!**

🏢 **Організація:** {law_info.get('organization', 'Не визначено')}
📋 **Тип:** {law_info.get('situation', 'Не визначено')}
📚 **Параграфи:** {', '.join(law_info.get('paragraphs', []))}

{contacts_info}
━━━━━━━━━━━━━━━━━━━━

📝 **ВІДПОВІДЬ:**

{user_response}
"""
        
        # Додаємо попередження про шахрайство
        if fraud_warning:
            result += f"\n━━━━━━━━━━━━━━━━━━━━\n\n{fraud_warning}"
        
        # 7. Відправка перекладу
        if translated_text and user['language'] in ['uk', 'ru']:
            safe_translated = translated_text.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
            lang_name = 'українська' if user['language'] == 'uk' else 'русский'
            translation_msg = f"🌐 **Переклад листа ({lang_name}):**\n\n{safe_translated}"
            for i in range(0, len(translation_msg), 4000):
                await update.message.reply_text(
                    translation_msg[i:i+4000],
                    parse_mode='Markdown'
                )
        
        # 8. Відправка результату
        safe_result = result.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`')
        for i in range(0, len(safe_result), 4000):
            await update.message.reply_text(
                safe_result[i:i+4000],
                parse_mode='Markdown'
            )
        
        # 9. Німецька версія (DIN 5008)
        if german_response and LETTER_GENERATOR:
            german_msg = f'''

━━━━━━━━━━━━━━━━━━━━

🇩🇪 **ГОТОВИЙ ЛИСТ НІМЕЦЬКОЮ (DIN 5008)**

Цей лист можна скопіювати та відправити:

────────────────────

{german_response}

────────────────────

💡 **Порада:** Скопіюйте текст та відправте на email або поштою.'''
            
            for i in range(0, len(german_msg), 4000):
                await update.message.reply_text(
                    german_msg[i:i+4000],
                    parse_mode='Markdown'
                )
            
            # 10. Генерація PDF
            if PDF_GENERATOR:
                try:
                    pdf_path = generate_letter_pdf(
                        analysis=law_info,
                        response_text=german_response,
                        filename=f'letter_{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
                    )
                    
                    with open(pdf_path, 'rb') as f:
                        await update.message.reply_document(
                            document=f,
                            caption='📄 **Готовий PDF-лист**\n\nМожна роздрукувати та відправити поштою.',
                            parse_mode='Markdown'
                        )
                    logger.info("✅ PDF відправлено")
                except Exception as e:
                    logger.error(f"❌ Помилка генерації PDF: {e}")
        
        # 11. Збереження в БД
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        photos_list = context.user_data.get('letter_photos', [])
        first_photo = photos_list[0] if photos_list else None
        c.execute("""
            INSERT INTO letters (chat_id, text, letter_type, analysis, response, photo_path)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (chat_id, text[:500], law_info.get('organization', 'unknown'), str(law_info), user_response, first_photo))
        conn.commit()
        conn.close()
        
        logger.info(f"Аналіз завершено для chat_id={chat_id}")
        
    except Exception as e:
        logger.error(f"Помилка аналізу: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Помилка аналізу: {str(e)}\n\n"
            "Спробуйте ще раз або зверніться до підтримки."
        )
    
    # Очищаємо тимчасове сховище
    context.user_data['letter_photos'] = []
    context.user_data['letter_text'] = ''
    
    # Повернення до меню
    keyboard = [
        [t['menu']['upload']],
        [t['menu']['history']],
        [t['menu']['lawyer']],
        [t['menu']['settings'], t['menu']['help']]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        f"{t['welcome']}\n\n"
        "Що ще бажаєте зробити?",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def handle_more_pages(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка вибору користувача щодо ще сторінок."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    if not user:
        await update.message.reply_text(t['not_registered'])
        return ConversationHandler.END

    text = update.message.text.strip()
    logger.info(f"handle_more_pages: отримано текст: '{text}'")

    # Перевіряємо чи це кнопка "✅ Все, аналізуй"
    if "Все" in text or "аналіз" in text or "анализ" in text:
        logger.info(f"✅ Користувач обрав 'Все, аналізуй'")
        
        # Використовуємо накопичений текст
        full_text = context.user_data.get('letter_text', '')
        
        if not full_text.strip():
            await update.message.reply_text("❌ Помилка: немає накопиченого тексту.")
            return ConversationHandler.END
        
        logger.info(f"Об'єднаний текст: {len(full_text)} символів")
        
        # Очищаємо тимчасове сховище
        context.user_data['letter_photos'] = []
        context.user_data['letter_text'] = ''
        
        # Викликаємо аналіз тексту напряму
        # Створюємо фейкове повідомлення для analyze_and_respond
        class FakeMessage:
            def __init__(self, text):
                self.text = text
            async def reply_text(self, text, **kwargs):
                pass
        
        class FakeUpdate:
            def __init__(self, message):
                self.message = message
                self.effective_chat = type('Chat', (), {'id': chat_id})()
        
        fake_update = FakeUpdate(FakeMessage(full_text))
        return await handle_letter(fake_update, context)
    
    elif "Ще" in text or "ще" in text or "сторінку" in text:
        logger.info(f"📄 Користувач обрав 'Ще сторінку'")
        await update.message.reply_text(
            "📄 **Надішліть наступну сторінку**\n\n"
            "Надішліть фото наступної сторінки документа або вставте текст.",
            parse_mode='Markdown'
        )
        return WAITING_FOR_LETTER
    
    else:
        logger.warning(f"❌ Невідомий вибір: '{text}'")
        keyboard = [
            [t['menu']['upload']],
            [t['menu']['history']],
            [t['menu']['lawyer']],
            [t['menu']['settings'], t['menu']['help']]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"❌ Невідомий вибір: '{text}'. Оберіть дію:",
            reply_markup=reply_markup
        )
        return ConversationHandler.END

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати історію листів."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, letter_type, timestamp, text
        FROM letters
        WHERE chat_id=?
        ORDER BY timestamp DESC
        LIMIT 20
    """, (chat_id,))
    letters = c.fetchall()
    conn.close()

    if not letters:
        await update.message.reply_text("📋 Історія порожня.\n\nВи ще не завантажували листи.")
        return ConversationHandler.END

    # Переклад назв типів
    type_names_translated = {
        'uk': {
            'debt_collection': '💰 Боргові',
            'tenancy': '🏠 Оренда',
            'employment': '💼 Jobcenter',
            'administrative': '📋 Адмін',
            'personal': '👨‍👩‍👦 Особистий',
            'general': '📄 Загальний'
        },
        'ru': {
            'debt_collection': '💰 Долговые',
            'tenancy': '🏠 Аренда',
            'employment': '💼 Jobcenter',
            'administrative': '📋 Админ',
            'personal': '👨‍👩‍👦 Личный',
            'general': '📄 Общий'
        },
        'de': {
            'debt_collection': '💰 Schulden',
            'tenancy': '🏠 Miete',
            'employment': '💼 Jobcenter',
            'administrative': '📋 Verwaltung',
            'personal': '👨‍👩‍👦 Persönlich',
            'general': '📄 Allgemein'
        },
        'en': {
            'debt_collection': '💰 Debt',
            'tenancy': '🏠 Tenancy',
            'employment': '💼 Jobcenter',
            'administrative': '📋 Admin',
            'personal': '👨‍👩‍👦 Personal',
            'general': '📄 General'
        }
    }

    names = type_names_translated.get(lang, type_names_translated['uk'])

    for i, (id, letter_type, timestamp, text) in enumerate(letters, 1):
        type_name = names.get(letter_type, '📄 Лист')
        preview = text[:50].replace('\n', ' ') if text else 'Фото листа'

        keyboard = [[InlineKeyboardButton(f"{type_name} #{i} — {preview}...", callback_data=f'letter_{id}')]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            f"**{type_name} #{i}**\n📅 {timestamp}\n\n_{preview}_...",
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
        await asyncio.sleep(0.5)

    return ConversationHandler.END

async def view_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Перегляд конкретного листа."""
    query = update.callback_query
    await query.answer()

    letter_id = query.data.replace('letter_', '')
    chat_id = query.message.chat_id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT text, letter_type, analysis, response, photo_path, timestamp
        FROM letters
        WHERE id=? AND chat_id=?
    """, (letter_id, chat_id))
    letter = c.fetchone()
    conn.close()

    if not letter:
        await query.edit_message_text("❌ Лист не знайдено.")
        return

    text, letter_type, analysis, response, photo_path, timestamp = letter

    # Спочатку показуємо фото якщо є
    if photo_path and Path(photo_path).exists():
        try:
            with open(photo_path, 'rb') as f:
                await context.bot.send_photo(
                    chat_id=chat_id,
                    photo=f,
                    caption=f"📄 **Лист #{letter_id}**\n📅 {timestamp}",
                    parse_mode='Markdown'
                )
        except Exception as e:
            logger.error(f"Помилка відправки фото: {e}")

    # Показуємо інформацію
    full_info = f"""📋 **ІНФОРМАЦІЯ ПРО ЛИСТ #{letter_id}**

📅 **Дата:** {timestamp}

📝 **ОРИГІНАЛЬНИЙ ТЕКСТ:**
_{text[:500 if len(text) > 500 else len(text)]}{'...' if len(text) > 500 else ''}_

━━━━━━━━━━━━━━━━━━━━

📊 **АНАЛІЗ:**
{analysis[:1000 if len(analysis) > 1000 else len(analysis)]}

━━━━━━━━━━━━━━━━━━━━

📝 **ВІДПОВІДЬ:**
{response}

━━━━━━━━━━━━━━━━━━━━

🔙 Натисніть кнопку щоб повернутися."""

    keyboard = [[InlineKeyboardButton("🔙 Назад", callback_data='back_to_history')]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await context.bot.send_message(
        chat_id=chat_id,
        text=full_info,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

    try:
        await query.delete_message()
    except:
        pass

async def back_to_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Повернення до історії."""
    query = update.callback_query
    await query.answer()
    await show_history(update, context)

async def lawyer_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Інформація про допомогу адвоката."""
    await update.message.reply_text(
        "⚖️ **Допомога адвоката**\n\n"
        "📞 **Гарячі лінії:**\n"
        "• Telefonseelsorge: 0800 111 0 111\n"
        "• Rechtsantragsstelle: безкоштовна допомога\n\n"
        "💰 **Beratungshilfe** — субсидія на юридичну допомогу.\n\n"
        "Бажаєте замовити платну консультацію?",
        parse_mode='Markdown',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("📞 Замовити дзвінок", callback_data="lawyer_request")
        ]])
    )
    return ConversationHandler.END

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Допомога."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    await update.message.reply_text(
        f"❓ **{t['menu']['help']}**\n\n"
        "Цей бот допомагає аналізувати юридичні листи.\n\n"
        "📌 **Як користуватися:**\n"
        "1. Зареєструйтесь (/start)\n"
        "2. Надішліть фото або текст листа\n"
        "3. Отримайте аналіз та шаблон відповіді\n\n"
        "⚡ **Швидкі команди:**\n"
        "/jobcenter - довідка Jobcenter\n"
        "/inkasso - довідка борги\n"
        "/miete - довідка оренда\n\n"
        "⚠️ **Важливо:** Бот не замінює адвоката!",
        parse_mode='Markdown'
    )
    return ConversationHandler.END

async def settings_menu(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Меню налаштувань."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    if not user:
        await update.message.reply_text(t['not_registered'])
        return ConversationHandler.END

    keyboard = [
        [t['settings']['language']],
        [t['settings']['back']]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"{t['settings']['title']}\n\n"
        f"🌐 Поточна мова: {lang.upper()}",
        reply_markup=reply_markup
    )
    return ConversationHandler.END

async def settings_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Вибір мови в налаштуваннях."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])

    keyboard = [[lang] for lang in AVAILABLE_LANGUAGES.keys()]
    keyboard.append([t['settings']['back']])
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    await update.message.reply_text(
        f"🌐 **{t['settings']['language']}**\n\n"
        "Оберіть мову інтерфейсу:",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )
    return WAITING_FOR_SETTINGS_LANGUAGE

async def settings_language_selected(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Збереження вибору мови."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    selected_text = update.message.text.strip()

    logger.info(f"Вибрано мову: {selected_text}")

    # Знаходимо мову за текстом кнопки
    selected_lang = None
    for btn_text, lang_code in AVAILABLE_LANGUAGES.items():
        if btn_text in selected_text or lang_code in selected_text.lower():
            selected_lang = lang_code
            break

    if not selected_lang:
        logger.info(f"Мову не знайдено, повернення в меню")
        return await settings_menu(update, context)

    # Оновлюємо мову в БД
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("UPDATE users SET language=? WHERE chat_id=?", (selected_lang, chat_id))
    conn.commit()
    conn.close()

    logger.info(f"Мову змінено на: {selected_lang}")

    # Отримуємо переклад для нової мови
    t = INTERFACE_TRANSLATIONS.get(selected_lang, INTERFACE_TRANSLATIONS['uk'])

    # Повертаємо меню з новою мовою
    keyboard = [
        [t['menu']['upload']],
        [t['menu']['history']],
        [t['menu']['lawyer']],
        [t['menu']['settings'], t['menu']['help']]
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    lang_names = {'uk': 'Українська', 'ru': 'Русский', 'de': 'Deutsch', 'en': 'English'}
    await update.message.reply_text(
        t['settings']['language_selected'].format(lang_names.get(selected_lang, selected_lang)),
        reply_markup=reply_markup
    )

    return ConversationHandler.END

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Скасування дії."""
    await update.message.reply_text("❌ Дію скасовано.")
    return ConversationHandler.END

async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка натискань кнопок."""
    query = update.callback_query
    await query.answer()

    if query.data == "lawyer_request":
        await query.edit_message_text(
            "✅ Вашу заявку прийнято!\n\n"
            "Наш менеджер зв'яжеться з вами протягом 24 годин."
        )

async def letter_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка вибору листа."""
    query = update.callback_query
    if query.data.startswith('letter_'):
        await view_letter(update, context)
    elif query.data == 'back_to_history':
        await back_to_history(update, context)

# Швидкі команди
async def cmd_jobcenter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Швидка довідка Jobcenter."""
    await update.message.reply_text(
        "💼 **Jobcenter - Швидка довідка**\n\n"
        "📞 **Гарячі лінії:**\n"
        "• Telefonseelsorge: 0800 111 0 111\n\n"
        "⚖️ **Ваші права:**\n"
        "• § 59 SGB II - Запрошення\n"
        "• § 31 SGB II - Санкції\n"
        "• § 309 SGB III - Офіційні документи\n\n"
        "⚠️ **Важливо:** З'являйтесь на всі запрошення!",
        parse_mode='Markdown'
    )

async def cmd_inkasso(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Швидка довідка Inkasso."""
    await update.message.reply_text(
        "💰 **Inkasso - Швидка довідка**\n\n"
        "⚖️ **Ваші права:**\n"
        "• BGB § 286 - Прострочення\n"
        "• BGB § 288 - Проценти (5% річних)\n"
        "• BGB § 194 - Строк давності (3 роки)\n\n"
        "🛡️ **Захист:** Вимагайте докази боргу!\n\n"
        "⚠️ **Шахраї:** Вимагають Western Union - це обман!",
        parse_mode='Markdown'
    )

async def cmd_miete(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Швидка довідка оренда."""
    await update.message.reply_text(
        "🏠 **Оренда - Швидка довідка**\n\n"
        "⚖️ **Ваші права:**\n"
        "• BGB § 535 - Орендодавець зобов'язаний\n"
        "• BGB § 558 - Підвищення (макс 20% за 3 роки)\n"
        "• BGB § 543 - Виселення (тільки 2+ місяці несплати)\n\n"
        "🛡️ **Захист:** Mieterbund (спілка орендарів)\n\n"
        "⚠️ **Важливо:** Не підписуйте без перевірки!",
        parse_mode='Markdown'
    )

def main():
    """Запуск бота."""
    logger.info("Запуск Client Bot v4.0 Full Integration...")

    # Ініціалізація БД
    init_db()

    # Створення додатку
    application = Application.builder().token(BOT_TOKEN).build()

    # Conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.Regex("^📝 Реєстрація$"), register_start),
            MessageHandler(filters.Regex("^📝 Регистрация$"), register_start),
            MessageHandler(filters.Regex("^📝 Registrierung$"), register_start),
            MessageHandler(filters.Regex("^📝 Registration$"), register_start),
            MessageHandler(filters.Regex("^📤 Завантажити лист$"), upload_start),
            MessageHandler(filters.Regex("^📤 Загрузить письмо$"), upload_start),
            MessageHandler(filters.Regex("^📤 Brief hochladen$"), upload_start),
            MessageHandler(filters.Regex("^📤 Upload letter$"), upload_start),
        ],
        states={
            WAITING_FOR_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            WAITING_FOR_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_language)],
            WAITING_FOR_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_country)],
            WAITING_FOR_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_status)],
            WAITING_FOR_LETTER: [
                MessageHandler(filters.PHOTO, handle_letter),
                MessageHandler(filters.Document.ALL, handle_letter),
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_letter),
            ],
            WAITING_FOR_MORE_PAGES: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_more_pages),
            ],
            WAITING_FOR_SETTINGS_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_language_selected)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(CallbackQueryHandler(letter_callback))

    # Швидкі команди
    application.add_handler(CommandHandler("jobcenter", cmd_jobcenter))
    application.add_handler(CommandHandler("inkasso", cmd_inkasso))
    application.add_handler(CommandHandler("miete", cmd_miete))

    application.add_handler(MessageHandler(filters.Regex("^(📋 Історія листів|📋 История писем|📋 Briefverlauf|📋 Letter history)$"), show_history))
    application.add_handler(MessageHandler(filters.Regex("^(⚖️ Замовити перевірку адвоката|⚖️ Заказать проверку адвоката|⚖️ Anwalt prüfen|⚖️ Lawyer review)$"), lawyer_help))
    application.add_handler(MessageHandler(filters.Regex("^(❓ Допомога|❓ Помощь|❓ Hilfe|❓ Help)$"), help_command))
    application.add_handler(MessageHandler(filters.Regex("^(⚙️ Налаштування|⚙️ Настройки|⚙️ Einstellungen|⚙️ Settings)$"), settings_menu))
    application.add_handler(MessageHandler(filters.Regex("^(🌐 Мова / Language|🌐 Язык / Language|🌐 Sprache / Language|🌐 Language)$"), settings_language))
    application.add_handler(MessageHandler(filters.Regex("^(🔙 Назад|🔙 Zurück|🔙 Back)$"), settings_menu))

    # Запуск
    logger.info("✅ Client Bot v4.0 Full готовий до запуску!")
    logger.info(f"📊 Підключені модулі:")
    logger.info(f"  - Advanced Translator: {ADVANCED_TRANSLATOR}")
    logger.info(f"  - Advanced OCR: {ADVANCED_OCR}")
    logger.info(f"  - Legal Database: {LEGAL_DATABASE}")
    logger.info(f"  - Multi-page Handler: {MULTI_PAGE_HANDLER}")
    logger.info(f"  - Fraud Detection: {FRAUD_DETECTION}")
    logger.info(f"  - Smart Law Reference: {SMART_LAW_REFERENCE}")
    logger.info(f"  - Improved Responses: {IMPROVED_RESPONSES}")
    logger.info(f"  - Letter Generator: {LETTER_GENERATOR}")
    logger.info(f"  - LLM Orchestrator: {LLM_ORCHESTRATOR}")
    logger.info(f"  - PDF Generator: {PDF_GENERATOR}")
    
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
