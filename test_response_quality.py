#!/usr/bin/env python3
"""
🧪 ТЕСТ ЯКОСТІ ВІДПОВІДЕЙ БОТА

Перевіряє якість відповідей які бот рекомендує відправляти.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from smart_law_reference import analyze_letter_smart, generate_response_smart

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
    print(f"\n{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{text.center(70)}{Colors.END}")
    print(f"{Colors.CYAN}{Colors.BOLD}{'='*70}{Colors.END}\n")

# ============================================================================
# ТЕСТОВІ ЛИСТИ
# ============================================================================

test_letters = [
    {
        'name': 'Jobcenter Einladung (Лист 1)',
        'text': '''Jobcenter Berlin Mitte
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
Ansprechpartner: Frau Schmidt

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktuelle Meldebescheinigung
- Lebenslauf (CV)
- Zeugnisse und Qualifikationsnachweise
- Nachweise über Bewerbungen der letzten 3 Monate

Wichtiger Hinweis:
Gemäß § 59 SGB II sind Sie verpflichtet, zu allen Einladungen des Jobcenters zu erscheinen. Bei unentschuldigtem Fehlen kann Ihre Leistung um 30% gekürzt werden (§ 31 SGB II).

Bei Krankheit müssen Sie uns unverzüglich eine ärztliche Bescheinigung vorlegen.

Mit freundlichen Grüßen

Im Auftrag

Maria Schmidt
Beraterin

Kundennummer: 123ABC456
Telefon: 030 1234 5678
E-Mail: kontakt@jobcenter-berlin-mitte.de
''',
        'expected_org': 'jobcenter',
        'expected_sit': 'einladung',
        'expected_paras': ['§ 59 SGB II', '§ 31 SGB II'],
        'expected_date': '12.03.2026',
        'expected_time': '10:00',
        'expected_customer_number': '123ABC456'
    },
    {
        'name': 'Inkasso Mahnung (Лист 6)',
        'text': '''CreditProtect Inkasso GmbH
Forderungsstraße 789
20095 Hamburg

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Hamburg, 20.02.2026

Erste Mahnung
Forderungsnummer: 2026/12345

Sehr geehrter Herr Shevchenko,

leider mussten wir feststellen, dass Sie Ihrer Zahlungsverpflichtung nicht nachgekommen sind.

Offener Betrag: 350,00 EUR
Fälligkeit: 15.02.2026

Bitte überweisen Sie den Betrag bis zum 05.03.2026 auf unser Konto:

IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Commerzbank Hamburg

Verwendungszweck: 2026/12345

Bei Fragen stehen wir Ihnen unter 040 9876 5432 zur Verfügung.

Mit freundlichen Grüßen

CreditProtect Inkasso GmbH

Thomas Weber
Geschäftsführer

Telefon: 040 9876 5432
''',
        'expected_org': 'inkasso',
        'expected_sit': 'forderung',
        'expected_paras': [],
        'expected_amount': '350,00',
        'expected_iban': 'DE89 3704 0044 0532 0130 00'
    },
    {
        'name': 'Vermieter Mieterhöhung (Лист 10)',
        'text': '''Vermieter Hans Müller
Wohnungsstraße 12
13351 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 18.02.2026

Mieterhöhung bis zur ortsüblichen Vergleichsmiete

Sehr geehrter Herr Shevchenko,

die Miete für Ihre Wohnung in der Müllerstraße 45, Apt. 12, beträgt derzeit 450,00 EUR kalt.

Nach Überprüfung der ortsüblichen Vergleichsmiete müssen wir die Miete anpassen. Der aktuelle Mietspiegel Berlin 2026 zeigt, dass vergleichbare Wohnungen in Ihrer Lage durchschnittlich 550,00 EUR kosten.

Wir erhöhen daher die Miete wie folgt:

Aktuelle Miete: 450,00 EUR
Neue Miete: 550,00 EUR
Erhöhung: 100,00 EUR (22,2%)

Die Mieterhöhung tritt ab dem 01.05.2026 in Kraft.

Rechtliche Hinweise:
Gemäß § 558 BGB kann die Miete bis zur ortsüblichen Vergleichsmiete erhöht werden. Die Erhöhung beträgt maximal 20% innerhalb von 3 Jahren (§ 558 Abs. 3 BGB).

Sie haben ein Widerspruchsrecht bis zum 30.04.2026.

Mit freundlichen Grüßen

Hans Müller
Vermieter

Telefon: 0171 234 5678
''',
        'expected_org': 'vermieter',
        'expected_sit': 'mieterhöhung',
        'expected_paras': ['§ 558 BGB'],
        'expected_amount': '100,00',
        'expected_date': '01.05.2026'
    }
]

# ============================================================================
# ОЦІНКА ЯКОСТІ ВІДПОВІДІ
# ============================================================================

def evaluate_response_quality(response_text, test_case, law_info):
    """Оцінка якості відповіді за 10-бальною шкалою."""
    
    score = 0
    max_score = 10
    issues = []
    strengths = []
    
    # 1. Перевірка довжини (має бути 80+ символів)
    if len(response_text) >= 80:
        score += 1
        strengths.append("✅ Достатня довжина")
    else:
        issues.append(f"❌ Занадто коротка ({len(response_text)} символів)")
    
    # 2. Перевірка наявності звертання
    if any(word in response_text.lower() for word in ['шановний', 'шановна', 'sehr geehrte', 'уважаемый']):
        score += 1
        strengths.append("✅ Є звертання")
    else:
        issues.append("❌ Немає звертання")
    
    # 3. Перевірка наявності конкретики (дати, суми, номери)
    has_specifics = False
    
    # Дати
    if test_case.get('expected_date') and test_case['expected_date'] in response_text:
        score += 1
        strengths.append(f"✅ Є дата з листа ({test_case['expected_date']})")
        has_specifics = True
    elif '[' in response_text and 'ДАТА' in response_text:
        issues.append("❌ Шаблонне місце [ДАТА] замість конкретного значення")
    
    # Час
    if test_case.get('expected_time') and test_case['expected_time'] in response_text:
        score += 1
        strengths.append(f"✅ Є час з листа ({test_case['expected_time']})")
        has_specifics = True
    elif '[' in response_text and 'ЧАС' in response_text:
        issues.append("❌ Шаблонне місце [ЧАС] замість конкретного значення")
    
    # Суми
    if test_case.get('expected_amount') and test_case['expected_amount'] in response_text:
        score += 1
        strengths.append(f"✅ Є сума з листа ({test_case['expected_amount']})")
        has_specifics = True
    
    # Номер клієнта
    if test_case.get('expected_customer_number') and test_case['expected_customer_number'] in response_text:
        score += 1
        strengths.append(f"✅ Є номер клієнта")
        has_specifics = True
    elif '[' in response_text and 'НОМЕР' in response_text:
        issues.append("❌ Шаблонне місце [НОМЕР] замість конкретного значення")
    
    if not has_specifics and len(response_text) < 150:
        issues.append("❌ Відповідь занадто загальна, без конкретики")
    
    # 4. Перевірка наявності законів
    if test_case.get('expected_paras'):
        for para in test_case['expected_paras']:
            if para in response_text:
                score += 1
                strengths.append(f"✅ Є посилання на {para}")
    
    # 5. Перевірка структури
    if '📋' in response_text or '📅' in response_text or '⚖️' in response_text:
        score += 1
        strengths.append("✅ Є emoji структура")
    
    # 6. Перевірка закінчення
    if any(word in response_text.lower() for word in ['з повагою', 'mit freundlichen grüßen', 'с уважением']):
        score += 1
        strengths.append("✅ Є підпис")
    else:
        issues.append("❌ Немає підпису")
    
    # 7. Перевірка на повноту (наявність 3+ речень)
    sentences = response_text.count('.') + response_text.count('!') + response_text.count('?')
    if sentences >= 3:
        score += 1
        strengths.append(f"✅ Достатня кількість речень ({sentences})")
    else:
        issues.append(f"❌ Замало речень ({sentences})")
    
    # 8. Перевірка чи є конкретні дії
    action_words = ['підтверджую', 'прошу', 'подаю', 'заперечую', 'bestätige', 'widerspreche', 'просьба']
    if any(word in response_text.lower() for word in action_words):
        score += 1
        strengths.append("✅ Є конкретна дія")
    else:
        issues.append("❌ Немає конкретної дії")
    
    # 9. Бонус за довжину (>200 символів)
    if len(response_text) > 200:
        score += 1
        strengths.append("✅ Розгорнута відповідь")
    
    # 10. Бонус за структуру (абзаци)
    if '\n\n' in response_text:
        score += 1
        strengths.append("✅ Є структура з абзацами")
    
    return score, max_score, strengths, issues


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def main():
    print_header("🧪 ТЕСТ ЯКОСТІ ВІДПОВІДЕЙ БОТА v4.4")
    print(f"\n{Colors.YELLOW}ТЕСТУЄМО ПОКРАЩЕНУ ВЕРСІЮ (improved_response_generator){Colors.END}\n")
    
    # Імпортуємо покращену версію
    import sys
    sys.path.insert(0, str(Path(__file__).parent / 'src'))
    from improved_response_generator import generate_response_smart_improved
    
    total_score = 0
    total_max = 0
    
    for i, test_case in enumerate(test_letters, 1):
        print(f"\n{Colors.BLUE}{'='*70}{Colors.END}")
        print(f"{Colors.BOLD}ТЕСТ {i}: {test_case['name']}{Colors.END}")
        print(f"{'='*70}\n")
        
        # Отримуємо аналіз з ПОКРАЩЕНОЇ версії
        result = analyze_letter_smart(test_case['text'], 'uk')
        response_uk, law_info = generate_response_smart_improved(test_case['text'], 'uk')
        response_de, _ = generate_response_smart_improved(test_case['text'], 'de')
        
        print(f"{Colors.GREEN}🏢 Організація:{Colors.END} {law_info.get('organization', 'N/A')}")
        print(f"{Colors.GREEN}📋 Ситуація:{Colors.END} {law_info.get('situation', 'N/A')}")
        print(f"{Colors.GREEN}📚 Параграфи:{Colors.END} {law_info.get('paragraphs', [])}")
        print(f"{Colors.GREEN}💡 Поради:{Colors.END} {result.get('tips', [])}")
        
        print(f"\n{Colors.YELLOW}📝 ВІДПОВІДЬ (UK):{Colors.END}")
        print(f"{Colors.CYAN}{response_uk}{Colors.END}")
        
        print(f"\n{Colors.YELLOW}📝 ANTWORT (DE):{Colors.END}")
        print(f"{Colors.CYAN}{response_de}{Colors.END}")
        
        # Оцінка якості
        score, max_score, strengths, issues = evaluate_response_quality(response_uk, test_case, law_info)
        
        print(f"\n{Colors.BOLD}📊 ОЦІНКА ЯКОСТІ: {score}/{max_score}{Colors.END}")
        
        if strengths:
            print(f"\n{Colors.GREEN}✅ СИЛЬНІ СТОРОНИ:{Colors.END}")
            for s in strengths:
                print(f"  {s}")
        
        if issues:
            print(f"\n{Colors.RED}❌ ПРОБЛЕМИ:{Colors.END}")
            for issue in issues:
                print(f"  {issue}")
        
        total_score += score
        total_max += max_score
    
    # Підсумки
    print_header("📊 ПІДСУМКОВА ОЦІНКА")
    
    percentage = (total_score / total_max) * 100 if total_max > 0 else 0
    
    print(f"\nЗагальна оцінка: {Colors.BOLD}{total_score}/{total_max} ({percentage:.1f}%){Colors.END}")
    
    if percentage >= 80:
        print(f"{Colors.GREEN}✅ ВІДМІННО - Відповіді якісні{Colors.END}")
    elif percentage >= 60:
        print(f"{Colors.YELLOW}⚠️ ДОБРЕ - Потрібні невеликі покращення{Colors.END}")
    elif percentage >= 40:
        print(f"{Colors.YELLOW}⚠️ ЗАДОВІЛЬНО - Потрібні покращення{Colors.END}")
    else:
        print(f"{Colors.RED}❌ ПОГАНО - Відповіді потребують серйозного доопрацювання{Colors.END}")
    
    print(f"\n{Colors.BOLD}📋 РЕКОМЕНДАЦІЇ:{Colors.END}")
    print("1. ✅ Додати автоматичне заповнення шаблонних полів ([ДАТА], [ЧАС], [НОМЕР])")
    print("2. ✅ Розширити шаблони відповідей (до 150-200 символів)")
    print("3. ✅ Додати конкретні посилання на параграфи з листа")
    print("4. ✅ Додати структурированість (emoji, абзаци)")
    print("5. ✅ Додати конкретні дії (підтверджую, прошу, заперечую)")
    
    return percentage

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 60 else 1)
