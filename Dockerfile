# Gov.de Bot Docker Image
# Німецький юридичний бот з OCR та перекладом

FROM python:3.11-slim

# Мітки
LABEL maintainer="Gov.de Team"
LABEL version="4.3"
LABEL description="German Legal Document Analyzer Bot"

# Змінні оточення
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    DEBIAN_FRONTEND=noninteractive

# Робоча директорія
WORKDIR /app

# Встановлення системних залежностей
RUN apt-get update && apt-get install -y --no-install-recommends \
    # Tesseract OCR з німецькою мовою
    tesseract-ocr \
    tesseract-ocr-deu \
    tesseract-ocr-eng \
    tesseract-ocr-ukr \
    libtesseract-dev \
    libleptonica-dev \
    \
    # OpenCV залежності
    libgl1-mesa-glx \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgomp1 \
    \
    # Poppler для PDF
    poppler-utils \
    \
    # Інші утиліти
    git \
    curl \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Копіюємо requirements.txt
COPY requirements.txt .

# Встановлення Python залежностей
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Копіюємо код проекту
COPY src/ ./src/
COPY data/ ./data/
COPY logs/ ./logs/
COPY uploads/ ./uploads/

# Створюємо директорії для даних
RUN mkdir -p /app/data /app/logs /app/uploads /app/test_letters

# Встановлюємо права доступу
RUN chmod -R 755 /app

# Порт для Flask (якщо використовується вебхук)
EXPOSE 5000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; sys.path.insert(0, 'src'); from monitoring import get_health_checker; print('OK')" || exit 1

# Команда запуску
CMD ["python", "src/bots/client_bot.py"]
