# 🐳 DOCKER ЗАПУСК

**Статус:** Docker встановлено ✅

---

## ✅ ЩО ВЖЕ ГОТОВО

```bash
# Docker встановлено
Docker version 29.2.1 ✅

# Docker Compose встановлено
Docker Compose version v5.1.0 ✅

# Docker працює
Docker Desktop running ✅
```

---

## 🚀 ЗАПУСК БОТА В DOCKER

### Крок 1: Зберіть образ

```bash
cd /Users/alex/Desktop/project/Gov.de

# Build (перший раз може тривати 5-10 хв)
docker compose build
```

### Крок 2: Запустіть

```bash
# Запуск
docker compose up

# Або в фоновому режимі
docker compose up -d
```

### Крок 3: Перевірте

```bash
# Перегляд логів
docker compose logs -f

# Статус
docker compose ps
```

### Крок 4: Зупиніть

```bash
# Зупинити
docker compose down
```

---

## ⚠️ МОЖЛИВІ ПРОБЛЕМИ

### Проблема 1: Build не працює

```bash
# Очистити кеш
docker system prune -a

# Спробувати знову
docker compose build --no-cache
```

### Проблема 2: Tesseract не працює

```bash
# Перевірити в контейнері
docker compose run --rm gov-de-bot tesseract --version
```

### Проблема 3: Бот не запускається

```bash
# Переглянути логи
docker compose logs gov-de-bot

# Перевірити .env
docker compose config
```

---

## 🎯 АЛЬТЕРНАТИВА: Запуск без Docker

Якщо Docker не працює:

```bash
cd /Users/alex/Desktop/project/Gov.de

# Встановити Tesseract (якщо немає)
brew install tesseract tesseract-lang

# Запустити бота
python3 src/bots/client_bot.py
```

---

## 📊 ПЕРЕВІРКА СИСТЕМИ

```bash
# Запустити перевірку
bash check_system.sh
```

**Очікуваний результат:**
```
✅ Успішно: 20+
⚠️  Попередження: 0
❌ Проблем: 0

🎉 ВСЕ ГОТОВО!
```

---

**🎉 Docker готовий до використання!**
