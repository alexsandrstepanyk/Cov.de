# 🧹 DOCKER CLEANUP - Очищення кешу

## 📊 ПОТОЧНИЙ СТАН

```
✅ Готовий image: 1 (govde-gov-de-bot)
⚠️ Build cache: 3.18GB (зайве!)
⚠️ Dangling images: 1
```

---

## 🔍 ЧОМУ ТАК БАГАТО?

### Під час build Docker створює:

```
1. Проміжні шари (layers)
2. Build cache
3. Dangling images (помилкові/старі)
4. BuildKit cache
```

**Ваш випадок:**
```
Build cache: 3.18GB
Dangling: 1 image
```

Це **нормально** після першого build!

---

## 🧹 ЯК ОЧИСТИТИ

### Команда 1: Очистити build cache (безпечно)

```bash
docker builder prune -a -f
```

**Звільнить:** ~3GB

**Безпечно:** ✅ Так (не впливає на готові images)

---

### Команда 2: Очистити dangling images

```bash
docker image prune -f
```

**Звільнить:** ~100-500MB

**Безпечно:** ✅ Так

---

### Команда 3: Повне очищення (обережно!)

```bash
docker system prune -a -f
```

**Звільнить:** ~3-5GB

**Безпечно:** ⚠️ Ні! Видалить ВСІ images, не тільки dangling

---

## ✅ РЕКОМЕНДОВАНЕ ОЧИЩЕННЯ

### Безпечне (зараз):

```bash
# 1. Очистити build cache
docker builder prune -a -f

# 2. Очистити dangling images
docker image prune -f

# 3. Перевірити результат
docker images
```

**Звільнить:** ~3GB  
**Безпечно:** ✅ Так

---

## 📊 РЕЗУЛЬТАТ

### До очищення:
```
Images: 1 (3.18GB)
Build Cache: 3.18GB
Dangling: 1
────────────────────
Total: ~6.5GB
```

### Після очищення:
```
Images: 1 (3.18GB) ✅
Build Cache: 0GB ✅
Dangling: 0 ✅
────────────────────
Total: ~3.2GB
```

**Звільнено:** ~3.3GB

---

## 🎯 ЩОБ УНИКНУТИ В МАЙБУТНЬОМУ

### 1. Використовувати .dockerignore

```
# Вже є у вас
data/
logs/
uploads/
*.log
*.db
```

### 2. Multi-stage build

```dockerfile
# Зменшує розмір з 3GB до 1GB
FROM python:3.11-slim as builder
# ... build steps ...

FROM python:3.11-slim
# ... тільки необхідні файли ...
```

### 3. Регулярне очищення

```bash
# Раз на тиждень
docker builder prune -f
docker image prune -f
```

---

## 🚀 ШВИДКЕ ОЧИЩЕННЯ (1 команда)

```bash
docker builder prune -a -f && docker image prune -f
```

**Час:** 30 секунд  
**Звільнить:** ~3GB  
**Безпечно:** ✅

---

## 📝 ПЕРЕВІРКА ПІСЛЯ ОЧИЩЕННЯ

```bash
# Перевірити images
docker images

# Перевірити cache
docker builder du

# Перевірити загальне використання
docker system df
```

---

**🎉 Рекомендація: Очистіть build cache зараз!**

```bash
docker builder prune -a -f
```

---

*Останнє оновлення: 12 березня 2026*
