# 🐳 DOCKER BUILD & RUN - Gov.de Bot v4.0 Full Integration

**Версія:** 4.0 Full Integration  
**Статус:** ✅ ГОТОВО ДО ЗАПУСКУ  
**Оновлено:** 12 березня 2026

---

## 🎯 ЩО ЗМІНИЛОСЯ

### ✅ Повна інтеграція всіх модулів:

1. **Advanced OCR** - розпізнавання текстy (Tesseract + EasyOCR)
2. **Advanced Translator** - переклад з юридичним словником
3. **Legal Database** - 18 кодексів, 67+ параграфів
4. **Multi-page Handler** - багатосторінкові документи
5. **Fraud Detection** - виявлення шахрайства
6. **Smart Law Reference** - розумні посилання на закони
7. **Improved Response Generator** - покращені відповіді
8. **Letter Generator** - листи у форматі DIN 5008
9. **LLM Orchestrator** - мозок бота (опціонально)
10. **PDF Generator** - генерація PDF-листів

---

## 🚀 ШВИДКИЙ ЗАПУСК

### 1. Підготовка

```bash
# Перейти в директорію проекту
cd /Users/alex/Desktop/project/Gov.de

# Перевірити наявність .env
cp .env.example .env
nano .env  # Вставити TELEGRAM_BOT_TOKEN
```

### 2. Збірка та запуск

```bash
# Зупинити старі контейнери (якщо є)
docker compose down

# Зібрати образ без кешу (для чистої збірки)
docker compose build --no-cache

# Запустити бота
docker compose up -d

# Перегляд логів
docker compose logs -f gov-de-bot
```

---

## 📋 КОМАНДИ

### Базові:

```bash
# Зупинити бота
docker compose down

# Запустити бота
docker compose up -d

# Перегляд логів
docker compose logs -f gov-de-bot

# Перезапустити бота
docker compose restart gov-de-bot

# Статус контейнерів
docker compose ps
```

### Для розробки:

```bash
# Перезібрати образ
docker compose build --no-cache

# Запустити з пересборкою
docker compose up -d --build

# Очистити все (включаючи volumes)
docker compose down -v

# Переглянути логи останні 100 рядків
docker compose logs --tail=100 gov-de-bot
```

### Моніторинг:

```bash
# Статус бота
docker compose ps gov-de-bot

# Використання ресурсів
docker stats gov-de-bot

# Зайти в контейнер
docker exec -it gov-de-bot bash

# Перевірити health check
docker inspect --format='{{.State.Health.Status}}' gov-de-bot
```

---

## 🔧 КОНФІГУРАЦІЯ

### Змінні оточення (.env):

```bash
# Telegram Bot (ОБОВ'ЯЗКОВО)
TELEGRAM_BOT_TOKEN=8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0

# Twilio (не потрібно для Telegram)
# TWILIO_ACCOUNT_SID=...
# TWILIO_AUTH_TOKEN=...

# Ollama (опціонально для LLM)
OLLAMA_BASE_URL=http://ollama:11434

# PostgreSQL (опціонально)
POSTGRES_PASSWORD=secure_password
```

### Томи (Volumes):

| Том | Призначення |
|-----|-------------|
| `./data` | База даних законів, кеш |
| `./logs` | Логи бота |
| `./uploads` | Завантажені фото/PDF |
| `./users.db` | База даних користувачів |
| `.env` | Токени та налаштування |

### Порти:

| Сервіс | Порт | Призначення |
|--------|------|-------------|
| `gov-de-bot` | 5001 | Telegram Bot |
| `ollama` | 11434 | LLM (опціонально) |
| `postgres` | 5432 | PostgreSQL (опціонально) |
| `redis` | 6379 | Redis (опціонально) |

---

## 🧪 ТЕСТУВАННЯ

### 1. Перевірка здоров'я бота:

```bash
# Health check
docker compose exec gov-de-bot python -c "import sys; sys.path.insert(0, '/app/src'); from advanced_ocr import recognize_image; from advanced_translator import translate_text_async; from legal_database import analyze_letter; print('All modules OK')"
```

### 2. Перевірка модулів:

```bash
# Зайти в контейнер
docker exec -it gov-de-bot bash

# Перевірити Tesseract
tesseract --version
tesseract --list-langs  # Має бути: deu, eng, ukr, rus

# Перевірити Python модулі
python -c "import telegram; import easyocr; import ollama; print('OK')"
```

### 3. Тест бота:

```bash
# Відправити /start в Telegram
# Отримати меню
# Надіслати фото листа
# Отримати аналіз
```

---

## 🐛 ВИРІШЕННЯ ПРОБЛЕМ

### Бот не запускається:

```bash
# Переглянути логи
docker compose logs gov-de-bot

# Перевірити .env
docker compose config

# Перезібрати
docker compose build --no-cache
docker compose up -d
```

### Tesseract не працює:

```bash
# Перевірити наявність
docker exec gov-de-bot tesseract --version

# Перевірити мови
docker exec gov-de-bot tesseract --list-langs

# Має бути: deu, eng, ukr, rus
```

### Помилка "Permission denied":

```bash
# Виправити права на локальних папках
sudo chown -R $(whoami) data logs uploads users.db

# Перезапустити
docker compose down
docker compose up -d
```

### Конфлікт портів:

```bash
# Змінити порт в docker-compose.yml
ports:
  - "5002:5000"  # Замість 5001:5000

# Або знайти процес на порту
lsof -i :5001
kill <PID>
```

### Бот не обробляє листи:

```bash
# Перевірити логи
docker compose logs --tail=200 gov-de-bot | grep "Аналіз"

# Перевірити чи інтегровані модулі
docker exec gov-de-bot python -c "
import sys
sys.path.insert(0, '/app/src')
from bots.client_bot_v4_full import *
print(f'ADVANCED_OCR: {ADVANCED_OCR}')
print(f'ADVANCED_TRANSLATOR: {ADVANCED_TRANSLATOR}')
print(f'LEGAL_DATABASE: {LEGAL_DATABASE}')
print(f'LLM_ORCHESTRATOR: {LLM_ORCHESTRATOR}')
"
```

---

## 📊 РЕСУРСИ

### Використання пам'яті:

```
Бот (базовий):
  CPU: 5-10%
  RAM: 300-600MB
  Disk: 500MB

Бот + LLM (Ollama):
  CPU: 20-50%
  RAM: 2-4GB
  Disk: 5GB+
```

### Обмеження в docker-compose.yml:

```yaml
deploy:
  resources:
    limits:
      cpus: '2.0'
      memory: 2G
    reservations:
      cpus: '0.5'
      memory: 512M
```

---

## 🚀 ДЕПЛОЙ НА СЕРВЕР

### 1. Підготовка сервера:

```bash
# Встановити Docker
curl -fsSL https://get.docker.com | sh

# Клонувати проект
git clone <your-repo> gov-de
cd gov-de

# Скопіювати .env
cp .env.example .env
nano .env  # Відредагувати токени
```

### 2. Запуск:

```bash
# Запустити в фоні
docker compose up -d

# Перевірити
docker compose ps
docker compose logs -f
```

### 3. Auto-restart:

```yaml
# Вже налаштовано в docker-compose.yml
restart: unless-stopped
```

### 4. Моніторинг:

```bash
# Статус
docker compose ps

# логи
docker compose logs -f gov-de-bot

# Використання ресурсів
docker stats
```

---

## 📈 ПРОДУКТИВНІСТЬ

### Оптимізація Docker:

```dockerfile
# Вже реалізовано в Dockerfile:
✅ Multi-stage не потрібен (один етап)
✅ Кешування шарів (requirements.txt окремо)
✅ Мінімізація шарів (&& rm -rf ...)
✅ Non-root користувач (botuser)
✅ Health check
```

### Масштабування:

```bash
# Запустити кілька копій бота
docker compose up --scale gov-de-bot=3

# З балансировщиком навантаження
# (потрібно додати nginx service)
```

---

## 🔐 БЕЗПЕКА

### Реалізовано:

```yaml
✅ Non-root користувач (botuser)
✅ Read-only .env файл
✅ Обмеження ресурсів
✅ Health check
✅ Логування (50m, 5 файлів)
```

### Рекомендації:

```bash
# 1. Не зберігати токени в git
echo ".env" >> .gitignore

# 2. Використовувати Docker secrets (для production)
# 3. Регулярно оновлювати образи
docker compose pull
docker compose up -d

# 4. Моніторити логи
docker compose logs -f | grep -i error
```

---

## 📚 СТРУКТУРА ФАЙЛІВ

```
Gov.de/
├── Dockerfile              # Образ Docker
├── docker-compose.yml      # Конфігурація сервісів
├── .env                    # Токени (не в git!)
├── .env.example            # Приклад .env
├── src/
│   ├── bots/
│   │   ├── client_bot_v4_full.py  # ✅ НОВИЙ БОТ
│   │   ├── client_bot.py          # Старий бот
│   │   └── client_bot_functions.py
│   ├── advanced_ocr.py
│   ├── advanced_translator.py
│   ├── legal_database.py
│   ├── multi_page_handler.py
│   ├── fraud_detection.py
│   ├── smart_law_reference.py
│   ├── improved_response_generator.py
│   ├── letter_generator.py
│   ├── llm_orchestrator.py
│   └── pdf_generator.py
├── data/                   # Бази даних, кеш
├── logs/                   # Логи
├── uploads/                # Завантаження
└── users.db                # База користувачів
```

---

## 🎯 ПІДСУМКИ

### Що працює:

```
✅ Telegram Bot
✅ Advanced OCR (Tesseract + EasyOCR)
✅ Advanced Translator (юридичний словник)
✅ Legal Database (18 кодексів)
✅ Multi-page Handler
✅ Fraud Detection
✅ Smart Law Reference
✅ Improved Response Generator
✅ Letter Generator (DIN 5008)
✅ PDF Generator
✅ LLM Orchestrator (опціонально)
```

### Як запустити:

```bash
# Просто:
cd /Users/alex/Desktop/project/Gov.de
docker compose up -d

# Перегляд логів:
docker compose logs -f gov-de-bot
```

---

**🎉 Docker готовий до використання!**

```bash
# Запустити:
docker compose up -d

# Зупинити:
docker compose down
```

---

*Останнє оновлення: 12 березня 2026*  
*Версія: 4.0 Full Integration*
