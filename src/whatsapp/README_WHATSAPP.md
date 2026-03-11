# WhatsApp Bot v4.0 - Інструкція з встановлення та запуску

## 📋 Зміст

1. [Швидкий старт](#швидкий-старт)
2. [Налаштування Twilio WhatsApp API](#налаштування-twilio-whatsapp-api)
3. [Встановлення залежностей](#встановлення-залежностей)
4. [Запуск бота](#запуск-бота)
5. [Тестування](#тестування)
6. [Вирішення проблем](#вирішення-проблем)

---

## 🚀 Швидкий старт

### 1. Отримайте Twilio обліковий запис

1. Зареєструйтесь на [Twilio](https://www.twilio.com/try-twilio)
2. Отримайте безкоштовний тестовий кредит ($15-30)
3. Активуйте WhatsApp Sandbox (безкоштовно для тестування)

### 2. Налаштуйте змінні оточення

```bash
# .env файл
export TWILIO_ACCOUNT_SID="ACxxxxxxxxxxxxxxxxxxxxxxxx"
export TWILIO_AUTH_TOKEN="your_auth_token_here"
export TWILIO_WHATSAPP_NUMBER="whatsapp:+14155238886"
export WEBHOOK_VERIFY_TOKEN="gov_de_2026"
export FLASK_DEBUG="False"
```

### 3. Встановіть залежності

```bash
cd /Users/alex/Desktop/project/Gov.de
pip3 install -r requirements.txt
pip3 install twilio flask python-dotenv
```

### 4. Запустіть бота

```bash
# Спосіб 1: Безпосередньо
python3 src/whatsapp/whatsapp_bot.py

# Спосіб 2: Через скрипт
bash run_whatsapp_bot.sh

# Спосіб 3: В background
nohup python3 src/whatsapp/whatsapp_bot.py > logs/whatsapp_bot.log 2>&1 &
```

### 5. Налаштуйте вебхук

**Для тестування (локально):**

```bash
# Встановіть ngrok
brew install ngrok

# Запустіть тунель
ngrok http 5000
```

**Для продакшену:**

Налаштуйте вебхук на вашому сервері:
```
https://your-domain.com/whatsapp
```

---

## 📱 Налаштування Twilio WhatsApp API

### Крок 1: Реєстрація Twilio

1. Перейдіть на [Twilio.com](https://www.twilio.com/try-twilio)
2. Створіть обліковий запис
3. Підтвердіть email та телефон

### Крок 2: Отримання облікових даних

1. Увійдіть в [Twilio Console](https://console.twilio.com/)
2. Знайдіть **Account SID** на головній сторінці
3. Створіть **Auth Token** в налаштуваннях

```
Account SID: ACxxxxxxxxxxxxxxxxxxxxxxxx
Auth Token: xxxxxxxxxxxxxxxxxxxxxxxx
```

### Крок 3: Активація WhatsApp Sandbox

1. Перейдіть в **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Натисніть **Join Beta**
3. Отримайте номер Sandbox: `whatsapp:+14155238886`
4. Надішліть код з WhatsApp для підключення

### Крок 4: Налаштування вебхука

**Для локальної розробки:**

```bash
# Встановіть ngrok
brew install ngrok  # macOS
# або
sudo apt install ngrok  # Linux

# Запустіть
ngrok http 5000
```

Скопіюйте URL (наприклад, `https://abc123.ngrok.io`) і налаштуйте:

```bash
# Twilio Console → Messaging → Settings → WhatsApp Sandbox Settings
# Вставте URL у поле "WHEN A MESSAGE COMES IN"
https://abc123.ngrok.io/whatsapp
```

**Для продакшену:**

```bash
# На вашому сервері з публічним IP
https://your-domain.com/whatsapp
```

### Крок 5: Перевірка налаштувань

```bash
# Перевірка вебхука
curl -X GET "https://your-domain.com/webhook?hub.mode=subscribe&hub.verify_token=gov_de_2026&hub.challenge=test"

# Перевірка здоров'я бота
curl https://your-domain.com/health
```

---

## 📦 Встановлення залежностей

### Основні залежності

```bash
pip3 install twilio flask python-dotenv
```

### Перевірка існуючих залежностей

```bash
# Перевірка requirements.txt
cat requirements.txt

# Встановлення всіх залежностей
pip3 install -r requirements.txt
```

### Необов'язкові залежності

```bash
# Для розширеного OCR (якщо ще не встановлено)
pip3 install easyocr opencv-python

# Для перекладу
pip3 install googletrans==4.0.0-rc1

# Для NLP
python3 -m spacy download de_core_news_sm
```

---

## ▶️ Запуск бота

### Локальний запуск (розробка)

```bash
# Термінал 1: Запуск ngrok
ngrok http 5000

# Термінал 2: Запуск бота
cd /Users/alex/Desktop/project/Gov.de
python3 src/whatsapp/whatsapp_bot.py
```

### Продакшен запуск (сервер)

```bash
# Встановіть Gunicorn
pip3 install gunicorn

# Запустіть з Gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 src.whatsapp.whatsapp_bot:app

# Або через systemd (Linux)
sudo nano /etc/systemd/system/whatsapp-bot.service
```

**whatsapp-bot.service:**
```ini
[Unit]
Description=Gov.de WhatsApp Bot
After=network.target

[Service]
User=your_user
WorkingDirectory=/Users/alex/Desktop/project/Gov.de
Environment="PATH=/usr/bin:/usr/local/bin"
Environment="TWILIO_ACCOUNT_SID=ACxxx"
Environment="TWILIO_AUTH_TOKEN=xxx"
Environment="TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886"
ExecStart=/usr/bin/python3 src/whatsapp/whatsapp_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Активувати службу
sudo systemctl daemon-reload
sudo systemctl enable whatsapp-bot
sudo systemctl start whatsapp-bot

# Перевірка статусу
sudo systemctl status whatsapp-bot
```

### Docker запуск

```dockerfile
# Dockerfile
FROM python:3.9-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN pip install twilio flask gunicorn

COPY . .

EXPOSE 5000
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "src.whatsapp.whatsapp_bot:app"]
```

```bash
# Збірка та запуск
docker build -t govde-whatsapp .
docker run -p 5000:5000 -e TWILIO_ACCOUNT_SID=xxx -e TWILIO_AUTH_TOKEN=xxx govde-whatsapp
```

---

## 🧪 Тестування

### 1. Підключення до Sandbox

1. Відкрийте WhatsApp
2. Надішліть повідомлення на номер Sandbox
3. Введіть код підтвердження

### 2. Тестові сценарії

**Тест 1: Команда /start**
```
Надішліть: /start
Очікуйте: 👋 Вітаємо + меню
```

**Тест 2: Меню**
```
Надішліть: 1
Очікуйте: 📤 Будь ласка, надішліть фото
```

**Тест 3: Обробка фото**
```
Надішліть: Фото Jobcenter листа
Очікуйте: ✅ Аналіз завершено + переклад + параграфи
```

**Тест 4: Багатосторінковий документ**
```
1. Надішліть: Фото сторінки 1
2. Натисніть: ✅ Все, аналізуй
3. Очікуйте: Об'єднаний аналіз
```

**Тест 5: Історія**
```
Надішліть: 2
Очікуйте: 📊 Ваша історія листів
```

### 3. Автоматичні тести

```bash
# Запуск тестів
python3 test_whatsapp_bot.py

# Перевірка модулів
python3 -m py_compile src/whatsapp/whatsapp_bot.py
```

---

## 🔧 Вирішення проблем

### Бот не запускається

```bash
# Перевірка логів
tail -f logs/whatsapp_bot.log

# Перевірка портів
lsof -i :5000

# Перевірка змінних оточення
echo $TWILIO_ACCOUNT_SID
echo $TWILIO_AUTH_TOKEN
```

### Вебхук не працює

```bash
# Перевірка ngrok
curl https://your-ngrok-url.ngrok.io/health

# Перевірка вебхука
curl -X GET "https://your-ngrok-url.ngrok.io/webhook?hub.mode=subscribe&hub.verify_token=gov_de_2026&hub.challenge=test"
```

### Повідомлення не відправляються

1. Перевірте баланс Twilio
2. Переконайтесь що Sandbox активований
3. Перевірте логи Twilio в консолі

### OCR погано розпізнає

- Робіть фото при хорошому освітленні
- Тримайте камеру рівно
- Уникайте тіней та відблисків

### Переклад не працює

```bash
# Перевірка advanced_translator
python3 -c "from advanced_translator import translate_text_async; print('OK')"

# Перезапуск бота
pkill -f whatsapp_bot.py
python3 src/whatsapp/whatsapp_bot.py &
```

---

## 📊 Моніторинг

### Логи

```bash
# Перегляд логів в реальному часі
tail -f logs/whatsapp_bot.log

# Пошук помилок
grep ERROR logs/whatsapp_bot.log

# Статистика
grep "✅ Повідомлення надіслано" logs/whatsapp_bot.log | wc -l
```

### Twilio Console

1. **Messaging** → **Logs** → **Message Logs**
2. Перевірка статусу повідомлень
3. Перегляд помилок

### Метрики

```bash
# Кількість користувачів
sqlite3 users.db "SELECT COUNT(*) FROM users;"

# Кількість листів
sqlite3 users.db "SELECT COUNT(*) FROM letters;"

# Активність за день
sqlite3 users.db "SELECT DATE(created_at), COUNT(*) FROM users GROUP BY DATE(created_at);"
```

---

## 🆘 Підтримка

### Twilio Documentation

- [WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Messaging API](https://www.twilio.com/docs/messaging)
- [Support Forum](https://support.twilio.com/)

### Контакти

- **Telegram:** @govde_support
- **Email:** support@gov.de

---

## 📄 Ліцензія

Цей проект надається "як є" для освітніх цілей.

**Розроблено для допомоги українцям у Німеччині 🇺🇦🇩🇪**
