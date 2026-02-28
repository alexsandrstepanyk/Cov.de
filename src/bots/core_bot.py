#!/usr/bin/env python3
"""
Core Bot for Gov.de
Обробка листів: OCR, NLP аналіз, класифікація, генерація відповідей.
"""

import os
import sys
import logging
import sqlite3
from pathlib import Path
from datetime import datetime
import pytesseract
from PIL import Image
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from googletrans import Translator

# Додаємо parent до path для імпорту модулів
sys.path.insert(0, str(Path(__file__).parent.parent))

from ingestion import preprocess_text, load_letter
from nlp_analysis import analyze_text_advanced, classify_letter_type_advanced
from legal_db import get_relevant_laws
from response_generator import generate_response

# Налаштування логування
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('core_bot.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Ініціалізація перекладача
translator = Translator()

# Токен бота
BOT_TOKEN = "8204341583:AAFSPkKDrB6pbllz7CTKbRp7EVA9NbgfDJY"

# Папка для завантажень
Path('uploads').mkdir(exist_ok=True)

def init_db():
    """Ініціалізація бази даних."""
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY,
            chat_id INTEGER UNIQUE,
            username TEXT,
            password TEXT,
            language TEXT DEFAULT 'uk',
            country TEXT DEFAULT 'de',
            status TEXT DEFAULT 'resident',
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
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
    logger.info("Core Bot: База даних ініціалізована")

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
            'language': row[4],
            'country': row[5],
            'status': row[6]
        }
    return None

def extract_text_from_photo(photo_path: str, lang: str = 'deu') -> str:
    """Витягти текст з фото за допомогою OCR."""
    try:
        img = Image.open(photo_path)
        text = pytesseract.image_to_string(img, lang=lang)
        logger.info(f"OCR: витягнуто {len(text)} символів")
        return text
    except Exception as e:
        logger.error(f"OCR помилка: {e}")
        return ""

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /start."""
    await update.message.reply_text(
        "⚙️ **Core Bot**\n\n"
        "Цей бот обробляє юридичні листи.\n"
        "Він працює у фоновому режимі.\n\n"
        "Для взаємодії використовуйте @GovDeClientBot",
        parse_mode='Markdown'
    )

async def process_letter(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Обробка вхідного листа."""
    chat_id = update.effective_chat.id
    logger.info(f"Core Bot: Отримано повідомлення від chat_id={chat_id}")
    
    # Перевірка користувача
    user = get_user(chat_id)
    if not user:
        await update.message.reply_text(
            "❌ Користувача не знайдено.\n"
            "Спочатку зареєструйтесь у @GovDeClientBot"
        )
        return
    
    text = ""
    
    try:
        # Обробка фото
        if update.message.photo:
            await update.message.reply_text("⏳ Обробка фото...")
            
            photo = update.message.photo[-1]
            file = await photo.get_file()
            file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.jpg'
            await file.download_to_drive(file_path)
            
            text = extract_text_from_photo(file_path, lang='deu')
            
            if not text.strip():
                await update.message.reply_text(
                    "❌ Не вдалося розпізнати текст.\n"
                    "Спробуйте надіслати чіткіше фото."
                )
                return
        
        # Обробка документу (PDF)
        elif update.message.document:
            await update.message.reply_text("⏳ Обробка PDF...")
            
            doc = update.message.document
            file = await doc.get_file()
            file_path = f'uploads/{chat_id}_{datetime.now().strftime("%Y%m%d_%H%M%S")}.pdf'
            await file.download_to_drive(file_path)
            
            try:
                text = load_letter(file_path)
            except Exception as e:
                logger.error(f"PDF помилка: {e}")
                text = extract_text_from_photo(file_path, lang='deu')
        
        # Текстовий лист
        elif update.message.text:
            text = update.message.text
        
        if not text.strip():
            await update.message.reply_text("❌ Не вдалося отримати текст.")
            return
        
        logger.info(f"Core Bot: Текст отримано ({len(text)} символів)")

        # Попередня обробка
        text = preprocess_text(text)

        # NLP аналіз
        await update.message.reply_text("🔍 Аналіз тексту...")
        analysis = analyze_text_advanced(text)
        logger.info(f"Core Bot: Аналіз завершено: {analysis}")

        # Класифікація типу листа
        letter_type, _ = classify_letter_type_advanced(text)
        logger.info(f"Core Bot: Тип листа: {letter_type}")
        
        # Отримання законів
        laws = get_relevant_laws(letter_type, user['country'])
        logger.info(f"Core Bot: Закони отримано: {laws}")
        
        # Генерація відповіді
        await update.message.reply_text("📝 Генерація відповіді...")
        response = generate_response(letter_type, laws, user['language'], user['country'])
        
        # Збереження в БД
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("""
            INSERT INTO letters (chat_id, text, letter_type, analysis, response) 
            VALUES (?, ?, ?, ?, ?)
        """, (chat_id, text[:1000], letter_type, str(analysis), response))
        conn.commit()
        conn.close()
        logger.info(f"Core Bot: Лист збережено в БД")
        
        # Формування результату
        type_names = {
            'debt_collection': '💰 Боргові зобов\'язання',
            'tenancy': '🏠 Оренда житла',
            'employment': '💼 Праця / Jobcenter',
            'administrative': '📋 Адміністративний лист',
            'general': '📄 Загальний лист'
        }
        
        laws_text = ''.join('• ' + law + '\n' for law in laws['laws'])
        result = (
            f"✅ **Аналіз завершено!**\n\n"
            f"📌 **Тип листа:** {type_names.get(letter_type, letter_type)}\n\n"
            f"🔍 **Ключові слова:**\n"
            f"{', '.join(analysis['keywords'][:5]) if analysis['keywords'] else 'Не визначено'}\n\n"
            f"📚 **Релевантні закони:**\n"
            f"{laws_text}\n\n"
            f"⚠️ **Наслідки:**\n{laws['consequences']}\n\n"
            f"━━━━━━━━━━━━━━━━━━━━\n\n"
            f"📝 **Пропонована відповідь:**\n\n{response}"
        )
        
        # Відправка частинами
        for i in range(0, len(result), 4000):
            await update.message.reply_text(
                result[i:i+4000],
                parse_mode='Markdown'
            )
        
        logger.info(f"Core Bot: Аналіз завершено для chat_id={chat_id}")
        
    except Exception as e:
        logger.error(f"Core Bot: Помилка обробки: {e}", exc_info=True)
        await update.message.reply_text(
            f"❌ Помилка обробки: {str(e)}\n\n"
            "Спробуйте ще раз або зверніться до підтримки."
        )

async def analyze_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Команда /analyze для тестування."""
    if len(context.args) < 2:
        await update.message.reply_text(
            "Використання: /analyze <тип> <текст>\n"
            "Типи: debt_collection, tenancy, employment, general"
        )
        return
    
    letter_type = context.args[0]
    text = ' '.join(context.args[1:])
    
    laws = get_relevant_laws(letter_type, 'de')
    response = generate_response(letter_type, laws, 'uk', 'de')
    
    await update.message.reply_text(f"📝 Відповідь:\n\n{response}")

def main():
    """Запуск бота."""
    logger.info("Core Bot: Запуск...")
    
    # Ініціалізація БД
    init_db()
    
    # Створення додатку
    application = Application.builder().token(BOT_TOKEN).build()
    
    # Обробники
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("analyze", analyze_command))
    application.add_handler(MessageHandler(filters.ALL, process_letter))
    
    # Запуск
    logger.info("Core Bot: Polling запущено")
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
