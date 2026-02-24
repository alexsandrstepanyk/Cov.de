# 🚀 ШВИДКИЙ СТАРТ

## 1️⃣ Запуск бота

```bash
bash run_all_bots.sh
```

## 2️⃣ Знайдіть бота у Telegram

@GovDeClientBot

## 3️⃣ Натисніть /start

## 4️⃣ Зареєструйтесь

Введіть:
- Username
- Пароль
- Мова (Українська)
- Країна (Німеччина)
- Статус (Резидент)

## 5️⃣ Завантажте лист

Надішліть:
- 📷 Фото листа (чітке)
- 📄 Текст листа
- 📎 PDF файл

## 6️⃣ Отримайте аналіз

Бот надасть:
- ✅ Тип листа
- 📚 Закони
- ⚠️ Наслідки
- 📝 Відповідь

---

## 📊 Логи

```bash
tail -f logs/client_bot.log
```

## ⏹️ Зупинка

```bash
# Натисніть Ctrl+C у терміналі
# або
pkill -f client_bot.py
```

## 🆘 Проблеми?

```bash
# Перевірте тести
python3 test_system.py

# Перевірте spaCy
python3 -m spacy download de_core_news_sm

# Перезапустіть
bash run_all_bots.sh
```
