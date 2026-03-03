#!/usr/bin/env python3
"""
FINAL TEST v8.2 - Комплексне тестування на 50 листах
Тестує всі компоненти системи v8.2
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

def test_smart_analysis():
    """Тестування Smart Letter Analysis."""
    print_header("1️⃣ SMART LETTER ANALYSIS")
    
    from smart_letter_analysis import analyze_letter_smart
    
    test_letter = """Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch
Ihr Zeichen: 123ABC456

Sehr geehrter Herr Shevchenko,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: Montag, 12.03.2026, um 10:00 Uhr
Ort: Jobcenter Berlin Mitte, Raum 3.12

Gemäß § 59 SGB II sind Sie verpflichtet...

Mit freundlichen Grüßen
Maria Schmidt
Beraterin

Kundennummer: 123ABC456"""
    
    start = time.time()
    result = analyze_letter_smart(test_letter, 'uk')
    elapsed = time.time() - start
    
    print(f"⏱️ Час: {elapsed:.2f}s")
    print(f"✅ Організація: {result.get('organization', '❌')}")
    print(f"✅ Тип: {result.get('letter_type', '❌')}")
    print(f"✅ Параграфи: {result.get('paragraphs', '❌')}")
    print(f"✅ Дати: {result.get('dates', '❌')}")
    print(f"✅ Номер: {result.get('customer_number', '❌')}")
    print(f"✅ Впевненість: {result.get('confidence', 0)*100:.0f}%")
    
    score = 0
    if result.get('organization'): score += 20
    if result.get('letter_type'): score += 20
    if result.get('paragraphs'): score += 20
    if result.get('dates'): score += 20
    if result.get('customer_number'): score += 20
    
    print(f"\n📊 Якість: {score}/100")
    return score

def test_german_parser():
    """Тестування German Legal Parser."""
    print_header("2️⃣ GERMAN LEGAL PARSER")
    
    from german_legal_parser import extract_legal_paragraphs
    
    test_texts = [
        ("§ 59 SGB II", 1),
        ("§ 811 Abs. 1 Nr. 11 ZPO", 1),
        ("§§ 3, 4 Nr. 3a UWG", 1),
        ("§ 291 i.V.m § 288 BGB", 2),
        ("7 L 3645/97", 1),
    ]
    
    total = 0
    passed = 0
    
    for text, expected in test_texts:
        paragraphs = extract_legal_paragraphs(text)
        found = len(paragraphs) if paragraphs else 0
        total += expected
        if found >= expected:
            passed += expected
            print(f"✅ {text}: {found} знайдено")
        else:
            print(f"❌ {text}: {found}/{expected} знайдено")
    
    score = int((passed / total) * 100) if total > 0 else 0
    print(f"\n📊 Якість: {score}/100")
    return score

def test_german_templates():
    """Тестування German Templates."""
    print_header("3️⃣ GERMAN TEMPLATES")
    
    from german_templates import generate_german_response_template
    
    test_analysis = {
        'recipient_name': 'Oleksandr Shevchenko',
        'recipient_address': 'Müllerstraße 45, Apt. 12',
        'recipient_city': '13351 Berlin',
        'sender_name': 'Jobcenter Berlin Mitte',
        'sender_address': 'Straße der Migration 123',
        'sender_city': '10115 Berlin',
        'date': '15.02.2026',
        'paragraphs': ['§ 59 SGB II'],
        'customer_number': '123ABC456',
        'letter_type': 'Einladung',
    }
    
    start = time.time()
    response = generate_german_response_template(test_analysis)
    elapsed = time.time() - start
    
    print(f"⏱️ Час: {elapsed:.2f}s")
    print(f"📄 Довжина: {len(response)} символів")
    
    score = 0
    if len(response) > 500: score += 30
    if 'Oleksandr Shevchenko' in response: score += 20
    if 'Jobcenter Berlin Mitte' in response: score += 20
    if '§ 59 SGB II' in response: score += 20
    if 'Mit freundlichen Grüßen' in response: score += 10
    
    print(f"\n📊 Якість: {score}/100")
    return score

def test_ukrainian_dictionary():
    """Тестування Ukrainian Dictionary."""
    print_header("4️⃣ UKRAINIAN DICTIONARY")
    
    from ukrainian_dictionary import fix_ukrainian_text, validate_ukrainian_quality
    
    test_texts = [
        "Шановний Herr Oleksandr",
        "According to § 59 SGB II",
        "o'clock 10:00",
        "Situationem",
    ]
    
    total = len(test_texts)
    passed = 0
    
    for text in test_texts:
        fixed = fix_ukrainian_text(text)
        quality = validate_ukrainian_quality(fixed)
        
        if quality['score'] >= 90:
            passed += 1
            print(f"✅ {text} → {fixed} ({quality['score']}/100)")
        else:
            print(f"⚠️ {text} → {fixed} ({quality['score']}/100)")
    
    score = int((passed / total) * 100) if total > 0 else 0
    print(f"\n📊 Якість: {score}/100")
    return score

def test_response_validator():
    """Тестування Response Validator."""
    print_header("5️⃣ RESPONSE VALIDATOR")
    
    from response_validator import validate_response
    
    test_responses = [
        ("Шановний Herr Oleksandr, According to § 59", 'uk'),
        ("Ich kann nicht helfen", 'de'),
        ("Шановний(а), Отримав(ла) Ваше запрошення. Згідно з § 59 SGB II...", 'uk'),
        ("Sehr geehrte Damen und Herren, hiermit bestätige ich. Mit freundlichen Grüßen", 'de'),
    ]
    
    total = len(test_responses)
    passed = 0
    
    for text, lang in test_responses:
        result = validate_response(text, lang)
        
        if result['valid']:
            passed += 1
            print(f"✅ {lang}: {result['score']}/100 - Валідно")
        else:
            print(f"❌ {lang}: {result['score']}/100 - Проблеми: {', '.join(result['issues'])}")
    
    score = int((passed / total) * 100) if total > 0 else 0
    print(f"\n📊 Якість: {score}/100")
    return score

def test_50_letters():
    """Тестування на 50 листах."""
    print_header("6️⃣ ТЕСТУВАННЯ НА 50 ЛИСТАХ")
    
    letters_dir = Path('test_letters_500')
    if not letters_dir.exists():
        print("❌ Директорія test_letters_500 не знайдена!")
        print("Спочатку запустіть: python3 generate_500_test_letters.py")
        return 0
    
    from smart_letter_analysis import analyze_letter_smart
    
    letter_files = sorted(letters_dir.glob('letter_*.txt'))[:50]
    
    print(f"Тестуємо {len(letter_files)} листів...\n")
    
    results = {
        'organization': 0,
        'letter_type': 0,
        'paragraphs': 0,
        'dates': 0,
        'total': 0,
    }
    
    for i, letter_file in enumerate(letter_files, 1):
        with open(letter_file, 'r', encoding='utf-8') as f:
            letter_content = f.read()
        
        result = analyze_letter_smart(letter_content, 'uk')
        
        results['total'] += 1
        if result.get('organization') and result.get('organization') != 'Невизначено':
            results['organization'] += 1
        if result.get('letter_type') and result.get('letter_type') != 'Загальний лист':
            results['letter_type'] += 1
        if result.get('paragraphs'):
            results['paragraphs'] += 1
        if result.get('dates'):
            results['dates'] += 1
        
        if i % 10 == 0:
            print(f"   Оброблено {i}/{len(letter_files)}...")
    
    # Підсумки
    print(f"\n📊 РЕЗУЛЬТАТИ:")
    print(f"   Організації: {results['organization']}/{results['total']} ({results['organization']/results['total']*100:.0f}%)")
    print(f"   Типи листів: {results['letter_type']}/{results['total']} ({results['letter_type']/results['total']*100:.0f}%)")
    print(f"   Параграфи: {results['paragraphs']}/{results['total']} ({results['paragraphs']/results['total']*100:.0f}%)")
    print(f"   Дати: {results['dates']}/{results['total']} ({results['dates']/results['total']*100:.0f}%)")
    
    avg = (
        results['organization'] +
        results['letter_type'] +
        results['paragraphs'] +
        results['dates']
    ) / (results['total'] * 4) * 100
    
    score = int(avg)
    print(f"\n📊 Загальна якість: {score}/100")
    return score

def main():
    print_header("🧪 ФІНАЛЬНЕ ТЕСТУВАННЯ v8.2")
    print(f"Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    scores = []
    
    # Тести
    scores.append(test_smart_analysis())
    scores.append(test_german_parser())
    scores.append(test_german_templates())
    scores.append(test_ukrainian_dictionary())
    scores.append(test_response_validator())
    scores.append(test_50_letters())
    
    # Підсумки
    print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    
    total_score = sum(scores) / len(scores)
    
    print(f"Загальна якість: {Colors.BOLD}{total_score:.1f}/100{Colors.END}")
    
    if total_score >= 90:
        print(f"{Colors.GREEN}✅ ВІДМІННО{Colors.END}")
    elif total_score >= 80:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END}")
    else:
        print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END}")
    
    print(f"\n📋 ДЕТАЛІ:")
    print(f"  Smart Analysis: {scores[0]}/100")
    print(f"  German Parser: {scores[1]}/100")
    print(f"  German Templates: {scores[2]}/100")
    print(f"  Ukrainian Dictionary: {scores[3]}/100")
    print(f"  Response Validator: {scores[4]}/100")
    print(f"  50 Letters Test: {scores[5]}/100")
    
    print(f"\nЧас завершення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Збереження результатів
    output_file = Path('FINAL_TEST_RESULTS_v8.2.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'version': 'v8.2',
            'total_score': total_score,
            'scores': {
                'smart_analysis': scores[0],
                'german_parser': scores[1],
                'german_templates': scores[2],
                'ukrainian_dictionary': scores[3],
                'response_validator': scores[4],
                '50_letters_test': scores[5],
            }
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результати збережено: {output_file.absolute()}")

if __name__ == '__main__':
    main()
