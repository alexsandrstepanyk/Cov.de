# 🚀 WhatsApp Bot - ШВИДКА ІНСТРУКЦІЯ

**5 хвилин до запуску!**

---

## ⚡ ШВИДКИЙ СТАРТ

### 1. Встановлення (2 хвилини)

```bash
cd /Users/alex/Desktop/project/Gov.de

# Встановити залежності
pip3 install twilio flask python-dotenv

# Встановити Tesseract (якщо немає)
brew install tesseract
brew install tesseract-lang

# Встановити Ngrok (якщо немає)
brew install ngrok
```

### 2. Запуск бота (30 секунд)

```bash
# Термінал 1
python3 src/whatsapp/whatsapp_bot.py
```

### 3. Запуск ngrok (30 секунд)

```bash
# Термінал 2
ngrok http 5000
```

### 4. Налаштування вебхука (1 хвилина)

1. Скопіюйте URL з ngrok (наприклад, `https://abc123.ngrok.io`)
2. Зайдіть в [Twilio Console](https://console.twilio.com/)
3. **Messaging** → **Settings** → **WhatsApp Sandbox Settings**
4. Вставте: `https://xxx.ngrok.io/whatsapp`
5. Натисніть **Save**

### 5. Тестування (1 хвилина)

1. Відкрийте WhatsApp
2. Надішліть `/start` на номер Sandbox
3. Отримайте меню!

---

## 📋 ПЕРЕВІРКА

```bash
# Перевірка що бот працює
curl http://localhost:5000/health

# Має повернути:
# {"status": "healthy", "version": "4.0", ...}
```

---

## 🔑 ВАШІ КЛЮЧІ ВЖЕ В .env

```bash
cat .env

# TWILIO_ACCOUNT_SID=Q4V1TE5HBN7YRF69FVV3EQJ3
# TWILIO_AUTH_TOKEN=db5d8ee1e990413876541cd045499e72
```

---

## 🆘 ЯКЩО ЩОСЬ НЕ ПРАЦЮЄ

### Бот не запускається:
```bash
# Перевірте помилки
python3 src/whatsapp/whatsapp_bot.py 2>&1 | tail -20
```

### Вебхук не працює:
```bash
# Перевірте ngrok
curl https://your-ngrok-url.ngrok.io/health
```

### Tesseract не розпізнає:
```bash
# Перевірте мови
tesseract --list-langs
# Повинні бути: deu, eng
```

---

## 📚 ПОВНА ДОКУМЕНТАЦІЯ

- `docs/WHATSAPP_SETUP.md` - Повний гід
- `WHATSAPP_FINAL_REPORT.md` - Фінальний звіт
- `CHANGELOG_WHATSAPP.md` - Історія змін

---

**🇺🇦🇩🇪 Розроблено для допомоги українцям у Німеччині**
