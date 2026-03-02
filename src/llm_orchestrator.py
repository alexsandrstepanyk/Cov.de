#!/usr/bin/env python3
"""
LLM Orchestrator for Gov.de Bot v5.0
Єдиний "мозок" бота який аналізує листи з Ollama LLM + RAG

Архітектура:
1. Отримує текст листа (з OCR або тексту)
2. LLM аналізує (витягує дані, визначає тип)
3. RAG знаходить相关法律 в базі
4. LLM генерує відповідь (UK + DE)
5. Повертає структурований результат
"""

import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logger = logging.getLogger('llm_orchestrator')

# Імпорт LLM модулів
try:
    from local_llm import analyze_letter_llm, generate_response_llm
    LLM_AVAILABLE = True
    logger.info("✅ LLM модулі підключено")
except Exception as e:
    LLM_AVAILABLE = False
    logger.warning(f"⚠️ LLM модулі недоступні: {e}")

# Імпорт RAG
try:
    import chromadb
    RAG_AVAILABLE = True
    logger.info("✅ RAG підключено")
except Exception as e:
    RAG_AVAILABLE = False
    logger.warning(f"⚠️ RAG недоступний: {e}")


class LLMOrchestrator:
    """
    Оркестратор для LLM аналізу листів.
    
    Працює як "мозок" бота:
    - Аналізує вхідний текст
    - Витягує всі дані автоматично
    - Знаходить相关法律 в RAG базі
    - Генерує відповіді українською та німецькою
    """
    
    def __init__(self, rag_db_path: str = 'data/legal_database_chroma'):
        """Ініціалізація оркестратора."""
        self.rag_collection = None
        
        # Підключення до RAG бази
        if RAG_AVAILABLE:
            try:
                client = chromadb.PersistentClient(path=str(Path(rag_db_path)))
                self.rag_collection = client.get_collection(name='german_laws')
                logger.info(f"✅ RAG база підключено: {rag_db_path}")
            except Exception as e:
                logger.warning(f"⚠️ RAG база не підключена: {e}")
    
    def analyze_letter(self, text: str) -> Dict:
        """
        Повний аналіз листа з LLM.
        
        Args:
            text: Текст листа німецькою
            
        Returns:
            Dict з повним аналізом
        """
        if not LLM_AVAILABLE:
            return {'error': 'LLM недоступний'}
        
        logger.info(f"🔍 Початок LLM аналізу: {len(text)} символів")
        
        # Крок 1: LLM аналіз (витягування даних)
        analysis = analyze_letter_llm(text, use_rag=False)
        
        # Крок 2: RAG пошук相关法律
        if self.rag_collection and 'paragraphs' in analysis:
            rag_context = self._search_related_laws(analysis)
            analysis['rag_context'] = rag_context
            logger.info(f"✅ RAG знайдено {len(rag_context)}相关法律")
        
        # Крок 3: Додаткова обробка
        analysis['text_length'] = len(text)
        analysis['is_complete'] = self._validate_analysis(analysis)
        
        logger.info(f"✅ Аналіз завершено: {analysis.get('organization', 'N/A')}")
        
        return analysis
    
    def generate_responses(self, text: str, analysis: Dict, lang: str = 'uk') -> Dict:
        """
        Генерація відповідей з LLM.
        
        Args:
            text: Оригінальний текст листа
            analysis: Результат аналізу
            lang: Мова користувача
            
        Returns:
            Dict з відповідями
        """
        if not LLM_AVAILABLE:
            return {'error': 'LLM недоступний'}
        
        logger.info(f"📝 Генерація відповідей (lang={lang})")
        
        responses = {
            'lang': lang,
            'analysis': analysis,
        }
        
        # Крок 4: Генерація відповіді мовою користувача
        try:
            response_user = generate_response_llm(text, analysis, lang)
            responses['response_user'] = response_user
            responses['response_user_length'] = len(response_user)
            logger.info(f"✅ Відповідь {lang}: {len(response_user)} символів")
        except Exception as e:
            logger.error(f"Помилка генерації {lang}: {e}")
            responses['response_user'] = f"Помилка: {str(e)}"
        
        # Крок 5: Генерація німецької відповіді (DIN 5008)
        try:
            response_de = generate_response_llm(text, analysis, 'de')
            responses['response_de'] = response_de
            responses['response_de_length'] = len(response_de)
            logger.info(f"✅ Відповідь DE: {len(response_de)} символів")
        except Exception as e:
            logger.error(f"Помилка генерації DE: {e}")
            responses['response_de'] = f"Error: {str(e)}"
        
        return responses
    
    def _search_related_laws(self, analysis: Dict) -> List[Dict]:
        """Пошук相关法律 в RAG базі."""
        if not self.rag_collection:
            return []
        
        related_laws = []
        
        # Пошук за організацією
        org = analysis.get('organization', '').lower()
        if 'jobcenter' in org or 'arbeitsagentur' in org:
            results = self.rag_collection.query(
                query_texts=['Jobcenter SGB II SGB III'],
                n_results=3
            )
            if results['documents']:
                related_laws.extend(results['documents'][0])
        
        elif 'finanzamt' in org or 'steuer' in org:
            results = self.rag_collection.query(
                query_texts=['Finanzamt Steuer AO'],
                n_results=3
            )
            if results['documents']:
                related_laws.extend(results['documents'][0])
        
        elif 'inkasso' in org or 'forderung' in org:
            results = self.rag_collection.query(
                query_texts=['Inkasso Mahnung BGB'],
                n_results=3
            )
            if results['documents']:
                related_laws.extend(results['documents'][0])
        
        elif 'vermieter' in org or 'miete' in org:
            results = self.rag_collection.query(
                query_texts=['Vermieter Miete BGB'],
                n_results=3
            )
            if results['documents']:
                related_laws.extend(results['documents'][0])
        
        return related_laws
    
    def _validate_analysis(self, analysis: Dict) -> bool:
        """Перевірка чи аналіз повний."""
        required_fields = [
            'organization',
            'letter_type',
        ]
        
        return all(field in analysis for field in required_fields)
    
    def process_letter(self, text: str, lang: str = 'uk') -> Dict:
        """
        Повна обробка листа (аналіз + відповіді).
        
        Args:
            text: Текст листа
            lang: Мова користувача
            
        Returns:
            Dict з повним результатом
        """
        logger.info(f"🧠 Початок повної обробки (lang={lang})")
        
        # Аналіз
        analysis = self.analyze_letter(text)
        
        # Генерація відповідей
        responses = self.generate_responses(text, analysis, lang)
        
        # Фінальний результат
        result = {
            'success': True,
            'analysis': analysis,
            'responses': responses,
            'user_lang': lang,
        }
        
        logger.info(f"✅ Повна обробка завершена")
        
        return result


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ (для інтеграції в бота)
# ============================================================================

orchestrator = None

def get_orchestrator() -> LLMOrchestrator:
    """Отримати або створити оркестратор."""
    global orchestrator
    if orchestrator is None:
        orchestrator = LLMOrchestrator()
    return orchestrator

def process_letter_with_llm(text: str, lang: str = 'uk') -> Dict:
    """
    Головна функція для інтеграції в client_bot.py.
    
    Args:
        text: Текст листа (з OCR або тексту)
        lang: Мова користувача
        
    Returns:
        Dict з результатом:
        {
            'success': True/False,
            'analysis': {...},
            'response_uk': '...',
            'response_de': '...',
            'translated_text': '...',
        }
    """
    try:
        orch = get_orchestrator()
        result = orch.process_letter(text, lang)
        
        return {
            'success': result.get('success', False),
            'analysis': result.get('analysis', {}),
            'response_user': result.get('responses', {}).get('response_user', ''),
            'response_de': result.get('responses', {}).get('response_de', ''),
            'response_user_length': result.get('responses', {}).get('response_user_length', 0),
            'response_de_length': result.get('responses', {}).get('response_de_length', 0),
        }
        
    except Exception as e:
        logger.error(f"Помилка LLM обробки: {e}", exc_info=True)
        return {
            'success': False,
            'error': str(e),
            'response_user': f"Помилка: {str(e)}",
            'response_de': f"Error: {str(e)}",
        }


if __name__ == '__main__':
    # Тестування
    print("="*70)
    print("  🧠 ТЕСТУВАННЯ LLM ОРКЕСТРАТОРА")
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

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)
- Zeugnisse und Qualifikationsnachweise

Gemäß § 59 SGB II sind Sie verpflichtet...

Mit freundlichen Grüßen
Maria Schmidt
Beraterin

Kundennummer: 123ABC456"""
    
    print(f"\n📄 Вхідний текст: {len(test_text)} символів")
    
    result = process_letter_with_llm(test_text, 'uk')
    
    print(f"\n✅ Результат:")
    print(f"  Success: {result.get('success')}")
    print(f"  Організація: {result.get('analysis', {}).get('organization', 'N/A')}")
    print(f"  Відповідь UK: {result.get('response_user_length', 0)} символів")
    print(f"  Відповідь DE: {result.get('response_de_length', 0)} символів")
    
    print(f"\n📝 ВІДПОВІДЬ (UK, перші 500 символів):")
    print(result.get('response_user', '')[:500] + "...")
    
    print(f"\n📝 ANTWORT (DE, перші 500 символів):")
    print(result.get('response_de', '')[:500] + "...")
