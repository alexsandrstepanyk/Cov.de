# 🚀 ІНСТРУКЦІЯ ІЗ ЗАПУСКУ БОТА v4.0

## 📋 ПЕРЕД ЗАПУСКОМ

### 1. Перевірте встановлені залежності:
```bash
cd /Users/alex/Desktop/project/Gov.de
pip3 install -r requirements.txt
```

### 2. Переконайтесь що всі файли на місці:
```bash
ls -la src/bots/client_bot.py
ls -la src/advanced_ocr.py
ls -la src/advanced_translator.py
ls -la src/legal_database.py
ls -la data/legal_database.db
```

**Очікуваний результат:**
```
✅ src/bots/client_bot.py (1,315 рядків)
✅ src/advanced_ocr.py (18,446 байти)
✅ src/advanced_translator.py (23,286 байти)
✅ src/legal_database.py (40,103 байти)
✅ data/legal_database.db (73 KB)
```

---

## 🎯 ЗАПУСК БОТА

### Спосіб 1: Прямий запуск
```bash
cd /Users/alex/Desktop/project/Gov.de
python3 src/bots/client_bot.py
```

### Спосіб 2: Через скрипт
```bash
cd /Users/alex/Desktop/project/Gov.de
chmod +x run_all_bots.sh
./run_all_bots.sh
```

### Спосіб 3: В фоновому режимі (screen)
```bash
cd /Users/alex/Desktop/project/Gov.de
screen -S govbot
python3 src/bots/client_bot.py
# Ctrl+A, D для від'єднання
```

### Спосіб 4: В фоновому режимі (nohup)
```bash
cd /Users/alex/Desktop/project/Gov.de
nohup python3 src/bots/client_bot.py > bot.log 2>&1 &
# Перегляд логів: tail -f bot.log
```

---

## ✅ ПЕРЕВІРКА РОБОТИ

### 1. Знайдіть бота в Telegram:
- **Бот:** `@ClientCovde_bot`
- **Токен:** В файлі `src/bots/client_bot.py` (рядок 73)

### 2. Протестуйте основний функціонал:

#### Реєстрація:
```
1. Натисніть /start
2. Оберіть "📝 Реєстрація"
3. Введіть ім'я
4. Оберіть мову (🇺🇦 Українська / 🇩🇪 Deutsch)
5. Оберіть країну (🇩🇪 Німеччина)
6. Оберіть статус (🏠 Резидент / 🇩🇪 Громадянин)
```

#### Завантаження документу:
```
1. Натисніть "📤 Завантажити лист"
2. Надішліть фото німецького документу
3. Зачекайте на обробку
4. Отримайте аналіз
```

#### Тестування багатосторінковості:
```
1. Надішліть перше фото
2. Бот запитає "Чи є ще сторінки?"
3. Натисніть "📄 Надіслати ще сторінку"
4. Надішліть друге фото
5. Натисніть "✅ Все, аналізуй"
6. Отримайте об'єднаний аналіз
```

---

## 🔧 ВИРІШЕННЯ ПРОБЛЕМ

### Помилка: "No module named 'telegram'"
```bash
pip3 install python-telegram-bot
```

### Помилка: "No module named 'easyocr'"
```bash
pip3 install easyocr
```

### Помилка: "No module named 'googletrans'"
```bash
pip3 install googletrans==4.0.0-rc1
```

### Помилка: "Token invalid"
Перевірте токен в файлі `src/bots/client_bot.py` (рядок 73):
```python
BOT_TOKEN = "8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0"
```

### Бот не відповідає на фото
Перевірте логи:
```bash
tail -f bot.log
```

### OCR погано розпізнає текст
1. Переконайтесь що фото якісне
2. Спробуйте краще освітлення
3. Уникайте тіней та відблисків
4. Тримайте камеру рівно

---

## 📊 МОНІТОРИНГ

### Перегляд логів:
```bash
# В реальному часі
tail -f bot.log

# Останні 50 рядків
tail -n 50 bot.log

# Пошук помилок
grep "ERROR" bot.log
```

### Перевірка процесу:
```bash
# Знайти процес бота
ps aux | grep client_bot

# Зупинити бота
pkill -f client_bot.py

# Перезапустити
pkill -f client_bot.py && python3 src/bots/client_bot.py &
```

---

## 🆘 ТЕХНІЧНА ПІДТРИМКА

### Файли для діагностики:
- `bot.log` - логи бота
- `users.db` - база користувачів
- `data/legal_database.db` - база законів

### Контакти:
- **Розробник:** [Ваші контакти]
- **GitHub:** [Посилання на репозиторій]
- **Документація:** `README.md`, `ROADMAP.md`

---

## 📝 ОНОВЛЕННЯ

### З версії 3.x на 4.0:
```bash
# Зробити backup
cp src/bots/client_bot.py src/bots/client_bot_backup_3x.py

# Замінити файл
cp src/bots/client_bot_v4.py src/bots/client_bot.py

# Перезапустити бота
pkill -f client_bot.py
python3 src/bots/client_bot.py &
```

### Перевірка версії:
```bash
# В логах має бути:
# "Запуск Client Bot v4.0..."
# "✅ Client Bot v4.0 готовий до запуску!"
```

---

## ✅ ЧЕКЛИСТ ЗАПУСКУ

- [ ] Встановлено Python 3.8+
- [ ] Встановлено всі залежності (`pip3 install -r requirements.txt`)
- [ ] Файл `client_bot.py` оновлено до v4.0
- [ ] Токен бота правильний
- [ ] Бот запущений (`python3 src/bots/client_bot.py`)
- [ ] Бот відповідає на `/start`
- [ ] Реєстрація працює
- [ ] Завантаження фото працює
- [ ] OCR розпізнає текст
- [ ] Аналіз з законами працює
- [ ] Багатосторінкові документи працюють
- [ ] Переклад працює

---

## 🎯 НОВІ ФУНКЦІЇ v4.0

### Багатосторінкові документи:
```
1. Надішліть перше фото
2. Бот запитає "Чи є ще сторінки?"
3. Оберіть "📄 Надіслати ще сторінку"
4. Надішліть наступні фото
5. Оберіть "✅ Все, аналізуй"
```

### Розгорнуті відповіді:
- ✅ Закони та параграфи
- ✅ Наслідки невиконання
- ✅ Поради для користувача
- ✅ Двомовні відповіді (UA + DE)

### Advanced OCR:
- ✅ Попередня обробка фото
- ✅ Оцінка якості
- ✅ Кілька рушіїв (Tesseract + EasyOCR)

### Advanced Translator:
- ✅ Юридичний словник (50+ термінів)
- ✅ Кешування (7 днів)
- ✅ Кілька сервісів (Google + LibreTranslate)

---

**Створено:** 28 лютого 2026  
**Версія:** v4.0  
**Статус:** ✅ **ГОТОВО ДО ЗАПУСКУ**
