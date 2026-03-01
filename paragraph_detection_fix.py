#!/usr/bin/env python3
"""
Paragraph Detection Fix for Long Documents
Виправлення для виявлення параграфів у великих документах
"""

import re
from typing import List, Dict


def extract_paragraphs_improved(text: str) -> List[str]:
    """
    Extract German law paragraphs with improved regex.
    Supports multiple formats:
    - § 286 BGB
    - BGB § 286
    - § 59 SGB II
    - § 288 Abs. 1 BGB
    - BGB § 492 Abs. 1
    """
    
    paragraphs = []
    
    # Pattern 1: § 286 BGB or § 288 Abs. 1 BGB
    pattern1 = r'§\s*(\d+[a-z]?)(?:\s*Abs\.\s*\d+)?\s*(BGB|SGB|ZPO|AO|VwVfG|StGB|HGB|GG|InsO|GmbHG|AktG)'
    for match in re.finditer(pattern1, text, re.IGNORECASE):
        para_num, code = match.groups()
        paragraphs.append(f"§ {para_num} {code}")
    
    # Pattern 2: BGB § 286 or BGB § 492 Abs. 1
    pattern2 = r'(BGB|SGB|ZPO|AO|VwVfG|StGB|HGB|GG|InsO|GmbHG|AktG)\s*§\s*(\d+[a-z]?)(?:\s*Abs\.\s*\d+)?'
    for match in re.finditer(pattern2, text, re.IGNORECASE):
        code, para_num = match.groups()
        paragraphs.append(f"{code} § {para_num}")
    
    # Pattern 3: § 59 SGB II or § 31 SGB II
    pattern3 = r'§\s*(\d+)\s*(SGB)\s*(I|II|III)'
    for match in re.finditer(pattern3, text, re.IGNORECASE):
        para_num, code, book = match.groups()
        paragraphs.append(f"§ {para_num} {code} {book}")
    
    # Pattern 4: Standalone paragraphs (e.g., just "§ 286")
    pattern4 = r'§\s*(\d+[a-z]?)(?!\s*(BGB|SGB|ZPO|AO|VwVfG|StGB|HGB))'
    for match in re.finditer(pattern4, text, re.IGNORECASE):
        para_num = match.group(1)
        # Try to find context
        start = max(0, match.start() - 50)
        end = min(len(text), match.end() + 50)
        context = text[start:end].lower()
        
        # Infer code from context
        if 'bürgerliches' in context or 'vertrag' in context:
            paragraphs.append(f"§ {para_num} BGB")
        elif 'sozial' in context or 'jobcenter' in context:
            paragraphs.append(f"§ {para_num} SGB")
        elif 'gericht' in context or 'prozess' in context:
            paragraphs.append(f"§ {para_num} ZPO")
        elif 'steuer' in context or 'finanzamt' in context:
            paragraphs.append(f"§ {para_num} AO")
    
    return list(set(paragraphs))


def test_paragraph_detection():
    """Test improved paragraph detection."""
    
    test_cases = [
        {
            'name': 'Jobcenter Letter',
            'text': '''
            Jobcenter Berlin
            § 59 SGB II, § 31 SGB II, § 32 SGB II
            BGB § 286
            § 288 Abs. 1 BGB
            § 309 SGB III
            § 60 SGB I
            ''',
            'expected': ['§ 59 SGB II', '§ 31 SGB II', '§ 32 SGB II', '§ 309 SGB III', '§ 60 SGB I', '§ 286 BGB', '§ 288 BGB']
        },
        {
            'name': 'Inkasso Letter',
            'text': '''
            CreditProtect Inkasso
            BGB § 286 - Verzug des Schuldners
            BGB § 288 - Verzugszinsen
            BGB § 280 - Schadensersatz
            BGB § 492 - Verbraucherdarlehensvertrag
            ZPO § 794 - Vollstreckungstitel
            ''',
            'expected': ['§ 286 BGB', '§ 288 BGB', '§ 280 BGB', '§ 492 BGB', '§ 794 ZPO']
        },
        {
            'name': 'Gericht Letter',
            'text': '''
            Amtsgericht Berlin
            ZPO § 330 - Versäumnisurteil
            ZPO § 331 - Voraussetzungen
            ZPO § 335 - Fristen
            BGB § 286 - Verzug
            BGB § 288 - Verzugszinsen
            ''',
            'expected': ['§ 330 ZPO', '§ 331 ZPO', '§ 335 ZPO', '§ 286 BGB', '§ 288 BGB']
        },
        {
            'name': 'Vermieter Letter',
            'text': '''
            Hausverwaltung Schmidt
            § 558 BGB - Mieterhöhung
            § 559 BGB - Modernisierung
            § 555b BGB - Modernisierungsmaßnahmen
            § 555d BGB - Ankündigung
            ''',
            'expected': ['§ 558 BGB', '§ 559 BGB', '§ 555b BGB', '§ 555d BGB']
        }
    ]
    
    print("\n" + "="*80)
    print(" ТЕСТУВАННЯ ВИЯВЛЕННЯ ПАРАГРАФІВ (Покращений Regex)")
    print("="*80 + "\n")
    
    total_tests = 0
    passed_tests = 0
    
    for test in test_cases:
        total_tests += 1
        result = extract_paragraphs_improved(test['text'])
        
        # Check if all expected paragraphs are found
        found_all = True
        missing = []
        
        for expected_para in test['expected']:
            # Normalize for comparison
            expected_normalized = expected_para.replace('  ', ' ').upper()
            found = False
            
            for found_para in result:
                found_normalized = found_para.replace('  ', ' ').upper()
                # Check if they match (allowing for different orderings)
                if expected_normalized == found_normalized:
                    found = True
                    break
            
            if not found:
                found_all = False
                missing.append(expected_para)
        
        if found_all:
            print(f"✅ {test['name']}: PASS")
            print(f"   Знайдено: {len(result)} параграфів")
            passed_tests += 1
        else:
            print(f"❌ {test['name']}: FAIL")
            print(f"   Не знайдено: {missing}")
            print(f"   Знайдено: {result}")
        
        print()
    
    print("="*80)
    print(f" РЕЗУЛЬТАТ: {passed_tests}/{total_tests} ({passed_tests/total_tests*100:.1f}%)")
    print("="*80)
    
    return passed_tests == total_tests


def analyze_long_document(text: str) -> Dict:
    """Complete analysis of long document."""
    
    from client_bot_functions import check_if_document
    
    # Extract paragraphs
    paragraphs = extract_paragraphs_improved(text)
    
    # Extract amounts
    amounts = re.findall(r'(\d{1,3}(?:\.\d{3})*,\d{2}\s*EUR)', text)
    
    # Extract dates
    dates = re.findall(r'(\d{1,2}\.\d{1,2}\.\d{2,4})', text)
    
    # Extract times
    times = re.findall(r'(\d{1,2}:\d{2})\s*Uhr', text)
    
    # Extract phone numbers
    phones = re.findall(r'(?:Telefon|Tel|Fax)[:\s]*(\+?\d[\d\s\-\(\)]{8,}\d)', text, re.IGNORECASE)
    
    # Extract emails
    emails = re.findall(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
    
    # Extract IBAN
    ibans = re.findall(r'(DE\d{2}\s?\d{8,})', text, re.IGNORECASE)
    
    # Classification
    classification = check_if_document(text)
    
    return {
        'length': len(text),
        'classification': classification,
        'paragraphs': paragraphs,
        'amounts': list(set(amounts)),
        'dates': list(set(dates)),
        'times': list(set(times)),
        'phones': phones,
        'emails': emails,
        'ibans': ibans
    }


if __name__ == '__main__':
    # Run tests
    success = test_paragraph_detection()
    
    if success:
        print("\n✅ Всі тести пройшли! Можна інтегрувати в client_bot_functions.py")
    else:
        print("\n⚠️ Деякі тести не пройшли. Потрібне доопрацювання.")
    
    # Test on real long document
    print("\n" + "="*80)
    print(" АНАЛІЗ РЕАЛЬНОГО ВЕЛИКОГО ДОКУМЕНТУ")
    print("="*80)
    
    long_doc = '''
Jobcenter Berlin Mitte
Bescheid über Leistungskürzung

§ 59 SGB II, § 31 SGB II, § 32 SGB II
BGB § 286, BGB § 288
§ 309 SGB III
§ 60 SGB I
§ 48 SGB X

Regelsatz: 563,00 EUR
Kürzung: 168,90 EUR
Neuer Betrag: 394,10 EUR

Termine:
10.01.2026 um 10:00 Uhr
24.01.2026 um 14:30 Uhr
07.02.2026 um 09:00 Uhr

Kontakt:
Telefon: 030 1234-5678
E-Mail: max.mustermann@jobcenter-ge.de
IBAN: DE89 2005 0550 1234 5678 90
'''
    
    analysis = analyze_long_document(long_doc)
    
    print(f"\nДовжина: {analysis['length']} символів")
    print(f"Класифікація: {analysis['classification']['is_document']}")
    print(f"Знайдено параграфів: {len(analysis['paragraphs'])}")
    print(f"  → {analysis['paragraphs']}")
    print(f"Знайдено сум: {len(analysis['amounts'])}")
    print(f"  → {analysis['amounts']}")
    print(f"Знайдено дат: {len(analysis['dates'])}")
    print(f"  → {analysis['dates']}")
    print(f"Знайдено часу: {len(analysis['times'])}")
    print(f"  → {analysis['times']}")
    print(f"Знайдено телефонів: {len(analysis['phones'])}")
    print(f"  → {analysis['phones']}")
    print(f"Знайдено email: {len(analysis['emails'])}")
    print(f"  → {analysis['emails']}")
    print(f"Знайдено IBAN: {len(analysis['ibans'])}")
    print(f"  → {analysis['ibans']}")
