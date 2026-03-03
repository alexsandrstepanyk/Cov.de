# 🎯 СТРАТЕГІЯ ДОСЯГНЕННЯ 90%+ ЯКОСТІ

**Дата:** 3 березня 2026  
**Ціль:** Підняти якість з 70% до 90%+  
**Статус:** 📋 **ПЛАН РОЗРОБКИ**

---

## 📊 ПОТОЧНИЙ СТАН:

| Компонент | v7.0 | Ціль | Різниця |
|-----------|------|------|---------|
| **Українська** | 80/100 | 95/100 | **+15** |
| **Німецька** | 60/100 | 95/100 | **+35** |
| **Загалом** | 70/100 | 95/100 | **+25** |

---

## 🔍 АНАЛІЗ ПРОБЛЕМ:

### 1. Німецька відповідь - КРИТИЧНО (60/100)

**Проблеми:**
```
❌ "Ich kann nicht helfen" - ВІДМОВА (30 балів)
❌ Немає конкретних даних з листа (20 балів)
❌ Неправильні імена/міста/дати (15 балів)
❌ Мало символів (245 замість 500+) (10 балів)
```

**Причина:** Ollama Llama 3.2 3B не слухає промпт

**Рішення:** **FALLBACK ШАБЛОНИ** замість LLM

---

### 2. Українська відповідь - СЕРЕДНЬО (80/100)

**Проблеми:**
```
⚠️ Суржик ("o'clock", "documental materials") (10 балів)
⚠️ Неправильні відмінки (5 балів)
⚠️ Мало символів (540 замість 1000+) (5 балів)
```

**Причина:** LLM змішує мови

**Рішення:** **СЛОВНИК ТЕРМІНІВ** + **ПРИКЛАДИ**

---

## 🎯 ПЛАН ДОСЯГНЕННЯ 90%+:

### Крок 1: Fallback шаблони для німецької (+35%)

**Створити `src/german_templates.py`:**
```python
def generate_german_response_fallback(analysis: Dict) -> str:
    """Генерація німецької відповіді з шаблону."""
    
    # Отримуємо дані з листа
    recipient_name = analysis.get('recipient_name', '')
    recipient_address = analysis.get('recipient_address', '')
    sender_name = analysis.get('sender_name', '')
    sender_address = analysis.get('sender_address', '')
    date = analysis.get('date', '')
    paragraph = analysis.get('paragraphs', ['§'])[0]
    
    # Шаблон DIN 5008
    template = f"""{recipient_name}
{recipient_address}

{sender_name}
{sender_address}

Berlin, {date}

Ihr Schreiben vom {date}

Sehr geehrte(r) {sender_name.split()[-1]},

hiermit bestätige ich den Empfang Ihres Schreibens.

Ich nehme zur Kenntnis:
- {paragraph}
- [Інші пункти з листа]

Mit freundlichen Grüßen
{recipient_name}"""
    
    return template
```

**Очікуваний результат:**
- ✅ 100% без відмов
- ✅ 100% з конкретними даними
- ✅ 500+ символів
- ✅ **Якість: 95/100**

---

### Крок 2: Словник термінів для української (+15%)

**Створити `src/ukrainian_dictionary.py`:**
```python
CORRECT_TERMS = {
    # ЗАБОРОНЕНІ → ПРАВИЛЬНІ
    'визначаємося': 'Отримав(ла)',
    'Situation': 'ситуація',
    'o\'clock': 'о',
    'documental materials': 'документи',
    'Herr': 'пан',
    'Frau': 'пані',
    'According to': 'Згідно з',
    'required': 'необхідно',
    'come for': 'прийти на',
    'personal conversation': 'особиста розмова',
}

def fix_ukrainian_text(text: str) -> str:
    """Виправлення суржику в українській відповіді."""
    result = text
    for wrong, correct in CORRECT_TERMS.items():
        result = result.replace(wrong, correct)
    return result
```

**Очікуваний результат:**
- ✅ 0% суржику
- ✅ 100% правильні терміни
- ✅ 1000+ символів
- ✅ **Якість: 95/100**

---

### Крок 3: Валідація перед відправкою (+5%)

**Створити `src/response_validator.py`:**
```python
def validate_response(response: str, lang: str) -> Dict:
    """Перевірка якості відповіді перед відправкою."""
    
    issues = []
    score = 100
    
    if lang == 'uk':
        # Перевірка на суржик
        for wrong in ['Herr', 'Frau', 'According', 'o\'clock']:
            if wrong in response:
                issues.append(f'Суржик: {wrong}')
                score -= 10
        
        # Перевірка довжини
        if len(response) < 1000:
            issues.append(f'Мало символів: {len(response)}')
            score -= 5
    
    elif lang == 'de':
        # Перевірка на відмову
        for refusal in ['Ich kann nicht', 'falsche', 'Behörde']:
            if refusal in response:
                issues.append(f'Відмова: {refusal}')
                score -= 30
        
        # Перевірка на placeholder'и
        for ph in ['[Name]', '[Datum]', '[Adresse]']:
            if ph in response:
                issues.append(f'Placeholder: {ph}')
                score -= 10
    
    return {
        'valid': score >= 90,
        'score': score,
        'issues': issues,
    }
```

**Очікуваний результат:**
- ✅ 100% відповідей перевірено
- ✅ Відфільтровано погані відповіді
- ✅ **Якість: +5%**

---

### Крок 4: Замінити LLM на шаблони для німецької

**Виправити `src/local_llm.py`:**
```python
def generate_response_llm(text: str, analysis: Dict, lang: str = 'uk') -> str:
    if lang == 'de':
        # ВИКОРИСТОВУВАТИ ШАБЛОН ЗАМІСТЬ LLM!
        from german_templates import generate_german_response_fallback
        return generate_german_response_fallback(analysis)
    
    # Для української - LLM + словник
    from ukrainian_dictionary import fix_ukrainian_text
    response = generate_with_llm(text, analysis, 'uk')
    return fix_ukrainian_text(response)
```

---

## 📈 ОЧІКУВАНІ РЕЗУЛЬТАТИ:

### Після всіх виправлень:

| Компонент | v7.0 | v8.0 (план) | Зміна |
|-----------|------|-------------|-------|
| **Українська** | 80/100 | 95/100 | **+15** ✅ |
| **Німецька** | 60/100 | 95/100 | **+35** ✅ |
| **Загалом** | 70/100 | 95/100 | **+25** ✅ |

### Деталізація:

**Українська (95/100):**
```
✅ 0% суржику (0/100 → 100/100)
✅ 100% правильні терміни (70/100 → 100/100)
✅ 1000+ символів (50/100 → 100/100)
✅ Всі параграфи з листа (80/100 → 100/100)
✅ Всі дані з листа (80/100 → 100/100)
```

**Німецька (95/100):**
```
✅ 0% відмов (0/100 → 100/100)
✅ 100% конкретні дані (40/100 → 100/100)
✅ 500+ символів (50/100 → 100/100)
✅ Правильні імена/міста/дати (60/100 → 100/100)
✅ DIN 5008 формат (70/100 → 100/100)
```

---

## 🛠️ НЕОБХІДНІ ФАЙЛИ:

### Створити:
1. `src/german_templates.py` - шаблони німецької
2. `src/ukrainian_dictionary.py` - словник термінів
3. `src/response_validator.py` - валідація
4. `src/fallback_generator.py` - fallback логіка

### Виправити:
1. `src/local_llm.py` - використати fallback
2. `src/bots/client_bot.py` - додати валідацію

---

## ⏱️ ЧАС РЕАЛІЗАЦІЇ:

| Крок | Час | Пріоритет |
|------|-----|-----------|
| 1. Fallback шаблони DE | 1 година | 🔴 Високий |
| 2. Словник української | 30 хв | 🔴 Високий |
| 3. Валідація | 30 хв | 🟡 Середній |
| 4. Інтеграція | 1 година | 🔴 Високий |
| 5. Тестування | 1 година | 🟡 Середній |
| **Всього** | **4 години** | |

---

## 📊 МЕТРИКИ УСПІХУ:

### Критерії 90%+:

**Українська:**
- [ ] 0% суржику (жодних Herr, Frau, According)
- [ ] 1000+ символів
- [ ] Всі параграфи з листа
- [ ] Всі дані з листа (ім'я, дата, час, номер)
- [ ] Професійні терміни

**Німецька:**
- [ ] 0% відмов (жодних "Ich kann nicht")
- [ ] 500+ символів
- [ ] Конкретні дані з листа
- [ ] Правильні імена/міста/дати
- [ ] DIN 5008 формат

**Загалом:**
- [ ] Середня якість 90%+
- [ ] Час обробки <60s
- [ ] 0% критичних помилок

---

## ✅ ВИСНОВОК:

**Для досягнення 90%+ потрібно:**

1. **Відмовитися від LLM для німецької** → fallback шаблони
2. **Додати словник для української** → виправлення суржику
3. **Додати валідацію** → фільтрація поганих відповідей
4. **Протестувати на 50 листах** → підтвердження 90%+

**Час:** 4 години  
**Складність:** Середня  
**Ризики:** Мінімальні (fallback шаблони надійніші за LLM)

---

**Створено:** 3 березня 2026  
**Версія:** v8.0 (план)  
**Ціль:** 90%+ якість  
**Статус:** 📋 **ГОТОВО ДО РЕАЛІЗАЦІЇ**
