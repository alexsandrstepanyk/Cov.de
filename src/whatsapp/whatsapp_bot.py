#!/usr/bin/env python3
"""
WhatsApp Bot v4.0 для Gov.de - Розумний Аналізатор Юридичних Листів
Повний аналог Telegram бота з підтримкою WhatsApp через Twilio API

Функціонал:
- 📸 OCR розпізнавання (EasyOCR + Tesseract)
- 🌐 Розумний переклад (35+ юридичних термінів)
- ⚖️ Локальна база законів (18 кодексів, 67+ параграфів)
- 📝 Генерація відповідей українською + німецькою
- 📑 Багатосторінкова підтримка
- 🔍 Класифікація документів (5 типів)
- ⚠️ Виявлення шахрайства
"""

import os
import sys
import logging
import sqlite3
import tempfile
import base64
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from flask import Flask, request, jsonify
import requests
from PIL import Image
import pytesseract

# Налаштування логування (ПЕРЕД імпортом модулів)
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    handlers=[
        logging.FileHandler('logs/whatsapp_bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger('whatsapp_bot')

# Додаємо src до path для імпорту модулів
sys.path.insert(0, str(Path(__file__).parent.parent))
sys.path.insert(0, str(Path(__file__).parent.parent.parent / 'bots'))

# Імпорт модулів з Telegram бота
try:
    from advanced_ocr import recognize_image, extract_text_from_photo
    ADVANCED_OCR = True
except ImportError as e:
    ADVANCED_OCR = False
    logger.warning(f"⚠️ Advanced OCR не доступний: {e}")

try:
    from advanced_translator import translate_text
    ADVANCED_TRANSLATOR = True
except ImportError as e:
    ADVANCED_TRANSLATOR = False
    logger.warning(f"⚠️ Advanced Translator не доступний: {e}")

try:
    from legal_database import search_laws
    LEGAL_DATABASE = True
except ImportError as e:
    LEGAL_DATABASE = False
    logger.warning(f"⚠️ Legal Database не доступна: {e}")

try:
    from response_generator import generate_response
    RESPONSE_GENERATOR = True
except ImportError as e:
    RESPONSE_GENERATOR = False
    logger.warning(f"⚠️ Response Generator не доступний: {e}")

try:
    from fraud_detection import detect_fraud
    FRAUD_DETECTION = True
except ImportError as e:
    FRAUD_DETECTION = False
    logger.warning(f"⚠️ Fraud Detection не доступний: {e}")

try:
    from client_bot_functions import check_if_document
    CLIENT_FUNCTIONS = True
except ImportError as e:
    CLIENT_FUNCTIONS = False
    logger.warning(f"⚠️ Client Functions не доступні: {e}")

# ============================================================================
# КОНФІГУРАЦІЯ
# ============================================================================

# Twilio WhatsApp API
TWILIO_ACCOUNT_SID = os.getenv('TWILIO_ACCOUNT_SID', 'your_account_sid')
TWILIO_AUTH_TOKEN = os.getenv('TWILIO_AUTH_TOKEN', 'your_auth_token')
TWILIO_WHATSAPP_NUMBER = os.getenv('TWILIO_WHATSAPP_NUMBER', 'whatsapp:+14155238886')

# Flask вебхук
app = Flask(__name__)

# База даних користувачів
DB_PATH = Path(__file__).parent.parent.parent / 'users.db'

# Меню бота
MAIN_MENU = """
📋 Головне меню:

1️⃣ 📤 Завантажити лист
2️⃣ 📊 Історія листів
3️⃣ ⚙️ Налаштування
4️⃣ ℹ️ Допомога

Напишіть цифру або натисніть кнопку:
"""

SETTINGS_MENU = """
⚙️ Налаштування:

1️⃣ 🇺🇦 Мова: Українська
2️⃣ 🇷🇺 Мова: Русский
3️⃣ 🇩🇪 Мова: Deutsch
4️⃣ 🇬🇧 Мова: English

Напишіть цифру для зміни мови:
"""

HELP_TEXT = """
ℹ️ Допомога - Gov.de WhatsApp Bot v4.0

📸 Як відсканувати лист:
1. Надішліть фото юридичного листа
2. Бот розпізнає текст (OCR)
3. Перекладе українською
4. Знайде параграфи законів
5. Згенерує відповідь

📑 Багатосторінкові документи:
- Надішліть перше фото
- Бот запитає чи є ще сторінки
- Надішліть наступні фото
- Отримайте об'єднаний аналіз

⚠️ Увага:
- Бот не замінює адвоката
- Завжди перевіряйте відповіді
- Зберігайте копії листів

📞 Корисні контакти:
• Telefonseelsorge: 0800 111 0 111
• Beratungshilfe: Безкоштовна консультація
"""

# ============================================================================
# БАЗА ДАНИХ КОРИСТУВАЧІВ
# ============================================================================

def init_database():
    """Ініціалізація бази даних користувачів."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_id TEXT UNIQUE NOT NULL,
            phone_number TEXT,
            name TEXT,
            language TEXT DEFAULT 'uk',
            registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS letters (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            document_type TEXT,
            organization TEXT,
            paragraphs TEXT,
            translation TEXT,
            response TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users (id)
        )
    ''')
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS multi_page_sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            whatsapp_id TEXT NOT NULL,
            pages TEXT,
            current_page INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (whatsapp_id) REFERENCES users (whatsapp_id)
        )
    ''')
    
    conn.commit()
    conn.close()
    logger.info("✅ База даних ініціалізована")


def get_or_create_user(whatsapp_id: str, phone_number: str = None) -> Dict:
    """Отримати або створити користувача."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM users WHERE whatsapp_id = ?',
        (whatsapp_id,)
    )
    user = cursor.fetchone()
    
    if not user:
        cursor.execute(
            'INSERT INTO users (whatsapp_id, phone_number) VALUES (?, ?)',
            (whatsapp_id, phone_number)
        )
        conn.commit()
        cursor.execute(
            'SELECT * FROM users WHERE whatsapp_id = ?',
            (whatsapp_id,)
        )
        user = cursor.fetchone()
        logger.info(f"✅ Новий користувач: {whatsapp_id}")
    else:
        cursor.execute(
            'UPDATE users SET last_active = ? WHERE whatsapp_id = ?',
            (datetime.now(), whatsapp_id)
        )
        conn.commit()
    
    conn.close()
    return dict(user) if user else None


def save_letter(user_id: int, document_type: str, organization: str, 
                paragraphs: str, translation: str, response: str):
    """Зберегти лист в історію."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO letters (user_id, document_type, organization, paragraphs, translation, response)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (user_id, document_type, organization, paragraphs, translation, response))
    
    conn.commit()
    conn.close()
    logger.info(f"✅ Лист збережено для користувача {user_id}")


def get_user_letters(user_id: int, limit: int = 5) -> List[Dict]:
    """Отримати останні листи користувача."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM letters WHERE user_id = ? ORDER BY created_at DESC LIMIT ?',
        (user_id, limit)
    )
    letters = [dict(row) for row in cursor.fetchall()]
    
    conn.close()
    return letters


def get_multi_page_session(whatsapp_id: str) -> Optional[Dict]:
    """Отримати активну сесію багатосторінкового документу."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    
    cursor.execute(
        'SELECT * FROM multi_page_sessions WHERE whatsapp_id = ? ORDER BY created_at DESC LIMIT 1',
        (whatsapp_id,)
    )
    session = cursor.fetchone()
    
    conn.close()
    return dict(session) if session else None


def create_multi_page_session(whatsapp_id: str, page_data: str) -> int:
    """Створити нову сесію багатосторінкового документу."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO multi_page_sessions (whatsapp_id, pages, current_page)
        VALUES (?, ?, 1)
    ''', (whatsapp_id, page_data))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id


def update_multi_page_session(session_id: int, pages: str, current_page: int):
    """Оновити сесію багатосторінкового документу."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        UPDATE multi_page_sessions
        SET pages = ?, current_page = ?
        WHERE id = ?
    ''', (pages, current_page, session_id))
    
    conn.commit()
    conn.close()


def delete_multi_page_session(session_id: int):
    """Видалити сесію багатосторінкового документу."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute(
        'DELETE FROM multi_page_sessions WHERE id = ?',
        (session_id,)
    )
    
    conn.commit()
    conn.close()

# ============================================================================
# TWILIO WHATSAPP API
# ============================================================================

def send_whatsapp_message(to_number: str, message: str, media_url: str = None) -> bool:
    """
    Надіслати повідомлення через Twilio WhatsApp API.
    
    Args:
        to_number: Номер отримувача (whatsapp:+XXXXXXXXXXX)
        message: Текст повідомлення
        media_url: URL медіа (опціонально)
    
    Returns:
        bool: True якщо успішно
    """
    from twilio.rest import Client
    
    try:
        client = Client(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)
        
        message_params = {
            'from_': TWILIO_WHATSAPP_NUMBER,
            'to': to_number,
            'body': message
        }
        
        if media_url:
            message_params['media_url'] = media_url
        
        message = client.messages.create(**message_params)
        logger.info(f"✅ Повідомлення надіслано: {message.sid}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Помилка відправки повідомлення: {e}")
        return False


def download_media(media_url: str, auth_token: str) -> bytes:
    """
    Завантажити медіа файл з Twilio.
    
    Args:
        media_url: URL медіа файлу
        auth_token: Twilio auth token
    
    Returns:
        bytes: Бінарні дані файлу
    """
    headers = {
        'Authorization': f'Basic {base64.b64encode(f"{TWILIO_ACCOUNT_SID}:{auth_token}".encode()).decode()}'
    }
    
    response = requests.get(media_url, headers=headers)
    response.raise_for_status()
    
    return response.content

# ============================================================================
# ОБРОБКА ПОВІДОМЛЕНЬ
# ============================================================================

def process_text_message(whatsapp_id: str, message_text: str) -> str:
    """
    Обробка текстового повідомлення.
    
    Args:
        whatsapp_id: WhatsApp ID користувача
        message_text: Текст повідомлення
    
    Returns:
        str: Відповідь бота
    """
    user = get_or_create_user(whatsapp_id)
    
    # Перевірка активної сесії багатосторінкового документу
    session = get_multi_page_session(whatsapp_id)
    
    if session:
        # Користувач в режимі багатосторінкового документу
        if message_text.strip().lower() in ['✅ все, аналізуй', 'все аналізуй', 'аналізуй', 'готово']:
            return analyze_multi_page_document(whatsapp_id, session)
        elif message_text.strip().isdigit():
            # Це може бути номер сторінки або вибір меню
            return handle_menu_selection(whatsapp_id, message_text, user, session)
        else:
            return "📑 Будь ласка, надішліть наступну сторінку або натисніть '✅ Все, аналізуй'"
    
    # Звичайне меню
    if message_text.strip().isdigit():
        return handle_menu_selection(whatsapp_id, message_text, user, None)
    elif message_text.strip().lower() in ['/start', 'старт', 'почати']:
        return handle_start_command(user)
    else:
        return handle_unknown_command(user)


def handle_start_command(user: Dict) -> str:
    """Обробка команди /start."""
    return f"""
👋 Вітаємо, {user.get('name', 'Користувач')}!

🇩🇪 Gov.de WhatsApp Bot v4.0 - Розумний Аналізатор Юридичних Листів

{MAIN_MENU}
"""


def handle_unknown_command(user: Dict) -> str:
    """Обробка невідомої команди."""
    return f"""
⚠️ Я не зрозумів команду.

Будь ласка, використайте меню:
{MAIN_MENU}
"""


def handle_menu_selection(whatsapp_id: str, selection: str, user: Dict, session: Optional[Dict]) -> str:
    """Обробка вибору меню."""
    selection = selection.strip()
    
    if selection == '1':
        if session:
            return "📑 Ви вже в режимі багатосторінкового документу. Надішліть фото або натисніть '✅ Все, аналізуй'"
        return "📤 Будь ласка, надішліть фото юридичного листа"
    
    elif selection == '2':
        return show_letter_history(user)
    
    elif selection == '3':
        return SETTINGS_MENU
    
    elif selection == '4':
        return HELP_TEXT
    
    else:
        return handle_unknown_command(user)


def show_letter_history(user: Dict) -> str:
    """Показати історію листів."""
    letters = get_user_letters(user['id'], limit=5)
    
    if not letters:
        return "📊 У вас ще немає збережених листів."
    
    history = "📊 Ваша історія листів:\n\n"
    
    for i, letter in enumerate(letters, 1):
        created_at = letter.get('created_at', 'Невідомо')[:16]
        doc_type = letter.get('document_type', 'Невідомо')
        org = letter.get('organization', 'Невідомо')
        
        history += f"{i}. {created_at} - {doc_type} ({org})\n"
    
    history += "\nНадішліть новий лист для аналізу."
    
    return history

# ============================================================================
# ОБРОБКА ЗОБРАЖЕНЬ
# ============================================================================

def process_image_message(whatsapp_id: str, image_data: bytes) -> str:
    """
    Обробка зображення.
    
    Args:
        whatsapp_id: WhatsApp ID користувача
        image_data: Бінарні дані зображення
    
    Returns:
        str: Відповідь бота
    """
    user = get_or_create_user(whatsapp_id)
    
    # Перевірка активної сесії
    session = get_multi_page_session(whatsapp_id)
    
    try:
        # Збереження тимчасового файлу
        with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp_file:
            tmp_file.write(image_data)
            tmp_path = tmp_file.name
        
        # OCR розпізнавання
        if ADVANCED_OCR:
            ocr_result = recognize_image(tmp_path, lang='deu+eng')
            text = ocr_result.get('text', '')
            confidence = ocr_result.get('confidence', 0)
        else:
            # Fallback до простого pytesseract
            image = Image.open(tmp_path)
            text = pytesseract.image_to_string(image, lang='deu+eng')
            confidence = 0
        
        logger.info(f"📸 OCR завершено: {len(text)} символів, впевненість: {confidence}%")
        
        # Видалення тимчасового файлу
        os.unlink(tmp_path)
        
        if not text.strip():
            return "⚠️ Не вдалося розпізнати текст. Будь ласка, надішліть якісніше фото."
        
        # Перевірка на багатосторінковий документ
        if session:
            # Додавання сторінки до сесії
            pages = eval(session['pages']) if session['pages'] else []
            pages.append({'text': text, 'confidence': confidence, 'path': tmp_path})
            
            update_multi_page_session(session['id'], str(pages), len(pages))
            
            return f"""
✅ Сторінка {len(pages)} оброблена ({len(text)} символів)

📑 Чи є ще сторінки?

Надішліть наступне фото або напишіть:
✅ Все, аналізуй
"""
        else:
            # Односторінковий документ
            return analyze_single_page_document(whatsapp_id, user, text, confidence)
    
    except Exception as e:
        logger.error(f"❌ Помилка обробки зображення: {e}")
        return "⚠️ Помилка обробки фото. Будь ласка, спробуйте ще раз."


def analyze_single_page_document(whatsapp_id: str, user: Dict, text: str, confidence: float) -> str:
    """
    Аналіз односторінкового документу.
    
    Args:
        whatsapp_id: WhatsApp ID користувача
        user: Дані користувача
        text: Розпізнаний текст
        confidence: Впевненість OCR
    
    Returns:
        str: Результат аналізу
    """
    result = []
    
    # Класифікація документу
    if CLIENT_FUNCTIONS:
        doc_info = check_if_document(text)
        doc_type = doc_info.get('type', 'unknown')
        
        if doc_type == 'fraud':
            result.append("⚠️ УВАГА: Можливе шахрайство!")
            result.append("")
            fraud_indicators = doc_info.get('fraud_indicators', [])
            for indicator in fraud_indicators:
                result.append(f"• {indicator}")
            result.append("")
            result.append("Будь ласка, зверніться до юриста для перевірки.")
            return "\n".join(result)
        
        elif doc_type not in ['legal', 'official']:
            result.append(f"⚠️ УВАГА: Це не юридичний лист!")
            result.append("")
            result.append(f"📄 Тип документу: {doc_info.get('type_name', 'Невідомо')}")
            result.append("")
            result.append("Цей бот призначений для аналізу юридичних листів від:")
            result.append("• Jobcenter")
            result.append("• Орендодавця")
            result.append("• Кредиторів (Inkasso)")
            result.append("• Державних установ")
            return "\n".join(result)
    
    # Переклад тексту
    result.append("⏳ Переклад тексту...")
    full_response = "\n".join(result)

    if ADVANCED_TRANSLATOR:
        translation = translate_text(text, src='de', dest='uk')
    else:
        translation = "⚠️ Переклад тимчасово недоступний"
    
    # Аналіз закону
    if LEGAL_DATABASE:
        laws = search_laws(text)
        paragraphs = ", ".join([f"{law['code']} {law['paragraph']}" for law in laws[:5]])
    else:
        paragraphs = "Невідомо"
    
    # Генерація відповіді
    if RESPONSE_GENERATOR:
        response = generate_response(text, translation, laws if LEGAL_DATABASE else [])
    else:
        response = "⚠️ Генерація відповіді тимчасово недоступна"
    
    # Формування фінального повідомлення
    final_result = []
    final_result.append("✅ Аналіз завершено!")
    final_result.append("")
    final_result.append(f"📌 Тип листа: {doc_info.get('type_name', 'Невідомо')}")
    final_result.append(f"🏢 Організація: {doc_info.get('organization', 'Невідомо')}")
    final_result.append(f"📚 ПАРАГРАФИ: {paragraphs}")
    final_result.append("")
    final_result.append("🌐 Переклад листа (українська):")
    final_result.append(translation)
    final_result.append("")
    final_result.append("📝 ВІДПОВІДЬ:")
    final_result.append(response)
    final_result.append("")
    final_result.append("📑 Чи є ще сторінки?")
    final_result.append("")
    final_result.append("Надішліть наступне фото або напишіть:")
    final_result.append("✅ Все, аналізуй")
    
    # Створення сесії для можливого багатосторінкового документу
    create_multi_page_session(whatsapp_id, str([{'text': text, 'confidence': confidence}]))
    
    # Збереження в історію
    save_letter(
        user['id'],
        doc_info.get('type_name', 'unknown'),
        doc_info.get('organization', 'unknown'),
        paragraphs,
        translation,
        response
    )
    
    return "\n".join(final_result)


def analyze_multi_page_document(whatsapp_id: str, session: Dict) -> str:
    """
    Аналіз багатосторінкового документу.
    
    Args:
        whatsapp_id: WhatsApp ID користувача
        session: Дані сесії
    
    Returns:
        str: Результат аналізу
    """
    user = get_or_create_user(whatsapp_id)
    pages = eval(session['pages'])
    
    result = []
    all_text = "\n\n".join([page['text'] for page in pages])
    
    result.append(f"📑 Об'єднано {len(pages)} сторінок ({len(all_text)} символів)")
    result.append("")
    
    # Класифікація
    if CLIENT_FUNCTIONS:
        doc_info = check_if_document(all_text)
        doc_type = doc_info.get('type', 'unknown')
        
        if doc_type == 'fraud':
            result.append("⚠️ УВАГА: Можливе шафрайство!")
            fraud_indicators = doc_info.get('fraud_indicators', [])
            for indicator in fraud_indicators:
                result.append(f"• {indicator}")
            delete_multi_page_session(session['id'])
            return "\n".join(result)
        
        elif doc_type not in ['legal', 'official']:
            result.append(f"⚠️ УВАГА: Це не юридичний лист!")
            result.append(f"📄 Тип документу: {doc_info.get('type_name', 'Невідомо')}")
            delete_multi_page_session(session['id'])
            return "\n".join(result)
    
    # Переклад
    result.append("⏳ Переклад...")
    if ADVANCED_TRANSLATOR:
        translation = translate_text(all_text, src='de', dest='uk')
    else:
        translation = "⚠️ Переклад тимчасово недоступний"
    
    # Аналіз закону
    if LEGAL_DATABASE:
        laws = search_laws(all_text)
        paragraphs = ", ".join([f"{law['code']} {law['paragraph']}" for law in laws[:5]])
    else:
        paragraphs = "Невідомо"
    
    # Генерація відповіді
    if RESPONSE_GENERATOR:
        response = generate_response(all_text, translation, laws if LEGAL_DATABASE else [])
    else:
        response = "⚠️ Генерація відповіді тимчасово недоступна"
    
    # Формування фінального повідомлення
    final_result = []
    final_result.append("✅ Аналіз завершено!")
    final_result.append("")
    final_result.append(f"📑 Сторінок: {len(pages)}")
    final_result.append(f"📌 Тип листа: {doc_info.get('type_name', 'Невідомо')}")
    final_result.append(f"🏢 Організація: {doc_info.get('organization', 'Невідомо')}")
    final_result.append(f"📚 ПАРАГРАФИ: {paragraphs}")
    final_result.append("")
    final_result.append("🌐 Переклад листа (українська):")
    final_result.append(translation)
    final_result.append("")
    final_result.append("📝 ВІДПОВІДЬ:")
    final_result.append(response)
    
    # Збереження в історію
    save_letter(
        user['id'],
        doc_info.get('type_name', 'unknown'),
        doc_info.get('organization', 'unknown'),
        paragraphs,
        translation,
        response
    )
    
    # Видалення сесії
    delete_multi_page_session(session['id'])
    
    return "\n".join(final_result)

# ============================================================================
# WEBHOOK ROUTES
# ============================================================================

@app.route('/webhook', methods=['GET'])
def verify_webhook():
    """Перевірка вебхука від Twilio."""
    mode = request.args.get('hub.mode')
    token = request.args.get('hub.verify_token')
    challenge = request.args.get('hub.challenge')
    
    if mode == 'subscribe' and token == os.getenv('WEBHOOK_VERIFY_TOKEN', 'gov_de_2026'):
        logger.info("✅ Вебхук перевірено")
        return challenge, 200
    
    return "Forbidden", 403


@app.route('/whatsapp', methods=['POST'])
def handle_whatsapp_message():
    """
    Обробка вхідних повідомлень WhatsApp.
    
    Формат Twilio:
    {
        'AccountSid': 'ACxxxx',
        'ApiVersion': '2010-04-01',
        'Body': 'Привіт',
        'From': 'whatsapp:+49123456789',
        'To': 'whatsapp:+14155238886',
        'MediaUrl0': 'https://api.twilio.com/...',
        'MediaType0': 'image/jpeg',
        ...
    }
    """
    try:
        data = request.form
        logger.info(f"📨 Вхідне повідомлення: {data.get('Body', 'media')}")
        
        whatsapp_id = data.get('From', '')
        from_number = whatsapp_id.replace('whatsapp:', '')
        
        # Отримати або створити користувача
        user = get_or_create_user(whatsapp_id, from_number)
        
        # Перевірка на медіа
        media_url = data.get('MediaUrl0')
        
        if media_url:
            # Завантаження медіа
            media_content = download_media(media_url, TWILIO_AUTH_TOKEN)
            response_text = process_image_message(whatsapp_id, media_content)
        else:
            # Текстове повідомлення
            message_text = data.get('Body', '')
            response_text = process_text_message(whatsapp_id, message_text)
        
        # Відправка відповіді
        if response_text:
            # Розділення довгих повідомлень
            max_length = 1600
            chunks = [response_text[i:i+max_length] for i in range(0, len(response_text), max_length)]
            
            for chunk in chunks:
                send_whatsapp_message(whatsapp_id, chunk)
        
        return "OK", 200
    
    except Exception as e:
        logger.error(f"❌ Помилка обробки повідомлення: {e}")
        return "Error", 500


@app.route('/health', methods=['GET'])
def health_check():
    """Перевірка здоров'я бота."""
    return jsonify({
        'status': 'healthy',
        'version': '4.0',
        'modules': {
            'ocr': ADVANCED_OCR,
            'translator': ADVANCED_TRANSLATOR,
            'legal_db': LEGAL_DATABASE,
            'response_gen': RESPONSE_GENERATOR,
            'fraud_detect': FRAUD_DETECTION
        }
    }), 200

# ============================================================================
# ЗАПУСК
# ============================================================================

if __name__ == '__main__':
    logger.info("🚀 WhatsApp Bot v4.0 запускається...")
    
    # Ініціалізація бази даних
    init_database()

    # Запуск Flask сервера на порту 5001 (5000 зайнято AirPlay)
    app.run(
        host='0.0.0.0',
        port=5001,
        debug=os.getenv('FLASK_DEBUG', 'False').lower() == 'true'
    )
