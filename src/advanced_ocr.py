#!/usr/bin/env python3
"""
Advanced OCR Module for Gov.de
Покращене розпізнавання тексту з фото з попередньою обробкою та контролем якості.
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import numpy as np

logger = logging.getLogger(__name__)


class AdvancedOCR:
    """
    Клас для розширеного OCR з підтримкою кількох рушіїв
    та попередньої обробки зображень.
    """
    
    def __init__(self):
        self.engines = {}
        self._init_engines()
    
    def _init_engines(self):
        """Ініціалізація OCR рушіїв."""
        # Tesseract
        try:
            import pytesseract
            self.engines['tesseract'] = pytesseract
            logger.info("✅ Tesseract OCR ініціалізовано")
        except Exception as e:
            logger.warning(f"❌ Tesseract недоступний: {e}")
        
        # EasyOCR
        try:
            import easyocr
            self.easyocr_reader = easyocr.Reader(['de', 'en'], gpu=False, verbose=False)
            self.engines['easyocr'] = self.easyocr_reader
            logger.info("✅ EasyOCR ініціалізовано")
        except Exception as e:
            logger.warning(f"❌ EasyOCR недоступний: {e}")
        
        # OpenCV для обробки зображень
        try:
            import cv2
            self.cv2 = cv2
            logger.info("✅ OpenCV ініціалізовано")
        except Exception as e:
            logger.warning(f"❌ OpenCV недоступний: {e}")
    
    def preprocess_image(self, image_path: str) -> Tuple[any, Dict]:
        """
        Попередня обробка зображення для покращення OCR.
        
        Args:
            image_path: Шлях до зображення
            
        Returns:
            (оброблене зображення, метадані)
        """
        if 'cv2' not in self.__dict__ or self.cv2 is None:
            try:
                from PIL import Image
                img = Image.open(image_path)
                return img, {'width': img.size[0], 'height': img.size[1]}
            except Exception as e:
                logger.error(f"Помилка відкриття зображення: {e}")
                return None, {}
        
        try:
            # Зчитування зображення
            img = self.cv2.imread(image_path)
            if img is None:
                raise ValueError("Не вдалося зчитати зображення")
            
            original = img.copy()
            metadata = {
                'width': img.shape[1],
                'height': img.shape[0],
                'original': original
            }
            
            # Конвертація в сірий
            gray = self.cv2.cvtColor(img, self.cv2.COLOR_BGR2GRAY)
            
            # Видалення шуму
            denoised = self.cv2.fastNlMeansDenoising(gray, None, 10, 7, 21)
            
            # Підвищення контрасту (CLAHE)
            clahe = self.cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
            enhanced = clahe.apply(denoised)
            
            # Бінаризація (адаптивна)
            binary = self.cv2.adaptiveThreshold(
                enhanced, 255,
                self.cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                self.cv2.THRESH_BINARY, 11, 2
            )
            
            # Визначення кута нахилу
            angle = self._detect_skew(binary)
            if abs(angle) > 0.5:
                logger.info(f"Виявлено нахил: {angle:.2f}°, вирівнюємо...")
                enhanced = self._deskew(enhanced, angle)
            
            metadata['processed'] = enhanced
            metadata['gray'] = gray
            metadata['binary'] = binary
            metadata['quality'] = self._assess_image_quality(enhanced)
            
            logger.info(f"Якість зображення: {metadata['quality']}")
            
            return enhanced, metadata
            
        except Exception as e:
            logger.error(f"Помилка попередньої обробки: {e}")
            # Fallback на PIL
            try:
                from PIL import Image
                img = Image.open(image_path)
                return img, {'width': img.size[0], 'height': img.size[1]}
            except:
                return None, {}
    
    def _detect_skew(self, image: np.ndarray) -> float:
        """
        Визначення кута нахилу документа.
        
        Args:
            image: Зображення у відтінках сірого
            
        Returns:
            Кут нахилу в градусах
        """
        try:
            # Визначення країв
            edges = self.cv2.Canny(image, 50, 150, apertureSize=3)
            
            # Знаходження ліній
            lines = self.cv2.HoughLines(edges, 1, np.pi / 180, 200)
            
            if lines is None:
                return 0.0
            
            # Обчислення середнього кута
            angles = []
            for rho, theta in lines[:100]:  # Обмежуємо кількість
                angle = (theta * 180 / np.pi) - 90
                if -45 < angle < 45:  # Ігноруємо вертикальні лінії
                    angles.append(angle)
            
            if not angles:
                return 0.0
            
            return np.median(angles)
            
        except Exception as e:
            logger.error(f"Помилка визначення нахилу: {e}")
            return 0.0
    
    def _deskew(self, image: np.ndarray, angle: float) -> np.ndarray:
        """
        Вирівнювання зображення.
        
        Args:
            image: Зображення
            angle: Кут нахилу
            
        Returns:
            Вирівняне зображення
        """
        try:
            (h, w) = image.shape[:2]
            center = (w // 2, h // 2)
            
            # Матриця обертання
            M = self.cv2.getRotationMatrix2D(center, angle, 1.0)
            
            # Обертання
            rotated = self.cv2.warpAffine(
                image, M, (w, h),
                flags=self.cv2.INTER_CUBIC,
                borderMode=self.cv2.BORDER_REPLICATE
            )
            
            return rotated
            
        except Exception as e:
            logger.error(f"Помилка вирівнювання: {e}")
            return image
    
    def _assess_image_quality(self, image: np.ndarray) -> Dict:
        """
        Оцінка якості зображення для OCR.
        
        Args:
            image: Зображення у відтінках сірого
            
        Returns:
            Dict з оцінками якості
        """
        try:
            # Розмитість (variance of Laplacian)
            laplacian = self.cv2.Laplacian(image, self.cv2.CV_64F)
            blur_score = laplacian.var()
            
            # Контраст
            contrast = image.std()
            
            # Яскравість
            brightness = image.mean()
            
            # Співвідношення сторін (чи схоже на документ)
            h, w = image.shape
            aspect_ratio = w / float(h)
            
            quality = 'good'
            issues = []
            
            if blur_score < 100:
                quality = 'poor'
                issues.append('зображення занадто розмите')
            elif blur_score < 500:
                quality = 'fair'
                issues.append('можливе невелике розмиття')
            
            if contrast < 30:
                issues.append('низький контраст')
            
            if brightness < 50 or brightness > 200:
                issues.append('проблеми з освітленням')
            
            return {
                'score': blur_score,
                'contrast': contrast,
                'brightness': brightness,
                'aspect_ratio': aspect_ratio,
                'quality': quality,
                'issues': issues,
                'recommendations': self._get_recommendations(quality, issues)
            }
            
        except Exception as e:
            logger.error(f"Помилка оцінки якості: {e}")
            return {'quality': 'unknown', 'issues': [], 'recommendations': []}
    
    def _get_recommendations(self, quality: str, issues: List[str]) -> List[str]:
        """
        Отримання порад для покращення якості фото.
        
        Args:
            quality: Загальна оцінка якості
            issues: Список проблем
            
        Returns:
            Список порад
        """
        recommendations = []
        
        if quality in ['poor', 'fair']:
            recommendations.append('📸 Зробіть фото з кращим освітленням')
            recommendations.append('📐 Тримайте камеру рівно паралельно документу')
        
        if 'зображення занадто розмите' in issues:
            recommendations.append('🔍 Сфокусуйте камеру перед зйомкою')
            recommendations.append('✋ Використовуйте штатив або упріть руки')
        
        if 'низький контраст' in issues:
            recommendations.append('💡 Додайте більше світла')
            recommendations.append('🌗 Уникайте тіней на документі')
        
        if 'проблеми з освітленням' in issues:
            recommendations.append('💡 Використовуйте рівномірне освітлення')
            recommendations.append('🚫 Уникайте відблисків')
        
        if not recommendations:
            recommendations.append('✅ Якість фото добра для розпізнавання')
        
        return recommendations
    
    def recognize_with_tesseract(self, image, lang: str = 'deu+eng') -> str:
        """
        Розпізнавання з Tesseract з різними режимами.
        
        Args:
            image: Зображення (numpy array або PIL)
            lang: Мова розпізнавання
            
        Returns:
            Розпізнаний текст
        """
        if 'tesseract' not in self.engines:
            return ""
        
        try:
            import pytesseract
            from PIL import Image
            
            # Конвертація numpy array в PIL якщо потрібно
            if isinstance(image, np.ndarray):
                image = Image.fromarray(image)
            
            # Базовий режим
            config_psm6 = r'--oem 3 --psm 6'  # Припустити однорідний блок тексту
            text_psm6 = pytesseract.image_to_string(image, lang=lang, config=config_psm6)
            
            # Режим для документів
            config_psm4 = r'--oem 3 --psm 4'  # Припустити одну колонку тексту
            text_psm4 = pytesseract.image_to_string(image, lang=lang, config=config_psm4)
            
            # Обираємо кращий результат (довший текст)
            text = text_psm6 if len(text_psm6) > len(text_psm4) else text_psm4
            
            logger.info(f"Tesseract: розпізнано {len(text)} символів")
            return text.strip()
            
        except Exception as e:
            logger.error(f"Tesseract помилка: {e}")
            return ""
    
    def recognize_with_easyocr(self, image) -> str:
        """
        Розпізнавання з EasyOCR.
        
        Args:
            image: Зображення (шлях або numpy array)
            
        Returns:
            Розпізнаний текст
        """
        if 'easyocr' not in self.engines:
            return ""
        
        try:
            # EasyOCR працює з шляхом або numpy array
            if isinstance(image, np.ndarray):
                image_path = image
            else:
                image_path = str(image)
            
            results = self.easyocr_reader.readtext(image_path)
            text = ' '.join([r[1] for r in results])
            
            logger.info(f"EasyOCR: розпізнано {len(text)} символів")
            return text.strip()
            
        except Exception as e:
            logger.error(f"EasyOCR помилка: {e}")
            return ""
    
    def recognize(self, image_path: str, lang: str = 'de') -> Dict:
        """
        Основний метод для розпізнавання зображення.
        Використовує всі доступні рушії та обирає кращий результат.
        
        Args:
            image_path: Шлях до зображення
            lang: Мова розпізнавання
            
        Returns:
            Dict з результатами
        """
        result = {
            'text': '',
            'engine': 'none',
            'confidence': 0,
            'quality': {},
            'recommendations': []
        }
        
        # Попередня обробка
        processed_img, metadata = self.preprocess_image(image_path)
        
        if processed_img is None:
            logger.error("Не вдалося обробити зображення")
            return result
        
        result['quality'] = metadata.get('quality', {})
        result['recommendations'] = result['quality'].get('recommendations', [])
        
        # Спроба розпізнавання всіма рушіями
        texts = {}
        
        # Tesseract на обробленому зображенні
        if 'tesseract' in self.engines and processed_img is not None:
            texts['tesseract_processed'] = self.recognize_with_tesseract(
                processed_img, 
                lang='deu+eng'
            )
        
        # Tesseract на оригінальному зображенні
        if 'tesseract' in self.engines:
            from PIL import Image
            try:
                original_img = Image.open(image_path)
                texts['tesseract_original'] = self.recognize_with_tesseract(
                    original_img,
                    lang='deu+eng'
                )
            except Exception as e:
                logger.warning(f"Tesseract original failed: {e}")
        
        # EasyOCR
        if 'easyocr' in self.engines:
            texts['easyocr'] = self.recognize_with_easyocr(image_path)
        
        # Обираємо кращий результат
        best_text = ''
        best_engine = 'none'
        
        for engine, text in texts.items():
            if len(text) > len(best_text):
                best_text = text
                best_engine = engine
        
        result['text'] = best_text
        result['engine'] = best_engine
        result['confidence'] = len(best_text) / 100 if best_text else 0
        
        logger.info(f"Найкращий результат: {best_engine} - {len(best_text)} символів")
        
        return result


# Глобальний екземпляр для використання
_ocr_instance = None

def get_ocr() -> AdvancedOCR:
    """Отримати глобальний екземпляр OCR."""
    global _ocr_instance
    if _ocr_instance is None:
        _ocr_instance = AdvancedOCR()
    return _ocr_instance


def recognize_image(image_path: str, lang: str = 'de') -> Dict:
    """
    Розпізнати зображення з використанням покращеного OCR.
    
    Args:
        image_path: Шлях до зображення
        lang: Мова розпізнавання
        
    Returns:
        Dict з результатами
    """
    ocr = get_ocr()
    return ocr.recognize(image_path, lang)


def extract_text_from_photo(photo_path: str, lang: str = 'de') -> str:
    """
    Зворотньо сумісна функція для витягування тексту.
    
    Args:
        photo_path: Шлях до фото
        lang: Мова
        
    Returns:
        Розпізнаний текст
    """
    result = recognize_image(photo_path, lang)
    return result['text']


if __name__ == '__main__':
    # Тестування
    import sys
    
    if len(sys.argv) > 1:
        image_path = sys.argv[1]
        result = recognize_image(image_path)
        
        print("\n" + "="*60)
        print("  РЕЗУЛЬТАТИ РОЗПІЗНАВАННЯ")
        print("="*60)
        print(f"\n📊 Рушій: {result['engine']}")
        print(f"📈 Впевненість: {result['confidence']:.2f}")
        print(f"📝 Текст ({len(result['text'])} символів):")
        print("-"*60)
        print(result['text'])
        print("-"*60)
        
        if result.get('quality'):
            print(f"\n📋 Якість: {result['quality'].get('quality', 'unknown')}")
            if result['quality'].get('issues'):
                print(f"⚠️ Проблеми: {', '.join(result['quality']['issues'])}")
            if result.get('recommendations'):
                print(f"\n💡 Поради:")
                for rec in result['recommendations']:
                    print(f"  • {rec}")
    else:
        print("Використання: python3 advanced_ocr.py <image_path>")
