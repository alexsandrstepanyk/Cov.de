# 🦙 ВСТАНОВЛЕННЯ OLLAMA ТА LLM СИСТЕМИ
## Gov.de Bot - Local LLM Integration

---

## 📦 КРОК 1: ВСТАНОВЛЕННЯ OLLAMA

### macOS:
```bash
# Встановити через Homebrew
brew install ollama

# АБО завантажити з сайту
curl -fsSL https://ollama.com/install.sh | sh
```

### Перевірка:
```bash
ollama --version
# Очікуваний результат: ollama version 0.5.x
```

---

## 📦 КРОК 2: ЗАВАНТАЖЕННЯ МОДЕЛЕЙ

### Основна модель (Llama 3.2 - найкраща для німецької):
```bash
ollama pull llama3.2:3b
```

### Альтернативні моделі:
```bash
# Mistral (добра для юридичних текстів)
ollama pull mistral:7b

# Phi-3 (швидка, компактна)
ollama pull phi3:3.8b

# Німецька спеціалізована
ollama pull llama3.1:8b
```

---

## 📦 КРОК 3: ЗАПУСК OLLAMA

### В фоновому режимі:
```bash
# Запустити сервер
ollama serve

# В фоновому режимі (macOS/Linux)
nohup ollama serve > ollama.log 2>&1 &
```

### Перевірка:
```bash
curl http://localhost:11434/api/version
```

---

## 📦 КРОК 4: ВСТАНОВЛЕННЯ PYTHON ПАКЕТІВ

```bash
cd /Users/alex/Desktop/project/Gov.de
pip3 install ollama chromadb langchain langchain-community
```

---

## 📦 КРОК 5: СТВОРЕННЯ БАЗИ КОДЕКСІВ

### Запустити скрипт імпорту кодексів:
```bash
python3 src/setup_llm_database.py
```

Це створить:
- Векторну базу даних з німецькими кодексами
- 18 кодексів (BGB, SGB, AO, ZPO тощо)
- 67+ параграфів з описами

---

## 📦 КРОК 6: ТЕСТУВАННЯ

```bash
python3 src/test_llm_system.py
```

Очікуваний результат:
```
✅ Ollama підключено
✅ Модель llama3.2:3b завантажена
✅ Аналіз виконано
✅ Відповідь згенеровано
```

---

## 📦 КРОК 7: ІНТЕГРАЦІЯ В БОТА

### Замінити в client_bot.py:
```python
# Стара логіка:
from smart_law_reference import analyze_letter_smart

# Нова логіка:
from local_llm import analyze_letter_llm, generate_response_llm
```

---

## ⚙️ КОНФІГУРАЦІЯ

### Файл: `config/llm_config.json`
```json
{
  "model": "llama3.2:3b",
  "temperature": 0.3,
  "max_tokens": 2000,
  "context_window": 4096,
  "rag_enabled": true,
  "database_path": "data/legal_database_chroma"
}
```

---

## 🚀 ШВИДКИЙ ЗАПУСК

```bash
# 1. Встановити Ollama
brew install ollama

# 2. Завантажити модель
ollama pull llama3.2:3b

# 3. Запустити сервер
ollama serve &

# 4. Створити базу кодексів
python3 src/setup_llm_database.py

# 5. Тест
python3 src/test_llm_system.py

# 6. Запустити бота
python3 src/bots/client_bot.py
```

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ

### До LLM:
```
❌ [ВІДПРАВНИК]
❌ [МІСТО]
❌ [НОМЕР]
❌ 300 символів
```

### Після LLM:
```
✅ Maria Schmidt
✅ Berlin
✅ 123ABC456
✅ 1000+ символів
✅ Повна німецька версія
```

---

## 🛠️ ВИРІШЕННЯ ПРОБЛЕМ

### Ollama не запускається:
```bash
# Перевірити порт
lsof -i :11434

# Вбити процес
killall ollama

# Перезапустити
ollama serve
```

### Модель не завантажується:
```bash
# Видалити і завантажити знову
ollama rm llama3.2:3b
ollama pull llama3.2:3b
```

### Повільна робота:
```bash
# Використати меншу модель
ollama pull phi3:3.8b

# Або зменшити контекст
# В llm_config.json: "context_window": 2048
```

---

**Створено:** 2 березня 2026  
**Версія:** LLM v1.0  
**Статус:** Готово до встановлення
