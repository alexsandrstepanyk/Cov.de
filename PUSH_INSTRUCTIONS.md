# 📤 Інструкція для пушу на GitHub

## ✅ Віддалений репозиторій вже додано:
```
origin  https://github.com/alexsandrstepanyk/Cov.de.git
```

## 🔑 Крок 1: Налаштуйте аутентифікацію

### Варіант A: Через SSH (рекомендується)

1. **Створіть SSH ключ** (якщо ще немає):
```bash
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. **Додайте ключ до GitHub:**
```bash
cat ~/.ssh/id_ed25519.pub
```
Скопіюйте вивід і додайте на https://github.com/settings/keys

3. **Перевірте з'єднання:**
```bash
ssh -T git@github.com
```

### Варіант B: Через HTTPS з токеном

1. **Створіть Personal Access Token:**
   - Зайдіть на https://github.com/settings/tokens
   - Натисніть "Generate new token"
   - Виберіть scope: `repo`
   - Скопіюйте токен

2. **Використовуйте токен замість пароля** при пуші

## 🚀 Крок 2: Виконайте пуш

```bash
cd /Users/alex/Desktop/project/Gov.de

# Переконайтесь що ви на main
git checkout main

# Додайте всі зміни
git add -A

# Зробіть коміт (якщо є зміни)
git commit -m "v6.3 - Повний переклад інтерфейсу"

# Запуште на GitHub
git push -u origin main --force
```

## 📦 Що буде завантажено:

✅ **Код:**
- src/bots/client_bot.py (950+ рядків)
- src/smart_law_reference.py (850+ рядків)
- src/response_generator.py (570+ рядків)
- src/fraud_detection.py (430+ рядків)
- src/nlp_analysis.py (450+ рядків)

✅ **Документація:**
- README.md
- ROADMAP.md
- TEST_REPORT.md
- PUSH_TO_GITHUB.md
- VERSION files

✅ **Тести:**
- test_all_letters.py
- test_system.py
- test_letters.md

✅ **Конфігурація:**
- requirements.txt
- .gitignore

❌ **НЕ буде завантажено:**
- logs/ (логи)
- users.db (база даних)
- uploads/ (файли користувачів)
- .env (токени)

## 🎯 Швидка команда (якщо SSH налаштовано):

```bash
cd /Users/alex/Desktop/project/Gov.de && git push -u origin main --force
```

## 📊 Статистика проекту:

- **Версія:** 6.3
- **Комітів:** 40+
- **Тегів:** v3.0, v3.1, v3.2, v3.3, v4.0, v5.0, v5.1, v6.0, v6.1, v6.2, v6.3
- **Рядків коду:** ~4000+
- **Мови:** UA, RU, DE, EN

## 🔗 Посилання на репозиторій:

https://github.com/alexsandrstepanyk/Cov.de

---

**Після пушу:** Поділіться посиланням! 🚀
