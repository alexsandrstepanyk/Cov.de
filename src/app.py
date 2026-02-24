"""
Telegram Bot for Gov.de Legal Analyzer
Bot client with core logic and country knowledge bases.
"""

import os
from pathlib import Path
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
import pytesseract
from PIL import Image
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from .ingestion import preprocess_text
from .nlp_analysis import analyze_text, classify_letter_type
from .legal_db import get_relevant_laws
from .response_generator import generate_response
from googletrans import Translator

# States for conversation
REGISTER_USERNAME, REGISTER_PASSWORD, REGISTER_LANGUAGE, REGISTER_COUNTRY, REGISTER_STATUS = range(5)
UPLOAD_LETTER = 6

translator = Translator()

# Database setup
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS users
                 (id INTEGER PRIMARY KEY, chat_id INTEGER UNIQUE, username TEXT, password TEXT, language TEXT, country TEXT, status TEXT)''')
    c.execute('''CREATE TABLE IF NOT EXISTS letters
                 (id INTEGER PRIMARY KEY, chat_id INTEGER, text TEXT, analysis TEXT, response TEXT, lawyer_review TEXT, timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_db()

# Ensure upload folder
Path('uploads').mkdir(exist_ok=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    keyboard = [['Реєстрація'], ['Завантажити лист']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Вітаємо! Оберіть дію:', reply_markup=reply_markup)
    return ConversationHandler.END

async def register_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text('Введіть username:')
    return REGISTER_USERNAME

async def register_username(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['username'] = update.message.text
    await update.message.reply_text('Введіть пароль:')
    return REGISTER_PASSWORD

async def register_password(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['password'] = generate_password_hash(update.message.text)
    keyboard = [['Українська'], ['Deutsch']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Оберіть мову:', reply_markup=reply_markup)
    return REGISTER_LANGUAGE

async def register_language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['language'] = 'uk' if update.message.text == 'Українська' else 'de'
    keyboard = [['Німеччина']]  # Add more countries
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Оберіть країну:', reply_markup=reply_markup)
    return REGISTER_COUNTRY

async def register_country(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['country'] = 'de' if update.message.text == 'Німеччина' else 'de'
    keyboard = [['Резидент'], ['Громадянин']]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
    await update.message.reply_text('Оберіть статус:', reply_markup=reply_markup)
    return REGISTER_STATUS

async def register_status(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    context.user_data['status'] = 'resident' if update.message.text == 'Резидент' else 'citizen'
    chat_id = update.effective_chat.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    try:
        c.execute("INSERT INTO users (chat_id, username, password, language, country, status) VALUES (?, ?, ?, ?, ?, ?)", 
                 (chat_id, context.user_data['username'], context.user_data['password'], context.user_data['language'], context.user_data['country'], context.user_data['status']))
        conn.commit()
        await update.message.reply_text('Реєстрація успішна!')
    except sqlite3.IntegrityError:
        await update.message.reply_text('Користувач вже існує.')
    finally:
        conn.close()
    return ConversationHandler.END

async def upload_start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE chat_id=?", (chat_id,))
    user = c.fetchone()
    conn.close()
    if not user:
        await update.message.reply_text('Спочатку зареєструйтесь.')
        return ConversationHandler.END
    await update.message.reply_text('Надішліть фото листа або текст:')
    return UPLOAD_LETTER

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    chat_id = update.effective_chat.id
    if update.message.photo:
        # Download photo
        photo = update.message.photo[-1]
        file = await photo.get_file()
        file_path = f'uploads/{chat_id}_{photo.file_id}.jpg'
        await file.download_to_drive(file_path)
        # OCR
        img = Image.open(file_path)
        text = pytesseract.image_to_string(img, lang='deu')
    elif update.message.text:
        text = update.message.text
    else:
        await update.message.reply_text('Надішліть фото або текст.')
        return UPLOAD_LETTER
    
    text = preprocess_text(text)
    
    # Get user
    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT language, country, status FROM users WHERE chat_id=?", (chat_id,))
    user_data = c.fetchone()
    user_lang, country, status = user_data
    
    # Analyze (simulate core calling country bot)
    analysis = analyze_text(text)
    letter_type = classify_letter_type(text)
    laws = get_relevant_laws(letter_type, country)
    
    explanation = f"Попередній аналіз: Лист стосується: {letter_type}. Статус: {status}. Можливі наслідки: {laws['consequences']}. Для точнішого зверніться до адвоката."
    if user_lang != 'uk':
        explanation = translator.translate(explanation, dest=user_lang).text
    
    response = generate_response(letter_type, laws, user_lang, country)
    
    # Store
    c.execute("INSERT INTO letters (chat_id, text, analysis, response) VALUES (?, ?, ?, ?)", 
             (chat_id, text, str(analysis), response))
    conn.commit()
    conn.close()
    
    await update.message.reply_text(f"Аналіз: {explanation}\n\nПропонована відповідь:\n{response}")
    return ConversationHandler.END

def main():
    application = Application.builder().token("YOUR_BOT_TOKEN").build()  # Replace with actual token
    
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), MessageHandler(filters.Regex("^Реєстрація$"), register_start), MessageHandler(filters.Regex("^Завантажити лист$"), upload_start)],
        states={
            REGISTER_USERNAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_username)],
            REGISTER_PASSWORD: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_password)],
            REGISTER_LANGUAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_language)],
            REGISTER_COUNTRY: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_country)],
            REGISTER_STATUS: [MessageHandler(filters.TEXT & ~filters.COMMAND, register_status)],
            UPLOAD_LETTER: [MessageHandler(filters.PHOTO | filters.TEXT & ~filters.COMMAND, handle_upload)],
        },
        fallbacks=[],
    )
    
    application.add_handler(conv_handler)
    application.run_polling()

if __name__ == '__main__':
    main()