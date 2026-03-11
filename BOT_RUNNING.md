# ✅ WhatsApp Bot ЗАПУЩЕНО!

**Статус:** ✅ Бот працює  
**Порт:** 5001  
**Дата:** 2026-03-06

---

## 🎉 БОТ ПРАЦЮЄ!

```
✅ Бот запущено на http://localhost:5001
✅ База даних ініціалізована
✅ Twilio підключено (баланс: $15.50)
```

---

## 📱 ЩОБ ПІДКЛЮЧИТИ WHATSAPP:

### Спосіб 1: Ngrok (безкоштовно, 5 хвилин)

1. **Зареєструйтесь на ngrok:**
   - Зайдіть на: https://dashboard.ngrok.com/signup
   - Створіть безкоштовний акаунт

2. **Отримайте токен:**
   - Після реєстрації: https://dashboard.ngrok.com/get-started/your-authtoken
   - Скопіюйте токен

3. **Встановіть токен:**
   ```bash
   ~/ngrok config add-authtoken ВАШ_ТОКЕН
   ```

4. **Запустіть ngrok:**
   ```bash
   ~/ngrok http 5001
   ```

5. **Скопіюйте URL:**
   ```
   Forwarding: https://xxx.ngrok.io -> http://localhost:5001
   ```

6. **Налаштуйте в Twilio:**
   - Зайдіть на: https://console.twilio.com/
   - Messaging → Settings → WhatsApp Sandbox Settings
   - Вставте: `https://xxx.ngrok.io/whatsapp`
   - Натисніть **Save**

---

### Спосіб 2: Cloudflare Tunnel (безкоштовно, без реєстрації)

```bash
# Встановіть cloudflared
brew install cloudflared

# Запустіть тунель
cloudflared tunnel --url http://localhost:5001
```

Скопіюйте URL з виводу та налаштуйте в Twilio.

---

### Спосіб 3: LocalXpose

```bash
brew install localxpose
loclx tunnel http --to localhost:5001
```

---

## 🧪 ТЕСТУВАННЯ

### Перевірка бота:

```bash
# Перевірка здоров'я
curl http://localhost:5001/health

# Має повернути:
# {"status": "healthy", "version": "4.0", ...}
```

### Перевірка вебхука:

```bash
curl "http://localhost:5001/webhook?hub.mode=subscribe&hub.verify_token=gov_de_2026&hub.challenge=test"
# Має повернути: test
```

---

## 📱 ПІДКЛЮЧЕННЯ ДО WHATSAPP

1. **Зайдіть в Twilio Console:**
   https://console.twilio.com/

2. **Messaging → Try it out → Send a WhatsApp message**

3. **Надішліть код з WhatsApp:**
   - Відкрийте WhatsApp
   - Надішліть код на номер `whatsapp:+14155238886`

4. **Налаштуйте вебхук** (після запуску ngrok):
   - Вставте URL: `https://xxx.ngrok.io/whatsapp`

5. **Тестуйте:**
   - Надішліть `/start` в WhatsApp
   - Отримайте меню!

---

## 🔧 КОМАНДИ

```bash
# Перевірка статусу бота
curl http://localhost:5001/health

# Перегляд логів
tail -f logs/whatsapp_bot.log

# Зупинка бота
pkill -f whatsapp_bot.py

# Запуск бота
python3 src/whatsapp/whatsapp_bot.py
```

---

## 📊 СТАТУС МОДУЛІВ

| Модуль | Статус |
|--------|--------|
| Twilio API | ✅ Підключено |
| Flask Webhook | ✅ Працює |
| База даних | ✅ Ініціалізовано |
| OCR (Tesseract) | ⚠️ Потребує встановлення |
| Переклад | ⚠️ Потребує налаштування |
| База законів | ✅ Працює |

---

## ⚠️ ВАЖЛИВО

1. **Бот працює на порту 5001** (не 5000)
2. **Ngrok потребує реєстрації** (безкоштовно)
3. **Webhook URL має закінчуватись на `/whatsapp`**

---

## 🆘 ПІДТРИМКА

Якщо потрібна допомога:
1. Перевірте логи: `tail -f logs/whatsapp_bot.log`
2. Перевірте Twilio Console: https://console.twilio.com/
3. Документація: `docs/WHATSAPP_SETUP.md`

---

**🇺🇦🇩🇪 Розроблено для допомоги українцям у Німеччині**
