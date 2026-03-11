# 🇩🇪 Gov.de WhatsApp Bot v4.0

**Повний аналог Telegram бота для WhatsApp**

[![Версія](https://img.shields.io/badge/версія-4.0.0-blue)](CHANGELOG_WHATSAPP.md)
[![Статус](https://img.shields.io/badge/статус-готово-green)](WHATSAPP_FINAL_REPORT.md)
[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)

---

## 🎯 Можливості

- 📸 **OCR розпізнавання** - EasyOCR + Tesseract
- 🌐 **Переклад** - 35+ юридичних термінів
- ⚖️ **База законів** - 18 кодексів, 67+ параграфів
- 📝 **Відповіді** - UA + DE мови
- 📑 **Багатосторінковість** - Об'єднання сторінок
- 🔍 **Класифікація** - 5 типів документів
- ⚠️ **Анти-шахрайство** - Виявлення fraud

---

## 🚀 Швидкий старт

```bash
# 1. Встановлення
pip3 install twilio flask python-dotenv

# 2. Запуск бота
python3 src/whatsapp/whatsapp_bot.py

# 3. Запуск ngrok (в окремому терміналі)
ngrok http 5000
```

**Детальна інструкція:** [WHATSAPP_QUICKSTART.md](WHATSAPP_QUICKSTART.md)

---

## 📁 Структура

```
Gov.de/
├── src/whatsapp/
│   ├── whatsapp_bot.py          # Головний бот
│   ├── README_WHATSAPP.md       # API документація
│   └── .env.example             # Шаблон
│
├── docs/
│   └── WHATSAPP_SETUP.md        # Повний гід
│
├── setup_whatsapp_bot.sh        # Встановлення
├── run_whatsapp_bot.sh          # Запуск
├── test_whatsapp_bot.py         # Тести
├── .env                         # Конфігурація
│
├── CHANGELOG_WHATSAPP.md        # Історія змін
├── WHATSAPP_FINAL_REPORT.md     # Звіт
└── WHATSAPP_QUICKSTART.md       # Швидка інструкція
```

---

## 📚 Документація

| Файл | Опис |
|------|------|
| [WHATSAPP_QUICKSTART.md](WHATSAPP_QUICKSTART.md) | ⚡ Швидка інструкція (5 хв) |
| [docs/WHATSAPP_SETUP.md](docs/WHATSAPP_SETUP.md) | 📖 Повний гід по встановленню |
| [src/whatsapp/README_WHATSAPP.md](src/whatsapp/README_WHATSAPP.md) | 🔧 API документація |
| [WHATSAPP_FINAL_REPORT.md](WHATSAPP_FINAL_REPORT.md) | 📊 Фінальний звіт |
| [CHANGELOG_WHATSAPP.md](CHANGELOG_WHATSAPP.md) | 📝 Історія змін |

---

## 🧪 Тестування

```bash
# Перевірка готовності
python3 check_status.py

# Автоматичні тести
python3 test_whatsapp_bot.py

# Перевірка здоров'я
curl http://localhost:5000/health
```

---

## 🔑 Конфігурація

Файл `.env` вже створено з вашими ключами:

```env
TWILIO_ACCOUNT_SID=Q4V1TE5HBN7YRF69FVV3EQJ3
TWILIO_AUTH_TOKEN=db5d8ee1e990413876541cd045499e72
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
```

---

## 📊 Архітектура

```
WhatsApp → Twilio API → Flask Webhook → Модулі аналізу → База даних
                                              ↓
            (OCR, Переклад, Закони, Відповіді, Fraud)
```

---

## 💰 Вартість

| Тариф | Повідомлення | Ціна |
|-------|--------------|------|
| **Sandbox** | 1000/24год | Безкоштовно ($15 кредит) |
| **Production** | Змінний | $0.005/вхідне, $0.008/вихідне |

---

## ⚠️ Обмеження

- Sandbox: 1000 повідомлень/24год
- Ngrok free: Змінює URL при запуску
- OCR: Потребує якісних фото

---

## 🆘 Підтримка

### Twilio:
- [Console](https://console.twilio.com/)
- [WhatsApp API](https://www.twilio.com/docs/whatsapp)
- [Support](https://support.twilio.com/)

### Проект:
- **Telegram:** @govde_support
- **Email:** support@gov.de

---

## 📄 Ліцензія

Цей проект надається "як є" для освітніх цілей.

---

**Розроблено для допомоги українцям у Німеччині 🇺🇦🇩🇪**

**Версія:** 4.0.0 | **Дата:** 2026-03-06 | **Статус:** ✅ ГОТОВО
