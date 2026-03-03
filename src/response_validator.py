#!/usr/bin/env python3
"""
Response Validator v8.0
Перевірка якості відповідей перед відправкою

Фільтрує погані відповіді та забезпечує 90%+ якість
"""

from typing import Dict, List


def validate_response(response: str, lang: str = 'uk') -> Dict:
    """
    Перевірка якості відповіді перед відправкою.
    
    Args:
        response: Текст відповіді
        lang: Мова відповіді ('uk' або 'de')
        
    Returns:
        Dict з результатами перевірки
    """
    
    issues = []
    score = 100
    
    if lang == 'uk':
        score, issues = validate_ukrainian(response)
    elif lang == 'de':
        score, issues = validate_german(response)
    
    return {
        'valid': score >= 90,
        'score': max(0, score),
        'issues': issues,
        'length': len(response),
        'lang': lang,
    }


def validate_ukrainian(text: str) -> tuple:
    """Перевірка української відповіді."""
    
    issues = []
    score = 100
    
    # 1. Перевірка на суржик (німецькі слова)
    german_words = ['Herr', 'Frau', 'Sehr', 'geehrte', 'Mit', 'freundlichen', 'Grüßen']
    for word in german_words:
        if word in text:
            issues.append(f'Німецьке слово: {word}')
            score -= 10
    
    # 2. Перевірка на суржик (англійські слова)
    english_words = ['According', 'required', 'come', 'personal', 'conversation', 'o\'clock', 'Situation', 'documental', 'materials']
    for word in english_words:
        if word in text:
            issues.append(f'Англійське слово: {word}')
            score -= 10
    
    # 3. Перевірка довжини
    if len(text) < 500:
        issues.append(f'Замало символів: {len(text)}')
        score -= 15
    elif len(text) < 1000:
        issues.append(f'Мало символів: {len(text)}')
        score -= 5
    
    # 4. Перевірка на правильні терміни
    required_terms = ['Отримав', 'згідно', 'Згідно']
    has_required = any(term in text for term in required_terms)
    if not has_required:
        issues.append('Немає правильних термінів')
        score -= 10
    
    # 5. Перевірка на повторення
    words = text.split()
    if len(words) > 50:
        for i in range(len(words) - 10):
            phrase = ' '.join(words[i:i+10])
            if words.count(phrase) > 3:
                issues.append(f'Повторення: "{phrase[:50]}..."')
                score -= 15
                break
    
    # 6. Перевірка на placeholder'и
    placeholders = ['[', ']', 'Ha3ba', 'Homep', 'Fpiaenue']
    for ph in placeholders:
        if ph in text:
            issues.append(f'Placeholder: {ph}')
            score -= 20
    
    return score, issues


def validate_german(text: str) -> tuple:
    """Перевірка німецької відповіді."""
    
    issues = []
    score = 100
    
    # 1. Перевірка на відмову
    refusals = [
        'Ich kann nicht',
        'Ich kann Ihnen nicht',
        'falsche',
        'fälschen',
        'Behörde',
        'Rechtsanwalt',
        'nicht dabei helfen',
        'nicht helfen',
    ]
    for refusal in refusals:
        if refusal in text:
            issues.append(f'Відмова: {refusal}')
            score -= 30
    
    # 2. Перевірка довжини
    if len(text) < 300:
        issues.append(f'Замало символів: {len(text)}')
        score -= 20
    elif len(text) < 500:
        issues.append(f'Мало символів: {len(text)}')
        score -= 10
    
    # 3. Перевірка на placeholder'и
    placeholders = ['[Name]', '[Datum]', '[Adresse]', '[Organisation]', '[']
    for ph in placeholders:
        if ph in text and ph != '[':
            issues.append(f'Placeholder: {ph}')
            score -= 15
    
    # 4. Перевірка на правильний формат DIN 5008
    din_elements = [
        'Sehr geehrte',
        'Mit freundlichen Grüßen',
        'Betreff',
    ]
    has_din = any(element in text for element in din_elements)
    if not has_din:
        issues.append('Немає формату DIN 5008')
        score -= 10
    
    # 5. Перевірка на повторення
    words = text.split()
    if len(words) > 50:
        for i in range(len(words) - 10):
            phrase = ' '.join(words[i:i+10])
            if words.count(phrase) > 3:
                issues.append(f'Повторення: "{phrase[:50]}..."')
                score -= 15
                break
    
    # 6. Перевірка на конкретні дані (імена, дати)
    import re
    has_name = bool(re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', text))
    has_date = bool(re.search(r'\d{2}\.\d{2}\.\d{4}', text))
    
    if not has_name:
        issues.append('Немає імені')
        score -= 10
    if not has_date:
        issues.append('Немає дати')
        score -= 10
    
    return score, issues


def validate_and_fix(response: str, lang: str = 'uk') -> Dict:
    """
    Перевірка та виправлення відповіді.
    
    Args:
        response: Текст відповіді
        lang: Мова відповіді
        
    Returns:
        Dict з виправленою відповіддю
    """
    
    # Перевірка
    validation = validate_response(response, lang)
    
    # Якщо якість низька - виправляємо
    if not validation['valid']:
        if lang == 'de':
            # Для німецької - використовуємо fallback шаблон
            from german_templates import generate_german_response_template
            response = generate_german_response_template({})
            validation = validate_response(response, lang)
        elif lang == 'uk':
            # Для української - виправляємо суржик
            from ukrainian_dictionary import fix_ukrainian_text
            response = fix_ukrainian_text(response)
            validation = validate_response(response, lang)
    
    return {
        'response': response,
        'validation': validation,
        'fixed': validation['valid'],
    }


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  ✅ ТЕСТУВАННЯ ВАЛІДАТОРА")
    print("="*80)
    
    test_cases = [
        {
            'text': "Шановний Herr Oleksandr, According to § 59 SGB II",
            'lang': 'uk',
            'name': 'Суржик UK',
        },
        {
            'text': "Ich kann nicht helfen. Bitte an Behörde wenden.",
            'lang': 'de',
            'name': 'Відмова DE',
        },
        {
            'text': "Шановний(а), Отримав(ла) Ваше запрошення. Згідно з § 59 SGB II...",
            'lang': 'uk',
            'name': 'Правильна UK',
        },
        {
            'text': "Sehr geehrte Damen und Herren, hiermit bestätige ich. Mit freundlichen Grüßen",
            'lang': 'de',
            'name': 'Правильна DE',
        },
    ]
    
    for test in test_cases:
        print(f"\n📝 {test['name']}:")
        print(f"  Довжина: {len(test['text'])} символів")
        
        result = validate_response(test['text'], test['lang'])
        print(f"  Якість: {result['score']}/100")
        print(f"  Валідно: {'✅' if result['valid'] else '❌'}")
        
        if result['issues']:
            print(f"  Проблеми:")
            for issue in result['issues']:
                print(f"    - {issue}")
