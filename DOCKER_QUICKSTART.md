# 🐳 DOCKER QUICKSTART для Gov.de

**Версія:** 4.3 Docker  
**Статус:** ✅ ГОТОВО ДО ВИКОРИСТАННЯ

---

## 🎯 НАВІЩО DOCKER?

### Проблеми які вирішує Docker:

```
❌ Tesseract OCR не встановлено
❌ Конфлікти залежностей
❌ "На моїй машині працює"
❌ Складна установка (30+ хв)
❌ Важкий деплой на сервер
```

### Рішення:

```
✅ Tesseract встановлено автоматично
✅ Всі залежності ізольовані
✅ однаково працює всюди
✅ Швидкий старт (5 хв)
✅ Деплой в 1 команду
```

---

## 🚀 ШВИДКИЙ СТАРТ

### 1. Встановлення Docker

**macOS:**
```bash
# Встановити Docker Desktop
brew install --cask docker
# Або завантажити з https://docker.com/products/docker-desktop
```

**Linux (Ubuntu/Debian):**
```bash
curl -fsSL https://get.docker.com | sh
sudo usermod -aG docker $USER
```

**Windows:**
```bash
# Встановити Docker Desktop
# https://docker.com/products/docker-desktop
```

### 2. Перевірка

```bash
docker --version
docker compose version
```

### 3. Запуск бота

```bash
# Зайти в директорію проекту
cd /Users/alex/Desktop/project/Gov.de

# Зібрати та запустити
docker compose up --build

# Або в фоновому режимі
docker compose up -d --build
```

### 4. Перевірка

```bash
# Перегляд логів
docker compose logs -f gov-de-bot

# Перевірка статусу
docker compose ps

# Зупинити
docker compose down
```

---

## 📋 КОМАНДИ

### Базові:

```bash
# Зібрати образ
docker compose build

# Запустити
docker compose up

# Запустити в фоні (-d)
docker compose up -d

# Зупинити
docker compose down

# Перезапустити
docker compose restart

# Перегляд логів
docker compose logs -f

# Статус контейнерів
docker compose ps
```

### Розширені:

```bash
# Запустити тільки бота (без LLM)
docker compose up gov-de-bot

# Запустити з LLM (Ollama)
docker compose --profile llm up

# Запустити з базою даних
docker compose --profile database up

# Запустити все
docker compose --profile llm --profile database up

# Очистити все (видалити volumes)
docker compose down -v

# Перезібрати образ
docker compose build --no-cache
```

---

## 🔧 КОНФІГУРАЦІЯ

### docker-compose.yml

**Сервіси:**

| Сервіс | Порт | Призначення |
|--------|------|-------------|
| `gov-de-bot` | 5000 | Головний бот |
| `ollama` | 11434 | LLM (опціонально) |
| `postgres` | 5432 | База даних (опціонально) |
| `redis` | 6379 | Кеш (опціонально) |

**Профілі:**

- `default` - тільки бот
- `llm` - бот + Ollama (GPU потрібно)
- `database` - бот + PostgreSQL
- `cache` - бот + Redis

### Змінні оточення (.env):

```bash
# Основні
TELEGRAM_BOT_TOKEN=your_token
TWILIO_ACCOUNT_SID=your_sid
TWILIO_AUTH_TOKEN=your_token

# База даних (якщо використовується PostgreSQL)
POSTGRES_PASSWORD=secure_password

# LLM (якщо використовується Ollama)
OLLAMA_BASE_URL=http://ollama:11434
```

---

## 📊 ОБ'ЄМИ ДАНИХ

### Розмір образів:

```
Базовий Python:     ~120MB
Tesseract OCR:      ~100MB
Залежності Python:  ~200MB
Код проекту:        ~50MB
─────────────────────────────
Разом:              ~470MB
```

### Використання ресурсів:

```
Бот:
  CPU: 5-10%
  RAM: 200-500MB
  Disk: 500MB

Бот + Ollama:
  CPU: 20-50%
  RAM: 2-4GB
  Disk: 5GB+
```

---

## 🐛 ВИРІШЕННЯ ПРОБЛЕМ

### Бот не запускається

```bash
# Переглянути логи
docker compose logs gov-de-bot

# Перевірити .env
docker compose config

# Перезібрати
docker compose build --no-cache
docker compose up -d
```

### Tesseract не працює

```bash
# Перевірити наявність
docker exec gov-de-bot tesseract --version

# Перевірити мови
docker exec gov-de-bot tesseract --list-langs

# Має бути: deu, eng, ukr
```

### Проблеми з правами доступу

```bash
# Виправити права на локальних папках
sudo chown -R $(whoami) data logs uploads

# Перезапустити
docker compose down
docker compose up -d
```

### Конфлікт портів

```bash
# Змінити порт в docker-compose.yml
ports:
  - "5001:5000"  # Замість 5000:5000

# Або зупинити інший процес
lsof -i :5000
kill <PID>
```

---

## 🚀 ДЕПЛОЙ НА СЕРВЕР

### 1. Підготовка сервера

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

### 2. Запуск

```bash
# Запустити в фоні
docker compose up -d

# Перевірити
docker compose ps
docker compose logs -f
```

### 3. Auto-restart

```yaml
# Вже налаштовано в docker-compose.yml
restart: unless-stopped
```

### 4. Моніторинг

```bash
# Статус
docker compose ps

# логи
docker compose logs -f

# Використання ресурсів
docker stats
```

---

## 📈 ПРОДУКТИВНІСТЬ

### Оптимізація:

```bash
# Використовувати multi-stage build
# (зменшить розмір з 500MB до 300MB)

# Кешування шарів
# (requirements.txt окремо від коду)

# Використовувати Alpine
# (менший розмір, але можливі проблеми з сумісністю)
```

### Масштабування:

```bash
# Запустити кілька копій бота
docker compose up --scale gov-de-bot=3

# З балансировником навантаження
# (потрібно додати nginx service)
```

---

## 🔐 БЕЗПЕКА

### Найкращі практики:

```yaml
# 1. Не використовувати root
user: "1000:1000"

# 2. Обмежити ресурси
deploy:
  resources:
    limits:
      cpus: '1'
      memory: 512M

# 3. Secrets для токенів
# (не зберігати в .env)
secrets:
  - telegram_token

# 4. Read-only filesystem
read_only: true
tmpfs:
  - /tmp
```

---

## 📚 КОРИСНІ ПОСИЛАННЯ

- [Docker Docs](https://docs.docker.com/)
- [Docker Compose Docs](https://docs.docker.com/compose/)
- [Docker Hub](https://hub.docker.com/)
- [Tesseract OCR Docker](https://hub.docker.com/r/tesseractshadowbox/tesseractocr)

---

## 🎯 ПІДСУМКИ

### Переваги Docker:

```
✅ Tesseract OCR встановлено
✅ Всі залежності працюють
✅ Швидкий старт (5 хв)
✅ Легкий деплой
✅ Ізольованість
✅ Відтворюваність
```

### Чи варто використовувати:

```
Розробка:     ✅ ТАК (легше тестувати)
Продакшен:    ✅ ТАК (легше деплоїти)
Локально:     ⚠️ Опціонально (якщо немає конфліктів)
```

---

**🎉 Docker готовий до використання!**

```bash
# Просто запустіть:
docker compose up --build
```

---

*Останнє оновлення: 10 березня 2026*  
*Версія: 4.3 Docker*
