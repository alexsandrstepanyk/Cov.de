# Gov.de Bot - Simple Dockerfile
# Telegram Bot v4.0 Full Integration

FROM python:3.11-slim

# Змінні оточення
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/app/src

WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y --no-install-recommends \
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    tesseract-ocr-ukr \
    tesseract-ocr-rus \
    libtesseract-dev \
    libleptonica-dev \
    poppler-utils \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Копіюємо requirements.txt
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --upgrade pip wheel setuptools && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir 'python-telegram-bot[job-queue]==20.7'

# Копіюємо код
COPY src/ ./src/
COPY data/legal_database.db ./data/legal_database.db

# Створюємо директорії
RUN mkdir -p /app/data /app/logs /app/uploads /app/storage/uploads && chmod -R 755 /app

# Запуск бота
CMD ["python", "src/bots/client_bot.py"]
