# 🚀 SERVER DEPLOYMENT GUIDE
## Gov.de Bot v4.5 - Production Deployment

## 📋 Вимоги до сервера

### Мінімальні вимоги:
- **OS:** Ubuntu 20.04+ / Windows 10+ / macOS
- **RAM:** 4GB (мінімум), 8GB (рекомендовано)
- **CPU:** 2 cores+
- **Storage:** 10GB+ вільного місця
- **Internet:** Стабільне з'єднання
- **Python:** 3.9+

---

## 🔧 ВАРІАНТ 1: Windows Server (Робочий ПК)

### Крок 1: Підготовка

```powershell
# 1. Перевір Python
python --version
# Має бути Python 3.9+

# 2. Створи папку для бота
mkdir C:\gov-de-bot
cd C:\gov-de-bot

# 3. Завантаж проект
git clone https://github.com/alexsandrstepanyk/Cov.de.git .
# АБО скопіюй вручну всі файли
```

### Крок 2: Встановлення залежностей

```powershell
# Встанови залежності
pip install -r requirements.txt

# Додатково для OCR
pip install pytesseract pillow
pip install easyocr

# Для Telegram
pip install python-telegram-bot==20.7

# Для перекладу
pip install googletrans==4.0.0-rc1

# Для PDF
pip install pdfminer.six

# Для NLP
pip install spacy
python -m spacy download de_core_news_sm
```

### Крок 3: Налаштування

```powershell
# 1. Створи .env файл
notepad .env

# 2. Додай токен бота
BOT_TOKEN=8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0

# 3. Збережи
```

### Крок 4: Запуск бота

```powershell
# Простий запуск
cd C:\gov-de-bot\src\bots
python client_bot.py

# Або через PM2 (рекомендовано)
npm install -g pm2
pm2 start client_bot.py --name gov-de-bot
pm2 save
pm2 startup
```

### Крок 5: Автозапуск при завантаженні

**Варіант A: Task Scheduler (Windows)**

1. Відкрий **Task Scheduler**
2. **Create Basic Task**
3. Name: `Gov.de Bot`
4. Trigger: **When the computer starts**
5. Action: **Start a program**
6. Program: `C:\Python39\python.exe`
7. Arguments: `C:\gov-de-bot\src\bots\client_bot.py`
8. Start in: `C:\gov-de-bot\src\bots`
9. Finish + **Open Properties**
10. ✅ **Run whether user is logged on or not**
11. ✅ **Run with highest privileges**

**Варіант B: PM2 (Краще)**

```powershell
# Встанови Node.js з https://nodejs.org

# Встанови PM2
npm install -g pm2

# Запусти бота
cd C:\gov-de-bot\src\bots
pm2 start client_bot.py --name gov-de-bot --interpreter python

# Збережи
pm2 save

# Автозапуск при старті Windows
pm2 startup
# Виконай команду яку видасть PM2
```

---

## 🐧 ВАРІАНТ 2: Linux Server (Ubuntu/Debian)

### Крок 1: Встановлення залежностей

```bash
# Онови систему
sudo apt update && sudo apt upgrade -y

# Встанови Python та залежності
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -t tesseract-ocr
sudo apt install -y libpoppler-cpp-dev

# Створи директорію
sudo mkdir -p /opt/gov-de-bot
sudo chown $USER:$USER /opt/gov-de-bot
cd /opt/gov-de-bot

# Завантаж проект
git clone https://github.com/alexsandrstepanyk/Cov.de.git .
# АБО скопіюй файли

# Створи віртуальне середовище
python3 -m venv venv
source venv/bin/activate

# Встанови залежності
pip install -r requirements.txt
```

### Крок 2: Systemd Service (Автозапуск)

```bash
# Створи service файл
sudo nano /etc/systemd/system/gov-de-bot.service

# Додай контент:
[Unit]
Description=Gov.de Telegram Bot
After=network.target

[Service]
Type=simple
User=your_username
WorkingDirectory=/opt/gov-de-bot/src/bots
ExecStart=/opt/gov-de-bot/venv/bin/python client_bot.py
Restart=always
RestartSec=10

# Environment
Environment="BOT_TOKEN=8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0"

[Install]
WantedBy=multi-user.target

# Збережи (Ctrl+O, Enter, Ctrl+X)

# Активуй service
sudo systemctl daemon-reload
sudo systemctl enable gov-de-bot
sudo systemctl start gov-de-bot

# Перевір статус
sudo systemctl status gov-de-bot

# Логи
sudo journalctl -u gov-de-bot -f
```

### Крок 3: PM2 (Альтернатива)

```bash
# Встанови Node.js
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# Встанови PM2
sudo npm install -g pm2

# Запусти бота
cd /opt/gov-de-bot/src/bots
pm2 start client_bot.py --name gov-de-bot --interpreter /opt/gov-de-bot/venv/bin/python

# Збережи
pm2 save

# Автозапуск
sudo pm2 startup
sudo env PATH=$PATH:/usr/bin pm2 startup systemd -u your_username --hp /home/your_username
```

---

## 🍎 ВАРІАНТ 3: macOS Server

### Крок 1: Встановлення

```bash
# Встанови Homebrew
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Встанови Python та залежності
brew install python@3.9
brew install tesseract
brew install poppler

# Створи директорію
mkdir -p ~/gov-de-bot
cd ~/gov-de-bot

# Завантаж проект
git clone https://github.com/alexsandrstepanyk/Cov.de.git .

# Встанови залежності
pip3 install -r requirements.txt
```

### Крок 2: Launchd (Автозапуск)

```bash
# Створи plist файл
nano ~/Library/LaunchAgents/com.govde.bot.plist

# Додай контент:
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.govde.bot</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/local/bin/python3</string>
        <string>/Users/your_username/gov-de-bot/src/bots/client_bot.py</string>
    </array>
    <key>WorkingDirectory</key>
    <string>/Users/your_username/gov-de-bot/src/bots</string>
    <key>RunAtLoad</key>
    <true/>
    <key>KeepAlive</key>
    <true/>
    <key>StandardOutPath</key>
    <string>/tmp/gov-de-bot.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/gov-de-bot.err</string>
</dict>
</plist>

# Збережи (Ctrl+O, Enter, Ctrl+X)

# Активуй
launchctl load ~/Library/LaunchAgents/com.govde.bot.plist
launchctl start com.govde.bot

# Перевір
launchctl list | grep govde
```

---

## 🔐 БЕЗПЕКА

### 1. Брандмауер

**Windows:**
```powershell
# Дозволь Python через брандмауер
netsh advfirewall firewall add rule name="Python Bot" dir=out action=allow program="C:\Python39\python.exe" enable=yes
```

**Linux:**
```bash
# Дозволь вихідні з'єднання (зазвичай відкрито за замовчуванням)
sudo ufw allow out 443/tcp  # HTTPS для Telegram API
```

### 2. Антивірус (Windows)

Додай виключення для:
- `C:\gov-de-bot\`
- `C:\Python39\python.exe`

### 3. Токен бота

**Ніколи не зберігай токен в коді!**

Використовуй `.env` файл:
```bash
# .env
BOT_TOKEN=your_token_here
```

В коді:
```python
from dotenv import load_dotenv
load_dotenv()
BOT_TOKEN = os.getenv('BOT_TOKEN')
```

---

## 📊 МОНІТОРИНГ

### 1. Перевірка статусу

**Windows (PM2):**
```powershell
pm2 status
pm2 logs gov-de-bot
```

**Linux (Systemd):**
```bash
sudo systemctl status gov-de-bot
sudo journalctl -u gov-de-bot -f
```

### 2. Логи

**Шляхи до логів:**
- Windows: `C:\gov-de-bot\logs\`
- Linux: `/var/log/gov-de-bot/` або `journalctl`
- macOS: `/tmp/gov-de-bot.log`

### 3. Сповіщення

Додай в код сповіщення якщо бот впав:

```python
# В client_bot.py, додай в except:
import requests

def send_admin_alert(error):
    admin_chat_id = YOUR_CHAT_ID
    message = f"🚨 БОТ ВПАВ!\n\nПомилка: {error}"
    requests.post(
        f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage",
        json={'chat_id': admin_chat_id, 'text': message}
    )
```

---

## 🔄 ОНОВЛЕННЯ

### Автоматичне оновлення

**Linux (cron):**
```bash
# Відкрий crontab
crontab -e

# Додай щоденне оновлення о 3 ночі
0 3 * * * cd /opt/gov-de-bot && git pull && sudo systemctl restart gov-de-bot
```

**Windows (Task Scheduler):**
1. Створи `.bat` файл:
```batch
@echo off
cd C:\gov-de-bot
git pull
pm2 restart gov-de-bot
```

2. Додай в Task Scheduler на 3:00

---

## ⚠️ ВИРІШЕННЯ ПРОБЛЕМ

### Бот не запускається

1. Перевір Python:
```bash
python --version
```

2. Перевір токен:
```bash
echo $BOT_TOKEN  # Linux/Mac
echo %BOT_TOKEN%  # Windows
```

3. Перевір логи:
```bash
# Systemd
sudo journalctl -u gov-de-bot -f

# PM2
pm2 logs gov-de-bot
```

### Бот падає через 5 хвилин

**Проблема:** Telegram API timeout

**Рішення:**
```python
# В client_bot.py, знайди Application.builder()
application = Application.builder() \
    .token(BOT_TOKEN) \
    .read_timeout(30) \
    .write_timeout(30) \
    .connect_timeout(30) \
    .pool_timeout(30) \
    .build()
```

### OCR не працює

**Windows:**
1. Завантаж Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
2. Встанови в `C:\Program Files\Tesseract-OCR`
3. Додай в PATH
4. Перезапусти бота

**Linux:**
```bash
sudo apt install tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
```

---

## 📈 ПРОДУКТИВНІСТЬ

### Оптимізація

1. **Кешування перекладів:**
```python
# Вже реалізовано в advanced_translator.py
# Кеш зберігається 7 днів
```

2. **Обмеження одночасних запитів:**
```python
# Додай в client_bot.py
application.max_concurrent_updates = 100
```

3. **Очищення старих логів:**
```bash
# Linux (cron)
0 4 * * 0 find /opt/gov-de-bot/logs -name "*.log" -mtime +7 -delete
```

---

## ✅ CHECKLIST

- [ ] Python 3.9+ встановлено
- [ ] Залежності встановлено
- [ ] Токен бота налаштовано
- [ ] Бот запускається вручну
- [ ] Автозапуск налаштовано
- [ ] Логи працюють
- [ ] Брандмауер налаштовано
- [ ] Моніторинг працює
- [ ] Оновлення налаштовано

---

## 🎯 РЕКОМЕНДАЦІЇ

### Для робочого ПК:

1. **Windows + PM2** - найпростіше
2. **Task Scheduler** - якщо не хочеш PM2
3. **Статична IP** - бажано для стабільності
4. **UPS** - захист від відключення світла

### Для продакшену:

1. **Linux VPS** (€5-10/міс)
   - Hetzner, DigitalOcean, Linode
   - Більш стабільно
   - Краща продуктивність

2. **Docker** - для ізоляції
3. **Monitoring** - Prometheus + Grafana
4. **Backups** - щоденні бекапи БД

---

## 📞 ПІДТРИМКА

Якщо щось не працює:

1. Перевір логи
2. Перевір статус service
3. Перевір з'єднання з Telegram
4. Перезапусти бота

**Команди для дебагу:**
```bash
# Перевірка процесу
ps aux | grep client_bot  # Linux/Mac
tasklist | findstr python  # Windows

# Перезапуск
sudo systemctl restart gov-de-bot  # Linux
pm2 restart gov-de-bot  # PM2
# Або вимкни/увімкни Task Scheduler  # Windows
```

---

**Створено:** March 1, 2026  
**Версія:** v4.5  
**Статус:** PRODUCTION READY ✅
