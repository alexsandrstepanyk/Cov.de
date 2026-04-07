# ✅ ЯК ПЕРЕВІРИТИ РОБОТУ БОТА

**Після того як Docker збереться і запуститься:**

---

## 1️⃣ ПЕРЕВІРКА СТАТУСУ

```bash
# Статус контейнера
docker compose ps

# Має бути:
# NAME         STATUS
# gov-de-bot   Up (healthy)
```

---

## 2️⃣ ПЕРЕВІРКА ЛОГІВ

```bash
# Перегляд логів
docker compose logs -f gov-de-bot

# Має бути в кінці:
# ✅ Advanced OCR підключено
# ✅ Advanced Translator підключено
# ✅ Legal Database підключено
# ✅ LLM Orchestrator підключено (v5.0 - мозок бота)
# ✅ Ollama підключено
# ✅ RAG підключено
# ✅ Client Bot v4.0 Full готовий до запуску!
```

---

## 3️⃣ ТЕСТ В TELEGRAM

### Крок 1: Відкрити Telegram

### Крок 2: Знайти бота

(Той самий бот з токеном `8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0`)

### Крок 3: Відправити `/start`

**Очікується:**
```
Вітаємо! Оберіть дію:

👤 Ваше ім'я
🌐 Мова: Українська
🏳️ Статус: resident

[📤 Завантажити лист]
[📋 Історія листів]
[⚖️ Замовити перевірку адвоката]
[⚙️ Налаштування] [❓ Допомога]
```

### Крок 4: Натиснути "📤 Завантажити лист"

**Очікується:**
```
📤 Завантаження листа

Надішліть:
• 📷 Фото листа (якісне, рівне освітлення)
• 📄 Текст листа
• 📎 PDF файл

Порада: Для кращого розпізнавання фото має бути чітким.
```

### Крок 5: Надіслати фото німецького листа

(Наприклад, тестовий лист з `test_letters/`)

### Крок 6: Отримати аналіз

**Очікується (через 10-25 секунд):**
```
✅ Аналіз завершено!

🏢 Організація: Jobcenter Berlin Mitte
📋 Тип: Einladung
📚 Параграфи: § 59 SGB II, § 31 SGB II

🔍 Контактні дані:
📞 Телефони: +49 30 1234567

━━━━━━━━━━━━━━━━━━━━

📝 ВІДПОВІДЬ:

Шановний(а) одержувач(у),

Отримав(ла) Ваше запрошення на співбесіду...
(1000+ символів, професійна українська)

━━━━━━━━━━━━━━━━━━━━

🇩🇪 ГОТОВИЙ ЛИСТ НІМЕЦЬКОЮ (DIN 5008)

Цей лист можна скопіювати та відправити:

────────────────────

Sehr geehrte Damen und Herren,

Bestätigung des Eingangs der Einladung...
(500+ символів, німецька)

────────────────────

💡 Порада: Скопіюйте текст та відправте на email або поштою.

📄 **Готовий PDF-лист**
[Файл letter_chatid_timestamp.pdf]
```

---

## 4️⃣ ПЕРЕВІРКА LLM + RAG

```bash
# Зайти в контейнер
docker exec -it gov-de-bot bash

# Перевірити RAG базу
python -c "
import chromadb
from pathlib import Path
client = chromadb.PersistentClient(path='/app/data/chroma_db')
collection = client.get_collection(name='german_laws')
print(f'RAG законів: {collection.count()}')
"

# Має бути: 5,084 законів

# Перевірити Ollama (якщо запущено)
curl http://host.docker.internal:11434/api/tags

# Має бути: {"models": [{"name": "llama3.2:3b"}]}
```

---

## 5️⃣ ШВИДКІ КОМАНДИ

```bash
# Статус
docker compose ps

# Логи
docker compose logs -f gov-de-bot

# Зупинити
docker compose down

# Запустити
docker compose up -d

# Перезапустити
docker compose restart gov-de-bot

# Видалити все і зібрати заново
docker compose down
docker rmi govde-gov-de-bot:latest
docker compose build --no-cache
docker compose up -d
```

---

## 🐛 ЯКЩО ЩОСЬ НЕ ПРАЦЮЄ

### Бот не запускається:

```bash
# Переглянути логи
docker compose logs gov-de-bot

# Виправити і перезібрати
docker compose down
docker compose build --no-cache
docker compose up -d
```

### Ollama не підключено:

```bash
# Перевірити чи запущено Ollama
docker compose --profile llm ps

# Або локально
ollama list

# Запустити Ollama
ollama serve
```

### RAG база не знайдена:

```bash
# Перевірити наявність
ls -la data/chroma_db/

# Має бути chroma.sqlite3 (70 MB)
```

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ

| Компонент | Статус | Очікування |
|-----------|--------|------------|
| Docker контейнер | ✅ Up (healthy) | Працює |
| Telegram Bot | ✅ Responding | Відповідає на /start |
| OCR | ✅ Working | Розпізнає текст |
| Translator | ✅ Working | Перекладає |
| Legal Database | ✅ Connected | 67+ параграфів |
| RAG ChromaDB | ✅ Connected | 5,084 законів |
| Ollama LLM | ⚠️ Опціонально | Потрібен для аналізу |
| PDF Generator | ✅ Working | Генерує PDF |

---

**🎉 Якщо все працює - бот готовий до використання!**

---

*Створено: 13 березня 2026*
