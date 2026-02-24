# Gov.de - Версія 3.0

## 📦 Інформація про версію

- **Версія:** 3.0
- **Дата:** 24 лютого 2026
- **Статус:** ✅ Стабільна робоча версія

## ✨ Що нового у версії 3.0

### Основні зміни:
1. **Спрощена реєстрація** — тільки ім'я (без паролю)
2. **Повна обробка листів** — OCR, NLP, класифікація
3. **Конкретні відповіді** — шаблони з законами
4. **Покращене логування** — файли logs/client_bot.log

### Виправлені проблеми:
- ✅ Прибрано зайвий крок з паролем
- ✅ Додано реальний токен бота
- ✅ Інтегровано всі модулі аналізу
- ✅ Покращено класифікацію типів листів
- ✅ Додано детальні шаблони відповідей

## 🏗️ Архітектура

```
Client Bot → Core Bot → DE Bot
(користувач)  (обробка)   (закони)
```

## 📁 Файли версії 3.0

### Боти:
- `src/bots/client_bot.py` — основний бот (547 рядків)
- `src/bots/core_bot.py` — обробка листів
- `src/bots/de_bot.py` — база законів

### Модулі:
- `src/ingestion.py` — завантаження файлів (PDF, фото, текст)
- `src/nlp_analysis.py` — NLP аналіз з spaCy
- `src/legal_db.py` — база німецьких законів
- `src/response_generator.py` — генерація відповідей

### Інше:
- `run_all_bots.sh` — запуск всіх ботів
- `test_system.py` — тестова система
- `requirements.txt` — залежності
- `README.md` — документація
- `QUICKSTART.md` — швидкий старт

## 🚀 Запуск

```bash
bash run_all_bots.sh
```

## 📱 Telegram бот

@GovDeClientBot

## 🧪 Тестування

```bash
python3 test_system.py
```

Всі тести: ✅ 6/6

## 📊 Статистика коду

| Файл | Рядків |
|------|--------|
| client_bot.py | 547 |
| core_bot.py | 252 |
| response_generator.py | 312 |
| nlp_analysis.py | 156 |
| legal_db.py | 98 |
| ingestion.py | 142 |
| **Разом** | **~1500+** |

## 📝 Зміни у базі даних

### Таблиця users:
```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER UNIQUE,
    username TEXT,          -- тільки ім'я
    language TEXT DEFAULT 'uk',
    country TEXT DEFAULT 'de',
    status TEXT DEFAULT 'resident',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

### Таблиця letters:
```sql
CREATE TABLE letters (
    id INTEGER PRIMARY KEY,
    chat_id INTEGER,
    text TEXT,
    letter_type TEXT,
    analysis TEXT,
    response TEXT,
    lawyer_review TEXT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
)
```

## 🎯 Функціонал

### Реєстрація (спрощена):
1. Введіть ім'я
2. Оберіть мову
3. Оберіть країну
4. Оберіть статус

### Завантаження листа:
- 📷 Фото (OCR розпізнавання)
- 📄 Текст
- 📎 PDF

### Аналіз:
- 🔍 Класифікація типу
- 📚 Закони (BGB, KSchG, SGB, VwVfG)
- ⚠️ Наслідки
- 📝 Відповідь

### Типи листів:
- 💰 Боргові (debt_collection)
- 🏠 Оренда (tenancy)
- 💼 Jobcenter (employment)
- 📋 Адміністративні (administrative)
- 📄 Загальні (general)

## 🔧 Залежності

```
spacy>=3.0.0
python-telegram-bot
pytesseract
pillow
pdfminer.six
googletrans==4.0.0rc1
werkzeug
```

## 📞 Контакти

Бот: @GovDeClientBot

---

**Збережено: 24 лютого 2026**
**Git тег: v3.0**
