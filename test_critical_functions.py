#!/usr/bin/env python3
"""
🧪 КОМПЛЕКСНИЙ ТЕСТ КРИТИЧНИХ ФУНКЦІЙ GOV.DE BOT v4.4

Тестує:
1. ✅ OCR розпізнавання (EasyOCR + Tesseract)
2. ✅ Переклад (Google Translate + LibreTranslate)
3. ✅ Юридичний словник
4. ✅ Класифікацію документів
5. ✅ Визначення параграфів
6. ✅ Fraud Detection

Використовує 20 тестових листів з 20_TEST_LETTERS.md
"""

import sys
import time
import re
from pathlib import Path
from datetime import datetime

# Додаємо src та src/bots до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'bots'))

# Кольори для виводу
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

def print_result(test_name, passed, details=""):
    status = f"{Colors.GREEN}✅ PASS{Colors.END}" if passed else f"{Colors.RED}❌ FAIL{Colors.END}"
    print(f"{status} | {test_name}")
    if details:
        print(f"       {details}")

# ============================================================================
# ТЕСТ 1: OCR РОЗПІЗНАВАННЯ
# ============================================================================
def test_ocr():
    print_header("ТЕСТ 1: OCR РОЗПІЗНАВАННЯ")
    
    results = []
    
    try:
        from advanced_ocr import recognize_image
        print(f"{Colors.GREEN}✅ Advanced OCR імпортовано{Colors.END}\n")
        
        # Тест на простому тексті
        test_text = """Jobcenter Berlin
Einladung zum Gespräch
Termin: 12.03.2026 um 10:00 Uhr"""
        
        # Створюємо тестове зображення
        from PIL import Image, ImageDraw, ImageFont
        img = Image.new('RGB', (400, 200), color='white')
        draw = ImageDraw.Draw(img)
        
        # Малюємо текст
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((10, 10), test_text, fill='black', font=font)
        
        # Зберігаємо тимчасове зображення
        test_img_path = Path(__file__).parent / 'test_ocr_temp.png'
        img.save(test_img_path)
        
        # Розпізнаємо
        start_time = time.time()
        result = recognize_image(str(test_img_path))
        elapsed = time.time() - start_time
        
        # Видаляємо тимчасовий файл
        test_img_path.unlink(missing_ok=True)
        
        if result:
            recognized_text = result.get('text', '')
            confidence = result.get('confidence', 0)
            
            passed = 'Jobcenter' in recognized_text or 'Einladung' in recognized_text
            details = f"Час: {elapsed:.2f}s, Впевненість: {confidence:.1f}%, Розпізнано: {len(recognized_text)} символів"
            print_result("OCR розпізнавання німецького тексту", passed, details)
            results.append(passed)
            
            if not passed:
                print(f"       {Colors.YELLOW}Розпізнаний текст: {recognized_text[:100]}...{Colors.END}")
        else:
            print_result("OCR розпізнавання", False, "Не вдалося розпізнати")
            results.append(False)
            
    except Exception as e:
        print_result("OCR тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ТЕСТ 2: ПЕРЕКЛАД
# ============================================================================
def test_translation():
    print_header("ТЕСТ 2: ПЕРЕКЛАД (GOOGLE + LIBRETRANSLATE)")
    
    results = []
    
    try:
        from advanced_translator import translate_text_async
        import asyncio
        
        print(f"{Colors.GREEN}✅ Advanced Translator імпортовано{Colors.END}\n")
        
        # Тестові фрази
        test_cases = [
            ("Einladung zum persönlichen Gespräch", "uk", ["Запрошення", "особистий"]),
            ("Leistungsbescheid", "uk", ["Рішення", "виплати"]),
            ("Kündigung", "uk", ["Розірвання", "звільнення"]),
            ("Mahnung", "uk", ["Нагадування", "борг"]),
        ]
        
        async def run_translation_tests():
            for text, target_lang, expected_keywords in test_cases:
                try:
                    start_time = time.time()
                    result_dict = await translate_text_async(text, 'de', target_lang)
                    elapsed = time.time() - start_time
                    
                    # Отримуємо текст з Dict
                    result_text = result_dict.get('text', '') if isinstance(result_dict, dict) else str(result_dict)
                    
                    # Перевіряємо наявність хоча б одного очікуваного слова
                    passed = any(kw in result_text for kw in expected_keywords) if result_text else False
                    details = f"{text} → {result_text[:60]} ({elapsed:.2f}s, {result_dict.get('service', 'unknown')})"
                    print_result(f"Переклад: {text}", passed, details)
                    results.append(passed)
                    
                except Exception as e:
                    print_result(f"Переклад: {text}", False, f"Помилка: {str(e)}")
                    results.append(False)
        
        asyncio.run(run_translation_tests())
        
    except Exception as e:
        print_result("Translation тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ТЕСТ 3: ЮРИДИЧНИЙ СЛОВНИК
# ============================================================================
def test_legal_dictionary():
    print_header("ТЕСТ 3: ЮРИДИЧНИЙ СЛОВНИК")
    
    results = []
    
    try:
        from bots.client_bot import post_process_translation, LEGAL_TRANSLATION_FIXES
        
        print(f"{Colors.GREEN}✅ Юридичний словник завантажено ({len(LEGAL_TRANSLATION_FIXES)} термінів){Colors.END}\n")
        
        # Тестові випадки
        test_cases = [
            ("вартістю 59 доларів сша", "§ 59 (параграф 59)"),
            ("вартістю 309 доларів сша", "§ 309 (параграф 309)"),
            ("SGB II", "SGB II (Соціальний кодекс II)"),
            ("BGB", "BGB (Цивільний кодекс)"),
        ]
        
        for input_text, expected in test_cases:
            result = post_process_translation(input_text)
            passed = expected in result
            details = f"{input_text} → {result}"
            print_result(f"Виправлення: {input_text}", passed, details)
            results.append(passed)
        
    except Exception as e:
        print_result("Legal Dictionary тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ТЕСТ 4: КЛАСИФІКАЦІЯ ДОКУМЕНТІВ
# ============================================================================
def test_document_classification():
    print_header("ТЕСТ 4: КЛАСИФІКАЦІЯ ДОКУМЕНТІВ")
    
    results = []
    
    try:
        from client_bot_functions import check_if_document
        
        print(f"{Colors.GREEN}✅ Client Bot Functions імпортовано{Colors.END}\n")
        
        # Тестові документи з 20_TEST_LETTERS.md
        test_documents = [
            ("""Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Einladung zum persönlichen Gespräch
Termin: Montag, 12.03.2026, um 10:00 Uhr
Gemäß § 59 SGB II sind Sie verpflichtet""", "jobcenter", "Jobcenter Einladung"),
            
            ("""CreditProtect Inkasso GmbH
Forderungsnummer: 2026/12345

Erste Mahnung
Offener Betrag: 350,00 EUR
Fälligkeit: 15.02.2026""", "inkasso", "Inkasso Mahnung"),
            
            ("""Vermieter Hans Müller
Mieterhöhung bis zur ortsüblichen Vergleichsmiete
Gemäß § 558 BGB""", "vermieter", "Mieterhöhung"),
            
            ("""Finanzamt Berlin
Einkommensteuerbescheid 2025
Festgesetzte Steuer: 3.200,00 EUR""", "finanzamt", "Steuerbescheid"),
        ]
        
        for doc_text, expected_type, description in test_documents:
            result = check_if_document(doc_text)
            
            is_correct_type = result.get('document_type') == expected_type
            is_legal = result.get('is_legal_document', False)
            
            passed = is_correct_type and is_legal
            details = f"Тип: {result.get('document_type', 'N/A')}, Legal: {is_legal}, Score: {result.get('official_score', 0)}"
            print_result(f"Класифікація: {description}", passed, details)
            results.append(passed)
        
    except Exception as e:
        print_result("Classification тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ТЕСТ 5: ВИЗНАЧЕННЯ ПАРАГРАФІВ
# ============================================================================
def test_paragraph_detection():
    print_header("ТЕСТ 5: ВИЗНАЧЕННЯ ПАРАГРАФІВ")
    
    results = []
    
    try:
        from legal_database import analyze_letter
        
        print(f"{Colors.GREEN}✅ Legal Database імпортовано{Colors.END}\n")
        
        # Тестові тексти з параграфами
        test_cases = [
            ("Gemäß § 59 SGB II sind Sie verpflichtet", ["§ 59 SGB II"]),
            ("nach § 558 Abs. 3 BGB kann die Miete", ["§ 558 BGB"]),
            ("gemäß § 31 SGB II kürzen wir", ["§ 31 SGB II"]),
            ("Gegen diesen Bescheid können Sie innerhalb eines Monats Widerspruch einlegen (§ 84 SGG)", ["§ 84 SGG"]),
        ]
        
        for text, expected_paras in test_cases:
            result = analyze_letter(text)
            found_paras = result.get('paragraphs', [])
            
            # Перевіряємо чи знайдено хоча б один очікуваний параграф
            passed = any(expected in str(found_paras) for expected in expected_paras)
            details = f"Знайдено: {found_paras}"
            print_result(f"Параграфи: {text[:50]}...", passed, details)
            results.append(passed)
        
    except Exception as e:
        print_result("Paragraph Detection тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ТЕСТ 6: FRAUD DETECTION
# ============================================================================
def test_fraud_detection():
    print_header("ТЕСТ 6: FRAUD DETECTION")
    
    results = []
    
    try:
        from fraud_detection import analyze_letter_for_fraud
        
        print(f"{Colors.GREEN}✅ Fraud Detection імпортовано{Colors.END}\n")
        
        # Тестові випадки
        test_cases = [
            ("""Sofort überweisen auf Konto: DE89 3704 0044 0532 0130 00
Ihr Konto wird gesperrt wenn Sie nicht zahlen!
Gewonnen! Lotto Gewinn 50.000 EUR""", True, "Очевидний fraud"),
            
            ("""Jobcenter Berlin
Einladung zum Gespräch
Termin: 12.03.2026 um 10:00 Uhr
Gemäß § 59 SGB II""", False, "Легітимний Jobcenter"),
            
            ("""Western Union Money Transfer
PIN erforderlich um Paket zu erhalten
DHL Paket konnte nicht zugestellt werden""", True, "Fake DHL"),
        ]
        
        for text, should_be_fraud, description in test_cases:
            # Створюємо mock extracted_data
            extracted_data = {
                'document_type': 'unknown',
                'organization': '',
                'paragraphs': [],
                'amounts': [],
                'dates': [],
                'phones': [],
                'emails': [],
                'urls': [],
                'iban': [],
            }
            
            result = analyze_letter_for_fraud(text, extracted_data)
            fraud_score = result.get('fraud_score', 0)
            is_fraud = result.get('is_likely_fraud', False)
            
            passed = is_fraud == should_be_fraud
            details = f"Fraud Score: {fraud_score}, Виявлено: {is_fraud}"
            print_result(f"Fraud: {description}", passed, details)
            results.append(passed)
        
    except Exception as e:
        print_result("Fraud Detection тест", False, f"Помилка: {str(e)}")
        results.append(False)
    
    return sum(results) / len(results) if results else 0

# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================
def main():
    print_header("🧪 КОМПЛЕКСНИЙ ТЕСТ КРИТИЧНИХ ФУНКЦІЙ v4.4")
    print(f"Час початку: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Шлях: {Path(__file__).parent}")
    
    # Запускаємо тести
    test_results = {
        "OCR": test_ocr(),
        "Translation": test_translation(),
        "Legal Dictionary": test_legal_dictionary(),
        "Document Classification": test_document_classification(),
        "Paragraph Detection": test_paragraph_detection(),
        "Fraud Detection": test_fraud_detection(),
    }
    
    # Підсумки
    print_header("📊 ПІДСУМКИ ТЕСТУВАННЯ")
    
    total_score = 0
    for test_name, score in test_results.items():
        percentage = score * 100
        total_score += score
        
        if percentage >= 90:
            status = f"{Colors.GREEN}✅ Відмінно{Colors.END}"
        elif percentage >= 70:
            status = f"{Colors.YELLOW}⚠️ Добре{Colors.END}"
        else:
            status = f"{Colors.RED}❌ Погано{Colors.END}"
        
        print(f"{test_name:.<40} {percentage:5.1f}% {status}")
    
    average = (total_score / len(test_results)) * 100
    
    print(f"\n{'СЕРЕДНЯ ОЦІНКА:':.<40} {average:5.1f}%", end="")
    
    if average >= 90:
        print(f" {Colors.GREEN}🏆 A (Відмінно){Colors.END}")
    elif average >= 80:
        print(f" {Colors.BLUE}✅ B (Добре){Colors.END}")
    elif average >= 70:
        print(f" {Colors.YELLOW}⚠️ C (Задовільно){Colors.END}")
    else:
        print(f" {Colors.RED}❌ D (Погано){Colors.END}")
    
    print(f"\nЧас завершення: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return average

if __name__ == "__main__":
    score = main()
    sys.exit(0 if score >= 70 else 1)
