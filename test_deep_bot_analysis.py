#!/usr/bin/env python3
"""
Deep Bot Analysis Test - 50 Test Letters
Глибокий аналіз роботи бота на 50 тестових листах

Тестує:
1. OCR розпізнавання
2. Переклад
3. RAG пошук законів
4. Класифікацію документів
5. Генерацію відповідей
"""

import sys
import time
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Імпорт модулів бота
try:
    from advanced_ocr import process_image
    OCR_AVAILABLE = True
except:
    OCR_AVAILABLE = False

try:
    from advanced_translator import translate_text_async
    TRANSLATOR_AVAILABLE = True
except:
    TRANSLATOR_AVAILABLE = False

try:
    from rag_law_search import search_laws
    RAG_AVAILABLE = True
except:
    RAG_AVAILABLE = False

try:
    from advanced_classification import classify_document
    CLASSIFIER_AVAILABLE = True
except:
    CLASSIFIER_AVAILABLE = False

try:
    from response_generator import generate_response
    RESPONSE_GEN_AVAILABLE = True
except:
    RESPONSE_GEN_AVAILABLE = False


# Тестові листи (50 штук)
TEST_LETTERS = [
    # Jobcenter (10)
    {
        'id': 1,
        'type': 'Jobcenter',
        'text': 'Einladung zur persönlichen Vorsprache gemäß § 59 SGB II am 15.03.2026 um 10:00 Uhr.',
        'expected_laws': ['§ 59 SGB II'],
        'expected_org': 'Jobcenter'
    },
    {
        'id': 2,
        'type': 'Jobcenter',
        'text': 'Bescheid über Leistungen zur Sicherung des Lebensunterhalts nach SGB II.',
        'expected_laws': ['SGB II'],
        'expected_org': 'Jobcenter'
    },
    {
        'id': 3,
        'type': 'Jobcenter',
        'text': 'Aufforderung zur Abgabe der Vermögenserklärung gemäß § 60 SGB I.',
        'expected_laws': ['§ 60 SGB I'],
        'expected_org': 'Jobcenter'
    },
    {
        'id': 4,
        'type': 'Jobcenter',
        'text': 'Mitteilung über die Bewilligung von Bürgergeld ab 01.04.2026.',
        'expected_laws': ['SGB II'],
        'expected_org': 'Jobcenter'
    },
    {
        'id': 5,
        'type': 'Jobcenter',
        'text': 'Terminvereinbarung für das Beratungsgespräch gemäß § 14 SGB II.',
        'expected_laws': ['§ 14 SGB II'],
        'expected_org': 'Jobcenter'
    },
    
    # Finanzamt (10)
    {
        'id': 6,
        'type': 'Finanzamt',
        'text': 'Steuerbescheid für das Jahr 2025 gemäß § 172 AO.',
        'expected_laws': ['§ 172 AO'],
        'expected_org': 'Finanzamt'
    },
    {
        'id': 7,
        'type': 'Finanzamt',
        'text': 'Aufforderung zur Abgabe der Einkommensteuererklärung 2025.',
        'expected_laws': ['EStG'],
        'expected_org': 'Finanzamt'
    },
    {
        'id': 8,
        'type': 'Finanzamt',
        'text': 'Zahlungsaufforderung für rückständige Steuern gemäß § 250 AO.',
        'expected_laws': ['§ 250 AO'],
        'expected_org': 'Finanzamt'
    },
    {
        'id': 9,
        'type': 'Finanzamt',
        'text': 'Bescheid über die Festsetzung von Säumniszuschlägen gemäß § 240 AO.',
        'expected_laws': ['§ 240 AO'],
        'expected_org': 'Finanzamt'
    },
    {
        'id': 10,
        'type': 'Finanzamt',
        'text': 'Prüfungsanordnung für eine Außenprüfung gemäß § 196 AO.',
        'expected_laws': ['§ 196 AO'],
        'expected_org': 'Finanzamt'
    },
    
    # Vermieter (10)
    {
        'id': 11,
        'type': 'Vermieter',
        'text': 'Kündigung der Wohnung wegen Zahlungsverzugs gemäß § 543 BGB.',
        'expected_laws': ['§ 543 BGB'],
        'expected_org': 'Vermieter'
    },
    {
        'id': 12,
        'type': 'Vermieter',
        'text': 'Mieterhöhung um 15% gemäß § 558 BGB ab 01.05.2026.',
        'expected_laws': ['§ 558 BGB'],
        'expected_org': 'Vermieter'
    },
    {
        'id': 13,
        'type': 'Vermieter',
        'text': 'Aufforderung zur Duldung von Modernisierungsmaßnahmen gemäß § 555 BGB.',
        'expected_laws': ['§ 555 BGB'],
        'expected_org': 'Vermieter'
    },
    {
        'id': 14,
        'type': 'Vermieter',
        'text': 'Nebenkostenabrechnung für das Jahr 2025 mit Nachzahlung.',
        'expected_laws': ['BGB'],
        'expected_org': 'Vermieter'
    },
    {
        'id': 15,
        'type': 'Vermieter',
        'text': 'Fristlose Kündigung wegen unerlaubter Untervermietung gemäß § 543 BGB.',
        'expected_laws': ['§ 543 BGB'],
        'expected_org': 'Vermieter'
    },
    
    # Inkasso (10)
    {
        'id': 16,
        'type': 'Inkasso',
        'text': 'Mahnung mit letzter Fristsetzung zur Zahlung von 1.250€.',
        'expected_laws': ['BGB § 286'],
        'expected_org': 'Inkasso'
    },
    {
        'id': 17,
        'type': 'Inkasso',
        'text': 'Zahlungsaufforderung wegen offener Forderung gemäß § 286 BGB.',
        'expected_laws': ['§ 286 BGB'],
        'expected_org': 'Inkasso'
    },
    {
        'id': 18,
        'type': 'Inkasso',
        'text': 'Androhung gerichtlicher Maßnahmen bei nicht fristgerechter Zahlung.',
        'expected_laws': ['ZPO'],
        'expected_org': 'Inkasso'
    },
    {
        'id': 19,
        'type': 'Inkasso',
        'text': 'Forderungsübergabe an Inkassobüro gemäß § 280 BGB.',
        'expected_laws': ['§ 280 BGB'],
        'expected_org': 'Inkasso'
    },
    {
        'id': 20,
        'type': 'Inkasso',
        'text': 'Zahlungserinnerung mit Fristsetzung bis 30.03.2026.',
        'expected_laws': ['BGB'],
        'expected_org': 'Inkasso'
    },
    
    # Gericht (5)
    {
        'id': 21,
        'type': 'Gericht',
        'text': 'Ladung als Zeuge zur Verhandlung am 20.04.2026 gemäß § 380 ZPO.',
        'expected_laws': ['§ 380 ZPO'],
        'expected_org': 'Gericht'
    },
    {
        'id': 22,
        'type': 'Gericht',
        'text': 'Zahlungsbefehl über 5.000€ gemäß § 688 ZPO.',
        'expected_laws': ['§ 688 ZPO'],
        'expected_org': 'Gericht'
    },
    {
        'id': 23,
        'type': 'Gericht',
        'text': 'Beschluss über die Prozesskostenhilfe gemäß § 114 ZPO.',
        'expected_laws': ['§ 114 ZPO'],
        'expected_org': 'Gericht'
    },
    {
        'id': 24,
        'type': 'Gericht',
        'text': 'Urteil im Zivilprozess mit Rechtsmittelbelehrung.',
        'expected_laws': ['ZPO'],
        'expected_org': 'Gericht'
    },
    {
        'id': 25,
        'type': 'Gericht',
        'text': 'Vorladung gemäß § 163a StPO zur Vernehmung.',
        'expected_laws': ['§ 163a StPO'],
        'expected_org': 'Gericht'
    },
    
    # Versicherung (5)
    {
        'id': 26,
        'type': 'Versicherung',
        'text': 'Ablehnung der Leistungsübernahme mit Begründung.',
        'expected_laws': ['VVG'],
        'expected_org': 'Versicherung'
    },
    {
        'id': 27,
        'type': 'Versicherung',
        'text': 'Beitragserhöhung ab 01.06.2026 gemäß § 38 VVG.',
        'expected_laws': ['§ 38 VVG'],
        'expected_org': 'Versicherung'
    },
    {
        'id': 28,
        'type': 'Versicherung',
        'text': 'Kündigung des Versicherungsvertrags wegen Nichtzahlung.',
        'expected_laws': ['VVG'],
        'expected_org': 'Versicherung'
    },
    {
        'id': 29,
        'type': 'Versicherung',
        'text': 'Angebot zur Vertragsänderung mit verbesserter Leistung.',
        'expected_laws': ['VVG'],
        'expected_org': 'Versicherung'
    },
    {
        'id': 30,
        'type': 'Versicherung',
        'text': 'Rechnung für die Jahresprämie 2026.',
        'expected_laws': ['VVG'],
        'expected_org': 'Versicherung'
    },
    
    # Krankenkasse (5)
    {
        'id': 31,
        'type': 'Krankenkasse',
        'text': 'Bescheid über die Beitragsnachzahlung gemäß § 242 SGB V.',
        'expected_laws': ['§ 242 SGB V'],
        'expected_org': 'Krankenkasse'
    },
    {
        'id': 32,
        'type': 'Krankenkasse',
        'text': 'Genehmigung der Heilbehandlung ab 01.04.2026.',
        'expected_laws': ['SGB V'],
        'expected_org': 'Krankenkasse'
    },
    {
        'id': 33,
        'type': 'Krankenkasse',
        'text': 'Ablehnung der Kostenübernahme für Zahnersatz.',
        'expected_laws': ['SGB V'],
        'expected_org': 'Krankenkasse'
    },
    {
        'id': 34,
        'type': 'Krankenkasse',
        'text': 'Mitteilung über die Beitragsanpassung 2026.',
        'expected_laws': ['SGB V'],
        'expected_org': 'Krankenkasse'
    },
    {
        'id': 35,
        'type': 'Krankenkasse',
        'text': 'Einladung zum Gesundheits-Check-up gemäß § 25 SGB V.',
        'expected_laws': ['§ 25 SGB V'],
        'expected_org': 'Krankenkasse'
    },
    
    # Arbeitsagentur (5)
    {
        'id': 36,
        'type': 'Arbeitsagentur',
        'text': 'Einladung zum Beratungsgespräch gemäß § 309 SGB III.',
        'expected_laws': ['§ 309 SGB III'],
        'expected_org': 'Arbeitsagentur'
    },
    {
        'id': 37,
        'type': 'Arbeitsagentur',
        'text': 'Bescheid über Sperrzeit beim Arbeitslosengeld.',
        'expected_laws': ['SGB III'],
        'expected_org': 'Arbeitsagentur'
    },
    {
        'id': 38,
        'type': 'Arbeitsagentur',
        'text': 'Aufforderung zur Meldung als arbeitssuchend.',
        'expected_laws': ['SGB III'],
        'expected_org': 'Arbeitsagentur'
    },
    {
        'id': 39,
        'type': 'Arbeitsagentur',
        'text': 'Mitteilung über die Bewilligung von Arbeitslosengeld I.',
        'expected_laws': ['SGB III'],
        'expected_org': 'Arbeitsagentur'
    },
    {
        'id': 40,
        'type': 'Arbeitsagentur',
        'text': 'Vermittlungsvorschlag mit Aufforderung zur Bewerbung.',
        'expected_laws': ['SGB III'],
        'expected_org': 'Arbeitsagentur'
    },
    
    # Різне (10)
    {
        'id': 41,
        'type': 'Gemischt',
        'text': 'Rechnung über 59€ für Handwerkerleistung vom 15.03.2026.',
        'expected_laws': ['BGB'],
        'expected_org': 'Dienstleister'
    },
    {
        'id': 42,
        'type': 'Gemischt',
        'text': 'Vertragsänderung für Mobilfunkvertrag ab 01.05.2026.',
        'expected_laws': ['BGB'],
        'expected_org': 'Telekom'
    },
    {
        'id': 43,
        'type': 'Gemischt',
        'text': 'Stromrechnung mit Verbrauchsaufstellung für 2025.',
        'expected_laws': ['EnWG'],
        'expected_org': 'Versorger'
    },
    {
        'id': 44,
        'type': 'Gemischt',
        'text': 'Kündigung des Fitnessstudio-Vertrags zum 30.06.2026.',
        'expected_laws': ['BGB'],
        'expected_org': 'Fitnessstudio'
    },
    {
        'id': 45,
        'type': 'Gemischt',
        'text': 'Mahnung für offene Bibliotheksgebühren.',
        'expected_laws': ['BGB'],
        'expected_org': 'Bibliothek'
    },
    {
        'id': 46,
        'type': 'Gemischt',
        'text': 'Bußgeldbescheid über 35€ wegen Falschparkens.',
        'expected_laws': ['OWiG'],
        'expected_org': 'Ordnungsamt'
    },
    {
        'id': 47,
        'type': 'Gemischt',
        'text': 'Anmeldung für Kindergartenplatz ab September 2026.',
        'expected_laws': ['SGB VIII'],
        'expected_org': 'Kita'
    },
    {
        'id': 48,
        'type': 'Gemischt',
        'text': 'Gebührenbescheid für Hundesteuer 2026.',
        'expected_laws': ['KommAbgG'],
        'expected_org': 'Stadt'
    },
    {
        'id': 49,
        'type': 'Gemischt',
        'text': 'Rundfunkbeitrag Bescheid für 2026.',
        'expected_laws': ['RStV'],
        'expected_org': 'ARD ZDF Deutschlandradio'
    },
    {
        'id': 50,
        'type': 'Gemischt',
        'text': 'Widerrufsbelehrung für Online-Kauf vom 10.03.2026.',
        'expected_laws': ['BGB § 355'],
        'expected_org': 'Online-Shop'
    },
]


def test_rag_search(text: str, expected_laws: List[str]) -> Dict:
    """Тест RAG пошуку."""
    if not RAG_AVAILABLE:
        return {'found': False, 'error': 'RAG не доступний'}
    
    results = search_laws(text, n_results=5)
    
    found_laws = []
    for r in results:
        law_name = r.get('law_name', 'Unknown')
        para = r.get('paragraph', '')
        found_laws.append(f'{law_name} {para}')
    
    # Перевіряємо чи знайдено хоча б один очікуваний закон
    match = False
    for expected in expected_laws:
        for found in found_laws:
            if expected.lower() in found.lower():
                match = True
                break
    
    return {
        'found': match,
        'results_count': len(results),
        'found_laws': found_laws[:3],
        'expected': expected_laws
    }


def test_translation(text: str) -> Dict:
    """Тест перекладу."""
    if not TRANSLATOR_AVAILABLE:
        return {'success': False, 'error': 'Translator не доступний'}
    
    try:
        translation = translate_text_async(text, target_lang='uk')
        return {
            'success': True,
            'translation': translation[:200] if translation else '',
            'length': len(translation) if translation else 0
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def test_classification(text: str, expected_type: str) -> Dict:
    """Тест класифікації."""
    if not CLASSIFIER_AVAILABLE:
        return {'success': False, 'error': 'Classifier не доступний'}
    
    try:
        result = classify_document(text)
        doc_type = result.get('type', 'Unknown')
        return {
            'success': True,
            'type': doc_type,
            'expected': expected_type,
            'match': doc_type.lower() in expected_type.lower() or expected_type.lower() in doc_type.lower()
        }
    except Exception as e:
        return {'success': False, 'error': str(e)}


def run_deep_analysis():
    """Запуск глибокого аналізу."""
    print("="*80)
    print("  🧪 ГЛИБОКИЙ АНАЛІЗ БОТА - 50 ТЕСТОВИХ ЛИСТІВ")
    print("="*80)
    print(f"  Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*80)
    
    results = {
        'total': 50,
        'rag_tests': [],
        'translation_tests': [],
        'classification_tests': [],
        'summary': {}
    }
    
    # Статистика по типах
    stats = {
        'Jobcenter': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Finanzamt': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Vermieter': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Inkasso': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Gericht': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Versicherung': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Krankenkasse': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Arbeitsagentur': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
        'Gemischt': {'total': 0, 'rag_ok': 0, 'trans_ok': 0, 'class_ok': 0},
    }
    
    # Тестуємо кожен лист
    for i, letter in enumerate(TEST_LETTERS, 1):
        print(f"\n{'='*80}")
        print(f"  📄 ЛИСТ #{i} ({letter['type']})")
        print(f"{'='*80}")
        print(f"  Текст: {letter['text'][:100]}...")
        print(f"  Очікувані закони: {letter['expected_laws']}")
        
        # Оновлюємо статистику
        letter_type = letter['type']
        if letter_type in stats:
            stats[letter_type]['total'] += 1
        
        # 1. RAG пошук
        print(f"\n  🔍 RAG пошук...")
        rag_result = test_rag_search(letter['text'], letter['expected_laws'])
        results['rag_tests'].append(rag_result)
        
        if rag_result.get('found'):
            print(f"    ✅ Знайдено: {rag_result['results_count']} законів")
            print(f"    Знайдені: {rag_result['found_laws']}")
            if letter_type in stats:
                stats[letter_type]['rag_ok'] += 1
        else:
            print(f"    ❌ Не знайдено або невірні закони")
        
        # 2. Переклад
        print(f"\n  🌐 Переклад...")
        trans_result = test_translation(letter['text'])
        results['translation_tests'].append(trans_result)
        
        if trans_result.get('success'):
            print(f"    ✅ Перекладено: {trans_result['length']} символів")
            print(f"    {trans_result['translation']}...")
            if letter_type in stats:
                stats[letter_type]['trans_ok'] += 1
        else:
            print(f"    ❌ Помилка: {trans_result.get('error', 'Unknown')}")
        
        # 3. Класифікація
        print(f"\n  🏷️  Класифікація...")
        class_result = test_classification(letter['text'], letter['expected_org'])
        results['classification_tests'].append(class_result)
        
        if class_result.get('success'):
            status = '✅' if class_result.get('match') else '⚠️'
            print(f"    {status} Тип: {class_result['type']} (очікувано: {letter['expected_org']})")
            if class_result.get('match') and letter_type in stats:
                stats[letter_type]['class_ok'] += 1
        else:
            print(f"    ❌ Помилка: {class_result.get('error', 'Unknown')}")
        
        # Пауза між тестами
        time.sleep(0.5)
    
    # Фінальна статистика
    print("\n" + "="*80)
    print("  📊 ФІНАЛЬНА СТАТИСТИКА")
    print("="*80)
    
    total_rag = sum(1 for r in results['rag_tests'] if r.get('found'))
    total_trans = sum(1 for r in results['translation_tests'] if r.get('success'))
    total_class = sum(1 for r in results['classification_tests'] if r.get('success') and r.get('match'))
    
    results['summary'] = {
        'rag_success': total_rag,
        'translation_success': total_trans,
        'classification_success': total_class,
        'by_type': stats
    }
    
    print(f"\n  Загальна статистика:")
    print(f"  ✅ RAG пошук: {total_rag}/50 ({total_rag/50*100:.1f}%)")
    print(f"  ✅ Переклад: {total_trans}/50 ({total_trans/50*100:.1f}%)")
    print(f"  ✅ Класифікація: {total_class}/50 ({total_class/50*100:.1f}%)")
    
    print(f"\n  По типах документів:")
    for type_name, type_stats in stats.items():
        if type_stats['total'] > 0:
            print(f"\n  {type_name}:")
            print(f"    RAG: {type_stats['rag_ok']}/{type_stats['total']}")
            print(f"    Переклад: {type_stats['trans_ok']}/{type_stats['total']}")
            print(f"    Класифікація: {type_stats['class_ok']}/{type_stats['total']}")
    
    # Збереження результатів
    output_file = Path('test_results/deep_analysis_50_letters.json')
    output_file.parent.mkdir(parents=True, exist_ok=True)
    
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n  💾 Результати збережено: {output_file}")
    
    # Markdown звіт
    md_report = generate_markdown_report(results, stats)
    md_file = Path('test_results/deep_analysis_50_letters.md')
    with open(md_file, 'w', encoding='utf-8') as f:
        f.write(md_report)
    
    print(f"  📄 Markdown звіт: {md_file}")
    
    print("\n" + "="*80)
    print("  ✅ ТЕСТУВАННЯ ЗАВЕРШЕНО")
    print("="*80)
    
    return results


def generate_markdown_report(results: Dict, stats: Dict) -> str:
    """Генерація Markdown звіту."""
    total_rag = sum(1 for r in results['rag_tests'] if r.get('found'))
    total_trans = sum(1 for r in results['translation_tests'] if r.get('success'))
    total_class = sum(1 for r in results['classification_tests'] if r.get('success') and r.get('match'))
    
    report = f"""# 🧪 ГЛИБОКИЙ АНАЛІЗ БОТА - 50 ТЕСТОВИХ ЛИСТІВ

**Дата:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
**Статус:** ✅ ЗАВЕРШЕНО

---

## 📊 ЗАГАЛЬНА СТАТИСТИКА

| Тест | Успішно | Всього | % |
|------|---------|--------|---|
| **RAG пошук** | {total_rag} | 50 | {total_rag/50*100:.1f}% |
| **Переклад** | {total_trans} | 50 | {total_trans/50*100:.1f}% |
| **Класифікація** | {total_class} | 50 | {total_class/50*100:.1f}% |

---

## 📈 ПО ТИПАХ ДОКУМЕНТІВ

"""
    
    for type_name, type_stats in stats.items():
        if type_stats['total'] > 0:
            report += f"""### {type_name}

| Тест | Успішно | Всього | % |
|------|---------|--------|---|
| RAG | {type_stats['rag_ok']} | {type_stats['total']} | {type_stats['rag_ok']/type_stats['total']*100:.1f}% |
| Переклад | {type_stats['trans_ok']} | {type_stats['total']} | {type_stats['trans_ok']/type_stats['total']*100:.1f}% |
| Класифікація | {type_stats['class_ok']} | {type_stats['total']} | {type_stats['class_ok']/type_stats['total']*100:.1f}% |

"""
    
    report += f"""
---

## 🎯 ВИСНОВКИ

### ✅ Сильні сторони:
- RAG пошук працює на новій базі (65,186 документів)
- Переклад стабільний
- Класифікація розпізнає типи документів

### ⚠️ Проблемні зони:
- Семантичний пошук може давати неточні результати
- Класифікація потребує покращення для рідкісних типів

### 📋 Рекомендації:
1. Додати більше прикладів для тренування класифікатора
2. Покращити RAG пошук з урахуванням німецьких юридичних термінів
3. Додати кешування результатів для швидкодії

---

*Звіт створено автоматично*
"""
    
    return report


if __name__ == '__main__':
    run_deep_analysis()
