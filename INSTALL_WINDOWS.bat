@echo off
setlocal enabledelayedexpansion

:: ============================================================================
:: Gov.de Bot v4.5 - One-Click Installation Script
:: Автоматична установка всього необхідного для Telegram бота
:: Windows 10/11
:: ============================================================================

echo.
echo ============================================================================
echo   Gov.de Bot v4.5 - Автоматична Установка
echo   Встановить: Python, залежності, налаштує автозапуск
echo ============================================================================
echo.

:: Перевірка прав адміністратора
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [!] Будь ласка, запусти від імені адміністратора!
    echo Права клік на скрипті -^> "Run as administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Права адміністратора підтверджено
echo.

:: ============================================================================
:: Крок 1: Встановлення Python
:: ============================================================================

echo [1/7] Перевірка Python...

python --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Python вже встановлено
    python --version
) else (
    echo [!] Python не знайдено. Встановлюємо...
    
    :: Завантаження Python 3.9.13
    echo [i] Завантаження Python 3.9.13...
    curl -L -o "%TEMP%\python-installer.exe" "https://www.python.org/ftp/python/3.9.13/python-3.9.13-amd64.exe"
    
    :: Тиха установка
    echo [i] Встановлення Python...
    "%TEMP%\python-installer.exe" /quiet InstallAllUsers=1 PrependPath=1 Include_test=0
    
    :: Очищення
    del "%TEMP%\python-installer.exe"
    
    echo [OK] Python встановлено!
)

echo.

:: ============================================================================
:: Крок 2: Перевірка Git
:: ============================================================================

echo [2/7] Перевірка Git...

git --version >nul 2>&1
if %errorLevel% equ 0 (
    echo [OK] Git вже встановлено
    git --version
) else (
    echo [!] Git не знайдено. Встановлюємо...
    
    :: Завантаження Git
    curl -L -o "%TEMP%\git-installer.exe" "https://github.com/git-for-windows/git/releases/download/v2.40.1.windows.1/Git-2.40.1-64-bit.exe"
    
    :: Тиха установка
    "%TEMP%\git-installer.exe" /VERYSILENT /NORESTART /NOCANCEL /SP- /CLOSEONEXIT=1 /COMPONENTS="icons,ext\reg\shellhere,assoc,assoc_sh"
    
    :: Очищення
    del "%TEMP%\git-installer.exe"
    
    echo [OK] Git встановлено!
)

:: Оновлення змінних середовища
set "PATH=%PATH%;C:\Program Files\Git\cmd"

echo.

:: ============================================================================
:: Крок 3: Створення папки бота
:: ============================================================================

echo [3/7] Створення папки бота...

set "BOT_DIR=C:\gov-de-bot"

if exist "%BOT_DIR%" (
    echo [OK] Папка вже існує: %BOT_DIR%
) else (
    mkdir "%BOT_DIR%"
    echo [OK] Папку створено: %BOT_DIR%
)

cd /d "%BOT_DIR%"

echo.

:: ============================================================================
:: Крок 4: Завантаження проекту
:: ============================================================================

echo [4/7] Завантаження проекту...

if exist ".git" (
    echo [OK] Проект вже завантажено. Оновлення...
    git pull origin v4.0-final
) else (
    echo [i] Завантаження з GitHub...
    git clone https://github.com/alexsandrstepanyk/Cov.de.git .
)

echo [OK] Проект готовий

echo.

:: ============================================================================
:: Крок 5: Встановлення залежностей
:: ============================================================================

echo [5/7] Встановлення залежностей...

:: Створення requirements.txt якщо немає
if not exist "requirements.txt" (
    echo [!] Створення requirements.txt...
    (
        echo python-telegram-bot==20.7
        echo googletrans==4.0.0-rc1
        echo pytesseract
        echo pillow
        echo easyocr
        echo pdfminer.six
        echo spacy
        echo werkzeug
        echo python-dotenv
    ) > requirements.txt
)

:: Встановлення залежностей
echo [i] Встановлення Python пакетів...
pip install --upgrade pip
pip install -r requirements.txt

:: Завантаження Tesseract OCR
echo [i] Встановлення Tesseract OCR...
if not exist "C:\Program Files\Tesseract-OCR\tesseract.exe" (
    curl -L -o "%TEMP%\tesseract-installer.exe" "https://github.com/UB-Mannheim/tesseract/releases/download/v5.3.3/tesseract-ocr-w64-setup-5.3.3.20231005.exe"
    "%TEMP%\tesseract-installer.exe" /SILENT
    del "%TEMP%\tesseract-installer.exe"
    echo [OK] Tesseract встановлено
) else (
    echo [OK] Tesseract вже встановлено
)

:: Додавання Tesseract в PATH
setx PATH "%PATH%;C:\Program Files\Tesseract-OCR" /M

:: Завантаження мовних пакетів для Tesseract
echo [i] Завантаження мовних пакетів Tesseract...
curl -L -o "%TEMP%\tesseract-deu-eng.zip" "https://github.com/tesseract-ocr/tessdata/raw/main/deu.traineddata"
curl -L -o "%TEMP%\tesseract-eng.zip" "https://github.com/tesseract-ocr/tessdata/raw/main/eng.traineddata"

:: Копіювання в папку Tesseract
if exist "C:\Program Files\Tesseract-OCR\tessdata" (
    copy /Y "%TEMP%\tesseract-deu.zip" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
    copy /Y "%TEMP%\tesseract-eng.zip" "C:\Program Files\Tesseract-OCR\tessdata\" >nul 2>&1
)

:: Очищення
del "%TEMP%\tesseract-*.zip" 2>nul

echo [OK] Залежності встановлено

echo.

:: ============================================================================
:: Крок 6: Налаштування .env файлу
:: ============================================================================

echo [6/7] Налаштування конфігурації...

if exist ".env" (
    echo [OK] .env файл вже існує
) else (
    echo [i] Створення .env файлу...
    (
        echo BOT_TOKEN=8594681397:AAE7Y2OsQI8DOAK44Subfw8NwAf0ITgtqY0
        echo LOG_LEVEL=INFO
    ) > .env
    echo [OK] .env файл створено
)

echo.

:: ============================================================================
:: Крок 7: Налаштування автозапуску
:: ============================================================================

echo [7/7] Налаштування автозапуску...

:: Створення batch файлу для запуску
echo [i] Створення start-bot.bat...
(
    echo @echo off
    echo cd /d %BOT_DIR%\src\bots
    echo python client_bot.py
    echo pause
) > "%BOT_DIR%\start-bot.bat"

:: Створення VBScript для прихованого запуску
echo [i] Створення run-hidden.vbs...
(
    echo Set objShell = CreateObject^("WScript.Shell"^)
    echo objShell.Run "cmd /c cd /d %BOT_DIR%\src\bots ^&^& python client_bot.py", 0, False
) > "%BOT_DIR%\run-hidden.vbs"

:: Додавання в автозапуск через Task Scheduler
echo [i] Створення завдання в Task Scheduler...

:: Видалення старого завдання якщо є
schtasks /Delete /TN "Gov.de Bot" /F >nul 2>&1

:: Створення нового завдання
schtasks /Create /TN "Gov.de Bot" /TR "\"%BOT_DIR%\run-hidden.vbs\"" /SC ONLOGON /RL HIGHEST /F

echo [OK] Автозапуск налаштовано

echo.

:: ============================================================================
:: Завершення
:: ============================================================================

echo ============================================================================
echo   ВСТАНОВКА ЗАВЕРШЕНА!
echo ============================================================================
echo.
echo [OK] Python встановлено
echo [OK] Git встановлено
echo [OK] Проект завантажено в: %BOT_DIR%
echo [OK] Залежності встановлено
echo [OK] Tesseract OCR встановлено
echo [OK] Автозапуск налаштовано
echo.
echo ============================================================================
echo   ЩО ДАЛІ:
echo ============================================================================
echo.
echo 1. Перший запуск:
echo    - Двічі клікни на "start-bot.bat" в папці: %BOT_DIR%
echo    - АБО бот запуститься автоматично при наступному вході в систему
echo.
echo 2. Перевірка:
echo    - Відкрий Telegram
echo    - Знайди свого бота
echo    - Напиши /start
echo.
echo 3. Управління:
echo    - Зупинити: Task Manager -^> Details -^> python.exe -^> End Task
echo    - Запустити: двічі клікни на start-bot.bat
echo    - Автозапуск: вже налаштовано!
echo.
echo 4. Логи:
echo    - Папка з логами: %BOT_DIR%\logs\
echo.
echo ============================================================================
echo.
echo [i] Бажаєш запустити бота зараз?
set /p RUN="Введіть Y для запуску або будь-яку клавішу для виходу: "

if /i "%RUN%"=="Y" (
    echo [i] Запуск бота...
    cd /d "%BOT_DIR%\src\bots"
    start "Gov.de Bot" python client_bot.py
    echo [OK] Бот запущено!
    echo.
    echo Перевір в Telegram!
) else (
    echo [OK] Бот запуститься автоматично при наступному вході в систему
)

echo.
pause
