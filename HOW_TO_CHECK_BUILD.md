# 📊 ЯК ПЕРЕВІРИТИ DOCKER BUILD СТАТУС

## 🎯 ШВИДКІ КОМАНДИ

### 1. Перевірити чи завершено build

```bash
docker images | grep gov-de
```

**Якщо бачите:**
```
govde-gov-de-bot   latest   1.2GB   2 minutes ago   ✅ ГОТОВО
```

**Якщо нічого немає:**
```
❌ Ще будується
```

---

### 2. Перевірити процес build

```bash
# Спосіб 1: Процеси
ps aux | grep docker | grep -v grep

# Спосіб 2: Docker events
docker events --filter "type=image" --since 5m
```

---

### 3. Перевірити Compose статус

```bash
docker compose ps
```

**Якщо бачите:**
```
NAME           STATUS
gov-de-bot     Up    ✅ ГОТОВО
```

---

## 🔍 ДЕТИЛЬНІ КОМАНДИ

### Всі Docker images:

```bash
docker images
```

### Останні події Docker:

```bash
docker events --since 10m
```

### Build логи (якщо ще будується):

```bash
# Спробувати запустити знову (покаже де зупинилось)
docker compose build
```

### Перевірити місце на диску:

```bash
docker system df
```

---

## 📊 ІНТЕРПРЕТАЦІЯ РЕЗУЛЬТАТІВ

### ✅ BUILD ЗАВЕРШЕНО:

```bash
$ docker images | grep gov-de

govde-gov-de-bot   latest   1.23GB   3 minutes ago
```

**Наступна дія:**
```bash
docker compose up
```

---

### ⏳ BUILD ЩЕ ТРИВАЄ:

```bash
$ docker images | grep gov-de
(нічого)

$ ps aux | grep docker
... com.docker.build ...
```

**Що робити:**
- Зачекати ще 1-2 хвилини
- Не закривати термінал
- Не вимикати Docker Desktop

---

### ❌ BUILD ЗУПИНИВСЯ:

```bash
$ docker compose build
... error ...
```

**Що робити:**
```bash
# Очистити кеш
docker system prune -a

# Спробувати знову
docker compose build --no-cache
```

---

## 🎯 КОРИСНІ КОМАНДИ ДЛЯ МОНІТОРИНГУ

### 1. Watch режим (оновлення кожні 2с):

```bash
watch -n 2 "docker images | grep gov-de || echo 'Ще будується...'"
```

### 2. Лог подій:

```bash
docker events --filter "type=image" --filter "action=save"
```

### 3. Розмір образу:

```bash
docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}"
```

---

## 📝 ЩО ОЧІКУВАТИ

### Під час build:

```
Step 1/8: FROM python:3.11-slim          ✅ 30s
Step 2/8: RUN apt-get install...         ✅ 60s
Step 3/8: COPY requirements.txt          ✅ 1s
Step 4/8: RUN pip install...             ✅ 96s ← найдовше
Step 5/8: COPY src/                      ✅ 2s
Step 6/8: RUN mkdir...                   ✅ 1s
Step 7/8: RUN chmod...                   ✅ 1s
Step 8/8: Exporting image...             ⏳ 30s
```

### Після build:

```
✅ Successfully built abc123def456
✅ Successfully tagged govde-gov-de-bot:latest
```

---

## 🚀 ЩО РОБИТИ ПІСЛЯ BUILD

### 1. Перевірити:

```bash
docker images | grep gov-de
```

### 2. Запустити:

```bash
docker compose up
```

### 3. Або в фоні:

```bash
docker compose up -d
```

### 4. Переглянути логи:

```bash
docker compose logs -f
```

---

## 🐛 ЯКЩО ЩОСЬ НЕ ТАК

### Build завис:

```bash
# Натисніть Ctrl+C
# Перезапустіть Docker Desktop
# Спробуйте знову
docker compose build
```

### Немає місця:

```bash
# Очистити старі images
docker system prune -a

# Перевірити місце
df -h
```

### Помилка:

```bash
# Показати детальну помилку
docker compose build --progress=plain
```

---

**🎉 Build завершено коли бачите image в `docker images`!**
