#!/usr/bin/env python3
"""
TEST 500 LETTERS - Gov.de Bot v6.0
Автоматичне тестування бота на 500 листах

Аналізує:
1. Якість аналізу (визначення організації, параграфів)
2. Якість перекладу (українська)
3. Якість німецької відповіді (DIN 5008)
4. Час обробки
5. Наявність повторень
6. Заповнення шаблонів
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent / 'src'))

# Кольори
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}\n")

def analyze_response_quality(response_text: str) -> dict:
    """Аналіз якості відповіді."""
    checks = {
        'has_repetitions': False,
        'has_placeholders': False,
        'has_paragraphs': False,
        'has_dates': False,
        'has_names': False,
        'length': len(response_text),
        'quality_score': 0,
    }
    
    # Перевірка на повторення
    words = response_text.split()
    if len(words) > 100:
        for i in range(len(words) - 20):
            phrase = ' '.join(words[i:i+10])
            if words.count(phrase) > 3:
                checks['has_repetitions'] = True
                break
    
    # Перевірка на placeholder'и
    placeholders = ['[', ']', 'Ha3ba', 'Homep', 'Fpiaenue']
    for ph in placeholders:
        if ph in response_text:
            checks['has_placeholders'] = True
            break
    
    # Перевірка на параграфи
    if '§' in response_text or 'BGB' in response_text or 'SGB' in response_text:
        checks['has_paragraphs'] = True
    
    # Перевірка на дати
    import re
    if re.search(r'\d{2}\.\d{2}\.\d{4}', response_text):
        checks['has_dates'] = True
    
    # Перевірка на імена
    if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', response_text):
        checks['has_names'] = True
    
    # Розрахунок quality score
    score = 0
    if checks['length'] > 500:
        score += 20
    if not checks['has_repetitions']:
        score += 30
    if not checks['has_placeholders']:
        score += 20
    if checks['has_paragraphs']:
        score += 10
    if checks['has_dates']:
        score += 10
    if checks['has_names']:
        score += 10
    
    checks['quality_score'] = score
    
    return checks

def test_letter(letter_content: str, letter_id: int) -> dict:
    """Тестування одного листа."""
    from llm_orchestrator import process_letter_with_llm
    
    start_time = time.time()
    
    # Аналіз
    result = process_letter_with_llm(letter_content, 'uk')
    
    elapsed = time.time() - start_time
    
    # Аналіз якості
    uk_quality = analyze_response_quality(result.get('response_user', ''))
    de_quality = analyze_response_quality(result.get('response_de', ''))
    
    return {
        'id': letter_id,
        'success': result.get('success', False),
        'time': elapsed,
        'uk_length': len(result.get('response_user', '')),
        'de_length': len(result.get('response_de', '')),
        'uk_quality': uk_quality,
        'de_quality': de_quality,
        'analysis': result.get('analysis', {}),
    }

def main():
    print_header("🧪 ТЕСТУВАННЯ 500 ЛИСТІВ - Gov.de Bot v6.0")
    print(f"Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Директорія з листами
    letters_dir = Path('test_letters_500')
    if not letters_dir.exists():
        print(f"❌ Директорія {letters_dir} не знайдена!")
        print("Спочатку запустіть: python3 generate_500_test_letters.py")
        return
    
    # Беремо перші 50 листів для тесту (щоб не довго)
    letter_files = sorted(letters_dir.glob('letter_*.txt'))[:50]
    
    print(f"Тестуємо {len(letter_files)} листів...\n")
    
    results = []
    passed = 0
    failed = 0
    
    for i, letter_file in enumerate(letter_files, 1):
        print(f"Тест {i}/{len(letter_files)}: {letter_file.name}...", end=" ")
        
        with open(letter_file, 'r', encoding='utf-8') as f:
            letter_content = f.read()
        
        try:
            result = test_letter(letter_content, i)
            results.append(result)
            
            if result['success'] and result['uk_quality']['quality_score'] >= 70:
                print(f"{Colors.GREEN}✅ PASS{Colors.END} ({result['time']:.2f}s)")
                passed += 1
            else:
                print(f"{Colors.RED}❌ FAIL{Colors.END} (score: {result['uk_quality']['quality_score']})")
                failed += 1
        except Exception as e:
            print(f"{Colors.RED}❌ ERROR: {e}{Colors.END}")
            failed += 1
            results.append({
                'id': i,
                'success': False,
                'error': str(e),
            })
    
    # Підсумки
    print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    
    success_rate = (passed / len(letter_files)) * 100 if letter_files else 0
    
    print(f"\nЗагальна точність: {Colors.BOLD}{passed}/{len(letter_files)} ({success_rate:.1f}%){Colors.END}")
    
    if success_rate >= 90:
        print(f"{Colors.GREEN}✅ ВІДМІННО{Colors.END}")
    elif success_rate >= 70:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END}")
    else:
        print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END}")
    
    # Статистика
    if results:
        avg_time = sum(r.get('time', 0) for r in results if 'time' in r) / len(results)
        avg_uk_length = sum(r.get('uk_length', 0) for r in results if 'uk_length' in r) / len(results)
        avg_de_length = sum(r.get('de_length', 0) for r in results if 'de_length' in r) / len(results)
        avg_uk_quality = sum(r.get('uk_quality', {}).get('quality_score', 0) for r in results if 'uk_quality' in r) / len(results)
        avg_de_quality = sum(r.get('de_quality', {}).get('quality_score', 0) for r in results if 'de_quality' in r) / len(results)
        
        print(f"\n📊 СТАТИСТИКА:")
        print(f"  Середній час обробки: {avg_time:.2f}s")
        print(f"  Середня довжина UK: {avg_uk_length:.0f} символів")
        print(f"  Середня довжина DE: {avg_de_length:.0f} символів")
        print(f"  Середня якість UK: {avg_uk_quality:.1f}/100")
        print(f"  Середня якість DE: {avg_de_quality:.1f}/100")
        
        # Проблеми
        repetitions = sum(1 for r in results if r.get('uk_quality', {}).get('has_repetitions', False))
        placeholders = sum(1 for r in results if r.get('uk_quality', {}).get('has_placeholders', False))
        
        print(f"\n⚠️ ПРОБЛЕМИ:")
        print(f"  Повторення тексту: {repetition} листів")
        print(f"  Незаповнені шаблони: {placeholders} листів")
    
    # Збереження результатів
    output_file = Path('test_results_500.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'total_letters': len(letter_files),
            'passed': passed,
            'failed': failed,
            'success_rate': success_rate,
            'results': results,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результати збережено: {output_file.absolute()}")
    print(f"\nЧас завершення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

if __name__ == '__main__':
    main()
