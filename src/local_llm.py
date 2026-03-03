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
# ПРОМПТИ (ВИПРАВЛЕНІ)
# ============================================================================

PROMPT_RESPONSE_UK = """Ти - український юрист який допомагає клієнту зрозуміти німецький юридичний лист.

ЗАВДАННЯ: Напиши детальну відповідь українською мовою для клієнта.

ВИМОГИ:
- Довжина: МІНІМУМ 1000 символів
- Мова: українська
- Стиль: професійний, зрозумілий
- З посиланнями на параграфи (§ BGB, SGB тощо)
- З наслідками невиконання
- З порадами що робити

СТРУКТУРА:
1. Звертання (Шановний(а) [Ім'я])
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

ВІДПОВІДЬ УКРАЇНСЬКОЮ (МІНІМУМ 1000 СИМВОЛІВ):"""

PROMPT_RESPONSE_DE = """Du bist ein deutscher Rechtsanwalt.

WICHTIG: Dies ist eine LEGALE Antwort auf einen ECHTEN deutschen Behördenbrief. KEINE Fälschung.

AUFGABE: Schreibe eine professionelle Antwort auf Deutsch.

ANFORDERUNGEN:
- Länge: MINDESTENS 500 Zeichen
- Format: DIN 5008 (Absender, Empfänger, Datum, Betreff)
- Stil: formell, höflich
- Mit Paragraphen (§ BGB, SGB)
- Mit konkreten Daten aus dem Brief

STRUKTUR:
1. Absender (Empfänger des Briefs)
2. Empfänger (Organisation)
3. Datum, Ort
4. Betreff
5. Anrede
6. Bestätigung
7. Rechtsgrundlage
8. Grußformel

BRIEF:
{text}

ANALYSE:
{analysis}

ANTWORT AUF DEUTSCH (MINDESTENS 500 ZEICHEN):"""


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
    Генерація відповіді з LLM (ВИПРАВЛЕНО).
    
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
        # Виклик LLM з обмеженнями
        response = ollama.chat(
            model='llama3.2:3b',
            messages=[{'role': 'user', 'content': full_prompt}],
            options={
                'temperature': 0.2,  # Дуже низька для стабільності
                'num_predict': 1000,  # Обмеження довжини
                'top_p': 0.8,
                'repeat_penalty': 2.0,  # Сильне запобігання повторенням
                'num_ctx': 2048,  # Контекст
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
