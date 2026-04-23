#!/usr/bin/env python3
"""
Bot RAG Integration for Gov.de
Інтеграція RAG пошуку в Telegram бота
"""

import logging
from pathlib import Path
from typing import Dict, Optional

logger = logging.getLogger('bot_rag')

# Імпорт RAG пошуку
try:
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from rag_law_search import search_laws, analyze_query_with_rag, get_law_text
    RAG_AVAILABLE = True
    logger.info("✅ RAG Search підключено")
except Exception as e:
    RAG_AVAILABLE = False
    logger.warning(f"⚠️ RAG Search недоступний: {e}")


def rag_search_handler(query: str, language: str = 'uk') -> Dict:
    """
    Обробник запитів з використанням RAG пошуку.
    
    Args:
        query: Текст запиту від користувача
        language: Мова відповіді
    
    Returns:
        Словник з результатами для відправки користувачу
    """
    if not RAG_AVAILABLE:
        return {
            'found': False,
            'message': '⚠️ RAG пошук тимчасово недоступний',
            'laws': []
        }
    
    # Аналіз запиту
    result = analyze_query_with_rag(query, language)
    
    if not result['found']:
        return result
    
    # Додаємо повний текст для першого закону
    if result['laws'] and 'search_results' in result:
        first_law = result['laws'][0]
        law_name = first_law['law_name']
        
        # Отримуємо повний текст
        full_text = get_law_text(law_name, max_chunks=5)
        
        # Формуємо розширену відповідь
        if language == 'uk':
            expanded_message = result['message']
            expanded_message += f"\n📖 **{law_name} - Повний текст:**\n"
            expanded_message += f"```\n{full_text[:1000]}..." if len(full_text) > 1000 else f"```\n{full_text}"
            expanded_message += "\n```"
            
            result['message'] = expanded_message
    
    return result


def search_paragraph(query: str, law_name: Optional[str] = None, language: str = 'uk') -> Dict:
    """
    Пошук конкретного параграфу.
    
    Args:
        query: Запит (наприклад, "§ 196" або "Kündigung frist")
        law_name: Назва закону (опціонально)
        language: Мова відповіді
    
    Returns:
        Словник з результатами
    """
    if not RAG_AVAILABLE:
        return {
            'found': False,
            'message': '⚠️ RAG пошук тимчасово недоступний',
            'paragraphs': []
        }
    
    # Формуємо запит
    if law_name:
        full_query = f"{law_name} {query}"
    else:
        full_query = query
    
    # Пошук з пріоритетом general
    results = search_laws(
        full_query,
        n_results=5,
        collections=['german_laws_general', 'german_laws_full']
    )
    
    if not results:
        return {
            'found': False,
            'message': f'❌ Нічого не знайдено за запитом "{query}"',
            'paragraphs': []
        }
    
    # Формуємо відповідь
    if language == 'uk':
        message = f"✅ Знайдено {len(results)} результатів:\n\n"
        
        for i, result in enumerate(results[:3], 1):
            law = result['law_name']
            para = result.get('paragraph', '')
            preview = result['content'][:200].replace('\n', ' ')
            
            message += f"{i}. **{law}** {para}\n"
            message += f"   _{preview}_...\n\n"
        
        # Додаємо повний текст першого результату
        if results:
            first = results[0]
            message += f"\n📖 **Повний текст {first['law_name']} {first.get('paragraph', '')}:**\n"
            message += f"```\n{first['content']}\n```"
    else:
        message = f"Found {len(results)} results:\n\n"
        for i, result in enumerate(results[:3], 1):
            message += f"{i}. **{result['law_name']}** {result.get('paragraph', '')}\n"
    
    return {
        'found': True,
        'message': message,
        'paragraphs': results,
        'parse_mode': 'Markdown'
    }


def quick_law_reference(law_name: str, language: str = 'uk') -> str:
    """
    Швидка довідка по закону.
    
    Args:
        law_name: Назва закону (BGB, SGB_2, тощо)
        language: Мова відповіді
    
    Returns:
        Текст з інформацією про закон
    """
    if not RAG_AVAILABLE:
        return "⚠️ RAG пошук тимчасово недоступний"
    
    # Пошук закону
    results = search_laws(law_name, n_results=10, collections=['german_laws_general'])
    
    if not results:
        return f"❌ Закон {law_name} не знайдено в базі"
    
    # Групуємо по параграфах
    paragraphs = {}
    for result in results:
        para = result.get('paragraph', 'Unknown')
        if para not in paragraphs:
            paragraphs[para] = result['content']
    
    # Формуємо відповідь
    if language == 'uk':
        response = f"📚 **{law_name}** - Знайдено параграфів: {len(paragraphs)}\n\n"
        
        for para, content in list(paragraphs.items())[:5]:
            response += f"**{para}**\n"
            response += f"_{content[:150]}..._\n\n"
        
        if len(paragraphs) > 5:
            response += f"_... ще {len(paragraphs) - 5} параграфів_"
    else:
        response = f"📚 **{law_name}** - Found {len(paragraphs)} paragraphs\n\n"
        for para, content in list(paragraphs.items())[:3]:
            response += f"**{para}**: {content[:100]}...\n"
    
    return response


# Тест
if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    
    print("\n" + "="*80)
    print("  🤖 ТЕСТУВАННЯ BOT RAG INTEGRATION")
    print("="*80)
    
    # Тест 1: Загальний запит
    print("\n📌 Тест 1: Загальний запит")
    result = rag_search_handler("Kündigung wohnung frist", language='uk')
    print(result['message'][:500])
    
    # Тест 2: Пошук параграфу
    print("\n📌 Тест 2: Пошук параграфу")
    result = search_paragraph("§ 196", law_name="BGB", language='uk')
    print(result['message'][:500])
    
    # Тест 3: Швидка довідка
    print("\n📌 Тест 3: Швидка довідка")
    result = quick_law_reference("BGB", language='uk')
    print(result[:500])
    
    print("\n" + "="*80)
    print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("="*80 + "\n")
