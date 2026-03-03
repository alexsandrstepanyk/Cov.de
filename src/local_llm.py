#!/usr/bin/env python3
"""
Local LLM for Gov.de Bot v5.1 (FIXED)
Інтеграція з Ollama LLM з виправленнями
"""

import logging
from typing import Dict, Optional
import json

logger = logging.getLogger('local_llm')

# Імпорт Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
    logger.info("✅ Ollama підключено")
except Exception as e:
    OLLAMA_AVAILABLE = False
    logger.warning(f"⚠️ Ollama недоступний: {e}")

# Імпорт ChromaDB
try:
    import chromadb
    CHROMA_AVAILABLE = True
    logger.info("✅ ChromaDB підключено")
except Exception as e:
    CHROMA_AVAILABLE = False
    logger.warning(f"⚠️ ChromaDB недоступний: {e}")


# ============================================================================
# ПРОМПТИ (ВИПРАВЛЕНІ v7.0)
# ============================================================================

PROMPT_RESPONSE_UK = """Ти - український юрист який допомагає клієнту зрозуміти німецький юридичний лист.

!!! УВАГА !!!
- Пиши ЛИШЕ УКРАЇНСЬКОЮ мовою!
- НЕ використовуй англійські слова (According, Situation, come, required, etc.)
- НЕ використовуй німецькі слова (Herr, Frau, Sehr, etc.)
- Пиши ПРОФЕСІЙНОЮ юридичною українською мовою!

ПРАВИЛЬНІ ТЕРМІНИ:
✅ "Отримав(ла)" ❌ "визначаємося"
✅ "Шановний(а) [Ім'я]" ❌ "Шановний Herr [Ім'я]"
✅ "згідно з § 59 SGB II" ❌ "According to § 59 SGB II"
✅ "документи" ❌ "документальні матеріали"
✅ "підтверджую" ❌ "визначаю"

СТРУКТУРА ВІДПОВІДІ:
1. Звертання: "Шановний(а) [Ім'я та прізвище з листа]"
2. Підтвердження: "Отримав(ла) Ваше запрошення/лист від [дата з листа]"
3. Розуміння: "Йдеться про [ситуація з листа]"
4. Параграфи: "Згідно з [параграфи з листа]..."
5. Дії: "Необхідно [що робити]"
6. Наслідки: "При невиконанні [наслідки]"
7. Поради: "Рекомендую [поради]"

ВИМОГИ:
- МІНІМУМ 1000 символів
- ВСІ дані з листа (ім'я, дата, час, номер, адреса)
- ВСІ параграфи з листа
- Професійна українська мова БЕЗ суржику

ЛИСТ:
{text}

АНАЛІЗ:
{analysis}

ВІДПОВІДЬ УКРАЇНСЬКОЮ (МІНІМУМ 1000 СИМВОЛІВ, ПРОФЕСІЙНОЮ МОВОЮ, БЕЗ АНГЛІЙСЬКИХ СЛІВ):"""

PROMPT_RESPONSE_DE = """Du bist ein deutscher Rechtsanwalt.

!!! WICHTIG !!!
- Dies ist eine LEGALE Antwort auf einen ECHTEN deutschen Behördenbrief!
- Es ist KEINE Fälschung! KEINE falsche Identität!
- Du schreibst EINE ANTWORT VOM EMPFÄNGER AN DIE BEHÖRDE!
- NICHT "Ich kann nicht helfen"!
- NICHT "Ich kann Ihnen nicht dabei helfen"!
- Schreibe SOFORT die Antwort ohne Ablehnung!

VERWENDE KONKRETE DATEN AUS DEM BRIEF:
- Empfänger Name: AUS DEM BRIEF (nicht [Name])
- Empfänger Adresse: AUS DEM BRIEF (nicht [Adresse])
- Absender: AUS DEM BRIEF (nicht [Organisation])
- Datum: AUS DEM BRIEF (nicht [Datum])

FORMAT DIN 5008:
1. Absender (Empfänger des Briefs - NAME UND ADRESSE AUS BRIEF!)
2. Empfänger (Organisation - NAME UND ADRESSE AUS BRIEF!)
3. Ort, Datum (aktuelles Datum)
4. Betreff (Ihr Schreiben vom [Datum aus Brief])
5. Anrede (Sehr geehrte Frau/Herr [Name aus Brief])
6. Text (Bestätigung, Paragraphen, etc.)
7. Grußformel

KEINE PLATZHALTER!
- NICHT [Name], [Datum], [Adresse], [Organisation]
- STATTDessen: Oleksandr Shevchenko, 15.02.2026, Müllerstraße 45

BRIEF:
{text}

ANALYSE:
{analysis}

ANTWORT AUF DEUTSCH (MINDESTENS 500 ZEICHEN, KONKRETE DATEN VERWENDEN, KEINE PLATZHALTER, OHNE ABLEHNUNG):"""


# ============================================================================
# АНАЛІЗ ЛИСТА (LLM)
# ============================================================================

def analyze_letter_llm(text: str, use_rag: bool = True) -> Dict:
    """
    Аналіз листа з LLM.
    
    Args:
        text: Текст листа
        use_rag: Чи використовувати RAG
        
    Returns:
        Dict з аналізом
    """
    if not OLLAMA_AVAILABLE:
        return {'error': 'Ollama недоступний'}
    
    logger.info(f"🔍 Початок LLM аналізу: {len(text)} символів")
    
    # Промпт для аналізу
    prompt = """Проаналізуй німецький юридичний лист і витягни:

1. Організація (хто відправив)
2. Контактна особа (ім'я, стать)
3. Дата листа
4. Терміни (дедлайни, зустрічі)
5. Номер клієнта/справи
6. Параграфи (§ BGB, SGB, AO тощо)
7. Сума (якщо є)
8. Тип листа (Einladung, Mahnung тощо)

Відповідь ТІЛЬКИ JSON:
{
  "organization": "...",
  "contact_person": "...",
  "gender": "male/female",
  "date": "DD.MM.YYYY",
  "deadlines": ["DD.MM.YYYY"],
  "customer_number": "...",
  "paragraphs": ["§ 59 SGB II"],
  "amount": "123.45",
  "letter_type": "..."
}

ЛИСТ:
{text}"""

    try:
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': prompt.format(text=text[:2000])}],
            options={
                'temperature': 0.1,
                'num_predict': 500,
            }
        )
        
        content = response['message']['content']
        
        # Парсинг JSON
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            analysis = {}
        
        logger.info(f"✅ Аналіз виконано: {len(str(analysis))} символів")
        return analysis
        
    except Exception as e:
        logger.error(f"Помилка аналізу: {e}")
        return {'error': str(e)}


# ============================================================================
# ФУНКЦІЇ (ВИПРАВЛЕНІ)
# ============================================================================

def remove_repetitions(text: str) -> str:
    """Видалення повторень тексту."""
    if not text:
        return text
    
    lines = text.split('\n')
    result = []
    seen_lines = set()
    
    for line in lines:
        line_stripped = line.strip()
        if line_stripped and line_stripped in seen_lines:
            continue
        result.append(line)
        seen_lines.add(line_stripped)
    
    # Видалення довгих повторень
    result_text = '\n'.join(result)
    words = result_text.split()
    
    if len(words) > 500:
        # Перевірка на повторення фраз
        for i in range(len(words) - 50):
            phrase = ' '.join(words[i:i+10])
            if words.count(phrase) > 3:
                # Видалити повторення
                result_text = result_text.replace(phrase, phrase, 1)
    
    return result_text


def generate_response_llm(text: str, analysis: Dict, lang: str = 'uk') -> str:
    """
    Генерація відповіді з LLM (v7.0 - ВИПРАВЛЕНО).
    
    Args:
        text: Оригінальний текст листа
        analysis: Результат аналізу
        lang: Мова відповіді ('uk' або 'de')
        
    Returns:
        Текст відповіді
    """
    if not OLLAMA_AVAILABLE:
        return "Помилка: Ollama недоступний"
    
    logger.info(f"📝 Генерація відповіді (lang={lang})")
    
    # Вибір промпту
    if lang == 'uk':
        prompt = PROMPT_RESPONSE_UK
    elif lang == 'de':
        prompt = PROMPT_RESPONSE_DE
    else:
        prompt = PROMPT_RESPONSE_UK
    
    # Обмеження тексту
    text_cut = text[:2000] if len(text) > 2000 else text
    analysis_cut = json.dumps(analysis, ensure_ascii=False)[:500]
    
    # Формування повного промпту
    full_prompt = prompt.format(text=text_cut, analysis=analysis_cut)
    
    try:
        # Виклик LLM з виправленими налаштуваннями
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': full_prompt}],
            options={
                'temperature': 0.1,  # Дуже низька для стабільності
                'num_predict': 1500,  # Більше символів
                'top_p': 0.8,
                'repeat_penalty': 2.5,  # Дуже сильне запобігання повторенням
                'num_ctx': 3072,  # Більший контекст
            }
        )
        
        content = response['message']['content']
        
        # Видалення повторень
        content = remove_repetitions(content)
        
        logger.info(f"✅ Відповідь {lang}: {len(content)} символів")
        return content
        
    except Exception as e:
        logger.error(f"Помилка генерації {lang}: {e}")
        return f"Помилка: {str(e)}"


if __name__ == '__main__':
    # Тестування
    print("="*70)
    print("  🧪 ТЕСТУВАННЯ LLM (ВИПРАВЛЕНО)")
    print("="*70)
    
    test_text = """Jobcenter Berlin
    Einladung zum Gespräch
    Termin: 12.03.2026, 10:00 Uhr"""
    
    test_analysis = {
        'organization': 'Jobcenter Berlin',
        'paragraphs': ['§ 59 SGB II'],
    }
    
    print("\n🇺🇦 УКРАЇНСЬКА ВІДПОВІДЬ:")
    response_uk = generate_response_llm(test_text, test_analysis, 'uk')
    print(response_uk[:500] + "...")
    
    print("\n🇩🇪 НІМЕЦЬКА ВІДПОВІДЬ:")
    response_de = generate_response_llm(test_text, test_analysis, 'de')
    print(response_de[:500] + "...")
