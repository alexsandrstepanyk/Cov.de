#!/usr/bin/env python3
"""
Local LLM for Gov.de Bot v5.1 (FIXED)
Інтеграція з Ollama LLM з виправленнями
"""

import logging
import os
from typing import Dict, Optional
import json
import requests

logger = logging.getLogger('local_llm')

# Отримуємо URL з змінної оточення (fallback для локального запуску)
OLLAMA_HOST = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')

# Перевіряємо доступність Ollama
try:
    r = requests.get(f'{OLLAMA_HOST}/api/tags', timeout=5)
    if r.status_code == 200:
        OLLAMA_AVAILABLE = True
        logger.info(f"✅ Ollama підключено ({OLLAMA_HOST})")
    else:
        OLLAMA_AVAILABLE = False
        logger.warning(f"⚠️ Ollama повернув статус {r.status_code}")
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
    Аналіз листа з LLM + RAG.

    Args:
        text: Текст листа
        use_rag: Чи використовувати RAG

    Returns:
        Dict з аналізом
    """
    if not OLLAMA_AVAILABLE:
        return {'error': 'Ollama недоступний'}

    logger.info(f"🔍 Початок LLM аналізу: {len(text)} символів")
    
    # RAG пошук相关法律
    rag_context = ""
    if use_rag:
        try:
            from fast_law_search import search_laws

            # Шукаємо закони за ключовими словами
            keywords = ['Jobcenter', 'Einladung', 'SGB', 'BGB', 'Mahnung']
            found_laws = []
            for keyword in keywords:
                if keyword.lower() in text.lower():
                    laws = search_laws(keyword, limit=3)
                    found_laws.extend(laws[:2])

            if found_laws:
                rag_context = "\n\nЗнайдені закони:\n"
                for law in found_laws[:5]:
                    rag_context += f"- {law.get('law', '')} {law.get('paragraph', '')}: {law.get('description', '')}\n"
                logger.info(f"✅ RAG знайдено законів: {len(found_laws)}")
        except Exception as e:
            logger.warning(f"⚠️ RAG пошук не вдався: {e}")

    # Промпт для аналізу (фігурні дужки JSON екрановані подвійними {{}})
    prompt = """Ти експерт з німецького права. Проаналізуй лист і витягни ВСІ дані у форматі JSON.

ПРАВИЛА:
1. Поверни ВИКЛЮЧНО JSON, без додаткового тексту
2. Не використовуй markdown, code blocks чи інший текст
3. Всі поля мають бути заповнені або порожній рядок ""
4. Масиви можуть бути порожні []

СТРУКТУРА JSON (обов'язково дотримуйся):
{{
  "organization": "точна назва організації з листа",
  "contact_person": "ім'я контактної особи",
  "gender": "male або female",
  "date": "дата листа у форматі DD.MM.YYYY",
  "deadlines": ["список усіх дат/дедлайнів"],
  "customer_number": "Kundennummer/Aktenzeichen",
  "paragraphs": ["ВСІ параграфи § що згадані в листі"],
  "amount": "сума якщо є",
  "letter_type": "Einladung/Mahnung/Schreiben/Kündigung тощо"
}}

ПРИКЛАД правильної відповіді:
{{"organization":"Jobcenter Berlin Mitte","contact_person":"Frau Schmidt","gender":"female","date":"15.02.2026","deadlines":["25.02.2026 10:00"],"customer_number":"123ABC456","paragraphs":["§ 59 SGB II","§ 31 SGB II"],"amount":"","letter_type":"Einladung"}}

ТЕПЕР ПРОАНАЛІЗУЙ ЦЕЙ ЛИСТ:
{text}"""

    try:
        # Прямий HTTP запит до Ollama API
        # Отримуємо модель з оточення
        llm_model = os.getenv('DEFAULT_LLM_MODEL', 'gemma:7b')
        
        response = requests.post(
            f'{OLLAMA_HOST}/api/chat',
            json={
                'model': llm_model,
                'messages': [{'role': 'user', 'content': prompt.format(text=text[:2000])}],
                'options': {
                    'temperature': 0.05,
                    'num_predict': 1000,
                    'top_p': 0.9,
                },
                'stream': False,
                'format': 'json'  # Вимушує Ollama повертати тільки JSON
            },
            timeout=90
        )
        
        response.raise_for_status()
        result = response.json()
        content = result['message']['content']

        # Парсинг JSON з кількома спробами
        import re
        
        # Спроба 1: Шукаємо JSON між фігурними дужками
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            try:
                analysis = json.loads(json_match.group())
                logger.info(f"✅ JSON розпаршено (спроба 1)")
            except json.JSONDecodeError:
                # Спроба 2: Очищаємо від markdown
                cleaned = json_match.group().replace('```json', '').replace('```', '').strip()
                analysis = json.loads(cleaned)
                logger.info(f"✅ JSON розпаршено (спроба 2)")
        else:
            logger.warning(f"⚠️ JSON не знайдено у відповіді: {content[:200]}")
            analysis = {}
        
        # Очищення ключів від нових рядків та пробілів
        cleaned_analysis = {}
        for key, value in analysis.items():
            clean_key = key.strip().strip('"').strip()
            cleaned_analysis[clean_key] = value
        analysis = cleaned_analysis
        
        # Перевірка що всі потрібні ключі є
        required_keys = ['organization', 'contact_person', 'gender', 'date', 'deadlines', 'customer_number', 'paragraphs', 'amount', 'letter_type']
        for key in required_keys:
            if key not in analysis:
                analysis[key] = '' if key != 'deadlines' and key != 'paragraphs' else []

        logger.info(f"✅ Аналіз виконано: organization='{analysis.get('organization', '')}', paragraphs={analysis.get('paragraphs', [])}")
        return analysis

    except Exception as e:
        import traceback
        tb = traceback.format_exc()
        logger.error(f"Помилка аналізу: {e}")
        logger.error(f"Full traceback:\n{tb}")
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
    Генерація відповіді з LLM (v8.0 - FALLBACK + СЛОВНИК).
    
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
    
    # v8.0: Для німецької використовуємо FALLBACK ШАБЛОНИ
    if lang == 'de':
        try:
            from german_templates import get_template_for_type
            letter_type = analysis.get('letter_type', 'Schreiben')
            response = get_template_for_type(letter_type, analysis)
            logger.info(f"✅ Німецька відповідь (шаблон): {len(response)} символів")
            return response
        except Exception as e:
            logger.error(f"Помилка fallback шаблону: {e}")
            # Якщо шаблон не спрацював - використовуємо LLM
            pass
    
    # Для української - LLM + СЛОВНИК
    if lang == 'uk':
        try:
            from ukrainian_dictionary import fix_ukrainian_text

            # Вибір промпту
            prompt = PROMPT_RESPONSE_UK

            # Обмеження тексту
            text_cut = text[:2000] if len(text) > 2000 else text
            analysis_cut = json.dumps(analysis, ensure_ascii=False)[:500]

            # Формування повного промпту
            full_prompt = prompt.format(text=text_cut, analysis=analysis_cut)

            # Отримуємо модель з оточення
            llm_model = os.getenv('DEFAULT_LLM_MODEL', 'gemma:7b')
            
            # Виклик LLM з виправленими налаштуваннями
            response = requests.post(
                f'{OLLAMA_HOST}/api/chat',
                json={
                    'model': llm_model,
                    'messages': [{'role': 'user', 'content': full_prompt}],
                    'options': {
                        'temperature': 0.1,
                        'num_predict': 1500,
                        'top_p': 0.8,
                        'repeat_penalty': 2.5,
                        'num_ctx': 3072,
                    },
                    'stream': False
                },
                timeout=120
            )
            
            response.raise_for_status()
            result = response.json()
            content = result['message']['content']

            # ВИПРАВЛЕННЯ СУРЖИКУ
            content = fix_ukrainian_text(content)
            
            # Видалення повторень
            content = remove_repetitions(content)
            
            logger.info(f"✅ Українська відповідь (LLM + словник): {len(content)} символів")
            return content
            
        except Exception as e:
            logger.error(f"Помилка генерації uk: {e}")
            return f"Помилка: {str(e)}"
    
    # Для інших мов
    return "Помилка: Непідтримувана мова"


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
