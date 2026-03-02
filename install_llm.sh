#!/bin/bash
# Quick Install Script for Gov.de Bot LLM System
# Встановлення Ollama + ChromaDB + залежності

echo "============================================================"
echo "  🦙 ВСТАНОВЛЕННЯ LLM СИСТЕМИ GOV.DE BOT v5.0"
echo "============================================================"

# Крок 1: Встановлення Ollama
echo ""
echo "1️⃣ ВСТАНОВЛЕННЯ OLLAMA..."

if command -v ollama &> /dev/null; then
    echo "✅ Ollama вже встановлено"
    ollama --version
else
    echo "⚠️ Ollama не встановлено - встановлюємо..."
    
    # macOS
    if [[ "$OSTYPE" == "darwin"* ]]; then
        if command -v brew &> /dev/null; then
            brew install ollama
        else
            echo "❌ Homebrew не знайдено"
            echo "Встановте: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
            exit 1
        fi
    else
        # Linux
        curl -fsSL https://ollama.com/install.sh | sh
    fi
fi

# Крок 2: Завантаження моделі
echo ""
echo "2️⃣ ЗАВАНТАЖЕННЯ МОДЕЛІ LLAMA 3.2..."

if ollama list | grep -q "llama3.2"; then
    echo "✅ Llama 3.2 вже завантажено"
else
    echo "⚠️ Завантаження Llama 3.2 3B (це може зайняти 5-10 хвилин)..."
    ollama pull llama3.2:3b
fi

# Крок 3: Встановлення Python пакетів
echo ""
echo "3️⃣ ВСТАНОВЛЕННЯ PYTHON ПАКЕТІВ..."

pip3 install ollama chromadb langchain langchain-community

# Крок 4: Запуск Ollama сервера
echo ""
echo "4️⃣ ЗАПУСК OLLAMA СЕРВЕРА..."

if pgrep -x "ollama" > /dev/null; then
    echo "✅ Ollama сервер вже запущено"
else
    echo "⚠️ Запуск Ollama сервера..."
    ollama serve &
    sleep 3
fi

# Крок 5: Створення RAG бази
echo ""
echo "5️⃣ СТВОРЕННЯ RAG БАЗИ КОДЕКСІВ..."

cd "$(dirname "$0")"
python3 src/setup_llm_database.py

# Крок 6: Тестування
echo ""
echo "6️⃣ ТЕСТУВАННЯ СИСТЕМИ..."

python3 src/test_llm_system.py

# Фінал
echo ""
echo "============================================================"
echo "  ✅ ВСТАНОВЛЕННЯ ЗАВЕРШЕНО!"
echo "============================================================"
echo ""
echo "Для запуску бота з LLM:"
echo "  1. Переконайтесь що Ollama працює: ollama serve"
echo "  2. Інтегруйте local_llm в client_bot.py"
echo "  3. Запустіть бота: python3 src/bots/client_bot.py"
echo ""
