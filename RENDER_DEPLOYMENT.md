## 🚀 РАЗВЕРТЫВАНИЕ НА RENDER.COM

### 📋 Предварительные требования:
- GitHub аккаунт (у вас уже есть: `alexsandrstepanyk/Cov.de`)
- Render аккаунт (бесплатно: https://render.com)
- Telegram Bot Token (уже есть в `.env`)

---

## ⚡ БЫСТРОЕ РАЗВЕРТЫВАНИЕ (5 минут):

### 1️⃣ Создать Background Service на Render

1. Перейти на https://render.com
2. Нажать **"New +"** → **"Background Worker"**
3. Выбрать **"Connect a Repository"**
4. Найти репозиторий: `alexsandrstepanyk/Cov.de`
5. Нажать **"Connect"**

### 2️⃣ Настройки Background Service

```
Name:              gov-de-bot
Environment:       Python
Build Command:     pip install -r requirements.txt
Start Command:     python src/bots/client_bot.py
```

### 3️⃣ Добавить Environment Variables

Нажать **"Add Environment Variable"** и добавить:

``` 
TELEGRAM_BOT_TOKEN=<your_telegram_bot_token>
TWILIO_ACCOUNT_SID=<your_twilio_account_sid>
TWILIO_AUTH_TOKEN=<your_twilio_auth_token>
TWILIO_WHATSAPP_NUMBER=whatsapp:+14155238886
OLLAMA_BASE_URL=http://localhost:11434
DATABASE_PATH=./data/legal_database.db
CHROMA_DB_PATH=./data/chroma_db
FLASK_DEBUG=False
```

### 4️⃣ Запустить сервис

Нажать **"Create Background Service"** - Render автоматически:
- Клонирует репозиторий
- Установит зависимости
- Запустит бота

---

## 📊 СТАТУС И МОНИТОРИНГ

После создания вы сможете:
- **Просмотреть логи**: На странице сервиса → "Logs"
- **Остановить/Перезагрузить**: Кнопки на странице сервиса
- **Просмотреть здоровье**: "Health" tab

### Ожидаемые логи при запуске:

```
✅ Client Bot v4.1 готовий до запуску!
✅ LLM Orchestrator підключено (v5.0 - мозок бота)
✅ RAG команди додано: /law, /search
Telegram API підключено
Application started
```

---

## 💡 ВАЖНО ДЛЯ RENDER:

### ✅ Что работает:
- Telegram Bot (polling mode) ✓
- OCR обработка изображений ✓
- Переклад тексту ✓
- LLM анализ ✓
- PDF генерация ✓

### ⚠️ Ограничения Free Plan:
- **750 часов/месяц** → достаточно для 24/7 (730 часов)
- Может быть задержка на холодный запуск
- При неактивности 15+ минут процесс может спать (но это нормально для polling)

### 🔧 Если бот перестанет отвечать:
1. Перейти на страницу сервиса на Render
2. Нажать **"Manual Deploy"** → **"Deploy latest commit"**
3. Или проверить логи на ошибки

---

## 🎯 ДЕМОНСТРАЦИЯ ЗАВТРА:

Когда развернете на Render, просто:
1. Откройте Telegram и напишите боту `/start`
2. Загрузите любое немецкое письмо (фото или текст)
3. Бот автоматически:
   - Распознает текст через OCR
   - Переведет на украинский/русский
   - Сделает полный анализ письма
   - Предложит готовую немецкую ответ в формате DIN 5008
   - Сгенерирует PDF файл

---

## 📞 КОНТАКТЫ И ПОМОЩЬ:

Если что-то не работает:
1. Проверьте логи на Render (вкладка "Logs")
2. Убедитесь что все Environment Variables добавлены
3. Нажмите "Manual Deploy" для перезагрузки

Бот уже полностью готов к продакшену! ✨
