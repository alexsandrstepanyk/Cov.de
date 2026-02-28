#!/usr/bin/env python3
"""
Test Script for Advanced OCR Module
Перевірка покращеного розпізнавання зображень
"""

import sys
from pathlib import Path

# Додаємо src до path
sys.path.insert(0, str(Path(__file__).parent / 'src'))

from advanced_ocr import AdvancedOCR, recognize_image

def print_separator(title: str):
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}\n")

def test_ocr_initialization():
    """Тест ініціалізації OCR рушіїв."""
    print_separator("🔧 Тест: Ініціалізація OCR рушіїв")
    
    ocr = AdvancedOCR()
    
    print("Доступні рушії:")
    for engine in ocr.engines:
        print(f"  ✅ {engine}")
    
    if not ocr.engines:
        print("  ❌ Жоден рушій не доступний")
        return False
    
    print(f"\nВсього рушіїв: {len(ocr.engines)}")
    return True

def test_image_quality_assessment():
    """Тест оцінки якості зображення."""
    print_separator("📊 Тест: Оцінка якості зображення")
    
    # Створюємо тестове зображення
    try:
        import numpy as np
        import cv2
        
        # Створення тестового зображення з текстом
        img = np.ones((400, 600), dtype=np.uint8) * 255
        cv2.putText(img, 'Test Text', (50, 200), cv2.FONT_HERSHEY_SIMPLEX, 
                   1.5, 0, 3)
        
        # Збереження
        test_path = '/tmp/test_ocr.jpg'
        cv2.imwrite(test_path, img)
        
        ocr = AdvancedOCR()
        processed, metadata = ocr.preprocess_image(test_path)
        
        if 'quality' in metadata:
            quality = metadata['quality']
            print(f"Якість: {quality.get('quality', 'unknown')}")
            print(f"Різкість: {quality.get('score', 0):.2f}")
            print(f"Контраст: {quality.get('contrast', 0):.2f}")
            print(f"Яскравість: {quality.get('brightness', 0):.2f}")
            
            if quality.get('issues'):
                print(f"\nПроблеми:")
                for issue in quality['issues']:
                    print(f"  ⚠️ {issue}")
            
            if quality.get('recommendations'):
                print(f"\nПоради:")
                for rec in quality['recommendations']:
                    print(f"  💡 {rec}")
            
            return True
        else:
            print("❌ Не вдалося оцінити якість")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_text_recognition():
    """Тест розпізнавання тексту."""
    print_separator("📝 Тест: Розпізнавання тексту")
    
    try:
        import numpy as np
        import cv2
        
        # Створення зображення з німецьким текстом
        img = np.ones((300, 800), dtype=np.uint8) * 255
        cv2.putText(img, 'Mahnung: Zahlung erforderlich', (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
        cv2.putText(img, 'Bitte uberweisen Sie 500 Euro', (50, 180), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
        cv2.putText(img, 'innerhalb von 7 Tagen', (50, 260), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, 0, 2)
        
        test_path = '/tmp/test_ocr_german.jpg'
        cv2.imwrite(test_path, img)
        
        # Розпізнавання
        result = recognize_image(test_path, lang='de')
        
        print(f"Рушій: {result['engine']}")
        print(f"Впевненість: {result['confidence']:.2f}")
        print(f"\nРозпізнаний текст ({len(result['text'])} символів):")
        print("-" * 60)
        print(result['text'])
        print("-" * 60)
        
        # Перевірка ключових слів
        text_lower = result['text'].lower()
        keywords_found = []
        
        for keyword in ['mahnung', 'zahlung', 'euro', 'tagen']:
            if keyword in text_lower:
                keywords_found.append(keyword)
        
        print(f"\n✅ Ключові слова знайдено: {', '.join(keywords_found)}")
        
        if len(keywords_found) >= 2:
            print("✅ Розпізнавання успішне!")
            return True
        else:
            print("⚠️ Розпізнавання часткове")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_image_preprocessing():
    """Тест попередньої обробки зображення."""
    print_separator("🎨 Тест: Попередня обробка зображення")
    
    try:
        import numpy as np
        import cv2
        
        # Створення зображення з шумом
        img = np.random.randint(0, 255, (300, 400), dtype=np.uint8)
        
        # Додавання тексту
        cv2.putText(img, 'Noisy Text', (50, 150), cv2.FONT_HERSHEY_SIMPLEX, 
                   1, 128, 2)
        
        test_path = '/tmp/test_noisy.jpg'
        cv2.imwrite(test_path, img)
        
        ocr = AdvancedOCR()
        processed, metadata = ocr.preprocess_image(test_path)
        
        print(f"Оригінал: {metadata.get('width', '?')}x{metadata.get('height', '?')}")
        print(f"Якість: {metadata.get('quality', {}).get('quality', 'unknown')}")
        
        if processed is not None:
            print("✅ Зображення оброблено")
            
            # Збереження обробленого зображення для перевірки
            output_path = '/tmp/test_processed.jpg'
            if isinstance(processed, np.ndarray):
                cv2.imwrite(output_path, processed)
                print(f"Збережено: {output_path}")
            
            return True
        else:
            print("❌ Не вдалося обробити зображення")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def test_multiple_engines():
    """Тест порівняння кількох OCR рушіїв."""
    print_separator("⚖️ Тест: Порівняння OCR рушіїв")
    
    try:
        import numpy as np
        import cv2
        
        # Створення тестового зображення
        img = np.ones((200, 600), dtype=np.uint8) * 255
        cv2.putText(img, 'Test: Rechnung Nr. 12345', (50, 100), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, 0, 2)
        
        test_path = '/tmp/test_compare.jpg'
        cv2.imwrite(test_path, img)
        
        ocr = AdvancedOCR()
        results = {}
        
        # Tesseract
        if 'tesseract' in ocr.engines:
            from PIL import Image
            text = ocr.recognize_with_tesseract(Image.open(test_path))
            results['tesseract'] = len(text)
            print(f"Tesseract: {len(text)} символів")
        
        # EasyOCR
        if 'easyocr' in ocr.engines:
            text = ocr.recognize_with_easyocr(test_path)
            results['easyocr'] = len(text)
            print(f"EasyOCR: {len(text)} символів")
        
        if results:
            best = max(results, key=results.get)
            print(f"\n✅ Найкращий: {best} ({results[best]} символів)")
            return True
        else:
            print("❌ Жоден рушій не доступний")
            return False
            
    except Exception as e:
        print(f"❌ Помилка: {e}")
        return False

def main():
    """Головна функція тестування."""
    print("\n" + "="*60)
    print("  ТЕСТУВАННЯ ADVANCED OCR MODULE")
    print("="*60)
    
    results = {
        'Ініціалізація': test_ocr_initialization(),
        'Оцінка якості': test_image_quality_assessment(),
        'Розпізнавання': test_text_recognition(),
        'Обробка': test_image_preprocessing(),
        'Порівняння': test_multiple_engines()
    }
    
    print_separator("📊 ПІДСУМКИ")
    
    passed = sum(1 for v in results.values() if v)
    total = len(results)
    
    for test, result in results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test}")
    
    print(f"\nРезультат: {passed}/{total} тестів пройдено")
    
    if passed == total:
        print("\n🎉 ВСІ ТЕСТИ УСПІШНІ!")
        return 0
    else:
        print("\n⚠️ Деякі тести не пройшли")
        return 1

if __name__ == '__main__':
    exit(main())
