#!/bin/bash
# Запуск всіх ботів Gov.de v4.1

echo "🚀 Запуск Gov.de Telegram ботів v4.1..."
echo ""

# Функція для перевірки процесу
check_python() {
    if ! command -v python3 &> /dev/null; then
        echo "❌ Помилка: python3 не знайдено"
        exit 1
    fi
}

# Перевірка Python
check_python

# Auto-install spaCy model
echo "📥 Перевірка spaCy моделей..."
python3 -m spacy validate de_core_news_sm 2>/dev/null
if [ $? -ne 0 ]; then
    echo "⬇️  Завантаження de_core_news_sm..."
    python3 -m spacy download de_core_news_sm
fi
echo ""

# Kill будь-яких існуючих ботів
echo "⏹️  Зупинка попередніх процесів..."
pkill -f "client_bot.py" 2>/dev/null || true
pkill -f "core_bot.py" 2>/dev/null || true
pkill -f "de_bot.py" 2>/dev/null || true
sleep 1

# Створення лог директорії
mkdir -p logs

echo ""
echo "📱 Запуск Client Bot..."
echo "   Лог: logs/client_bot.log"
python3 src/bots/client_bot.py > logs/client_bot.log 2>&1 &
CLIENT_PID=$!
echo "   PID: $CLIENT_PID"

sleep 2

echo "⚙️  Запуск Core Bot..."
echo "   Лог: logs/core_bot.log"
python3 src/bots/core_bot.py > logs/core_bot.log 2>&1 &
CORE_PID=$!
echo "   PID: $CORE_PID"

echo ""
echo "✅ Боти запущені!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "📋 ІНФОРМАЦІЯ"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "Client Bot PID: $CLIENT_PID"
echo "Core Bot PID: $CORE_PID"
echo ""
echo "📱 Telegram бот: @GovDeClientBot"
echo "   (або за токеном 8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0)"
echo ""
echo "📁 Лог файли:"
echo "   • logs/client_bot.log"
echo "   • logs/core_bot.log"
echo ""
echo "📊 Перегляд логів в реальному часі:"
echo "   tail -f logs/client_bot.log"
echo ""
echo "⏹️  Зупинка ботів:"
echo "   Ctrl+C або kill $CLIENT_PID $CORE_PID"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "🤖 Боти готові до роботи!"
echo ""

# Обробка Ctrl+C
trap "echo ''; echo '⏹️  Зупинка ботів...'; kill $CLIENT_PID $CORE_PID 2>/dev/null; echo '✅ Зупинено'; exit 0" INT

# Очікування
wait
