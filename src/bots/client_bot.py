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
    
    if user:
        # Зареєстрований користувач
        keyboard = [
            ['📤 Завантажити лист'],
            ['📋 Історія листів'],
            ['⚖️ Замовити перевірку адвоката'],
            ['❓ Допомога']
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            f"Вітаємо, {user['username']}! 👋\n\n"
            f"Ваш статус: {user['status']}\n"
            f"Країна: {user['country'].upper()}\n\n"
            f"Оберіть дію:",
            reply_markup=reply_markup
        )
    else:
        # Новий користувач
        keyboard = [['📝 Реєстрація']]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        await update.message.reply_text(
            "Вітаємо! 👋\n\n"
            "Я бот для аналізу юридичних листів.\n"
            "Я допоможу вам зрозуміти листи від:\n"
            "• Jobcenter\n"
            "• Орендодавця\n"
            "• Кредиторів\n"
            "• Інших установ\n\n"
            "Спочатку зареєструйтесь:",
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
    
    if not user:
        await update.message.reply_text("❌ Спочатку зареєструйтесь (/start)")
        return ConversationHandler.END
    
    await update.message.reply_text(
        "📤 **Завантаження листа**\n\n"
        "Надішліть:\n"
        "• 📷 Фото листа (якісне, рівне освітлення)\n"
        "• 📄 Текст листа\n"
        "• 📎 PDF файл\n\n"
        "*Порада:* Для кращого розпізнавання фото має бути чітким.",
        parse_mode='Markdown'
    )
    return WAITING_FOR_LETTER

async def handle_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Обробка завантаженого листа."""
    chat_id = update.effective_chat.id
    user = get_user(chat_id)
    text = ""
    
    # Отримання тексту з різних джерел
    if update.message.photo:
        # Обробка фото
        await update.message.reply_text("⏳ Обробка фото, зачекайте...")
        
        photo = update.message.photo[-1]  # Найкраща якість
        file = await photo.get_file()
        
        # Завантаження фото
        file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
        await file.download_to_drive(file_path)
        
        # OCR
        text = extract_text_from_photo(file_path, lang='deu')
        
        if not text.strip():
            await update.message.reply_text(
                "❌ Не вдалося розпізнати текст.\n"
                "Спробуйте надіслати інше фото або текст вручну."
            )
            return ConversationHandler.END
            
    elif update.message.document:
        # Обробка документа (PDF)
        await update.message.reply_text("⏳ Обробка PDF, зачекайте...")
        
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
        await update.message.reply_text("❌ Не вдалося отримати текст. Спробуйте ще раз.")
        return ConversationHandler.END
    
    logger.info(f"Отримано текст: {len(text)} символів")

    # Переклад тексту на українську (якщо мова користувача українська)
    translated_text = None
    if user['language'] == 'uk' and text.strip():
        try:
            await update.message.reply_text("⏳ Переклад тексту...")
            # googletrans 4.0.0rc1 працює асинхронно - використовуємо sync версію
            translation = await translator.translate(text, src='de', dest='uk')
            translated_text = translation.text
            logger.info(f"Переклад виконано: {len(translated_text)} символів")
        except Exception as e:
            logger.warning(f"Переклад не вдався: {e}")
            translated_text = text  # fallback

    # Відправка тексту на обробку (симуляція виклику core_bot)
    await update.message.reply_text("⏳ Аналіз листа, зачекайте...")

    # Імпортуємо модулі аналізу
    try:
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent))
        from ingestion import preprocess_text
        from nlp_analysis import analyze_text, classify_letter_type
        from legal_db import get_relevant_laws
        from response_generator import generate_response

        # Попередня обробка
        text = preprocess_text(text)

        # Аналіз
        analysis = analyze_text(text)
        letter_type = classify_letter_type(text)
        laws = get_relevant_laws(letter_type, user['country'])

        # Генерація відповіді
        response = generate_response(letter_type, laws, user['language'], user['country'])
        
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
            'general': '📄 Загальний лист'
        }
        
        # Формування результату
        result = (
            f"✅ **Аналіз завершено!**\n\n"
            f"📌 **Тип листа:** {type_names.get(letter_type, letter_type)}\n\n"
            f"🔍 **Ключові слова:**\n"
            f"{', '.join(analysis['keywords'][:5]) if analysis['keywords'] else 'Не визначено'}\n\n"
            f"📚 **Релевантні закони:**\n"
            f"{chr(10).join('• ' + law for law in laws['laws'])}\n\n"
            f"⚠️ **Наслідки:**\n{laws['consequences']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 **Пропонована відповідь:**\n\n{response}"
        )

        # Відправка перекладу (якщо є)
        if translated_text and user['language'] == 'uk':
            translation_msg = f"🌐 **Переклад листа (українська):**\n\n{translated_text}"
            for i in range(0, len(translation_msg), 4000):
                await update.message.reply_text(
                    translation_msg[i:i+4000],
                    parse_mode='Markdown'
                )

        # Відправка результату аналізу частинами
        for i in range(0, len(result), 4000):
            await update.message.reply_text(
                result[i:i+4000],
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
    await update.message.reply_text(
        "❓ **Допомога**\n\n"
        "Цей бот допомагає аналізувати юридичні листи німецькою мовою.\n\n"
        "📌 **Як користуватися:**\n"
        "1. Зареєструйтесь (/start)\n"
        "2. Надішліть фото або текст листа\n"
        "3. Отримайте аналіз та шаблон відповіді\n\n"
        "📷 **Поради для фото:**\n"
        "• Робіть фото при хорошому освітленні\n"
        "• Тримайте камеру рівно\n"
        "• Уникайте тіней та відблисків\n\n"
        "⚠️ **Важливо:** Цей бот не замінює професійного адвоката!",
        parse_mode='Markdown'
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
            MessageHandler(filters.Regex("^📤 Завантажити лист$"), upload_start),
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
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )
    
    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CallbackQueryHandler(button_callback))
    application.add_handler(MessageHandler(filters.Regex("^📋 Історія листів$"), show_history))
    application.add_handler(MessageHandler(filters.Regex("^⚖️ Замовити перевірку адвоката$"), lawyer_help))
    application.add_handler(MessageHandler(filters.Regex("^❓ Допомога$"), help_command))
    
    # Запуск
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
