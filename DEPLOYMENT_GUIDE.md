# 🚀 DEPLOYMENT GUIDE для Gov.de

**Версія:** 4.3  
**Статус:** ✅ ГОТОВО ДО ДЕПЛОЮ

---

## 📋 ВАРІАНТИ ДЕПЛОЮ

### 1. 🐳 Docker (РЕКОМЕНДОВАНО)

**Час:** 5-10 хвилин  
**Складність:** ⭐⭐  
**Вартість:** $5-10/місяць

```bash
# 1 команда для запуску
docker compose up -d --build
```

**Переваги:**
- ✅ Tesseract OCR включено
- ✅ Всі залежності працюють
- ✅ Легко масштабувати
- ✅ однаково всюди

**Інструкція:** `DOCKER_QUICKSTART.md`

---

### 2. 🖥️ VPS (Ubuntu/Debian)

**Час:** 15-20 хвилин  
**Складність:** ⭐⭐⭐  
**Вартість:** $5-10/місяць

#### Кроки:

```bash
# 1. Підключитися до сервера
ssh user@your-server-ip

# 2. Встановити залежності
sudo apt update
sudo apt install -y python3 python3-pip python3-venv
sudo apt install -y tesseract-ocr tesseract-ocr-deu tesseract-ocr-eng
sudo apt install -y libtesseract-dev libleptonica-dev
sudo apt install -y libgl1-mesa-glx libglib2.0-0
sudo apt install -y git curl

# 3. Клонувати проект
git clone <your-repo> gov-de
cd gov-de

# 4. Створити віртуальне оточення
python3 -m venv venv
source venv/bin/activate

# 5. Встановити залежності
pip install -r requirements.txt

# 6. Налаштувати .env
cp .env.example .env
nano .env  # Відредагувати токени

# 7. Запустити бота
nohup python3 src/bots/client_bot.py > nohup.out 2>&1 &

# 8. Перевірити
tail -f nohup.out
```

#### Auto-restart (systemd):

```bash
# Створити service файл
sudo nano /etc/systemd/system/gov-de-bot.service
```

```ini
[Unit]
Description=Gov.de Telegram Bot
After=network.target

[Service]
Type=simple
User=ubuntu
WorkingDirectory=/home/ubuntu/gov-de
Environment="PATH=/home/ubuntu/gov-de/venv/bin"
ExecStart=/home/ubuntu/gov-de/venv/bin/python3 src/bots/client_bot.py
Restart=always

[Install]
WantedBy=multi-user.target
```

```bash
# Увімкнути service
sudo systemctl daemon-reload
sudo systemctl enable gov-de-bot
sudo systemctl start gov-de-bot

# Перевірити статус
sudo systemctl status gov-de-bot

# Переглянути логи
sudo journalctl -u gov-de-bot -f
```

---

### 3. ☁️ Cloud Platforms

#### Heroku:

**Час:** 10 хвилин  
**Складність:** ⭐⭐  
**Вартість:** $7/місяць

```bash
# 1. Встановити Heroku CLI
brew install heroku/brew/heroku  # macOS
curl https://cli-assets.heroku.com/install.sh | sh  # Linux

# 2. Логін
heroku login

# 3. Створити додаток
heroku create gov-de-bot

# 4. Додати buildpacks
heroku buildpacks:add heroku/python
heroku buildpacks:add --index 1 https://github.com/heroku/heroku-buildpack-apt

# 5. Створити apt file (для Tesseract)
echo "tesseract-ocr" > Aptfile
echo "tesseract-ocr-deu" >> Aptfile
echo "tesseract-ocr-eng" >> Aptfile
git add Aptfile
git commit -m "Add Aptfile for Tesseract"

# 6. Налаштувати змінні
heroku config:set TELEGRAM_BOT_TOKEN=your_token
heroku config:set TWILIO_ACCOUNT_SID=your_sid
heroku config:set TWILIO_AUTH_TOKEN=your_token

# 7. Деплой
git push heroku main

# 8. Перевірити
heroku logs --tail
heroku ps
```

#### Railway.app:

**Час:** 5 хвилин  
**Складність:** ⭐  
**Вартість:** $5/місяць

```bash
# 1. Встановити Railway CLI
npm i -g @railway/cli

# 2. Логін
railway login

# 3. Ініціалізувати проект
railway init

# 4. Додати змінні оточення
railway variables set TELEGRAM_BOT_TOKEN=your_token

# 5. Деплой
railway up

# 6. Відкрити логи
railway logs
```

#### Render.com:

**Час:** 10 хвилин  
**Складність:** ⭐⭐  
**Вартість:** $7/місяць

```bash
# 1. Створити веб-сервіс на render.com
# 2. Підключити GitHub репозиторій
# 3. Додати змінні оточення
# 4. Build Command: pip install -r requirements.txt
# 5. Start Command: python src/bots/client_bot.py
```

---

## 🔐 БЕЗПЕКА

### Secrets Management:

```bash
# ❌ НЕ зберігайте токени в коді
# ❌ НЕ комітьте .env файл

# ✅ Використовуйте secrets manager
# Docker Secrets
echo "your_token" | docker secret create telegram_token -

# AWS Secrets Manager
aws secretsmanager create-secret --name gov-de/tokens

# HashiCorp Vault
vault kv put secret/gov-de telegram_token=your_token
```

### Environment Variables:

```bash
# ✅ Завжди використовуйте змінні оточення
import os
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')

# ✅ Перевіряйте наявність змінних
if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN not set!")
```

---

## 📊 МОНІТОРИНГ

### Health Checks:

```python
# В бота додати health endpoint
from flask import Flask
app = Flask(__name__)

@app.route('/health')
def health():
    return {'status': 'healthy', 'version': '4.3'}
```

### Logging:

```bash
# Docker
docker compose logs -f gov-de-bot

# Systemd
sudo journalctl -u gov-de-bot -f

# Heroku
heroku logs --tail

# Railway
railway logs
```

### Metrics:

```python
# Додати Prometheus metrics
from prometheus_client import Counter, Histogram

# Track requests
REQUESTS = Counter('bot_requests_total', 'Total bot requests')
RESPONSE_TIME = Histogram('bot_response_seconds', 'Bot response time')
```

---

## 🔄 CI/CD

### GitHub Actions:

```yaml
# .github/workflows/deploy.yml
name: Deploy to Production

on:
  push:
    branches: [ main ]

jobs:
  deploy:
    runs-on: ubuntu-latest
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Build Docker image
      run: docker build -t gov-de-bot .
    
    - name: Push to Registry
      run: |
        docker tag gov-de-bot registry.example.com/gov-de-bot:latest
        docker push registry.example.com/gov-de-bot:latest
    
    - name: Deploy to Server
      run: |
        ssh user@server "cd /app && docker compose pull && docker compose up -d"
```

---

## 🐛 ВИРІШЕННЯ ПРОБЛЕМ

### Бот не запускається:

```bash
# 1. Перевірити логи
docker compose logs gov-de-bot
# або
sudo journalctl -u gov-de-bot -f

# 2. Перевірити змінні оточення
docker compose config
# або
printenv | grep BOT

# 3. Перевірити права доступу
ls -la .env
chmod 600 .env

# 4. Перезапустити
docker compose restart
# або
sudo systemctl restart gov-de-bot
```

### Tesseract не працює:

```bash
# Перевірити наявність
docker exec gov-de-bot tesseract --version

# Перевірити мови
docker exec gov-de-bot tesseract --list-langs

# Має бути: deu, eng, ukr
```

### Пам'ять закінчується:

```bash
# Обмежити використання пам'яті
# В docker-compose.yml:
services:
  gov-de-bot:
    deploy:
      resources:
        limits:
          memory: 512M
```

---

## 📈 МАСШТАБУВАННЯ

### Horizontal Scaling:

```bash
# Запустити кілька копій
docker compose up --scale gov-de-bot=3

# З балансировником (nginx)
docker compose -f docker-compose.yml -f docker-compose.prod.yml up
```

### Database Scaling:

```bash
# Використовувати PostgreSQL замість SQLite
docker compose --profile database up

# Або зовнішня база (AWS RDS, etc.)
DATABASE_URL=postgresql://user:pass@host:5432/dbname
```

### Caching:

```bash
# Додати Redis для кешування
docker compose --profile cache up

# В коді використовувати Redis cache
from redis import Redis
cache = Redis(host='redis', port=6379)
```

---

## 💰 ВАРТІСТЬ

| Платформа | Місяць | Рік | Переваги |
|-----------|--------|-----|----------|
| **Docker VPS** | $5-10 | $60-120 | Повний контроль |
| **Heroku** | $7 | $84 | Легко |
| **Railway** | $5 | $60 | Дуже легко |
| **Render** | $7 | $84 | Хороший баланс |
| **AWS EC2** | $10-20 | $120-240 | Масштабовано |

---

## ✅ ЧЕКЛИСТ ДЕПЛОЮ

- [ ] Токени налаштовано в .env
- [ ] Tesseract встановлено
- [ ] Всі залежності працюють
- [ ] Бот запускається
- [ ] логи працюють
- [ ] Health check налаштовано
- [ ] Auto-restart увімкнено
- [ ] Моніторинг працює
- [ ] Backup налаштовано

---

## 🎯 РЕКОМЕНДАЦІЇ

### Для старту:
```
✅ Docker (локально)
✅ Railway.app (продакшен)
```

### Для зростання:
```
✅ Docker + VPS (продакшен)
✅ PostgreSQL (база даних)
✅ Redis (кешування)
```

### Для великих навантажень:
```
✅ Kubernetes
✅ AWS/GCP/Azure
✅ Load Balancer
✅ Multiple replicas
```

---

**🚀 ГОТОВО ДО ДЕПЛОЮ!**

---

*Останнє оновлення: 10 березня 2026*  
*Версія: 4.3*
