#!/usr/bin/env python3
"""
Cerebras AI Integration for Gov.de Bot
Інтеграція Cerebras LLM для покращених відповідей
"""

import os
import logging
from typing import Optional, Dict
from pathlib import Path

logger = logging.getLogger('cerebras_integration')

# Спроба імпорту cerebras
try:
    from cerebras.cloud.sdk import Cerebras
    CEREBRAS_AVAILABLE = True
    logger.info("✅ Cerebras SDK підключено")
except Exception as e:
    CEREBRAS_AVAILABLE = False
    logger.warning(f"⚠️ Cerebras SDK недоступний: {e}")
    logger.info("💡 Встановіть: pip install cerebras-cloud-sdk")


class CerebrasLLM:
    """Клас для роботи з Cerebras AI."""
    
    def __init__(self, api_key: Optional[str] = None, model: str = "llama3.1-8b-8192"):
        """
        Ініціалізація Cerebras LLM.
        
        Args:
            api_key: API ключ Cerebras (або з .env CEREBRAS_API_KEY)
            model: Модель для використання
        """
        self.api_key = api_key or os.getenv('CEREBRAS_API_KEY')
        self.model = model
        self.client = None
        
        if not self.api_key:
            logger.warning("⚠️ Cerebras API ключ не знайдено!")
            return
        
        if CEREBRAS_AVAILABLE:
            try:
                self.client = Cerebras(api_key=self.api_key)
                logger.info(f"✅ Cerebras підключено (модель: {model})")
            except Exception as e:
                logger.error(f"❌ Помилка підключення Cerebras: {e}")
    
    def generate_response(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        max_tokens: int = 1024,
        temperature: float = 0.7
    ) -> str:
        """
        Генерація відповіді через Cerebras.
        
        Args:
            prompt: Запит користувача
            system_prompt: Системна інструкція
            max_tokens: Максимальна кількість токенів
            temperature: Температура генерації
        
        Returns:
            Згенерована відповідь
        """
        if not self.client:
            return self._fallback_response(prompt)
        
        try:
            messages = []
            
            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})
            
            messages.append({"role": "user", "content": prompt})
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )
            
            return response.choices[0].message.content
        
        except Exception as e:
            logger.error(f"❌ Помилка Cerebras: {e}")
            return self._fallback_response(prompt)
    
    def _fallback_response(self, prompt: str) -> str:
        """Fallback відповідь якщо Cerebras недоступний."""
        logger.warning("⚠️ Використовую fallback відповідь")
        return f"[Cerebras недоступний] Ваш запит: {prompt[:100]}..."
    
    def analyze_letter(self, text: str, language: str = 'uk') -> Dict:
        """
        Аналіз юридичного листа.
        
        Args:
            text: Текст листа
            language: Мова відповіді
        
        Returns:
            Словник з аналізом
        """
        system_prompt = f"""Ти юрист-експерт з німецького права.
Проаналізуй лист та надай:
1. Тип листа (оренда, робота, податки, тощо)
2. Організацію що відправила
3. Ключові параграфи законів
4. Рекомендації дій

Відповідай мовою: {language}"""
        
        prompt = f"Проаналізуй цей німецький юридичний лист:\n\n{text}"
        
        response = self.generate_response(prompt, system_prompt)
        
        return {
            'analysis': response,
            'model': self.model,
            'success': True
        }
    
    def search_laws(self, query: str, context: str = "") -> str:
        """
        Пошук та аналіз законів з контекстом.
        
        Args:
            query: Запит
            context: Додатковий контекст (RAG результати)
        
        Returns:
            Відповідь з посиланнями на закони
        """
        system_prompt = """Ти експерт з німецького права.
Надай точну відповідь з посиланнями на конкретні параграфи законів (BGB, SGB, AO, тощо).
Використовуй тільки перевірену інформацію."""
        
        prompt = f"Запит: {query}\n\nКонтекст з RAG бази:\n{context}" if context else f"Запит: {query}"
        
        return self.generate_response(prompt, system_prompt)
    
    def translate_legal_text(self, text: str, target_lang: str = 'uk') -> str:
        """
        Переклад юридичного тексту.
        
        Args:
            text: Текст для перекладу
            target_lang: Цільова мова
        
        Returns:
            Перекладений текст
        """
        system_prompt = f"""Ти професійний перекладач юридичних текстів.
Перекладай точно, зберігаючи юридичні терміни.
Мова перекладу: {target_lang}"""
        
        prompt = f"Переклади цей німецький юридичний текст:\n\n{text}"
        
        return self.generate_response(prompt, system_prompt)


# Глобальний екземпляр
_cerebras_llm = None


def get_cerebras_llm() -> Optional[CerebrasLLM]:
    """Отримати глобальний екземпляр Cerebras LLM."""
    global _cerebras_llm
    
    if _cerebras_llm is None:
        _cerebras_llm = CerebrasLLM()
    
    return _cerebras_llm


# Тест
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("  🧠 ТЕСТУВАННЯ CEREBRAS AI")
    print("="*80)
    
    llm = get_cerebras_llm()
    
    if llm and llm.client:
        print("\n✅ Cerebras підключено!")
        
        # Тест 1: Проста відповідь
        print("\n📌 Тест 1: Проста відповідь")
        response = llm.generate_response("Що таке BGB?")
        print(f"Відповідь: {response[:200]}...")
        
        # Тест 2: Аналіз листа
        print("\n📌 Тест 2: Аналіз листа")
        test_letter = "Sehr geehrte Damen und Herren, hiermit kündige ich meinen Mietvertrag."
        analysis = llm.analyze_letter(test_letter, language='uk')
        print(f"Аналіз: {analysis['analysis'][:200]}...")
        
        print("\n" + "="*80)
        print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
        print("="*80)
    else:
        print("\n❌ Cerebras не підключено")
        print("💡 Додайте CEREBRAS_API_KEY в .env файл")
        print("\n" + "="*80)
