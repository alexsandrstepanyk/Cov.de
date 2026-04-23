# 🤖 RAG Інтеграція в Telegram Бота

## ✅ Що було зроблено

### 1. RAG База Даних
- **german_laws_general**: 16,133 записів (16 PDF кодексів)
- **german_laws_full**: 25,100 записів (повна база)
- **obsidian_rag_export**: 17 законів для візуалізації

### 2. Нові Модулі

#### `rag_law_search.py`
Пошук законів у ChromaDB RAG базі:
- `search_laws(query, n_results, collections)` - базовий пошук
- `search_laws_by_paragraph(law_name, paragraph)` - пошук параграфу
- `get_law_text(law_name, paragraph, max_chunks)` - отримання повного тексту
- `analyze_query_with_rag(query, language)` - аналіз запиту

#### `bot_rag_integration.py`
Інтеграція RAG пошуку в бота:
- `rag_search_handler(query, language)` - обробник запитів
- `search_paragraph(query, law_name, language)` - пошук параграфу
- `quick_law_reference(law_name, language)` - швидка довідка

### 3. Оновлений `client_bot.py`

#### Нові команди:
- `/law <запит>` - пошук закону
  - `/law BGB` - пошук по закону
  - `/law BGB § 196` - пошук параграфу
  - `/law Kündigung frist` - пошук по темі

- `/search <запит>` - розширений RAG пошук

#### Автоматичний пошук:
При завантаженні листа бот **автоматично** шукає закони в RAG базі та відправляє результати окремим повідомленням.

---

## 📊 Як це працює

### Автоматичний RAG пошук

```
Користувач → Завантажує лист (фото/PDF/текст)
     ↓
Бот → OCR/розпізнавання тексту
     ↓
RAG пошук → ChromaDB (german_laws_general + german_laws_full)
     ↓
Результат → Знайдені закони з текстом
     ↓
Відповідь → Користувач отримує:
            1. RAG результати (нові закони)
            2. Стандартний аналіз (smart_law_reference)
            3. Відповідь (response_generator)
```

### Приклад використання

**Користувач** завантажує лист з текстом:
```
Sehr geehrte Damen und Herren,
hiermit kündige ich meinen Mietvertrag fristgerecht zum 31.03.2024.
Mit freundlichen Grüßen
```

**Бот** знаходить в RAG базі:
```
✅ Знайдено законів: 2

📚 **BGB**
   Параграфи: § 573, § 573c, § 543
   Джерело: german_laws_general

📚 **BGB**
   Параграфи: § 535, § 543
   Джерело: german_laws_full

📖 **BGB - Повний текст:**
```
§ 573 Ordentliche Kündigung des Vermieters
(1) Der Vermieter kann nur kündigen, wenn...
```
```

---

## 🎯 Тестування

### Перевірка RAG пошуку:
```bash
cd /Users/alex/Desktop/project/Gov.de
python3 src/rag_law_search.py
```

### Перевірка Bot інтеграції:
```bash
cd /Users/alex/Desktop/project/Gov.de
python3 src/bot_rag_integration.py
```

### Запуск бота:
```bash
cd /Users/alex/Desktop/project/Gov.de
python3 -m src.bots.client_bot
```

---

## 📁 Структура файлів

```
Gov.de/
├── data/
│   └── legal_database_chroma/       # ChromaDB RAG база
│       ├── german_laws_general      # 16,133 записів
│       └── german_laws_full         # 25,100 записів
├── obsidian_rag_export/             # Obsidian база
│   ├── .obsidian/
│   ├── 00_RAG_Index.md
│   ├── BGB.md
│   ├── SGB_2.md
│   └── ... (17 законів)
├── src/
│   ├── rag_law_search.py            # RAG пошук
│   ├── bot_rag_integration.py       # Bot інтеграція
│   ├── bots/
│   │   └── client_bot.py            # Оновлений бот
│   └── smart_law_reference.py       # Стара система (залишена)
└── RAG_INTEGRATION.md               # Цей файл
```

---

## 🔧 Налаштування

### Зміна пріоритету колекцій:
```python
# В bot_rag_integration.py
results = search_laws(
    query,
    n_results=5,
    collections=['german_laws_general', 'german_laws_full']  # Пріоритет general
)
```

### Зміна розміру batch:
```python
# В upload_general_laws_to_rag.py
BATCH_SIZE = 200  # Збільшено для швидкості
```

---

## ⚠️ Важливо

1. **RAG пошук працює паралельно** зі старою системою (`smart_law_reference.py`)
2. **Стара система не видалена** - використовується як fallback
3. **RAG результати відправляються першими** - перед стандартним аналізом

---

## 🚀 Майбутні покращення

- [ ] Додати посилання між законами в Obsidian
- [ ] Інтеграція з LLM для кращих відповідей
- [ ] Кешування популярних запитів
- [ ] Статистика RAG пошуку
- [ ] Розширення бази новими кодексами

---

## 📞 Команди для користувачів

| Команда | Опис |
|---------|------|
| `/law <запит>` | Пошук закону по назві |
| `/search <запит>` | Розширений RAG пошук |
| `/jobcenter` | Швидка довідка Jobcenter |
| `/inkasso` | Швидка довідка Inkasso |
| `/miete` | Швидка довідка оренди |

---

**✅ RAG інтеграція завершена та готова до використання!**
