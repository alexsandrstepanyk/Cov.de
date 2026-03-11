#!/bin/bash
# Запуск WhatsApp Bot v4.0

echo "🚀 Gov.de WhatsApp Bot v4.0"
echo "============================"
echo ""

# Перевірка Python
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 не знайдено!"
    exit 1
fi

echo "✅ Python3: $(python3 --version)"

# Перевірка залежностей
echo ""
echo "📦 Перевірка залежностей..."

REQUIRED_PACKAGES="twilio flask pillow pytesseract"
MISSING_PACKAGES=""

for package in $REQUIRED_PACKAGES; do
    if ! python3 -c "import $package" 2>/dev/null; then
        MISSING_PACKAGES="$MISSING_PACKAGES $package"
    fi
done

if [ -n "$MISSING_PACKAGES" ]; then
    echo "⚠️  Відсутні пакунки:$MISSING_PACKAGES"
    echo ""
    echo "Встановлення..."
    pip3 install twilio flask python-dotenv
fi

echo "✅ Залежності встановлено"

# Перевірка змінних оточення
echo ""
echo "🔑 Перевірка змінних оточення..."

if [ -f ".env" ]; then
    echo "✅ .env файл знайдено"
    export $(cat .env | grep -v '^#' | xargs)
else
    echo "⚠️  .env файл не знайдено. Використовуються змінні оточення."
fi

if [ -z "$TWILIO_ACCOUNT_SID" ]; then
    echo "❌ TWILIO_ACCOUNT_SID не встановлено!"
    exit 1
fi

if [ -z "$TWILIO_AUTH_TOKEN" ]; then
    echo "❌ TWILIO_AUTH_TOKEN не встановлено!"
    exit 1
fi

echo "✅ Змінні оточення налаштовано"

# Створення директорії для логів
echo ""
echo "📁 Створення директорій..."
mkdir -p logs
echo "✅ Директорії створено"

# Перевірка бази даних
echo ""
echo "🗄️  Перевірка бази даних..."
if [ ! -f "users.db" ]; then
    echo "⚠️  users.db не знайдено. Буде створено автоматично."
else
    echo "✅ База даних знайдено"
fi

# Запуск бота
echo ""
echo "🤖 Запуск WhatsApp Bot..."
echo ""
echo "Вебхук URL: http://0.0.0.0:5000/whatsapp"
echo "Health check: http://localhost:5000/health"
echo ""
echo "Для зупинки натисніть Ctrl+C"
echo ""

python3 src/whatsapp/whatsapp_bot.py
