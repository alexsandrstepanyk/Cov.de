# 🇩🇪 Gov.de WhatsApp Bot v4.0 - Повний Гід по Встановленню

**Версія:** 1.0  
**Дата:** 2026-03-06  
**Статус:** ✅ ГОТОВО ДО ЗАПУСКУ

---

## 📋 Зміст

1. [Огляд](#огляд)
2. [Що ми створили](#що-ми-створили)
3. [Автоматичне встановлення](#автоматичне-встановлення)
4. [Ручне встановлення](#ручне-встановлення)
5. [Налаштування Twilio](#налаштування-twilio)
6. [Запуск бота](#запуск-бота)
7. [Тестування](#тестування)
8. [Вирішення проблем](#вирішення-проблем)
9. [Зміни в проекті](#зміни-в-проекті)

---

## 🎯 Огляд

Цей документ описує процес встановлення та запуску **WhatsApp Bot v4.0** - повного аналога Telegram бота Gov.de для WhatsApp.

### Що робить цей бот:

- 📸 **OCR розпізнавання** - розпізнає текст з фото документів
- 🌐 **Переклад** - перекладає німецькі юридичні листи українською
- ⚖️ **База законів** - знаходить параграфи законів (18 кодексів, 67+ параграфів)
- 📝 **Генерація відповідей** - створює готові відповіді українською + німецькою
- 📑 **Багатосторінковість** - підтримує документи з кількох сторінок
- 🔍 **Класифікація** - визначає тип документу (5 типів)
- ⚠️ **Анти-шахрайство** - виявляє підозрілі листи

---

## 📦 Що ми створили

### Нові файли:

```
Gov.de/
├── setup_whatsapp_bot.sh        # ⭐ Скрипт автоматичного встановлення
├── run_whatsapp_bot.sh          # ⭐ Скрипт запуску бота
├── test_whatsapp_bot.py         # ⭐ Тести для WhatsApp бота
├── check_status.py              # ⭐ Перевірка готовності
├── .env                         # ⭐ Змінні оточення (з вашими ключами)
│
├── src/whatsapp/
│   ├── whatsapp_bot.py          # ⭐ Головний код бота (1100+ рядків)
│   ├── README_WHATSAPP.md       # 📚 Інструкція з API
│   └── .env.example             # 📝 Шаблон змінних оточення
│
├── docs/
│   └── WHATSAPP_SETUP.md        # 📖 Цей файл
│
└── CHANGELOG_WHATSAPP.md        # 📝 Історія змін
```

### Інтегровані модулі (з Telegram бота):

- ✅ `advanced_ocr.py` - Розпізнавання тексту
- ✅ `advanced_translator.py` - Переклад з юридичним словником
- ✅ `legal_database.py` - База німецьких законів
- ✅ `response_generator.py` - Генерація відповідей
- ✅ `fraud_detection.py` - Виявлення шахрайства
- ✅ `client_bot_functions.py` - Класифікація документів

---

## 🚀 Автоматичне Встановлення

### Швидка команда:

```bash
cd /Users/alex/Desktop/project/Gov.de
chmod +x setup_whatsapp_bot.sh
bash setup_whatsapp_bot.sh
```

### Що робить скрипт:

| Крок | Дія | Результат |
|------|-----|-----------|
| 1 | Перевірка системи | macOS/Linux, Python, pip |
| 2 | Встановлення Tesseract | OCR для розпізнавання тексту |
| 3 | Встановлення Ngrok | Тунель для вебхука |
| 4 | Встановлення Python пакетів | twilio, flask, python-dotenv |
| 5 | Створення .env | Змінні оточення з вашими ключами |
| 6 | Створення директорій | logs/, uploads/, data/ |
| 7 | Ініціалізація бази даних | users.db з таблицями |
| 8 | Перевірка коду | Компіляція whatsapp_bot.py |
| 9 | Фінальна перевірка | check_status.py |

### Після виконання:

Скрипт покаже:
```
✅ ВСЕ ГОТОВО! Можна запускати бота.
```

---

## 🛠️ Ручне Встановлення

Якщо автоматичне встановлення не працює, виконайте кроки вручну:

### Крок 1: Встановлення Tesseract

**macOS:**
```bash
brew install tesseract
brew install tesseract-lang  # Мовні пакети
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get update
sudo apt-get install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

**Перевірка:**
```bash
tesseract --version
tesseract --list-langs  # Повинні бути deu, eng
```

### Крок 2: Встановлення Ngrok

**macOS:**
```bash
brew install ngrok
```

**Linux:**
```bash
wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
sudo tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
```

**Реєстрація:**
1. Зайдіть на [ngrok.com](https://ngrok.com)
2. Зареєструйтесь (безкоштовно)
3. Отримайте токен: `ngrok config add-authtoken YOUR_TOKEN`

### Крок 3: Встановлення Python пакетів

```bash
cd /Users/alex/Desktop/project/Gov.de

# Створення віртуального оточення (рекомендується)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux

# Встановлення залежностей
pip install --upgrade pip
pip install twilio flask python-dotenv
pip install -r requirements.txt
```

### Крок 4: Налаштування .env

Файл `.env` вже створено з вашими ключами:

```env
TWILIO_ACCOUNT_SID=Q4V1TE5HBN7YRF69FVV3EQJ3
TWILIO_AUTH_TOKEN=db5d8ee1e990413876541cd045499e72
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

**Перевірка:**
```bash
cat .env
```

### Крок 5: Ініціалізація бази даних

```bash
python3 << 'EOF'
import sqlite3

conn = sqlite3.connect('users.db')
cursor = conn.cursor()

cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        whatsapp_id TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        name TEXT,
        language TEXT DEFAULT 'uk',
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
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
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

cursor.execute('''
    CREATE TABLE IF NOT EXISTS multi_page_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        whatsapp_id TEXT NOT NULL,
        pages TEXT,
        current_page INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

conn.commit()
conn.close()
print("✅ База даних ініціалізовано")
EOF
```

### Крок 6: Перевірка готовності

```bash
python3 check_status.py
```

**Очікуваний результат:**
```
✅ Twilio: версія
✅ Flask: версія
✅ Tesseract: доступний
✅ База даних: існує
✅ Код бота: існує
✅ .env файл: існує

РЕЗУЛЬТАТ: 6/6 перевірок пройдено
✅ ВСЕ ГОТОВО!
```

---

## 📱 Налаштування Twilio

### Крок 1: Реєстрація

1. Зайдіть на [Twilio.com](https://www.twilio.com/try-twilio)
2. Натисніть "Sign Up"
3. Введіть email та телефон
4. Підтвердіть email (код прийде на пошту)
5. Підтвердіть телефон (код прийде в SMS)

### Крок 2: Отримання облікових даних

1. Увійдіть в [Twilio Console](https://console.twilio.com/)
2. На головній сторінці знайдіть:
   - **Account SID**: `Q4V1TE5HBN7YRF69FVV3EQJ3` (вже є в .env)
   - **Auth Token**: Натисніть "Show" та скопіюйте (вже є в .env)

### Крок 3: Активація WhatsApp Sandbox

1. Зайдіть в **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Натисніть **Join Beta** (якщо потрібно)
3. Побачите інструкцію:
   ```
   Send a WhatsApp message to:
   whatsapp:+14155238886
   
   Your code: XXX-XXX
   ```
4. Відкрийте WhatsApp на телефоні
5. Надішліть код на номер `+14155238886`
6. Отримаєте підтвердження: "Twilio: Your sandbox access code has been confirmed!"

### Крок 4: Налаштування вебхука

**Після запуску бота та ngrok:**

1. Запустіть ngrok (див. нижче)
2. Скопіюйте URL (наприклад, `https://abc123.ngrok.io`)
3. В Twilio Console:
   - **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
   - Вставте URL у поле **"WHEN A MESSAGE COMES IN"**:
     ```
     https://abc123.ngrok.io/whatsapp
     ```
   - Натисніть **Save**

---

## ▶️ Запуск Бота

### Термінал 1: Запуск бота

```bash
cd /Users/alex/Desktop/project/Gov.de

# Активація віртуального оточення (якщо створено)
source venv/bin/activate

# Запуск
python3 src/whatsapp/whatsapp_bot.py
```

**Очікуваний вивід:**
```
2026-03-06 10:00:00 - whatsapp_bot - INFO - 🚀 WhatsApp Bot v4.0 запускається...
2026-03-06 10:00:00 - whatsapp_bot - INFO - ✅ База даних ініціалізована
 * Running on http://0.0.0.0:5000
 * Running on http://127.0.0.1:5000
```

### Термінал 2: Запуск ngrok

```bash
ngrok http 5000
```

**Очікуваний вивід:**
```
Session Status                online
Account                       Your Name
Version                       3.x.x
Region                        Europe (Frankfurt)
Forwarding                    https://abc123.ngrok.io -> http://localhost:5000
```

**Скопіюйте Forwarding URL** для налаштування вебхука в Twilio.

### Термінал 3: Моніторинг логів

```bash
tail -f logs/whatsapp_bot.log
```

---

## 🧪 Тестування

### Тест 1: Перевірка здоров'я бота

```bash
curl http://localhost:5000/health
```

**Очікувана відповідь:**
```json
{
  "status": "healthy",
  "version": "4.0",
  "modules": {
    "ocr": true,
    "translator": true,
    "legal_db": true,
    "response_gen": true,
    "fraud_detect": true
  }
}
```

### Тест 2: Перевірка вебхука

```bash
curl "http://localhost:5000/webhook?hub.mode=subscribe&hub.verify_token=gov_de_2026&hub.challenge=test"
```

**Очікувана відповідь:**
```
test
```

### Тест 3: WhatsApp Sandbox

1. Відкрийте WhatsApp
2. Знайдіть контакт з номером Sandbox
3. Надішліть: `/start`
4. Очікуйте відповідь:
   ```
   👋 Вітаємо, Користувач!
   
   🇩🇪 Gov.de WhatsApp Bot v4.0 - Розумний Аналізатор Юридичних Листів
   
   📋 Головне меню:
   
   1️⃣ 📤 Завантажити лист
   2️⃣ 📊 Історія листів
   3️⃣ ⚙️ Налаштування
   4️⃣ ℹ️ Допомога
   ```

### Тест 4: Аналіз документу

1. Надішліть `1` в WhatsApp
2. Зробіть фото німецького листа (Jobcenter, Finanzamt, тощо)
3. Надішліть фото в WhatsApp
4. Очікуйте:
   ```
   ✅ Аналіз завершено!
   
   📌 Тип листа: 💼 Праця / Jobcenter
   🏢 Організація: Jobcenter
   📚 ПАРАГРАФИ: § 59 SGB II, § 309 SGB III
   
   🌐 Переклад листа (українська):
   [Переклад]
   
   📝 ВІДПОВІДЬ:
   [Готова відповідь]
   ```

### Тест 5: Автоматичні тести

```bash
python3 test_whatsapp_bot.py
```

---

## 🔧 Вирішення Проблем

### Бот не запускається

**Проблема:**
```
ModuleNotFoundError: No module named 'twilio'
```

**Рішення:**
```bash
source venv/bin/activate  # Активація віртуального оточення
pip install twilio flask python-dotenv
```

### Вебхук не працює

**Проблема:** Twilio не може підключитися до вебхука

**Рішення:**
1. Перевірте що ngrok запущено
2. Скопіюйте новий URL (ngrok змінює URL при кожному запуску)
3. Оновіть вебхук в Twilio Console
4. Перевірте:
   ```bash
   curl https://your-ngrok-url.ngrok.io/health
   ```

### Tesseract не розпізнає німецьку

**Проблема:**
```
tesseract --list-langs  # немає deu
```

**Рішення:**
```bash
# macOS
brew install tesseract-lang

# Linux
sudo apt-get install tesseract-ocr-deu
```

### Повідомлення не відправляються

**Проблема:** WhatsApp не отримує відповіді

**Рішення:**
1. Перевірте баланс Twilio Console
2. Переконайтесь що Sandbox активований
3. Перевірте логи:
   ```bash
   tail -f logs/whatsapp_bot.log
   ```
4. Перевірте Twilio Message Logs в Console

### Помилка "Invalid Account SID"

**Проблема:** Неправильні облікові дані

**Рішення:**
1. Перевірте `.env`:
   ```bash
   cat .env
   ```
2. Перевірте в Twilio Console:
   - Account SID: `Q4V1TE5HBN7YRF69FVV3EQJ3`
   - Auth Token: оновіть якщо змінився
3. Перезапустіть бота

### Багатосторінковий документ не працює

**Проблема:** Бот не запам'ятовує сторінки

**Рішення:**
1. Перевірте базу даних:
   ```bash
   sqlite3 users.db "SELECT * FROM multi_page_sessions;"
   ```
2. Перезапустіть бота
3. Спробуйте знову

---

## 📊 Зміни в Проекті

### Додані файли:

| Файл | Призначення | Рядків |
|------|-------------|--------|
| `setup_whatsapp_bot.sh` | Автоматичне встановлення | 350+ |
| `run_whatsapp_bot.sh` | Запуск бота | 80+ |
| `test_whatsapp_bot.py` | Тести | 200+ |
| `check_status.py` | Перевірка готовності | 80+ |
| `src/whatsapp/whatsapp_bot.py` | Головний бот | 1100+ |
| `.env` | Змінні оточення | 20 |
| `WHATSAPP_SETUP.md` | Ця документація | 500+ |
| `CHANGELOG_WHATSAPP.md` | Історія змін | - |

### Інтегровані модулі:

Всі модулі з Telegram бота тепер працюють в WhatsApp:

- ✅ `advanced_ocr.py` (450+ рядків)
- ✅ `advanced_translator.py` (650+ рядків)
- ✅ `legal_database.py` (872 рядки)
- ✅ `response_generator.py` (565 рядків)
- ✅ `fraud_detection.py` (431 рядків)
- ✅ `client_bot_functions.py` (683 рядки)

### База даних:

Нові таблиці в `users.db`:

```sql
users                  -- Користувачі WhatsApp
letters                -- Історія листів
multi_page_sessions    -- Багатосторінкові сесії
```

---

## 📞 Підтримка

### Twilio ресурси:

- [WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Messaging API](https://www.twilio.com/docs/messaging)
- [Support Forum](https://support.twilio.com/)

### Ngrok ресурси:

- [Ngrok Docs](https://ngrok.com/docs)
- [Troubleshooting](https://ngrok.com/docs/errors)

### Контакти проекту:

- **Telegram:** @govde_support
- **Email:** support@gov.de

---

## 📄 Ліцензія

Цей проект надається "як є" для освітніх цілей.

---

**Розроблено для допомоги українцям у Німеччині 🇺🇦🇩🇪**

**Версія:** 4.0  
**Дата:** 2026-03-06  
**Статус:** ✅ ГОТОВО ДО ЗАПУСКУ
