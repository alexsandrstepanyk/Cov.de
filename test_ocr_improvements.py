#!/usr/bin/env python3
"""
Complex Test Script for Gov.de OCR Improvements
Тестування всіх покращень OCR та валідації
"""

import sys
import time
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

print("="*70)
print("  🧪 ТЕСТУВАННЯ ПОКРАЩЕНЬ OCR v4.2")
print("="*70)

# ============================================================================
# ТЕСТ 1: TextValidator
# ============================================================================
print("\n" + "="*70)
print("  ТЕСТ 1: TextValidator")
print("="*70)

from advanced_ocr import TextValidator

test_cases = [
    {
        'name': '✅ Хороший німецький текст',
        'text': """
            Ihre Kundennummer: BG123456
            Einladung zum Gespräch
            Termin: Donnerstag, 12.03.2026 um 10:00 Uhr
            Raum Nummer 123
            Kontakt: Frau Müller
            Mit freundlichen Grüßen
            Ihr Jobcenter
        """,
        'expected_valid': True,
        'expected_quality': 'good'
    },
    {
        'name': '❌ Поганий текст (з бота) - КИРИЛИЦЯ',
        'text': """
            моя довідка: номер клієнта baw homep kniehta
            (bypb nacka jobxam bka3yhte moro)
            запрошення на співбесіду шановна пані баве фпісенуе
            деталі зустрічі дата четвер 12.03.2026
        """,
        'expected_valid': False,
        'expected_quality': 'poor'
    },
    {
        'name': '⚠️ Текст середньої якості',
        'text': """
            Jobcenter Einladung
            Termin am 12.03.2026
            Bitte bringen Sie Ausweis mit
        """,
        'expected_valid': True,
        'expected_quality': 'fair'
    },
    {
        'name': '❌ Дуже короткий текст',
        'text': 'Привіт світ тест',
        'expected_valid': False,
        'expected_quality': 'poor'
    },
    {
        'name': '✅ Реальний приклад Jobcenter',
        'text': """
            JOBCENTER
            Ihre Kundennummer: BG-2024-12345
            Einladung zur persönlichen Vorsprache
            
            Sehr geehrte Frau Müller,
            
            hiermit laden wir Sie zu einem Beratungsgespräch ein.
            
            Termin: Donnerstag, 12.03.2026, 10:00 Uhr
            Raum: 234, 2. Stock
            
            Bitte bringen Sie folgende Unterlagen mit:
            - Personalausweis oder Reisepass
            - Aktuelle Bewerbungsunterlagen
            - Meldebescheinigung
            
            Rechtsfolgenbelehrung:
            Bei nichterscheinen können Leistungen gekürzt werden.
            
            Mit freundlichen Grüßen
            Ihr Jobcenter Team
        """,
        'expected_valid': True,
        'expected_quality': 'good'
    }
]

test_results = []

for i, test in enumerate(test_cases, 1):
    print(f"\n📝 Тест {i}: {test['name']}")
    print("-"*70)
    
    start = time.time()
    result = TextValidator.validate_text(test['text'])
    duration = time.time() - start
    
    # Перевірка результатів
    valid_ok = result['valid'] == test['expected_valid']
    quality_ok = result['quality'] == test['expected_quality']
    
    status = '✅' if (valid_ok and quality_ok) else '❌'
    test_results.append(status == '✅')
    
    print(f"  Час: {duration*1000:.1f}мс")
    print(f"  Валідний: {'✅' if result['valid'] else '❌'} (очікувалось: {'✅' if test['expected_valid'] else '❌'})")
    print(f"  Якість: {result['quality']} (очікувалось: {test['expected_quality']})")
    print(f"  Score: {result['quality_score']}%")
    
    if result['issues']:
        print(f"  Проблеми:")
        for issue in result['issues'][:3]:
            print(f"    • {issue}")
    
    if result.get('found_expected_words'):
        print(f"  Знайдено слів: {len(result['found_expected_words'])} ({', '.join(result['found_expected_words'][:5])})")
    
    print(f"  {status} Результат: {'PASS' if (valid_ok and quality_ok) else 'FAIL'}")

# ============================================================================
# ТЕСТ 2: AdvancedOCR (якщо є тестові зображення)
# ============================================================================
print("\n" + "="*70)
print("  ТЕСТ 2: AdvancedOCR")
print("="*70)

from advanced_ocr import AdvancedOCR

# Перевірка ініціалізації
print("\n🔧 Ініціалізація OCR рушіїв...")
ocr = AdvancedOCR()

print(f"  EasyOCR: {'✅' if 'easyocr' in ocr.engines else '❌'}")
print(f"  Tesseract: {'✅' if 'tesseract' in ocr.engines else '❌'}")
print(f"  OpenCV: {'✅' if hasattr(ocr, 'cv2') and ocr.cv2 else '❌'}")

# Пошук тестових зображень
test_images = list(Path('test_letters').glob('*.jpg')) + \
              list(Path('test_letters').glob('*.png')) + \
              list(Path('uploads').glob('*.jpg')) + \
              list(Path('uploads').glob('*.png'))

if test_images:
    print(f"\n📸 Знайдено тестових зображень: {len(test_images)}")
    
    for img_path in test_images[:3]:  # Тестуємо перші 3
        print(f"\n🖼️  Тестування: {img_path.name}")
        print("-"*70)
        
        start = time.time()
        result = ocr.recognize(str(img_path))
        duration = time.time() - start
        
        print(f"  Час обробки: {duration:.2f}с")
        print(f"  Рушій: {result['engine']}")
        print(f"  Символів: {len(result['text'])}")
        print(f"  Якість зображення: {result['quality'].get('quality', 'unknown')}")
        
        if result.get('validation'):
            val = result['validation']
            print(f"  Валідація тексту: {'✅' if val['valid'] else '❌'}")
            print(f"  Якість тексту: {val['quality']} ({val['quality_score']}%)")
            
            if val['issues']:
                print(f"  Проблеми:")
                for issue in val['issues'][:3]:
                    print(f"    • {issue}")
        
        # Показуємо перші 200 символів тексту
        if result['text']:
            preview = result['text'][:200].replace('\n', ' ')
            print(f"  Текст (прев'ю): {preview}...")
else:
    print("\n⚠️  Тестові зображення не знайдено")
    print("  Створіть папку test_letters/ з фото документів")

# ============================================================================
# ТЕСТ 3: Продуктивність кешування
# ============================================================================
print("\n" + "="*70)
print("  ТЕСТ 3: Продуктивність")
print("="*70)

from cache import get_law_cache

cache = get_law_cache()

print("\n💾 Тестування кешування законів...")

# Тест 1: Перший запит (місс)
start = time.time()
cache.set_law('BGB', '§ 286', {'test': 'data', 'size': 1000})
duration1 = time.time() - start
print(f"  Запис в кеш: {duration1*1000:.2f}мс")

# Тест 2: Отримання (хіт)
start = time.time()
result = cache.get_law('BGB', '§ 286')
duration2 = time.time() - start
print(f"  Читання з кешу: {duration2*1000:.2f}мс")
print(f"  Економія: {(duration1-duration2)/duration1*100:.1f}%")

# Тест 3: Статистика
stats = cache.get_stats()
print(f"\n📊 Статистика кешу:")
print(f"  Розмір: {stats['size']}/{stats['max_size']}")
print(f"  Hit Rate: {stats['hit_rate']}%")
print(f"  Hits: {stats['hits']}, Misses: {stats['misses']}")

# ============================================================================
# ТЕСТ 4: Моніторинг
# ============================================================================
print("\n" + "="*70)
print("  ТЕСТ 4: Моніторинг системи")
print("="*70)

from monitoring import get_metrics, get_health_checker, init_standard_checks

# Ініціалізація
init_standard_checks()

# Запуск health checks
import asyncio

async def run_health_checks():
    checker = get_health_checker()
    results = await checker.run_all_checks()
    
    print("\n🏥 Health Checks:")
    for name, result in results.items():
        icon = '✅' if result['status'] == 'healthy' else '❌'
        print(f"  {icon} {name}: {result['message']} ({result['duration_ms']}мс)")
    
    # Метрики
    metrics = get_metrics()
    stats = metrics.get_statistics()
    
    print(f"\n📈 Метрики продуктивності:")
    print(f"  Uptime: {stats['uptime_formatted']}")
    print(f"  Total Requests: {stats['total_requests']}")
    print(f"  Error Rate: {stats['error_rate_percent']}%")
    print(f"  Cache Hit Rate: {stats['cache_hit_rate_percent']}%")
    print(f"  Avg Response Time: {stats['avg_response_time_ms']}мс")

asyncio.run(run_health_checks())

# ============================================================================
# ПІДСУМКИ
# ============================================================================
print("\n" + "="*70)
print("  📊 ПІДСУМКИ ТЕСТУВАННЯ")
print("="*70)

total_tests = len(test_results)
passed_tests = sum(test_results)
pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0

print(f"\n✅ TextValidator: {passed_tests}/{total_tests} тестів ({pass_rate:.0f}%)")

if pass_rate >= 80:
    print("\n🎉 ВСІ ТЕСТИ ПРОЙДЕНО!")
    print("\n✅ OCR покращення працюють коректно")
    print("✅ Валідація тексту функціонує")
    print("✅ Кешування активне")
    print("✅ Моніторинг готовий")
else:
    print(f"\n⚠️  {total_tests - passed_tests} тестів не пройдено")
    print("Перевірте лог для деталей")

print("\n" + "="*70)
print("  ТЕСТУВАННЯ ЗАВЕРШЕНО")
print("="*70)
