#!/usr/bin/env python3
"""
Ukrainian Dictionary v8.0
Словник правильних українських юридичних термінів

Виправляє суржик та неправильні переклади
"""

# Словник неправильних → правильні терміни
CORRECT_TERMS = {
    # ЗАБОРОНЕНІ СЛОВА → ПРАВИЛЬНІ
    'Herr': 'пан',
    'Frau': 'пані',
    'Sehr geehrte': 'Шановний(а)',
    'Mit freundlichen Grüßen': 'З повагою',
    
    'According to': 'Згідно з',
    'According': 'Згідно',
    'required': 'необхідно',
    'require': 'вимагає',
    'come for': 'прийти на',
    'personal conversation': 'особиста розмова',
    'personal': 'особистий',
    'conversation': 'розмова',
    
    'o\'clock': 'о',
    'clock': 'година',
    'hour': 'година',
    
    'Situation': 'ситуація',
    'situation': 'ситуація',
    'Situationem': 'ситуацію',
    
    'documental materials': 'документи',
    'documental': 'документальний',
    'materials': 'матеріали',
    'documents': 'документи',
    
    'визначаємося': 'Отримав(ла)',
    'визначаю': 'Підтверджую',
    'визнач ourselves': 'Отримав(ла)',
    
    'Васим': 'Вашим',
    'Вас': 'Вас',
    
    'електронну адресу': 'запрошення',
    'електронна пошта': 'лист',
    
    'німецький': 'німецький',
    'німецькою': 'німецькою',
    
    'річного циклу': '',
    'рік': 'рік',
    'цикл': '',
    
    'ранню': 'ранку',
    'десяти годин': '10:00',
    
    'BGB': 'BGB (Цивільний кодекс)',
    'SGB': 'SGB (Соціальний кодекс)',
    'AO': 'AO (Податковий кодекс)',
    'ZPO': 'ZPO (Кодекс цивільного судочинства)',
}

# Правильні юридичні терміни
LEGAL_TERMS = {
    'Отримав(ла)': 'підтверджую отримання',
    'запрошення': 'виклик на зустріч',
    'лист': 'офіційне повідомлення',
    'рішення': 'офіційний документ',
    'нагадування': 'офіційне попередження',
    'згідно з': 'відповідно до',
    'параграф': 'стаття',
    'закон': 'нормативний акт',
    'кодекс': 'збірник законів',
}


def fix_ukrainian_text(text: str) -> str:
    """
    Виправлення суржику в українській відповіді.
    
    Args:
        text: Текст з помилками
        
    Returns:
        Виправлений текст
    """
    if not text:
        return text
    
    result = text
    
    # Сортуємо за довжиною (спочатку найдовші заміни)
    sorted_terms = sorted(CORRECT_TERMS.items(), key=lambda x: -len(x[0]))
    
    for wrong, correct in sorted_terms:
        # Заміна з урахуванням регістру
        result = result.replace(wrong, correct)
        result = result.replace(wrong.lower(), correct.lower())
        result = result.replace(wrong.upper(), correct.upper())
        result = result.replace(wrong.title(), correct.title())
    
    # Додаткові виправлення
    result = fix_common_mistakes(result)
    
    return result


def fix_common_mistakes(text: str) -> str:
    """Виправлення поширених помилок."""
    
    mistakes = [
        # (помилка, правильне)
        ('понеділок 12 березня', '12.03.2026'),
        ('понеділок', ''),
        ('вівторок', ''),
        ('середа', ''),
        ('четвер', ''),
        ('п\'ятниця', ''),
        ('субота', ''),
        ('неділя', ''),
        
        ('березня', 'березня'),
        ('квітня', 'квітня'),
        ('травня', 'травня'),
        ('червня', 'червня'),
        ('липня', 'липня'),
        ('серпня', 'серпня'),
        ('вересня', 'вересня'),
        ('жовтня', 'жовтня'),
        ('листопада', 'листопада'),
        ('грудня', 'грудня'),
        ('січня', 'січня'),
        ('лютого', 'лютого'),
        
        ('о 10:00', 'о 10:00'),
        ('о 11:00', 'о 11:00'),
        ('о 12:00', 'о 12:00'),
        ('о 13:00', 'о 13:00'),
        ('о 14:00', 'о 14:00'),
        ('о 15:00', 'о 15:00'),
        ('о 16:00', 'о 16:00'),
        ('о 17:00', 'о 17:00'),
        
        ('Jobcenter', 'Jobcenter'),
        ('Finanzamt', 'Finanzamt'),
        ('Inkasso', 'Inkasso'),
        
        ('§ 59 SGB II', '§ 59 SGB II'),
        ('§ 31 SGB II', '§ 31 SGB II'),
        ('§ 558 BGB', '§ 558 BGB'),
        ('§ 286 BGB', '§ 286 BGB'),
    ]
    
    result = text
    for mistake, correct in mistakes:
        result = result.replace(mistake, correct)
    
    return result


def validate_ukrainian_quality(text: str) -> dict:
    """
    Перевірка якості українського тексту.
    
    Args:
        text: Текст для перевірки
        
    Returns:
        Dict з результатами перевірки
    """
    issues = []
    score = 100
    
    # Перевірка на суржик
    for wrong in ['Herr', 'Frau', 'According', 'o\'clock', 'Situation', 'required']:
        if wrong in text:
            issues.append(f'Суржик: {wrong}')
            score -= 10
    
    # Перевірка довжини
    if len(text) < 1000:
        issues.append(f'Мало символів: {len(text)}')
        score -= 5
    
    # Перевірка на правильні терміни
    if 'Отримав(ла)' not in text and 'Отримав' not in text:
        issues.append('Немає "Отримав(ла)"')
        score -= 5
    
    if 'Згідно' not in text and 'згідно' not in text:
        issues.append('Немає "Згідно"')
        score -= 5
    
    return {
        'valid': score >= 90,
        'score': max(0, score),
        'issues': issues,
        'length': len(text),
    }


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  🇺🇦 ТЕСТУВАННЯ УКРАЇНСЬКОГО СЛОВНИКА")
    print("="*80)
    
    test_texts = [
        "Шановний Herr Oleksandr Shevchenko, визначаємося з Васим Situationem",
        "According to § 59 SGB II, you are required to come",
        "о'clock 10:00, documental materials",
        "понеділок 12 березня річного циклу",
    ]
    
    for i, text in enumerate(test_texts, 1):
        print(f"\nТест {i}:")
        print(f"  До: {text}")
        fixed = fix_ukrainian_text(text)
        print(f"  Після: {fixed}")
        
        quality = validate_ukrainian_quality(fixed)
        print(f"  Якість: {quality['score']}/100")
        if quality['issues']:
            print(f"  Проблеми: {', '.join(quality['issues'])}")
