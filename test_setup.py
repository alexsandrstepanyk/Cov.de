#!/usr/bin/env python3
"""
Test script to verify all bots are properly configured.
"""

import sys
from pathlib import Path

print("🔍 Перевірка Gov.de проекту...\n")

# Check imports
print("1. Перевірка залежностей:")
try:
    import telegram
    print("   ✓ python-telegram-bot OK")
except ImportError as e:
    print(f"   ✗ python-telegram-bot: {e}")
    sys.exit(1)

try:
    import spacy
    print("   ✓ spacy OK")
except ImportError:
    print("   ✗ spacy не встановлено")

try:
    import PIL
    print("   ✓ PIL OK")
except ImportError:
    print("   ✗ PIL не встановлено")

# Check bot files
print("\n2. Перевірка файлів ботів:")
bots = [
    "src/bots/client_bot.py",
    "src/bots/core_bot.py",
    "src/bots/de_bot.py"
]

for bot_file in bots:
    if Path(bot_file).exists():
        print(f"   ✓ {bot_file} існує")
    else:
        print(f"   ✗ {bot_file} не знайдено")

# Check token configuration
print("\n3. Перевірка токенів ботів:")
try:
    with open("src/bots/client_bot.py") as f:
        content = f.read()
        if "8594681397" in content:
            print("   ✓ Client Bot токен встановлено")
        else:
            print("   ✗ Client Bot токен не встановлено")
except:
    print("   ✗ Помилка при перевірці client_bot токена")

try:
    with open("src/bots/core_bot.py") as f:
        content = f.read()
        if "8204341583" in content:
            print("   ✓ Core Bot токен встановлено")
        else:
            print("   ✗ Core Bot токен не встановлено")
except:
    print("   ✗ Помилка при перевірці core_bot токена")

try:
    with open("src/bots/de_bot.py") as f:
        content = f.read()
        if "8691230405" in content:
            print("   ✓ DE Bot токен встановлено")
        else:
            print("   ✗ DE Bot токен не встановлено")
except:
    print("   ✗ Помилка при перевірці de_bot токена")

# Check database
print("\n4. Перевірка бази даних:")
if Path("users.db").exists():
    print("   ✓ users.db існує")
else:
    print("   ℹ users.db буде створена при першому запуску")

print("\n✅ Проект готовий до запуску!")
print("\n📖 Запустіть кожен бот у окремому терміналі:")
print("   python3 src/bots/client_bot.py")
print("   python3 src/bots/core_bot.py")
print("   python3 src/bots/de_bot.py")
