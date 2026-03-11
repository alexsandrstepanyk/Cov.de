#!/bin/bash
# Gov.de System Check Script
# Перевірка всіх залежностей та готовності системи

echo "============================================================"
echo "  🧪 GOV.DE SYSTEM CHECK"
echo "============================================================"
echo ""

# Кольори
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Лічильники
PASS=0
FAIL=0
WARN=0

# Функція перевірки
check() {
    local name=$1
    local cmd=$2
    
    if eval $cmd > /dev/null 2>&1; then
        echo -e "${GREEN}✅${NC} $name"
        ((PASS++))
        return 0
    else
        echo -e "${RED}❌${NC} $name"
        ((FAIL++))
        return 1
    fi
}

# Функція попередження
warn() {
    local name=$1
    echo -e "${YELLOW}⚠️${NC} $name"
    ((WARN++))
}

echo "📦 СИСТЕМНІ ЗАЛЕЖНОСТІ"
echo "------------------------------------------------------------"

# Python
check "Python 3.9+" "python3 --version"
PYTHON_VERSION=$(python3 --version 2>&1 | cut -d' ' -f2)

# Pip
check "Pip" "pip3 --version"

# Tesseract
if check "Tesseract OCR" "tesseract --version"; then
    # Перевірка мов
    if tesseract --list-langs 2>&1 | grep -q "deu"; then
        echo -e "${GREEN}  ✅ Німецька мова (deu)${NC}"
    else
        echo -e "${RED}  ❌ Німецька мова відсутня${NC}"
        echo "     Встановити: brew install tesseract-lang"
    fi
    
    if tesseract --list-langs 2>&1 | grep -q "ukr"; then
        echo -e "${GREEN}  ✅ Українська мова (ukr)${NC}"
    else
        warn "Українська мова відсутня (опціонально)"
    fi
else
    echo "     Встановити: brew install tesseract tesseract-lang"
fi

# EasyOCR
if check "EasyOCR (Python)" "python3 -c 'import easyocr'"; then
    echo -e "${GREEN}  ✅ EasyOCR встановлено${NC}"
else
    echo "     Встановити: pip3 install easyocr"
fi

# OpenCV
if check "OpenCV (Python)" "python3 -c 'import cv2'"; then
    echo -e "${GREEN}  ✅ OpenCV встановлено${NC}"
else
    echo "     Встановити: pip3 install opencv-python-headless"
fi

# PyTesseract
check "PyTesseract (Python)" "python3 -c 'import pytesseract'"

# PIL/Pillow
check "Pillow (Python)" "python3 -c 'from PIL import Image'"

echo ""
echo "🐳 DOCKER"
echo "------------------------------------------------------------"

# Docker
if command -v docker &> /dev/null; then
    check "Docker" "docker --version"
    DOCKER_VERSION=$(docker --version 2>&1)
    echo "     $DOCKER_VERSION"
    
    # Docker running?
    if docker info &> /dev/null; then
        echo -e "${GREEN}  ✅ Docker запущено${NC}"
    else
        echo -e "${RED}  ❌ Docker не запущено${NC}"
        echo "     Запустіть Docker Desktop"
    fi
else
    echo -e "${RED}❌ Docker не встановлено${NC}"
    echo "   Встановити:"
    echo "   macOS: brew install --cask docker"
    echo "   або: https://docker.com/products/docker-desktop"
fi

# Docker Compose
if command -v docker-compose &> /dev/null; then
    check "Docker Compose" "docker-compose --version"
elif command -v docker &> /dev/null && docker compose version &> /dev/null 2>&1; then
    check "Docker Compose (plugin)" "docker compose version"
else
    echo -e "${RED}❌ Docker Compose не встановлено${NC}"
    echo "   Входить до складу Docker Desktop"
fi

echo ""
echo "📦 PYTHON ЗАЛЕЖНОСТІ"
echo "------------------------------------------------------------"

# Перевірка requirements.txt
if [ -f "requirements.txt" ]; then
    check "requirements.txt існує" "test -f requirements.txt"
    
    # Перевірка основних пакетів
    python3 -c "import spacy" 2>/dev/null && echo -e "${GREEN}  ✅ spacy${NC}" || echo -e "${RED}  ❌ spacy${NC}"
    python3 -c "import transformers" 2>/dev/null && echo -e "${GREEN}  ✅ transformers${NC}" || echo -e "${RED}  ❌ transformers${NC}"
    python3 -c "import torch" 2>/dev/null && echo -e "${GREEN}  ✅ torch${NC}" || echo -e "${RED}  ❌ torch${NC}"
    python3 -c "import googletrans" 2>/dev/null && echo -e "${GREEN}  ✅ googletrans${NC}" || echo -e "${RED}  ❌ googletrans${NC}"
    python3 -c "import telegram" 2>/dev/null && echo -e "${GREEN}  ✅ python-telegram-bot${NC}" || echo -e "${RED}  ❌ python-telegram-bot${NC}"
else
    echo -e "${RED}❌ requirements.txt не знайдено${NC}"
fi

echo ""
echo "📁 ФАЙЛИ ПРОЕКТУ"
echo "------------------------------------------------------------"

check "src/advanced_ocr.py" "test -f src/advanced_ocr.py"
check "src/advanced_translator.py" "test -f src/advanced_translator.py"
check "src/legal_database.py" "test -f src/legal_database.py"
check "src/cache.py" "test -f src/cache.py"
check "src/monitoring.py" "test -f src/monitoring.py"
check "src/ocr_integration.py" "test -f src/ocr_integration.py"
check ".env" "test -f .env"
check "Dockerfile" "test -f Dockerfile"
check "docker-compose.yml" "test -f docker-compose.yml"

echo ""
echo "🔐 ЗМІННІ ОТОВЧЕННЯ (.env)"
echo "------------------------------------------------------------"

if [ -f ".env" ]; then
    if grep -q "TELEGRAM_BOT_TOKEN" .env; then
        TOKEN=$(grep "TELEGRAM_BOT_TOKEN" .env | cut -d'=' -f2)
        if [ "$TOKEN" != "your_telegram_bot_token_here" ] && [ -n "$TOKEN" ]; then
            echo -e "${GREEN}✅ TELEGRAM_BOT_TOKEN налаштовано${NC}"
            ((PASS++))
        else
            echo -e "${YELLOW}⚠️ TELEGRAM_BOT_TOKEN потребує заміни${NC}"
            ((WARN++))
        fi
    else
        echo -e "${RED}❌ TELEGRAM_BOT_TOKEN відсутний${NC}"
        ((FAIL++))
    fi
    
    if grep -q "TWILIO_AUTH_TOKEN" .env; then
        TOKEN=$(grep "TWILIO_AUTH_TOKEN" .env | cut -d'=' -f2)
        if [ "$TOKEN" != "your_twilio_auth_token_here" ] && [ -n "$TOKEN" ]; then
            echo -e "${GREEN}✅ TWILIO_AUTH_TOKEN налаштовано${NC}"
            ((PASS++))
        else
            echo -e "${YELLOW}⚠️ TWILIO_AUTH_TOKEN потребує заміни${NC}"
            ((WARN++))
        fi
    fi
else
    echo -e "${RED}❌ .env файл відсутний${NC}"
    echo "   Скопіюйте: cp .env.example .env"
fi

echo ""
echo "============================================================"
echo "  📊 ПІДСУМКИ"
echo "============================================================"
echo -e "${GREEN}✅ Успішно:${NC} $PASS"
echo -e "${YELLOW}⚠️  Попередження:${NC} $WARN"
echo -e "${RED}❌ Проблем:${NC} $FAIL"
echo ""

if [ $FAIL -eq 0 ]; then
    echo -e "${GREEN}🎉 ВСЕ ГОТОВО!${NC}"
    echo ""
    echo "🚀 Запуск бота:"
    echo "   python3 src/bots/client_bot.py"
    echo ""
    echo "🐳 Запуск в Docker:"
    echo "   docker compose up --build"
else
    echo -e "${YELLOW}⚠️  Є проблеми які потрібно вирішити${NC}"
    echo ""
    echo "📝 Інструкції:"
    echo "   - Прочитайте DOCKER_QUICKSTART.md"
    echo "   - Прочитайте DEPLOYMENT_GUIDE.md"
fi

echo ""
echo "============================================================"

# Exit code
if [ $FAIL -eq 0 ]; then
    exit 0
else
    exit 1
fi
