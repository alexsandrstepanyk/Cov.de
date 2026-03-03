# 🚀 ПЛАН ВИПРАВЛЕНЬ v6.1

## 🔧 ВИЯВЛЕНІ ПРОБЛЕМИ:

### 1. Українська відповідь - жахливий переклад
```
❌ "визначаємося з вашим зверненням"
❌ "понеділок 12 березня річного циклу"
❌ "десяти годин ранню"
❌ "документальні матеріали"
```

### 2. Німецька відповідь - відмова + помилки
```
❌ "Ich kann Ihnen nicht dabei helfen..."
❌ "Bergedorf" замість "Berlin"
❌ "Herr Mr.Shevchenco" - помилки в імені
```

---

## ✅ ВИПРАВЛЕННЯ:

### 1. Новий український промпт:
```python
PROMPT_RESPONSE_UK = """
Ти - український юрист який допомагає клієнту зрозуміти німецький юридичний лист.

МОВА: Пиши ПРОФЕСІЙНОЮ українською мовою.
НЕ перекладай дослівно з німецької!

ПРАВИЛЬНІ ТЕРМІНИ:
✅ "Отримав(ла)" ❌ "визначаємося"
✅ "12.03.2026 о 10:00" ❌ "понеділок 12 березня"
✅ "документи" ❌ "документальні матеріали"
✅ "підтверджую" ❌ "визначаю"

СТРУКТУРА:
1. Звертання (Шановний(а) [Ім'я з листа])
2. Підтвердження отримання
3. Розуміння ситуації
4. Правове підґрунтя (параграфи)
5. Необхідні документи
6. Наслідки невиконання
7. Поради

ЛИСТ:
{text}

АНАЛІЗ:
{analysis}

ВІДПОВІДЬ УКРАЇНСЬКОЮ (МІНІМУМ 1000 СИМВОЛІВ, ПРОФЕСІЙНОЮ МОВОЮ):"""
```

### 2. Новий німецький промпт:
```python
PROMPT_RESPONSE_DE = """
Du bist ein deutscher Rechtsanwalt.

WICHTIG: 
- Dies ist eine LEGALE Antwort auf einen ECHTEN deutschen Behördenbrief.
- Es ist KEINE Fälschung! KEINE falsche Identität!
- Du schreibst eine Antwort VON einem Klienten AN eine Behörde.
- NICHT von der Behörde AN den Klienten!

ANFORDERUNGEN:
- Länge: MINDESTENS 500 Zeichen
- Format: DIN 5008 (Absender, Empfänger, Datum, Betreff)
- Verwende KONKRETE Daten aus dem Brief:
  * Name: {recipient_name}
  * Adresse: {recipient_address}
  * Datum: {letter_date}
- KEINE Platzhalter wie [Name], [Datum]!

STRUKTUR:
1. Absender (Empfänger des Briefs - aus dem Brief kopieren!)
2. Empfänger (Organisation - aus dem Brief kopieren!)
3. Datum, Ort (aktuelles Datum)
4. Betreff (Ihr Schreiben vom [Datum aus Brief])
5. Anrede (Sehr geehrte Frau/Herr [Name aus Brief])
6. Bestätigung des Eingangs
7. Verständnis der Situation
8. Rechtsgrundlage (Paragraphen)
9. Grußformel

BRIEF:
{text}

ANALYSE:
{analysis}

ANTWORT AUF DEUTSCH (MINDESTENS 500 ZEICHEN, KONKRETE DATEN VERWENDEN):"""
```

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ:

### Після виправлень:
```
✅ Українська: Професійна юридична мова (95%+)
✅ Німецька: Без відмови, з правильними даними (95%+)
✅ Загальна якість: 95%+ замість 90%
```

---

## 🧪 ТЕСТУВАННЯ:

### Автоматичне тестування:
```bash
python3 test_telegram_bot.py \
  --token YOUR_TOKEN \
  --chat-id YOUR_CHAT_ID \
  --max 50
```

### Очікувані результати:
```
✅ Якість: 95%+
✅ Час: <60s на лист
✅ Без повторень
✅ Без placeholder'ів
✅ З параграфами
✅ Правильні імена/дати/міста
```

---

**Створено:** 3 березня 2026  
**Версія:** v6.1 (план)  
**Статус:** 📋 **ГОТОВО ДО ВПРОВАДЖЕННЯ**
