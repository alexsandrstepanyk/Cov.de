#!/usr/bin/env python3
"""
Client Bot for Gov.de
Реєстрація користувачів, завантаження листів, меню.
"""

import os
import logging
import sqlite3
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
from googletrans import Translator

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Ініціалізація перекладача
translator = Translator()

# Токен бота
BOT_TOKEN = "8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0"

# Стани діалогу
WAITING_FOR_USERNAME = 1
WAITING_FOR_LANGUAGE = 2
WAITING_FOR_COUNTRY = 3
WAITING_FOR_STATUS = 4
WAITING_FOR_LETTER = 5
WAITING_FOR_SETTINGS_LANGUAGE = 6

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
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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

def extract_text_from_photo(photo_path: str, lang: str = 'de') -> str:
    """Витягти текст з фото за допомогою OCR."""
    text = ""
    
    # Спроба 1: pytesseract (якщо встановлено)
    try:
        import pytesseract
        from PIL import Image
        img = Image.open(photo_path)
        text = pytesseract.image_to_string(img, lang='deu+eng')
        logger.info(f"OCR (tesseract): витягнуто {len(text)} символів")
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"tesseract не доступний: {e}")
    
    # Спроба 2: EasyOCR (не потребує системних залежностей)
    try:
        import easyocr
        reader = easyocr.Reader(['en', 'de'], gpu=False, verbose=False)
        results = reader.readtext(photo_path)
        text = ' '.join([r[1] for r in results])
        logger.info(f"OCR (easyocr): витягнуто {len(text)} символів")
        if text.strip():
            return text
    except Exception as e:
        logger.warning(f"easyocr не доступний: {e}")
    
    # Спроба 3: PIL + простий аналіз
    try:
        from PIL import Image
        img = Image.open(photo_path)
        logger.info(f"Фото відкрито: {img.size}, формат: {img.format}")
        return f"[Фото отримано: {img.size[0]}x{img.size[1]} пікселів. Будь ласка, надішліть текст листа вручну або встановіть tesseract для автоматичного розпізнавання.]"
    except Exception as e:
        logger.error(f"Помилка відкриття фото: {e}")
        return ""

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

    await update.message.reply_text(
        t['upload']['title'],
        parse_mode='Markdown'
    )
    return WAITING_FOR_LETTER

async def handle_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка завантаженого листа."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    
    # Отримуємо мову користувача
    lang = user['language'] if user else 'uk'
    t = INTERFACE_TRANSLATIONS.get(lang, INTERFACE_TRANSLATIONS['uk'])
    
    text = ""

    # Отримання тексту з різних джерел
    if update.message.photo:
        # Обробка фото
        await update.message.reply_text(t['upload']['processing_photo'])
        
        photo = update.message.photo[-1]  # Найкраща якість
        file = await photo.get_file()
        
        # Завантаження фото
        file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        await file.download_to_drive(file_path)
        
        # OCR
        text = extract_text_from_photo(file_path, lang='deu')

        if not text.strip():
            await update.message.reply_text(
                t['upload']['error_not_recognized']
            )
            return ConversationHandler.END

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
            # Спроба OCR
            try:
                text = extract_text_from_photo(file_path, lang='deu')
            except:
                pass

    elif update.message.text:
        # Текстовий лист
        text = update.message.text

    if not text.strip():
        await update.message.reply_text(t['upload']['error_no_text'])
        return ConversationHandler.END

    logger.info(f"Отримано текст: {len(text)} символів")

    # Переклад тексту на рідну мову користувача
    translated_text = None
    if user['language'] in ['uk', 'ru'] and text.strip():
        try:
            await update.message.reply_text(t['upload']['processing_translation'])
            dest_lang = 'uk' if user['language'] == 'uk' else 'ru'
            translation = await translator.translate(text, src='de', dest=dest_lang)
            translated_text = translation.text
            logger.info(f"Переклад виконано: {len(translated_text)} символів")
        except Exception as e:
            logger.warning(f"Переклад не вдався: {e}")
            translated_text = text  # fallback

    # Відправка тексту на обробку
    await update.message.reply_text(t['upload']['processing_analysis'])

    # Імпортуємо модулі аналізу
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from ingestion import preprocess_text
        from nlp_analysis import analyze_text_advanced, classify_letter_type_advanced, get_laws_for_letter
        from smart_law_reference import analyze_letter_smart, get_law_reference
        from response_generator import generate_response
        from fraud_detection import (
            extract_phone_numbers, extract_emails, extract_websites,
            analyze_letter_for_fraud, generate_fraud_warning
        )

        # Попередня обробка
        text = preprocess_text(text)

        # РОЗШИРЕНИЙ АНАЛІЗ
        analysis = analyze_text_advanced(text)
        letter_type, classification_details = classify_letter_type_advanced(text)
        
        # РОЗУМНИЙ АНАЛІЗ ЗАКОНІВ
        smart_analysis = analyze_letter_smart(text, user['language'])
        law_info = smart_analysis['law_info']
        is_personal = smart_analysis.get('is_personal', False)
        
        # Отримуємо закони на основі типу листа
        laws = get_laws_for_letter(letter_type, text)
        
        logger.info(f"Тип листа: {letter_type}, Організація: {law_info.get('organization', 'N/A')}, Особистий: {is_personal}")
        logger.info(f"Параграфи: {law_info.get('paragraphs', [])}")

        # Anti-Fraud аналіз
        fraud_analysis = analyze_letter_for_fraud(text, {})
        fraud_warning = generate_fraud_warning(fraud_analysis)

        # Використовуємо розумну відповідь з smart_law_reference
        # Відповідь ТІЛЬКИ мовою користувача
        lang = user['language']
        
        # Отримуємо відповідь з правильними ключами
        if lang == 'uk':
            user_response = smart_analysis.get('response_uk', smart_analysis['response_de'])
        elif lang == 'ru':
            user_response = smart_analysis.get('response_ru', smart_analysis.get('response_uk', smart_analysis['response_de']))
        elif lang == 'de':
            user_response = smart_analysis.get('response_de', '')
        elif lang == 'en':
            user_response = smart_analysis.get('response_en', smart_analysis.get('response_de', ''))
        else:
            user_response = smart_analysis.get('response_uk', smart_analysis['response_de'])
        
        response = f"**{lang.upper()}:**\n{user_response}"
        
        # Додаємо поради з розумного аналізу
        smart_tips = "\n\n💡 **ПОРАДИ:**\n" + "\n".join(smart_analysis['tips'])
        
        # Збереження в БД
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO letters (chat_id, text, letter_type, analysis, response) 
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, text[:500], letter_type, str(analysis), response))
        conn.commit()
        conn.close()
        
        # Формування результату
        type_names = {
            'debt_collection': '💰 Боргові зобов\'язання',
            'tenancy': '🏠 Оренда житла',
            'employment': '💼 Праця / Jobcenter',
            'administrative': '📋 Адміністративний лист',
            'personal': '👨‍👩‍👦 Особисте листування',
            'insurance': '🏥 Страхова каса',
            'utility': '💡 Комунальні послуги',
            'general': '📄 Загальний лист'
        }

        # Додамо інформацію про впевненість класифікації
        scores = classification_details.get('scores', {})
        max_score = max(scores.values()) if scores else 0
        confidence = "✅ Впевнено" if max_score > 5 else "⚠️ Потребує перевірки" if max_score > 0 else "❓ Невизначено"

        # Витягнуті контактні дані
        phones = extract_phone_numbers(text)
        emails = extract_emails(text)
        websites = extract_websites(text)

        contacts_info = ""
        if phones:
            contacts_info += f"📞 **Телефони:** {', '.join(phones)}\n"
        if emails:
            contacts_info += f"📧 **Email:** {', '.join(emails)}\n"
        if websites:
            contacts_info += f"🌐 **Сайти:** {', '.join(websites)}\n"

        if contacts_info:
            contacts_info = f"🔍 **Контактні дані:**\n{contacts_info}\n"

        # Формування результату
        if is_personal:
            # Особистий лист - простий формат
            result = (
                f"✅ **Аналіз завершено!**\n\n"
                f"📌 **Тип листа:** 👨‍👩‍👦 Особисте листування\n"
                f"🏢 **Організація:** {law_info.get('organization', 'Не визначено')}\n\n"
                f"📝 **ВІДПОВІДЬ (двома мовами):**\n\n{response}{smart_tips}"
            )
        else:
            # Офіційний лист - повний формат з законами
            result = (
                f"✅ **Аналіз завершено!**\n\n"
                f"📌 **Тип листа:** {type_names.get(letter_type, letter_type)}\n"
                f"🏢 **Організація:** {law_info.get('organization', 'Не визначено')}\n"
                f"📋 **Ситуація:** {law_info.get('situation', 'Не визначено')}\n"
                f"🔍 **Впевненість:** {confidence}\n\n"
                f"📚 **ПАРАГРАФИ ДЛЯ ПОСИЛАННЯ:**\n"
                f"{chr(10).join('• ' + para for para in law_info.get('paragraphs', []))}\n\n"
                f"{contacts_info}"
                f"🔍 **Ключові слова:**\n"
                f"{', '.join(analysis['keywords'][:8]) if analysis['keywords'] else 'Не визначено'}\n\n"
                f"⚠️ **Наслідки:**\n{law_info.get('consequences', 'Не визначено')}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{fraud_warning}\n\n"
                f"━━━━━━━━━━━━━━━━━━━━\n\n"
                f"📝 **ВІДПОВІДЬ (двома мовами):**\n\n{response}{smart_tips}"
            )

        # Відправка перекладу (якщо є)
        if translated_text and user['language'] == 'uk':
            # Екрануємо Markdown символи
            safe_translated = translated_text.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[').replace(']', '\\]')
            translation_msg = f"🌐 **Переклад листа (українська):**\n\n{safe_translated}"
            for i in range(0, len(translation_msg), 4000):
                await update.message.reply_text(
                    translation_msg[i:i+4000],
                    parse_mode='Markdown'
                )

        # Екрануємо Markdown символи в результаті
        safe_result = result.replace('*', '\\*').replace('_', '\\_').replace('`', '\\`').replace('[', '\\[').replace(']', '\\]')
        
        # Відправка результату аналізу частинами
        for i in range(0, len(safe_result), 4000):
            await update.message.reply_text(
                safe_result[i:i+4000],
                parse_mode='Markdown'
            )
        
        logger.info(f"Аналіз завершено для chat_id={chat_id}, тип={letter_type}")
        
    except Exception as e:
        logger.error(f"Помилка аналізу: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Помилка аналізу: {str(e)}\n\n"
            "Спробуйте ще раз або зверніться до підтримки."
        )
    
    # Повернення до меню
    keyboard = [
        ['📤 Завантажити лист'],
        ['📋 Історія листів'],
        ['⚖️ Замовити перевірку адвоката'],
        ['❓ Допомога']
    ]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Що ще бажаєте зробити?",
        reply_markup=reply_markup
    )
    
    return ConversationHandler.END

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Показати історію листів."""
    chat_id = update.effective_chat.id
    
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("""
        SELECT id, letter_type, timestamp 
        FROM letters 
        WHERE chat_id=? 
        ORDER BY timestamp DESC 
        LIMIT 10
    """, (chat_id,))
    letters = c.fetchall()
    conn.close()
    
    if not letters:
        await update.message.reply_text("📋 Історія порожня.\n\nВи ще не завантажували листи.")
        return ConversationHandler.END
    
    result = "📋 **Ваша історія листів:**\n\n"
    for i, (id, letter_type, timestamp) in enumerate(letters, 1):
        type_names = {
            'debt_collection': '💰 Боргові',
            'tenancy': '🏠 Оренда',
            'employment': '💼 Jobcenter',
            'administrative': '📋 Адмін',
            'general': '📄 Загальний'
        }
        result += f"{i}. {type_names.get(letter_type, letter_type)} — {timestamp}\n"
    
    await update.message.reply_text(result, parse_mode='Markdown')
    return ConversationHandler.END

async def lawyer_help(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Інформація про допомогу адвоката."""
    await update.message.reply_text(
        "⚖️ **Допомога адвоката**\n\n"
        "Для складних випадків рекомендується звернутися до професійного юриста.\n\n"
        "📞 **Гарячі лінії для українців у Німеччині:**\n"
        "• Telefonseelsorge: 0800 111 0 111 (безкоштовно)\n"
        "• Rechtsantragsstelle: безкоштовна правова допомога\n\n"
        "💰 **Beratungshilfe** — субсидія на юридичну допомогу.\n"
        "Зверніться до місцевого суду (Amtsgericht) для отримання сертифікату.\n\n"
        "Бажаєте замовити платну консультацію адвоката через наш сервіс?",
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
        "📷 **Поради для фото:**\n"
        "• Робіть фото при хорошому освітленні\n"
        "• Тримайте камеру рівно\n"
        "• Уникайте тіней та відблисків\n\n"
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
    
    # Якщо не знайдено мову, повертаємось в меню
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

def main():
    """Запуск бота."""
    logger.info("Запуск Client Bot...")
    
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
            WAITING_FOR_SETTINGS_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, settings_language_selected)],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.Regex("^(📋 Історія листів|📋 История писем|📋 Briefverlauf|📋 Letter history)$"), show_history))
    application.add_handler(MessageHandler(filters.Regex("^(⚖️ Замовити перевірку адвоката|⚖️ Заказать проверку адвоката|⚖️ Anwalt prüfen|⚖️ Lawyer review)$"), lawyer_help))
    application.add_handler(MessageHandler(filters.Regex("^(❓ Допомога|❓ Помощь|❓ Hilfe|❓ Help)$"), help_command))
    application.add_handler(MessageHandler(filters.Regex("^(⚙️ Налаштування|⚙️ Настройки|⚙️ Einstellungen|⚙️ Settings)$"), settings_menu))
    application.add_handler(MessageHandler(filters.Regex("^(🌐 Мова / Language|🌐 Язык / Language|🌐 Sprache / Language|🌐 Language)$"), settings_language))
    application.add_handler(MessageHandler(filters.Regex("^(🔙 Назад|🔙 Zurück|🔙 Back)$"), settings_menu))
    # Обробка вибору мови - будь-який текст з назвою мови
    application.add_handler(MessageHandler(filters.Regex("^(🇺🇦|🇷🇺|🇩🇪|🇬🇧|Українська|Русский|Deutsch|English|UK|RU|DE|EN)"), settings_language_selected))
    
    # Запуск
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
