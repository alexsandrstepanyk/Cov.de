#!/usr/bin/env python3
"""
OCR Integration Module for Gov.de Bot
Інтеграція OCR валідації в Telegram бота
"""

import logging
from typing import Dict, List, Optional
from pathlib import Path

logger = logging.getLogger(__name__)

# Шаблони повідомлень для користувача
OCR_MESSAGES = {
    'cyrillic_detected': """
🔴 **Знайдено кирилицю в тексті!**

Схоже це **не німецький документ**, а український/російський текст.

📋 **Можливі причини:**
• Фото поганої якості (OCR помилився)
• Це не німецький документ
• Документ змішаною мовою

💡 **Що робити:**
1. Перевірте що документ німецькою мовою
2. Зробіть фото кращої якості
3. Використовуйте поради з `OCR_TIPS_UA.md`

Бажаєте надіслати інше фото?
""",

    'poor_quality': """
⚠️ **Якість тексту низька!**

OCR не зміг надійно розпізнати текст.

📋 **Проблеми:**
{issues}

💡 **Поради для кращого фото:**
• 💡 Використовуйте денне світло
• 📐 Тримайте телефон рівно над документом
• 🔍 Натисніть на екран для фокусу
• ✅ Переконайтесь що текст чіткий

📸 Повне керівництво: `OCR_TIPS_UA.md`

Бажаєте надіслати фото ще раз?
""",

    'fair_quality': """
⚠️ **Якість тексту задовільна**

Текст розпізнано, але можливі помилки.

📋 **Проблеми:**
{issues}

💡 **Для кращих результатів:**
• Зробіть фото з кращим освітленням
• Тримайте камеру рівно

Продовжити обробку чи надіслати нове фото?
""",

    'good_quality': """
✅ **Якість тексту добра!**

Текст успішно розпізнано. Обробка...
""",

    'too_short': """
📄 **Занадто мало тексту**

Надіслане фото містить замало тексту для аналізу.

💡 **Поради:**
• Переконайтесь що весь документ в кадрі
• Наберіть камеру ближче до документу
• Надішліть фото всього документу

Бажаєте надіслати нове фото?
""",

    'nonsense_detected': """
🔤 **Багато незрозумілих слів**

OCR погано розпізнав текст (багато "сміття").

📋 **Причини:**
• Фото занадто розмите
• Погане освітлення
• Текст зім'ятий або пошкоджений

💡 **Що робити:**
• Зробіть нове фото з кращим світлом
• Тримайте камеру стабільно
• Переконайтесь що документ рівний

Бажаєте спробувати ще раз?
"""
}


class OCRValidator:
    """
    Валідація OCR тексту для інтеграції в бота.
    Надає готові повідомлення для користувачів.
    """
    
    def __init__(self):
        from advanced_ocr import TextValidator
        self.validator = TextValidator
    
    def validate(self, text: str) -> Dict:
        """
        Валідація тексту з OCR.
        
        Args:
            text: Розпізнаний текст
            
        Returns:
            Dict з результатами та повідомленням
        """
        result = self.validator.validate_text(text)
        
        # Визначаємо тип повідомлення
        message_type = self._get_message_type(result)
        message = OCR_MESSAGES.get(message_type, '').strip()
        
        # Форматуємо повідомлення з проблемами
        if '{issues}' in message and result.get('issues'):
            issues_formatted = '\n'.join(f"  • {issue}" for issue in result['issues'][:5])
            message = message.format(issues=issues_formatted)
        
        result['message'] = message
        result['message_type'] = message_type
        
        return result
    
    def _get_message_type(self, result: Dict) -> str:
        """Визначає тип повідомлення на основі результатів."""
        
        # Критичні помилки
        if result.get('has_cyrillic'):
            return 'cyrillic_detected'
        
        if not result.get('valid'):
            quality = result.get('quality', 'poor')
            
            if quality == 'poor':
                # Перевіряємо конкретні проблеми
                issues = result.get('issues', [])
                
                if any('кирилицю' in str(i).lower() for i in issues):
                    return 'cyrillic_detected'
                
                if any('незрозумілих слів' in str(i).lower() for i in issues):
                    return 'nonsense_detected'
                
                if any('мало слів' in str(i).lower() or 'короткий' in str(i).lower() for i in issues):
                    return 'too_short'
                
                return 'poor_quality'
            
            elif quality == 'fair':
                return 'fair_quality'
        
        # Хороша якість
        if result.get('quality') == 'good':
            return 'good_quality'
        
        return 'fair_quality'
    
    def should_process(self, result: Dict) -> bool:
        """
        Визначає чи можна продовжувати обробку тексту.
        
        Args:
            result: Результат валідації
            
        Returns:
            True якщо можна продовжувати
        """
        # Не обробляємо критичні помилки
        if result.get('has_cyrillic'):
            return False
        
        if not result.get('valid'):
            return False
        
        # Обробляємо fair та good якість
        quality = result.get('quality', 'poor')
        return quality in ['fair', 'good']
    
    def get_recommendations(self, result: Dict) -> List[str]:
        """Отримує список порад для користувача."""
        return result.get('recommendations', [])


# Глобальний екземпляр
_ocr_validator = None


def get_ocr_validator() -> OCRValidator:
    """Отримує глобальний екземпляр валідатора."""
    global _ocr_validator
    if _ocr_validator is None:
        _ocr_validator = OCRValidator()
    return _ocr_validator


# Приклад використання в боті
if __name__ == '__main__':
    # Тестування
    logging.basicConfig(level=logging.INFO)
    
    validator = get_ocr_validator()
    
    test_texts = [
        ("✅ Хороший німецький", """
            Ihre Kundennummer: BG123456
            Einladung zum Gespräch
            Termin: Donnerstag, 12.03.2026 um 10:00 Uhr
        """),
        ("❌ Кирилиця", "моя довідка номер клієнта baw homep kniehta"),
        ("⚠️ Погана якість", "Jobcenter Termin am"),
    ]
    
    for name, text in test_texts:
        print(f"\n{'='*60}")
        print(f"Тест: {name}")
        print(f"{'='*60}")
        
        result = validator.validate(text)
        
        print(f"Валідний: {result['valid']}")
        print(f"Якість: {result['quality']} ({result['quality_score']}%)")
        print(f"Тип повідомлення: {result['message_type']}")
        print(f"\nПовідомлення:")
        print(result['message'])
        
        should_process = validator.should_process(result)
        print(f"\nОбробляти: {'✅' if should_process else '❌'}")
