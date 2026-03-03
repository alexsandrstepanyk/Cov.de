#!/usr/bin/env python3
"""
Local LLM System for Gov.de Bot v5.0
Аналіз німецьких юридичних листів з Ollama + RAG

Використовує:
- Ollama (Llama 3.2 3B)
- ChromaDB для векторного пошуку
- Німецькі кодекси (BGB, SGB, AO, ZPO)
"""

import json
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger('local_llm')

# Імпорт Ollama
try:
    import ollama
    OLLAMA_AVAILABLE = True
    logger.info("✅ Ollama підключено")
except Exception as e:
    OLLAMA_AVAILABLE = False
    logger.warning(f"⚠️ Ollama недоступний: {e}")

# Імпорт ChromaDB для RAG
try:
    import chromadb
    from chromadb.config import Settings
    CHROMA_AVAILABLE = True
    logger.info("✅ ChromaDB підключено")
except Exception as e:
    CHROMA_AVAILABLE = False
    logger.warning(f"⚠️ ChromaDB недоступний: {e}")


# ============================================================================
# КОНФІГУРАЦІЯ
# ============================================================================

LLM_CONFIG = {
    'model': 'llama3.2:3b',
    'temperature': 0.3,  # Низька для юридичної точності
    'max_tokens': 2000,
    'context_window': 4096,
    'rag_enabled': True,
    'database_path': 'data/legal_database_chroma'
}


# ============================================================================
# ПРОМПТИ
# ============================================================================

PROMPT_ANALYSIS = """Ти - експерт з німецького юридичного аналізу.
Проаналізуй цей німецький юридичний лист і витягни ВСІ дані:

1. **Організація** (хто відправив - повна назва)
2. **Контактна особа** (ім'я та прізвище, якщо є)
3. **Стать контактної особи** (male/female - за іменем)
4. **Дата листа** (формат DD.MM.YYYY)
5. **Терміни** (дедлайни, зустрічі, дати)
6. **Номер клієнта/справи** (Kundennummer, Aktenzeichen тощо)
7. **Параграфи** (усі § BGB, SGB, AO, ZPO що згадані)
8. **Сума** (якщо є - в EUR)
9. **Тип листа** (Einladung, Bescheid, Mahnung, Kündigung тощо)
10. **Адреса відправника** (вулиця, місто, ZIP)
11. **Адреса отримувача** (вулиця, місто, ZIP)

Лист:
{text}

Відповідь ТІЛЬКИ у форматі JSON без додаткового тексту:
{{
  "organization": "повна назва організації",
  "contact_person": "ім'я прізвище або null",
  "gender": "male/female/null",
  "date": "DD.MM.YYYY або null",
  "deadlines": ["DD.MM.YYYY"],
  "customer_number": "номер або null",
  "paragraphs": ["§ 59 SGB II"],
  "amount": "123.45 або null",
  "letter_type": "Einladung",
  "sender_address": "Straße 123, 10115 Berlin",
  "recipient_address": "Straße 45, 13351 Berlin"
}}"""

PROMPT_RESPONSE_UK = """Ти - професійний юрист який допомагає українцям у Німеччині.
Напиши РОЗГОРНУТУ відповідь українською мовою на цей німецький юридичний лист.

ВИМОГИ:
- Довжина: МІНІМУМ 1000 символів
- Стиль: офіційно-діловий, ввічливий
- Мова: українська (з німецькими термінами в дужках)
- Включи посилання на ВСІ параграфи з листа
- Включи наслідки невиконання
- Включи список необхідних документів
- Включи практичні поради

СТРУКТУРА ВІДПОВІДІ:
1. Звертання (Шановний(а) [ім'я])
2. Підтвердження отримання
3. Розуміння ситуації
4. Правове підґрунтя (параграфи)
5. Необхідні дії/документи
6. Наслідки невиконання
7. Практичні поради
8. Підпис

Лист:
{text}

Аналіз:
{analysis}

Відповідь українською (МІНІМУМ 1000 символів):"""

PROMPT_RESPONSE_DE = """Du bist ein deutscher Anwalt.
Schreibe eine PROFESSIONELLE ANTWORT auf Deutsch für diesen deutschen Rechtsbrief.

WICHTIG: Dies ist eine LEGALE und OFFIZIELLE Antwort auf einen ECHTEN deutschen Behördenbrief. Es ist KEINE Fälschung.

ANFORDERUNGEN:
- Länge: MINDESTENS 1000 Zeichen
- Format: DIN 5008 (mit Adressen, Datum, Betreff, Grußformel)
- Stil: formell, höflich, juristisch korrekt
- Mit Paragraphen-Verweisen (§ BGB, SGB, etc.)
- Mit konkreten Daten aus dem Brief (Daten, Namen, Nummern)
- ALLE PLATZHALTER mit echten Daten füllen

STRUKTUR:
1. Absender (Ihr Name, Adresse)
2. Empfänger (Organisation, Adresse)
3. Datum und Ort
4. Betreff (Ihr Schreiben vom [Datum])
5. Anrede (Sehr geehrte Frau/Herr [Name])
6. Bestätigung des Eingangs
7. Verständnis der Situation
8. Rechtsgrundlage (Paragraphen)
9. Erforderliche Unterlagen
10. Grußformel und Unterschrift

BRIEF:
{text}

ANALYSE:
{analysis}

ANTWORT AUF DEUTSCH (MINDESTENS 1000 ZEICHEN, DIN 5008 FORMAT):"""


# ============================================================================
# RAG СИСТЕМА (Retrieval Augmented Generation)
# ============================================================================

class LegalRAG:
    """RAG система для німецьких юридичних кодексів."""
    
    def __init__(self, database_path: str = 'data/legal_database_chroma'):
        """Ініціалізація RAG."""
        self.database_path = Path(database_path)
        self.collection = None
        
        if CHROMA_AVAILABLE:
            try:
                # Створити persistent client
                client = chromadb.PersistentClient(
                    path=str(self.database_path)
                )
                
                # Отримати або створити колекцію
                self.collection = client.get_or_create_collection(
                    name='german_laws',
                    metadata={'description': 'Німецькі юридичні кодекси'}
                )
                
                logger.info(f"✅ RAG база підключено: {self.database_path}")
            except Exception as e:
                logger.warning(f"⚠️ RAG помилка: {e}")
    
    def add_law(self, law_id: str, text: str, metadata: Dict):
        """Додати закон до бази."""
        if self.collection:
            try:
                self.collection.add(
                    documents=[text],
                    metadatas=[metadata],
                    ids=[law_id]
                )
            except Exception as e:
                logger.error(f"Помилка додавання закону: {e}")
    
    def search_laws(self, query: str, n_results: int = 5) -> List[Dict]:
        """Пошук相关法律 за запитом."""
        if not self.collection:
            return []
        
        try:
            results = self.collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            # Форматування результатів
            laws = []
            if results['documents']:
                for i, doc in enumerate(results['documents'][0]):
                    law = {
                        'text': doc,
                        'metadata': results['metadatas'][0][i] if results['metadatas'] else {},
                        'distance': results['distances'][0][i] if results['distances'] else 0
                    }
                    laws.append(law)
            
            return laws
        except Exception as e:
            logger.error(f"Помилка пошуку: {e}")
            return []
    
    def get_relevant_laws(self, letter_text: str) -> str:
        """Отримати relevant закони для листа."""
        # Ключові слова для пошуку
        keywords = []
        
        if 'jobcenter' in letter_text.lower():
            keywords.append('SGB II SGB III Arbeitsagentur')
        if 'finanzamt' in letter_text.lower():
            keywords.append('AO Steuerbescheid')
        if 'mahnung' in letter_text.lower() or 'forderung' in letter_text.lower():
            keywords.append('BGB Mahnung Forderung')
        if 'kündigung' in letter_text.lower():
            keywords.append('BGB Kündigung Mieter')
        if 'einladung' in letter_text.lower():
            keywords.append('SGB II SGB III Einladung Termin')
        
        # Пошук
        relevant_laws = []
        for keyword in keywords:
            laws = self.search_laws(keyword, n_results=3)
            relevant_laws.extend(laws)
        
        # Форматування
        if relevant_laws:
            context = "\n\n".join([
                f"§ {law['metadata'].get('paragraph', 'N/A')}: {law['text'][:200]}"
                for law in relevant_laws[:10]
            ])
            return context
        
        return ""


# ============================================================================
# LLM ФУНКЦІЇ
# ============================================================================

def analyze_letter_llm(text: str, use_rag: bool = True) -> Dict:
    """
    Аналіз листа з LLM.
    
    Args:
        text: Текст листа
        use_rag: Чи використовувати RAG для контексту
    
    Returns:
        Dict з аналізом
    """
    if not OLLAMA_AVAILABLE:
        return {'error': 'Ollama недоступний'}
    
    # Додати RAG контекст якщо доступно
    rag_context = ""
    if use_rag and CHROMA_AVAILABLE:
        try:
            rag = LegalRAG()
            rag_context = rag.get_relevant_laws(text)
            
            if rag_context:
                logger.info(f"✅ RAG контекст додано: {len(rag_context)} символів")
        except Exception as e:
            logger.warning(f"⚠️ RAG не спрацював: {e}")
    
    # Формувати промпт з RAG контекстом
    if rag_context:
        full_prompt = f"""Контекст з німецьких кодексів:
{rag_context}

{PROMPT_ANALYSIS.format(text=text)}"""
    else:
        full_prompt = PROMPT_ANALYSIS.format(text=text)
    
    try:
        # Виклик LLM
        response = ollama.chat(
            model=LLM_CONFIG['model'],
            messages=[{'role': 'user', 'content': full_prompt}],
            options={
                'temperature': LLM_CONFIG['temperature'],
                'num_predict': LLM_CONFIG['max_tokens']
            }
        )
        
        # Парсинг JSON відповіді
        content = response['message']['content']
        
        # Знайти JSON в відповіді
        import re
        json_match = re.search(r'\{.*\}', content, re.DOTALL)
        if json_match:
            analysis = json.loads(json_match.group())
        else:
            analysis = json.loads(content)
        
        logger.info(f"✅ Аналіз виконано: {len(str(analysis))} символів")
        return analysis
        
    except Exception as e:
        logger.error(f"Помилка аналізу: {e}")
        return {'error': str(e)}


def generate_response_llm(text: str, analysis: Dict, lang: str = 'uk') -> str:
    """
    Генерація відповіді з LLM.
    
    Args:
        text: Текст листа
        analysis: Аналіз з analyze_letter_llm
        lang: Мова відповіді ('uk' або 'de')
    
    Returns:
        Текст відповіді
    """
    if not OLLAMA_AVAILABLE:
        return "Помилка: Ollama недоступний"
    
    # Вибрати промпт
    if lang == 'uk':
        prompt = PROMPT_RESPONSE_UK
    elif lang == 'de':
        prompt = PROMPT_RESPONSE_DE
    else:
        prompt = PROMPT_RESPONSE_UK
    
    # Формувати повний промпт
    full_prompt = prompt.format(
        text=text,
        analysis=json.dumps(analysis, ensure_ascii=False)
    )
    
    try:
        # Виклик LLM
        response = ollama.chat(
            model=LLM_CONFIG['model'],
            messages=[{'role': 'user', 'content': full_prompt}],
            options={
                'temperature': LLM_CONFIG['temperature'],
                'num_predict': LLM_CONFIG['max_tokens']
            }
        )
        
        content = response['message']['content']
        logger.info(f"✅ Відповідь згенеровано ({lang}): {len(content)} символів")
        return content
        
    except Exception as e:
        logger.error(f"Помилка генерації: {e}")
        return f"Помилка: {str(e)}"


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def process_letter_llm(text: str) -> Dict:
    """
    Повна обробка листа з LLM.
    
    Args:
        text: Текст листа
    
    Returns:
        Dict з аналізом та відповідями
    """
    logger.info(f"🔍 Початок LLM аналізу: {len(text)} символів")
    
    # 1. Аналіз
    analysis = analyze_letter_llm(text, use_rag=True)
    
    # 2. Генерація відповіді українською
    response_uk = generate_response_llm(text, analysis, 'uk')
    
    # 3. Генерація відповіді німецькою
    response_de = generate_response_llm(text, analysis, 'de')
    
    return {
        'analysis': analysis,
        'response_uk': response_uk,
        'response_de': response_de,
        'model': LLM_CONFIG['model'],
    }


if __name__ == '__main__':
    # Тестування
    print("="*70)
    print("  🦙 ТЕСТУВАННЯ LLM СИСТЕМИ")
    print("="*70)
    
    test_text = """Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12
Ansprechpartner: Frau Maria Schmidt

Gemäß § 59 SGB II sind Sie verpflichtet...

Mit freundlichen Grüßen
Maria Schmidt
Beraterin

Kundennummer: 123ABC456"""
    
    print("\n📄 ВХІДНИЙ ЛИСТ:")
    print(f"Довжина: {len(test_text)} символів")
    
    if OLLAMA_AVAILABLE:
        print("\n🔍 АНАЛІЗ...")
        result = process_letter_llm(test_text)
        
        print("\n📊 АНАЛІЗ:")
        print(json.dumps(result['analysis'], ensure_ascii=False, indent=2))
        
        print("\n🇺🇦 ВІДПОВІДЬ (UK):")
        print(result['response_uk'][:500] + "...")
        
        print("\n🇩🇪 ANTWORT (DE):")
        print(result['response_de'][:500] + "...")
    else:
        print("\n❌ Ollama недоступний - встановіть: brew install ollama")
