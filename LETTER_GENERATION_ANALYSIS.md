# 📋 АНАЛІЗ: АВТОМАТИЧНА ГЕНЕРАЦІЯ НІМЕЦЬКИХ ЛИСТІВ
## Відповіді з персоналізацією та DIN 5008 форматом

**Дата:** 2 березня 2026  
**Статус:** План реалізації

---

## 🎯 ЗАВДАННЯ

**Потрібно:** При аналізі вхідного листа автоматично:
1. ✅ Визначати **отримувача** (Frau Müller, Herr Schmidt)
2. ✅ Визначати **адресу відправника** (користувача)
3. ✅ Визначати **адресу отримувача** (організація)
4. ✅ Генерувати **відповідь у форматі DIN 5008**
5. ✅ Використовувати **правильне звертання** (Sehr geehrte Frau/Herr)

---

## 📊 АНАЛІЗ СХОЖИХ СИСТЕМ

### 1. Rechtsantragsstelle (Німеччина)
**Як працює:**
- Автоматично генерує відповіді на офіційні листи
- Використовує шаблони з персоналізацією
- Формат: DIN 5008

**Особливості:**
- ✅ Автоматичне визначення статі (Frau/Herr)
- ✅ Правильні відмінки (Nominativ, Dativ)
- ✅ Професійні звертання

### 2. LawDevs / Legal Tech AI
**Як працює:**
- NLP для аналізу юридичних документів
- Extraction: імена, адреси, дати
- Генерація відповідей

**Особливості:**
- ✅ Regex + NER (Named Entity Recognition)
- ✅ Контекстуальне розуміння
- ✅ Мультиваріантність

### 3. Briefgenerator (Online Tools)
**Як працює:**
- Користувач вводить дані
- Система генерує лист
- Формат DIN 5008

**Особливості:**
- ✅ Стандартні шаблони
- ✅ Автоматичне форматування
- ❌ Немає автоматичного extraction

---

## 🔧 ТЕХНІЧНА РЕАЛІЗАЦІЯ

### Рівень 1: Extraction (Витягування даних)

#### 1.1 Визначення імені отримувача

**Regex патерни:**
```python
# Жінки
frau_pattern = r'(?:frau|ms\.)\s*([A-Z][a-z]+(?:-[A-Z][a-z]+)?\s+[A-Z][a-z]+)'

# Чоловіки  
herr_pattern = r'(?:herr|hr\.)\s*([A-Z][a-z]+(?:-[A-Z][a-z]+)?\s+[A-Z][a-z]+)'

# Універсальний
name_pattern = r'(?:frau|herr)\s+([A-Z][a-z]+(?:\s+[A-Z][a-z]+)+)'
```

**Приклади:**
```
Вхідне: "Frau Maria Müller"
→ Ім'я: "Maria"
→ Прізвище: "Müller"
→ Стать: "female"
→ Звертання: "Sehr geehrte Frau Müller"

Вхідне: "Herr Dr. Schmidt"
→ Ім'я: (немає)
→ Прізвище: "Schmidt"
→ Титул: "Dr."
→ Стать: "male"
→ Звертання: "Sehr geehrter Herr Dr. Schmidt"
```

#### 1.2 Визначення адрес

**Адреса відправника (організація):**
```python
sender_pattern = r'''
    ([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)  # Назва організації
    \n
    (.+?Straße\.?\s+\d+)              # Вулиця і номер
    \n
    (\d{5}\s+[A-Z][a-z]+)             # ZIP і місто
'''
```

**Адреса отримувача (користувач):**
```python
recipient_pattern = r'''
    (?:Herrn|Frau)\s+                 # Звертання
    ([A-Z][a-z]+\s+[A-Z][a-z]+)       # Ім'я прізвище
    \n
    (.+?Straße\.?\s+\d+)              # Вулиця і номер
    \n
    (\d{5}\s+[A-Z][a-z]+)             # ZIP і місто
'''
```

#### 1.3 Визначення контактних даних

```python
# Телефон
phone_pattern = r'(?:Telefon|Tel|Fax)[:\s]*(\+?\d[\d\s\-]+)'

# Email
email_pattern = r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'

# Вебсайт
website_pattern = r'(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})'
```

---

### Рівень 2: Генерація відповіді (DIN 5008)

#### 2.1 Структура листа

```
┌────────────────────────────────────────┐
│ [Ваше ім'я]                            │ ← Відправник
│ [Ваша вулиця]                          │
│ [Ваш ZIP + місто]                      │
│                                        │
│                                        │
│ [Організація]                          │ ← Отримувач
│ [Вулиця організації]                   │
│ [ZIP + місто організації]              │
│                                        │
│                        [Місто], [Дата] │ ← Дата
│                                        │
│ Betreff: [Тема листа]                  │ ← Тема
│                                        │
│ Sehr geehrte Frau [Прізвище],         │ ← Звертання
│                                        │
│ [Текст відповіді...]                   │
│                                        │
│ Mit freundlichen Grüßen               │ ← Підпис
│                                        │
│ [Ваше ім'я]                            │
└────────────────────────────────────────┘
```

#### 2.2 Автоматичне звертання

**Логіка:**
```python
def get_formal_salutation(gender, title, lastname):
    if gender == 'female':
        if title:
            return f"Sehr geehrte Frau {title} {lastname},"
        else:
            return f"Sehr geehrte Frau {lastname},"
    elif gender == 'male':
        if title:
            return f"Sehr geehrter Herr {title} {lastname},"
        else:
            return f"Sehr geehrter Herr {lastname},"
    else:
        return "Sehr geehrte Damen und Herren,"
```

**Приклади:**
```
Frau Maria Müller → "Sehr geehrte Frau Müller,"
Herr Dr. Schmidt → "Sehr geehrter Herr Dr. Schmidt,"
(невідомо) → "Sehr geehrте Damen und Herren,"
```

#### 2.3 Автоматична тема (Betreff)

**Логіка:**
```python
def generate_betreff(organization, situation, reference):
    templates = {
        'jobcenter': 'Ihre Einladung vom {date}',
        'inkasso': 'Ihre Forderung vom {date} - {reference}',
        'vermieter': 'Ihre Mieterhöhung vom {date}',
        'finanzamt': 'Ihr Steuerbescheid vom {date}',
    }
    
    template = templates.get(organization, 'Ihr Schreiben vom {date}')
    return template.format(date=reference, reference=reference)
```

---

### Рівень 3: Інтеграція в бота

#### 3.1 Модуль `letter_generator.py`

```python
#!/usr/bin/env python3
"""
Letter Generator Module v1.0
Генерація німецьких відповідей у форматі DIN 5008
"""

import re
from typing import Dict, Optional
from datetime import datetime

class LetterGenerator:
    """Генерація офіційних листів німецькою."""
    
    def __init__(self):
        self.sender_name = None
        self.sender_address = None
        self.sender_city = None
        self.recipient_org = None
        self.recipient_address = None
        self.recipient_city = None
        self.recipient_name = None
        self.recipient_gender = None
        self.recipient_title = None
        
    def extract_all_data(self, text: str) -> Dict:
        """Витягнути всі дані з листа."""
        data = {
            'sender': self.extract_sender(text),
            'recipient': self.extract_recipient(text),
            'contact': self.extract_contact(text),
            'reference': self.extract_reference(text),
        }
        return data
    
    def extract_sender(self, text: str) -> Dict:
        """Витягнути відправника (організацію)."""
        # Перша адреса в листі (зазвичай організація)
        org_match = re.search(
            r'([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\s*\n'
            r'(.+?Straße\.?\s*\d+)\s*\n'
            r'(\d{5}\s+[A-Z][a-z]+)',
            text
        )
        
        if org_match:
            return {
                'name': org_match.group(1),
                'address': org_match.group(2),
                'city': org_match.group(3),
            }
        return {}
    
    def extract_recipient(self, text: str) -> Dict:
        """Витягнути отримувача (користувача)."""
        # Отримувач (після Herrn/Frau)
        recipient_match = re.search(
            r'(?:Herrn|Frau)\s+'
            r'([A-Z][a-z]+\s+[A-Z][a-z]+)\s*\n'
            r'(.+?Straße\.?\s*\d+)\s*\n'
            r'(\d{5}\s+[A-Z][a-z]+)',
            text
        )
        
        if recipient_match:
            return {
                'name': recipient_match.group(1),
                'address': recipient_match.group(2),
                'city': recipient_match.group(3),
            }
        return {}
    
    def extract_contact_person(self, text: str) -> Dict:
        """Витягнути контактну особу (Frau/Herr)."""
        # Жінка
        frau_match = re.search(
            r'(?:Frau|Ms\.)\s*'
            r'([A-Z][a-z]+(?:-[A-Z][a-z]+)?)\s+'
            r'([A-Z][a-z]+)',
            text
        )
        
        if frau_match:
            return {
                'firstname': frau_match.group(1),
                'lastname': frau_match.group(2),
                'gender': 'female',
                'title': None,
            }
        
        # Чоловік (з титулом)
        herr_match = re.search(
            r'(?:Herr|Hr\.)\s*'
            r'(Dr\.|Prof\.|Dipl\.-Ing\.)?\s*'
            r'([A-Z][a-z]+)',
            text
        )
        
        if herr_match:
            return {
                'firstname': None,
                'lastname': herr_match.group(2),
                'gender': 'male',
                'title': herr_match.group(1),
            }
        
        return {}
    
    def generate_letter(self, data: Dict, response_type: str) -> str:
        """Згенерувати лист у форматі DIN 5008."""
        
        # Шапка (відправник)
        sender_block = f"""{data['user']['name']}
{data['user']['address']}
{data['user']['city']}"""

        # Отримувач
        recipient_block = f"""
{data['organization']['name']}
{data['organization']['address']}
{data['organization']['city']}"""

        # Дата
        today = datetime.now().strftime('%d.%m.%Y')
        city = data['user']['city'].split()[-1] if data['user']['city'] else ''
        date_line = f"\n{city}, {today}"

        # Тема
        betreff = self.generate_betreff(data, response_type)
        
        # Звертання
        salutation = self.generate_salutation(data['contact_person'])
        
        # Тіло листа
        body = self.generate_body(data, response_type)
        
        # Підпис
        closing = "\n\nMit freundlichen Grüßen\n\n"
        signature = data['user']['name']
        
        # Збірка всього
        letter = (
            f"{sender_block}\n"
            f"{recipient_block}\n"
            f"{date_line}\n\n"
            f"{betreff}\n\n"
            f"{salutation}\n\n"
            f"{body}\n"
            f"{closing}"
            f"{signature}"
        )
        
        return letter
    
    def generate_salutation(self, contact: Dict) -> str:
        """Згенерувати правильне звертання."""
        if not contact:
            return "Sehr geehrte Damen und Herren,"
        
        if contact['gender'] == 'female':
            if contact['title']:
                return f"Sehr geehrte Frau {contact['title']} {contact['lastname']},"
            else:
                return f"Sehr geehrte Frau {contact['lastname']},"
        
        elif contact['gender'] == 'male':
            if contact['title']:
                return f"Sehr geehrter Herr {contact['title']} {contact['lastname']},"
            else:
                return f"Sehr geehrter Herr {contact['lastname']},"
        
        return "Sehr geehrte Damen und Herren,"
    
    def generate_betreff(self, data: Dict, response_type: str) -> str:
        """Згенерувати тему листа."""
        date = data.get('reference_date', '[Datum]')
        ref = data.get('reference_number', '')
        
        templates = {
            'jobcenter_einladung': f"Ihre Einladung vom {date}",
            'jobcenter_bescheid': f"Ihr Bescheid vom {date}",
            'inkasso': f"Ihre Forderung vom {date} - {ref}",
            'vermieter': f"Ihre Mieterhöhung vom {date}",
            'finanzamt': f"Ihr Steuerbescheid vom {date}",
        }
        
        return templates.get(response_type, f"Ihr Schreiben vom {date}")
    
    def generate_body(self, data: Dict, response_type: str) -> str:
        """Згенерувати тіло листа."""
        # Використовуємо improved_response_generator
        from improved_response_generator import generate_improved_response
        
        # Отримуємо базову відповідь
        base_response = generate_improved_response(
            data['original_text'],
            data['law_info'],
            'de'
        )
        
        return base_response
```

---

## 📋 ПРИКЛАДИ РОБОТИ

### Приклад 1: Jobcenter Einladung

**Вхідний лист:**
```
Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch

Sehr geehrter Herr Shevchenko,

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12
Ansprechpartner: Frau Schmidt

Mit freundlichen Grüßen
Maria Schmidt
Beraterin
```

**Автоматично витягнуто:**
```python
{
    'organization': {
        'name': 'Jobcenter Berlin Mitte',
        'address': 'Straße der Migration 123',
        'city': '10115 Berlin'
    },
    'user': {
        'name': 'Oleksandr Shevchenko',
        'address': 'Müllerstraße 45, Apt. 12',
        'city': '13351 Berlin'
    },
    'contact_person': {
        'firstname': 'Maria',
        'lastname': 'Schmidt',
        'gender': 'female',
        'title': None
    },
    'reference_date': '12.03.2026',
    'reference_number': None
}
```

**Згенерована відповідь:**
```
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Berlin, 02.03.2026

Ihre Einladung vom 12.03.2026

Sehr geehrte Frau Schmidt,

📋 BESTÄTIGUNG DES EMPFANGS DER EINLADUNG

Ich habe Ihre Einladung zum Gespräch erhalten und bestätige 
meine Teilnahme.

✅ ICH BESTÄTIGE MEINE TEILNAHME:
📅 Datum: 12.03.2026
⏰ Uhrzeit: 10:00
📍 Ort: Jobcenter Berlin Mitte

Mit freundlichen Grüßen

Oleksandr Shevchenko
```

---

### Приклад 2: Inkasso Forderung

**Вхідний лист:**
```
CreditProtect Inkasso GmbH
Forderungsstraße 789
20095 Hamburg

Herrn
Oleksandr Shevchenko
Müllerstraße 45
13351 Berlin

Hamburg, 20.02.2026

Erste Mahnung
Forderungsnummer: 2026/12345

Sehr geehrter Herr Shevchenko,

offener Betrag: 350,00 EUR

Mit freundlichen Grüßen
Thomas Weber
Geschäftsführer
```

**Згенерована відповідь:**
```
Oleksandr Shevchenko
Müllerstraße 45
13351 Berlin

CreditProtect Inkasso GmbH
Forderungsstraße 789
20095 Hamburg

Berlin, 02.03.2026

Ihre Forderung vom 20.02.2026 - 2026/12345

Sehr geehrter Herr Weber,

📋 BETREFF: IHRER FORDERUNG 2026/12345

Ich habe Ihre Zahlungsaufforderung erhalten.

💰 INFORMATIONEN ZUR FORDERUNG:
• Betrag: 350,00 EUR
• Frist: 05.03.2026

⚖️ ANFRAGE GEMÄẞ BGB § 286:
Bitte senden Sie mir eine detaillierte Aufstellung.

Mit freundlichen Grüßen

Oleksandr Shevchenko
```

---

## 🎯 ПЕРЕВАГИ НОВОЇ СИСТЕМИ

### 1. ✅ Персоналізація
- Звертання по імені (Sehr geehrte Frau Schmidt)
- Правильні титули (Dr., Prof.)
- Врахування статі

### 2. ✅ Професійний формат
- DIN 5008 стандарт
- Правильне розташування адрес
- Автоматична дата

### 3. ✅ Автоматизація
- Немає ручного введення
- Всі дані з листа
- Миттєва генерація

### 4. ✅ Універсальність
- Підходить для всіх типів листів
- Jobcenter, Inkasso, Vermieter, Finanzamt
- Різні ситуації

---

## 🚀 ПЛАН РЕАЛІЗАЦІЇ

### Етап 1: Створення модуля (1-2 години)
- [ ] `letter_generator.py` - основний клас
- [ ] `extract_data()` - витягування даних
- [ ] `generate_letter()` - генерація листа
- [ ] `get_salutation()` - звертання

### Етап 2: Інтеграція в бота (1 година)
- [ ] Імпорт в `client_bot.py`
- [ ] Виклик після аналізу
- [ ] Додавання німецької версії

### Етап 3: Тестування (1 година)
- [ ] 20_TEST_LETTERS.md
- [ ] Перевірка extraction
- [ ] Перевірка формату

### Етап 4: Полірування (30 хв)
- [ ] Edge cases
- [ ] Покращення regex
- [ ] Документація

---

## 📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ

### До:
```
Sehr geehrte Damen und Herren,

Ich bestätige den Termin.

Mit freundlichen Grüßen
[Ім'я]
```

### Після:
```
Oleksandr Shevchenko
Müllerstraße 45
13351 Berlin

Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Berlin, 02.03.2026

Ihre Einladung vom 12.03.2026

Sehr geehrte Frau Schmidt,

📋 BESTÄTIGUNG...

Mit freundlichen Grüßen

Oleksandr Shevchenko
```

---

**Створено:** 2 березня 2026  
**Статус:** Готово до реалізації  
**Час реалізації:** ~4 години
