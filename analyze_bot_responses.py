#!/usr/bin/env python3
"""
ANALYZE BOT RESPONSES
Аналіз того що бот відправляє клієнту в Telegram

Перехоплює відповіді бота та аналізує:
1. Якість української відповіді
2. Якість німецької відповіді
3. Наявність повторень
4. Наявність шаблонів ([], [Ha3ba])
5. Довжина відповіді
6. Час обробки
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

def analyze_bot_response(response_text: str, response_type: str = 'uk') -> dict:
    """Аналіз відповіді бота."""
    analysis = {
        'type': response_type,
        'length': len(response_text),
        'has_repetitions': False,
        'has_placeholders': False,
        'has_paragraphs': False,
        'has_dates': False,
        'has_names': False,
        'word_count': len(response_text.split()),
        'issues': [],
        'quality_score': 0,
    }
    
    # 1. Перевірка на повторення
    words = response_text.split()
    if len(words) > 50:
        for i in range(len(words) - 10):
            phrase = ' '.join(words[i:i+10])
            if words.count(phrase) > 3:
                analysis['has_repetitions'] = True
                analysis['issues'].append(f'Повторення: "{phrase[:50]}..."')
                break
    
    # 2. Перевірка на placeholder'и
    placeholders = ['[', ']', 'Ha3ba', 'Homep', 'Fpiaenue', 'cniepobiTHMka', 'Bawe', 'Rum']
    for ph in placeholders:
        if ph in response_text:
            analysis['has_placeholders'] = True
            analysis['issues'].append(f'Placeholder: {ph}')
    
    # 3. Перевірка на параграфи
    import re
    if '§' in response_text or 'BGB' in response_text or 'SGB' in response_text or 'AO' in response_text:
        analysis['has_paragraphs'] = True
    
    # 4. Перевірка на дати
    if re.search(r'\d{2}\.\d{2}\.\d{4}', response_text):
        analysis['has_dates'] = True
    
    # 5. Перевірка на імена
    if re.search(r'[A-Z][a-z]+ [A-Z][a-z]+', response_text):
        analysis['has_names'] = True
    
    # 6. Розрахунок quality score
    score = 0
    if analysis['length'] > 500:
        score += 20
    if not analysis['has_repetitions']:
        score += 30
    if not analysis['has_placeholders']:
        score += 20
    if analysis['has_paragraphs']:
        score += 10
    if analysis['has_dates']:
        score += 10
    if analysis['has_names']:
        score += 10
    
    analysis['quality_score'] = score
    
    return analysis

def test_with_sample_letter():
    """Тестування на зразковому листі."""
    from llm_orchestrator import process_letter_with_llm
    
    # Зразковий лист Jobcenter
    sample_letter = """Jobcenter Berlin Mitte
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

Kundennummer: 123ABC456
Telefon: 030 1234 5678
"""
    
    print_header("🔍 АНАЛІЗ ВІДПОВІДЕЙ БОТА")
    print(f"Тестовий лист: Jobcenter Einladung")
    print(f"Довжина: {len(sample_letter)} символів\n")
    
    start_time = time.time()
    
    # Обробка
    result = process_letter_with_llm(sample_letter, 'uk')
    
    elapsed = time.time() - start_time
    
    print(f"⏱️ Час обробки: {elapsed:.2f}s\n")
    
    # Аналіз української відповіді
    print(f"{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}🇺🇦 УКРАЇНСЬКА ВІДПОВІДЬ{Colors.END}")
    print(f"{'='*80}")
    
    uk_response = result.get('response_user', '')
    uk_analysis = analyze_bot_response(uk_response, 'uk')
    
    print(f"Довжина: {uk_analysis['length']} символів")
    print(f"Кількість слів: {uk_analysis['word_count']}")
    print(f"Якість: {uk_analysis['quality_score']}/100")
    
    if uk_analysis['issues']:
        print(f"\n{Colors.RED}⚠️ ПРОБЛЕМИ:{Colors.END}")
        for issue in uk_analysis['issues']:
            print(f"  - {issue}")
    
    print(f"\n{Colors.CYAN}Текст (перші 500 символів):{Colors.END}")
    print(uk_response[:500] + "...\n")
    
    # Аналіз німецької відповіді
    print(f"{Colors.BLUE}{'='*80}{Colors.END}")
    print(f"{Colors.BOLD}🇩🇪 НІМЕЦЬКА ВІДПОВІДЬ{Colors.END}")
    print(f"{'='*80}")
    
    de_response = result.get('response_de', '')
    de_analysis = analyze_bot_response(de_response, 'de')
    
    print(f"Довжина: {de_analysis['length']} символів")
    print(f"Кількість слів: {de_analysis['word_count']}")
    print(f"Якість: {de_analysis['quality_score']}/100")
    
    if de_analysis['issues']:
        print(f"\n{Colors.RED}⚠️ ПРОБЛЕМИ:{Colors.END}")
        for issue in de_analysis['issues']:
            print(f"  - {issue}")
    
    print(f"\n{Colors.CYAN}Текст (перші 500 символів):{Colors.END}")
    print(de_response[:500] + "...\n")
    
    # Фінальний висновок
    print_header("📊 ВИСНОВКИ")
    
    total_score = (uk_analysis['quality_score'] + de_analysis['quality_score']) / 2
    
    if total_score >= 80:
        print(f"{Colors.GREEN}✅ ВІДМІННО{Colors.END} ({total_score:.1f}/100)")
    elif total_score >= 60:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ{Colors.END} ({total_score:.1f}/100)")
    else:
        print(f"{Colors.RED}❌ ПОТРЕБУЄ ПОКРАЩЕНЬ{Colors.END} ({total_score:.1f}/100)")
    
    print(f"\n📋 РЕКОМЕНДАЦІЇ:")
    
    if uk_analysis['has_repetitions'] or de_analysis['has_repetitions']:
        print("  1. ⚠️ Виправити повторення тексту")
    if uk_analysis['has_placeholders'] or de_analysis['has_placeholders']:
        print("  2. ⚠️ Виправити заповнення шаблонів")
    if not uk_analysis['has_paragraphs']:
        print("  3. ⚠️ Додати параграфи в українську відповідь")
    if not de_analysis['has_dates'] or not de_analysis['has_names']:
        print("  4. ⚠️ Додати конкретні дані в німецьку відповідь")
    
    # Збереження результатів
    output_file = Path('bot_response_analysis.json')
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump({
            'test_date': datetime.now().isoformat(),
            'elapsed_time': elapsed,
            'uk_response': uk_response,
            'uk_analysis': uk_analysis,
            'de_response': de_response,
            'de_analysis': de_analysis,
            'total_score': total_score,
        }, f, ensure_ascii=False, indent=2)
    
    print(f"\n💾 Результати збережено: {output_file.absolute()}")

def print_header(text):
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(80)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*80}{Colors.END}\n")

if __name__ == '__main__':
    test_with_sample_letter()
