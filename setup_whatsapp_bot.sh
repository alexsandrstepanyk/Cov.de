#!/bin/bash
# ============================================================================
# Gov.de WhatsApp Bot v4.0 - Автоматичне Встановлення
# ============================================================================
# Цей скрипт встановлює всі залежності та налаштовує WhatsApp бота
# Версія: 1.0
# Дата: 2026-03-06
# ============================================================================

set -e  # Зупинити при помилці

# Кольори для виводу
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Лог файлу
LOG_FILE="logs/whatsapp_setup.log"
mkdir -p logs

# Функція логування
log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1" | tee -a "$LOG_FILE"
}

success() {
    echo -e "${GREEN}[$(date '+%Y-%m-%d %H:%M:%S')] ✅${NC} $1" | tee -a "$LOG_FILE"
}

warning() {
    echo -e "${YELLOW}[$(date '+%Y-%m-%d %H:%M:%S')] ⚠️${NC} $1" | tee -a "$LOG_FILE"
}

error() {
    echo -e "${RED}[$(date '+%Y-%m-%d %H:%M:%S')] ❌${NC} $1" | tee -a "$LOG_FILE"
}

# ============================================================================
# КРОК 1: Перевірка системи
# ============================================================================
echo ""
log "🔍 КРОК 1: Перевірка системи..."
echo ""

# Перевірка macOS
if [[ "$OSTYPE" == "darwin"* ]]; then
    success "macOS виявлено"
    PACKAGE_MANAGER="brew"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    success "Linux виявлено"
    if command -v apt-get &> /dev/null; then
        PACKAGE_MANAGER="apt"
    elif command -v yum &> /dev/null; then
        PACKAGE_MANAGER="yum"
    else
        PACKAGE_MANAGER="unknown"
    fi
else
    warning "Невідома ОС: $OSTYPE"
    PACKAGE_MANAGER="unknown"
fi

# Перевірка Python
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version)
    success "$PYTHON_VERSION виявлено"
else
    error "Python3 не знайдено! Встановіть Python 3.8+"
    exit 1
fi

# Перевірка pip
if command -v pip3 &> /dev/null; then
    PIP_VERSION=$(pip3 --version)
    success "pip3 виявлено: $PIP_VERSION"
else
    error "pip3 не знайдено!"
    exit 1
fi

# ============================================================================
# КРОК 2: Встановлення системних залежностей
# ============================================================================
echo ""
log "📦 КРОК 2: Встановлення системних залежностей..."
echo ""

# Tesseract OCR
if command -v tesseract &> /dev/null; then
    TESSERACT_VERSION=$(tesseract --version | head -1)
    success "Tesseract вже встановлено: $TESSERACT_VERSION"
else
    warning "Tesseract не знайдено. Встановлення..."
    
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install tesseract
        success "Tesseract встановлено через Homebrew"
    elif [[ "$PACKAGE_MANAGER" == "apt" ]]; then
        sudo apt-get update
        sudo apt-get install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
        success "Tesseract встановлено через apt"
    elif [[ "$PACKAGE_MANAGER" == "yum" ]]; then
        sudo yum install -y tesseract
        success "Tesseract встановлено через yum"
    else
        warning "Не вдалося автоматично встановити Tesseract"
        warning "Встановіть вручну: https://tesseract-ocr.github.io/tessdoc/Installation.html"
    fi
fi

# Перевірка мовних пакетів Tesseract
if command -v tesseract &> /dev/null; then
    if tesseract --list-langs | grep -q "deu"; then
        success "Німецька мова для Tesseract доступна"
    else
        warning "Німецька мова для Tesseract відсутня"
        if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
            brew install tesseract-lang
        elif [[ "$PACKAGE_MANAGER" == "apt" ]]; then
            sudo apt-get install -y tesseract-ocr-deu
        fi
    fi
fi

# Ngrok
if command -v ngrok &> /dev/null; then
    NGROK_VERSION=$(ngrok --version | head -1)
    success "Ngrok вже встановлено: $NGROK_VERSION"
else
    warning "Ngrok не знайдено. Встановлення..."
    
    if [[ "$PACKAGE_MANAGER" == "brew" ]]; then
        brew install ngrok
        success "Ngrok встановлено через Homebrew"
    elif [[ "$PACKAGE_MANAGER" == "apt" ]]; then
        wget https://bin.equinox.io/c/bNyj1mQVY4c/ngrok-v3-stable-linux-amd64.tgz
        sudo tar xvzf ngrok-v3-stable-linux-amd64.tgz -C /usr/local/bin
        rm ngrok-v3-stable-linux-amd64.tgz
        success "Ngrok встановлено"
    else
        warning "Встановіть Ngrok вручну: https://ngrok.com/download"
    fi
fi

# ============================================================================
# КРОК 3: Встановлення Python залежностей
# ============================================================================
echo ""
log "🐍 КРОК 3: Встановлення Python залежностей..."
echo ""

# Створення віртуального оточення (опціонально)
if [ ! -d "venv" ]; then
    log "Створення віртуального оточення..."
    python3 -m venv venv
    success "Віртуальне оточення створено"
else
    success "Віртуальне оточення вже існує"
fi

# Активація віртуального оточення
log "Активація віртуального оточення..."
source venv/bin/activate

# Встановлення основних залежностей
log "Встановлення WhatsApp залежностей..."
pip install --upgrade pip
pip install twilio flask python-dotenv

# Встановлення залежностей з requirements.txt
if [ -f "requirements.txt" ]; then
    log "Встановлення залежностей з requirements.txt..."
    pip install -r requirements.txt
    success "Всі Python залежності встановлено"
else
    warning "requirements.txt не знайдено"
fi

# Перевірка встановлених пакетів
echo ""
log "Перевірка встановлених пакетів..."
python3 -c "
import twilio
import flask
import dotenv
import pytesseract
from PIL import Image
print('✅ twilio:', twilio.__version__)
print('✅ flask:', flask.__version__)
print('✅ python-dotenv:', dotenv.__version__)
print('✅ pytesseract:', pytesseract.__version__)
print('✅ pillow:', Image.__version__)
"

# ============================================================================
# КРОК 4: Налаштування змінних оточення
# ============================================================================
echo ""
log "⚙️  КРОК 4: Налаштування змінних оточення..."
echo ""

if [ -f ".env" ]; then
    success ".env файл вже існує"
    
    # Перевірка наявності ключів
    if grep -q "TWILIO_ACCOUNT_SID" .env && grep -q "TWILIO_AUTH_TOKEN" .env; then
        success "Twilio облікові дані знайдено"
    else
        warning "Twilio облікові дані відсутні в .env"
    fi
else
    warning ".env файл не знайдено. Створення з .env.example..."
    
    if [ -f "src/whatsapp/.env.example" ]; then
        cp src/whatsapp/.env.example .env
        success ".env створено"
        warning "Відредагуйте .env і вставте свої Twilio облікові дані"
    else
        error "src/whatsapp/.env.example не знайдено"
    fi
fi

# ============================================================================
# КРОК 5: Створення структури директорій
# ============================================================================
echo ""
log "📁 КРОК 5: Створення структури директорій..."
echo ""

mkdir -p logs
mkdir -p uploads
mkdir -p data

success "Директорії створено: logs/, uploads/, data/"

# ============================================================================
# КРОК 6: Ініціалізація бази даних
# ============================================================================
echo ""
log "🗄️  КРОК 6: Ініціалізація бази даних..."
echo ""

python3 << 'EOF'
import sqlite3
from pathlib import Path

db_path = Path('users.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# Таблиця користувачів
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        whatsapp_id TEXT UNIQUE NOT NULL,
        phone_number TEXT,
        name TEXT,
        language TEXT DEFAULT 'uk',
        registered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        last_active TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
''')

# Таблиця листів
cursor.execute('''
    CREATE TABLE IF NOT EXISTS letters (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        document_type TEXT,
        organization TEXT,
        paragraphs TEXT,
        translation TEXT,
        response TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users (id)
    )
''')

# Таблиця багатосторінкових сесій
cursor.execute('''
    CREATE TABLE IF NOT EXISTS multi_page_sessions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        whatsapp_id TEXT NOT NULL,
        pages TEXT,
        current_page INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (whatsapp_id) REFERENCES users (whatsapp_id)
    )
''')

conn.commit()
conn.close()
print("✅ База даних ініціалізовано: users.db")
EOF

# ============================================================================
# КРОК 7: Перевірка коду бота
# ============================================================================
echo ""
log "🤖 КРОК 7: Перевірка коду бота..."
echo ""

if [ -f "src/whatsapp/whatsapp_bot.py" ]; then
    # Перевірка синтаксису
    if python3 -m py_compile src/whatsapp/whatsapp_bot.py; then
        success "whatsapp_bot.py - синтаксис вірний"
    else
        error "Помилка синтаксису в whatsapp_bot.py"
        exit 1
    fi
else
    error "src/whatsapp/whatsapp_bot.py не знайдено"
    exit 1
fi

# ============================================================================
# КРОК 8: Фінальна перевірка
# ============================================================================
echo ""
log "🎯 КРОК 8: Фінальна перевірка..."
echo ""

# Створення файлу перевірки
cat > check_status.py << 'EOF'
#!/usr/bin/env python3
"""Перевірка готовності WhatsApp Bot"""

import sys
from pathlib import Path

print("=" * 60)
print("🔍 ПЕРЕВІРКА ГОТОВНОСТІ WHATSAPP BOT")
print("=" * 60)

checks = {
    'Twilio': False,
    'Flask': False,
    'Tesseract': False,
    'База даних': False,
    'Код бота': False,
    '.env файл': False,
}

# Перевірка Twilio
try:
    import twilio
    checks['Twilio'] = True
    print(f"✅ Twilio: {twilio.__version__}")
except:
    print("❌ Twilio не встановлено")

# Перевірка Flask
try:
    import flask
    checks['Flask'] = True
    print(f"✅ Flask: {flask.__version__}")
except:
    print("❌ Flask не встановлено")

# Перевірка Tesseract
try:
    import pytesseract
    pytesseract.get_tesseract_version()
    checks['Tesseract'] = True
    print("✅ Tesseract: доступний")
except:
    print("❌ Tesseract не доступний")

# Перевірка бази даних
db_path = Path('users.db')
if db_path.exists():
    checks['База даних'] = True
    print("✅ База даних: існує")
else:
    print("❌ База даних відсутня")

# Перевірка коду бота
bot_path = Path('src/whatsapp/whatsapp_bot.py')
if bot_path.exists():
    checks['Код бота'] = True
    print("✅ Код бота: існує")
else:
    print("❌ Код бота відсутній")

# Перевірка .env
env_path = Path('.env')
if env_path.exists():
    checks['.env файл'] = True
    print("✅ .env файл: існує")
else:
    print("❌ .env файл відсутній")

print("")
print("=" * 60)
passed = sum(checks.values())
total = len(checks)
print(f"РЕЗУЛЬТАТ: {passed}/{total} перевірок пройдено")
print("=" * 60)

if passed == total:
    print("\n✅ ВСЕ ГОТОВО! Можна запускати бота.")
    print("\nКоманда для запуску:")
    print("  python3 src/whatsapp/whatsapp_bot.py")
    sys.exit(0)
else:
    print("\n⚠️  ДЕЯКІ ПЕРЕВІРКИ НЕ ПРОЙДЕНО")
    sys.exit(1)
EOF

python3 check_status.py

# ============================================================================
# ФІНАЛЬНЕ ПОВІДОМЛЕННЯ
# ============================================================================
echo ""
echo ""
success "🎉 ВСТАНОВЛЕННЯ ЗАВЕРШЕНО!"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📚 НАСТУПНІ КРОКИ:"
echo ""
echo "1️⃣  Налаштуйте Twilio WhatsApp Sandbox:"
echo "   - Зайдіть на: https://console.twilio.com/"
echo "   - Messaging → Try it out → Send a WhatsApp message"
echo "   - Активуйте Sandbox"
echo ""
echo "2️⃣  Запустіть бота:"
echo "   python3 src/whatsapp/whatsapp_bot.py"
echo ""
echo "3️⃣  Запустіть ngrok (в окремому терміналі):"
echo "   ngrok http 5000"
echo ""
echo "4️⃣  Налаштуйте вебхук в Twilio:"
echo "   - Вставте URL з ngrok: https://xxx.ngrok.io/whatsapp"
echo ""
echo "5️⃣  Тестуйте:"
echo "   - Надішліть WhatsApp на номер Sandbox"
echo "   - Напишіть: /start"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "📄 Документація:"
echo "   - WHATSAPP_SETUP.md - Повна інструкція"
echo "   - src/whatsapp/README_WHATSAPP.md - API документація"
echo "   - CHANGELOG_WHATSAPP.md - Історія змін"
echo ""
echo "🔧 Команди:"
echo "   - Запуск: python3 src/whatsapp/whatsapp_bot.py"
echo "   - Тести: python3 test_whatsapp_bot.py"
echo "   - Статус: python3 check_status.py"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
