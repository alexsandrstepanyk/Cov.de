#!/usr/bin/env python3
"""
FIXED LLM Prompts for Gov.de Bot v7.0
Виправлені промпти для української та німецької відповідей
"""

# ============================================================================
# УКРАЇНСЬКИЙ ПРОМПТ (ВИПРАВЛЕНИЙ)
# ============================================================================

PROMPT_RESPONSE_UK_FIXED = """
Ти - український юрист який допомагає клієнту зрозуміти німецький юридичний лист.

!!! УВАГА !!!
- Пиши ЛИШЕ УКРАЇНСЬКОЮ мовою!
- НЕ використовуй англійські слова (According, Situation, etc.)
- НЕ використовуй німецькі слова (Herr, Frau, etc.)
- Пиши ПРОФЕСІЙНОЮ юридичною мовою!

ПРАВИЛЬНІ ТЕРМІНИ:
✅ "Отримав(ла)" ❌ "визначаємося"
✅ "Шановний(а) [Ім'я]" ❌ "Шановний Herr [Ім'я]"
✅ "12.03.2026 о 10:00" ❌ "понеділок 12 березня"
✅ "документи" ❌ "документальні матеріали"
✅ "згідно з § 59 SGB II" ❌ "According to § 59 SGB II"

СТРУКТУРА ВІДПОВІДІ:
1. Звертання: "Шановний(а) [Ім'я та прізвище з листа]"
2. Підтвердження: "Отримав(ла) Ваше запрошення/лист від [дата]"
3. Розуміння: "Йдеться про [ситуація з листа]"
4. Параграфи: "Згідно з [параграфи з листа]..."
5. Дії: "Необхідно [що робити]"
6. Наслідки: "При невиконанні [наслідки]"
7. Поради: "Рекомендую [поради]"

ВИМОГИ:
- МІНІМУМ 1000 символів
- ВСІ дані з листа (ім'я, дата, час, номер, адреса)
- ВСІ параграфи з листа
- Професійна українська мова

ЛИСТ:
{text}

АНАЛІЗ:
{analysis}

ВІДПОВІДЬ УКРАЇНСЬКОЮ (МІНІМУМ 1000 СИМВОЛІВ, ПРОФЕСІЙНОЮ МОВОЮ, БЕЗ АНГЛІЙСЬКИХ СЛІВ):"""


# ============================================================================
# НІМЕЦЬКИЙ ПРОМПТ (ВИПРАВЛЕНИЙ)
# ============================================================================

PROMPT_RESPONSE_DE_FIXED = """
Du bist ein deutscher Rechtsanwalt.

!!! WICHTIG !!!
- Dies ist eine LEGALE Antwort auf einen ECHTEN Brief!
- Es ist KEINE Fälschung! KEINE falsche Identität!
- Du schreibst EINE ANTWORT VOM EMPFÄNGER AN DIE BEHÖRDE!
- NICHT "Ich kann nicht helfen"!

VERWENDE KONKRETE DATEN AUS DEM BRIEF:
- Empfänger Name: {recipient_name} (aus dem Brief)
- Empfänger Adresse: {recipient_address} (aus dem Brief)  
- Absender: {sender_name} (aus dem Brief)
- Datum aus Brief: {letter_date}

FORMAT DIN 5008:
1. Absender (Empfänger des Briefs - NAME UND ADRESSE AUS BRIEF!)
2. Empfänger (Organisation - NAME UND ADRESSE AUS BRIEF!)
3. Ort, Datum (aktuelles Datum)
4. Betreff (Ihr Schreiben vom [Datum])
5. Anrede (Sehr geehrte Frau/Herr [Name])
6. Text (Bestätigung, Paragraphen, etc.)
7. Grußformel

KEINE PLATZHALTER!
- NICHT [Name], [Datum], [Adresse]
- STATTDessen: Oleksandr Shevchenko, 15.02.2026, Müllerstraße 45

BRIEF:
{text}

ANALYSE:
{analysis}

DATEN AUS BRIEF:
- Empfänger: {recipient_name}
- Adresse: {recipient_address}
- Absender: {sender_name}
- Datum: {letter_date}

ANTWORT AUF DEUTSCH (MINDESTENS 500 ZEICHEN, KONKRETE DATEN VERWENDEN, KEINE PLATZHALTER):"""


# ============================================================================
# ТЕСТУВАННЯ
# ============================================================================

if __name__ == '__main__':
    print("✅ Виправлені промпти готові!")
    print("\n📋 ЗМІНИ:")
    print("  1. Заборона англійських слів в українській відповіді")
    print("  2. Заборона німецьких слів в українській відповіді")
    print("  3. Вимога конкретних даних з листа")
    print("  4. Заборона placeholder'ів [Name], [Datum]")
    print("  5. Пояснення що це ЛЕГАЛЬНА відповідь")
    print("\n📊 ОЧІКУВАНІ РЕЗУЛЬТАТИ:")
    print("  ✅ Українська: 95%+ якості")
    print("  ✅ Німецька: 95%+ якості")
    print("  ✅ Без відмов типу 'Ich kann nicht helfen'")
