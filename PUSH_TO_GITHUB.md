# 📤 Інструкція для пушу на GitHub

## Крок 1: Створіть репозиторій на GitHub

1. Зайдіть на https://github.com/new
2. Назва репозиторію: `Gov.de` або `gov-de-telegram-bot`
3. Опис: `Мультикраїновий Аналізатор Юридичних Листів Telegram Bot`
4. Тип: **Public** (рекомендується) або Private
5. **НЕ** ініціалізуйте з README, .gitignore, або license (вже є)
6. Натисніть **Create repository**

## Крок 2: Додайте віддалений репозиторій

Після створення GitHub покаже команду на кшталт:
```bash
git remote add origin https://github.com/ВАШ_НІК/Gov.de.git
```

Виконайте в терміналі:
```bash
cd /Users/alex/Desktop/project/Gov.de
git remote add origin https://github.com/ВАШ_НІК/Gov.de.git
```

## Крок 3: Перевірте

```bash
git remote -v
```

Має показати:
```
origin  https://github.com/ВАШ_НІК/Gov.de.git (fetch)
origin  https://github.com/ВАШ_НІК/Gov.de.git (push)
```

## Крок 4: Запуште

```bash
# Переконайтесь що ви на main гілці
git branch -M main

# Запуште всі зміни
git push -u origin main

# Або якщо є теги
git push --follow-tags origin main
```

## Крок 5: Перевірте на GitHub

Зайдіть на https://github.com/ВАШ_НІК/Gov.de
Переконайтесь що всі файли завантажились.

---

## ⚠️ Важливо: Токени ботів

Перед пушем **видаліть токени** з коду або створіть `.env` файл:

### Створіть .env файл:
```bash
cat > .env << 'ENVEOF'
# Telegram Bot Tokens
CLIENT_BOT_TOKEN=8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0
CORE_BOT_TOKEN=8204341583:AAFSPkKDrB6pbllz7CTKbRp7EVA9NbgfDJY
DE_BOT_TOKEN=8691230405:AAEPaEM4l2A6kzsxFHnnkY5ICtfLnYZDYJw
ENVEOF
```

### Додайте .env до .gitignore:
```bash
echo ".env" >> .gitignore
```

### Оновіть боти для використання .env:
```python
import os
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv('CLIENT_BOT_TOKEN')
```

---

## 📦 Що буде завантажено:

✅ **Код:** ~2500+ рядків Python
✅ **Документація:** README, ROADMAP, TEST_REPORT
✅ **Тести:** test_all_letters.py, test_system.py
✅ **Конфігурація:** requirements.txt, .gitignore
✅ **Версії:** VERSION, VERSION_3.1, VERSION_3

❌ **Не буде завантажено:**
- logs/ (логи)
- uploads/ (завантажені файли)
- users.db (база даних)
- .env (токени)
- __pycache__/ (кеш Python)

---

## 🎯 Швидкі команди:

```bash
# Додати віддалений репозиторій
git remote add origin https://github.com/ВАШ_НІК/Gov.de.git

# Запушити
git push -u origin main

# Перевірити статус
git status

# Переглянути логи
git log --oneline
```

---

**Після пушу:** Поділіться посиланням на репозиторій! 🚀
