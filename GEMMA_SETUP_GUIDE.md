# Gemma LLM Integration для Gov.de Bot

## 📋 Огляд

Проект оновлено для використання **Google Gemma** замість Llama 3.2. Gemma - це ефективна, легка модель, оптимізована для локального запуску.

### Переваги Gemma
- ✅ **Швидше** - легше модель (7B параметрів)
- ✅ **Менше пам'яті** - ~5GB VRAM замість 8GB
- ✅ **Локально** - працює на звичайних машинах
- ✅ **Точна** - достатньо потужна для юридичного аналізу
- ✅ **Дешевше** - з точки зору обчислювальних ресурсів

---

## 🚀 Швидкий старт

### 1️⃣ Завантажити Ollama

Якщо ще не встановлено:
```bash
# macOS/Linux
curl -fsSL https://ollama.ai/install.sh | sh

# Або скачайте з https://ollama.ai
```

### 2️⃣ Завантажити Gemma модель

```bash
ollama pull gemma:7b
```

**Для меньше пам'яті (якщо проблеми):**
```bash
ollama pull gemma:2b
```

### 3️⃣ Перевірити завантаження

```bash
ollama list
# Повинна показати: gemma:7b    5.2 GB
```

### 4️⃣ Запустити Ollama

```bash
ollama serve
# Ollama буде доступна на http://localhost:11434
```

### 5️⃣ Настройти проект

**Копіюємо `.env.example` в `.env`:**
```bash
cp .env.example .env
```

**Оновлюємо `.env` (якщо потрібно):**
```bash
DEFAULT_LLM_MODEL=gemma:7b
OLLAMA_BASE_URL=http://localhost:11434
```

### 6️⃣ Запустити бот

```bash
python src/bots/client_bot.py
```

---

## 📊 Порівняння моделей

| Модель | Параметри | VRAM | Швидкість | Точність |
|--------|-----------|------|-----------|----------|
| **Gemma 7B** | 7B | ~5GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| **Gemma 2B** | 2B | ~2GB | ⚡⚡⚡⚡ | ⭐⭐⭐ |
| Llama 3.2 3B | 3B | ~3GB | ⚡⚡⚡ | ⭐⭐⭐⭐ |
| Llama 2 70B | 70B | ~40GB | ⚡ | ⭐⭐⭐⭐⭐ |

**Рекомендація для цього проекту: Gemma 7B** ✅

---

## 🔍 Тестування

### Тест 1: Перевірити Ollama

```bash
curl http://localhost:11434/api/tags
```

Результат повинен містити `gemma:7b`

### Тест 2: Просто запит

```bash
curl -X POST http://localhost:11434/api/generate \
  -d '{"model":"gemma:7b","prompt":"Привіт!","stream":false}'
```

### Тест 3: Запустити тест системи

```bash
python src/test_llm_system.py
```

---

## 🛠️ Налаштування

### Параметри Gemma

Для мережі (у `src/local_llm.py`):

```python
'options': {
    'temperature': 0.1,        # Низька температура для точності
    'num_predict': 1500,       # Max токенів на відповідь
    'top_p': 0.8,             # Nucleus sampling
    'repeat_penalty': 2.5,     # Запобігання повторам
    'num_ctx': 8192,          # Context size Gemma
}
```

### Оточення

Змінні в `.env`:

```bash
# LLM модель
DEFAULT_LLM_MODEL=gemma:7b

# Ollama сервер
OLLAMA_BASE_URL=http://localhost:11434

# RAG база
CHROMA_DB_PATH=./data/chroma_db
```

---

## 🐛 Вирішення проблем

### ❌ Ошибка: "Ollama is not running"

```bash
# 1. Запустити Ollama
ollama serve

# 2. У іншому терміналі перевірити
curl http://localhost:11434/api/tags
```

### ❌ "Model not found"

```bash
# Завантажити модель
ollama pull gemma:7b

# Перевірити
ollama list
```

### ❌ "Out of memory"

Використати меньше модель:
```bash
DEFAULT_LLM_MODEL=gemma:2b
ollama pull gemma:2b
```

### ❌ Повільно працює

- ✅ Використовувати GPU (якщо є)
- ✅ Зменшити `num_ctx` з 8192 на 4096
- ✅ Спробувати `gemma:2b`

---

## 🏗️ Docker інтеграція

Якщо використовуєте Docker:

### 1️⃣ Ollama у Docker (рекомендується)

```bash
docker run -d --name ollama -p 11434:11434 ollama/ollama
docker exec ollama ollama pull gemma:7b
```

### 2️⃣ Запустити бот

```bash
docker-compose up -d
```

**`docker-compose.yml` успадкує `OLLAMA_BASE_URL=http://host.docker.internal:11434`**

---

## 📈 Оптимізація

### Для проекту Gov.de

1. **RAG пошук** - користується ChromaDB, не залежить від моделі ✅
2. **Gemma 7B** - достатньо для юридичного аналізу
3. **Температура 0.1** - точні, послідовні відповіді
4. **Context size 8k** - достатньо для писем + закони

### Кількість документів

```
✅ 65,186 німецьких законів у ChromaDB
✅ Семантичний пошук (vector embeddings)
✅ Швидкий доступ (<100ms на запит)
```

---

## 📝 Масштабування

### Якщо потрібна більша точність:

```bash
DEFAULT_LLM_MODEL=llama3.2:8b
ollama pull llama3.2:8b
```

### Якщо потрібна більша швидкість:

```bash
DEFAULT_LLM_MODEL=gemma:2b
ollama pull gemma:2b
```

---

## ✅ Перевірка

Перевірити, що все працює:

```bash
# 1. Ollama запущена
curl http://localhost:11434/api/tags

# 2. Gemma завантажена
ollama list | grep gemma

# 3. RAG база готова
ls data/chroma_db/

# 4. Бот запущений
python src/bots/client_bot.py
```

---

## 🔗 Посилання

- [Ollama](https://ollama.ai)
- [Google Gemma](https://ai.google.dev/gemma)
- [ChromaDB](https://www.trychroma.com)
- [Gov.de Bot](https://github.com/)

---

**✅ Готово! Gemma успішно інтегрована в проект.**
