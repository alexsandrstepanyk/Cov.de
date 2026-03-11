#!/usr/bin/env python3
"""
Advanced OCR Module for Gov.de
Покращене розпізнавання тексту з фото з попередньою обробкою та контролем якості.
"""

import logging
import re
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
                'recommendations': self._get_recommendations(quality, issues, brightness, contrast)
            }
            
        except Exception as e:
            logger.error(f"Помилка оцінки якості: {e}")
            return {'quality': 'unknown', 'issues': [], 'recommendations': []}

    def _get_recommendations(self, quality: str, issues: List[str], brightness: float = 128, contrast: float = 50) -> List[str]:
        """
        Отримання інтерактивних порад для покращення якості фото з емодзі.

        Args:
            quality: Загальна оцінка якості ('poor', 'fair', 'good')
            issues: Список проблем
            brightness: Яскравість зображення (0-255)
            contrast: Контрастність зображення

        Returns:
            Список інтерактивних порад з емодзі
        """
        recommendations = []

        # Загальна оцінка
        if quality == 'poor':
            recommendations.append('😕 Якість фото **низька** для надійного розпізнавання')
            recommendations.append('')
        elif quality == 'fair':
            recommendations.append('⚠️ Якість фото **задовільна**, але можна краще')
            recommendations.append('')

        # 💡 Освітлення та яскравість
        if brightness < 50:
            recommendations.append('💡 **Тут темно!** Увімкніть світло або використайте спалах')
            recommendations.append('   → Темні фото важко розпізнати (яскравість: {:.0f}%)'.format(brightness/2.55))
            recommendations.append('')
        elif brightness > 200:
            recommendations.append('☀️ **Занадто яскраво!** Уникайте прямого сонячного світла')
            recommendations.append('   → Відблиски заважають розпізнаванню (яскравість: {:.0f}%)'.format(brightness/2.55))
            recommendations.append('')

        # 🌗 Контраст
        if contrast < 30:
            recommendations.append('🌗 **Низький контраст!** Документ зливається з фоном')
            recommendations.append('   → Покладіть документ на темний стіл')
            recommendations.append('   → Контрастність: {:.0f}% (потрібно >30%)'.format(contrast))
            recommendations.append('')

        # 🔍 Розмиття
        if 'зображення занадто розмите' in issues:
            recommendations.append('🔍 **Фото розмите!** Потрібно сфокусувати')
            recommendations.append('   → Натисніть на екран телефону для фокусу')
            recommendations.append('   → Зачекайте поки камера сфокусується')
            recommendations.append('   → Використовуйте обидві руки для стабільності')
            recommendations.append('')

        # 📐 Нахил
        if 'зображення повернуте' in issues:
            recommendations.append('📐 **Документ повернутий!** Вирівняйте горизонтально')
            recommendations.append('   → Тримайте телефон паралельно документу')
            recommendations.append('   → Усі кути документа мають бути видні')
            recommendations.append('')

        # ✋ Стабільність
        if 'рухи під час зйомки' in issues:
            recommendations.append('✋ **Камера тремтіла!** Зафіксуйте телефон')
            recommendations.append('   → Упріть руки об стіл')
            recommendations.append('   → Затримайте подих на момент зйомки')
            recommendations.append('')

        # 🚫 Відблиски
        if 'проблеми з освітленням' in issues:
            recommendations.append('🚫 **Відблики!** Змініть кут освітлення')
            recommendations.append('   → Уникайте ламп над документом')
            recommendations.append('   → Використовуйте розсіяне світло')
            recommendations.append('')

        # ✅ Якщо все добре
        if not recommendations or quality == 'good':
            recommendations.append('✅ **Якість фото добра!** Можна розпізнавати')
            recommendations.append('   → Дякуємо за якісне фото!')

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
        Розпізнавання з EasyOCR з покращеними налаштуваннями.

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

            # Покращені налаштування для німецьких документів
            results = self.easyocr_reader.readtext(
                image_path,
                paragraph=True,           # Об'єднувати в параграфи
                min_size=10,              # Мінімальний розмір тексту
                contrast_ths=0.1,         # Контраст для об'єднання
                adjust_contrast=0.5,      # Автоматичне покращення контрасту
                text_threshold=0.7,       # Поріг впевненості
                low_text=0.4,             # Мінімальна впевненість
                link_threshold=0.4,       # З'єднання тексту
                canvas_size=2048,         # Максимальний розмір
                mag_ratio=1.5,            # Збільшення масштабу
            )
            
            # Об'єднання результатів з розумними переносами рядків
            text_blocks = []
            for r in results:
                if len(r[1]) > 2:  # Ігноруємо дуже короткі фрагменти
                    text_blocks.append(r[1])
            
            text = '\n'.join(text_blocks)

            logger.info(f"EasyOCR: розпізнано {len(text)} символів ({len(results)} блоків)")
            return text.strip()

        except Exception as e:
            logger.error(f"EasyOCR помилка: {e}")
            return ""
    
    def recognize(self, image_path: str, lang: str = 'de') -> Dict:
        """
        Основний метод для розпізнавання зображення.
        Використовує всі доступні рушії та обирає кращий результат.
        Інтегровано з TextValidator для перевірки якості тексту.

        Args:
            image_path: Шлях до зображення
            lang: Мова розпізнавання

        Returns:
            Dict з результатами (включаючи validation)
        """
        result = {
            'text': '',
            'engine': 'none',
            'confidence': 0,
            'quality': {},
            'validation': {},
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

        # 🔍 ВАЛІДАЦІЯ ТЕКСТУ
        if best_text:
            result['validation'] = TextValidator.validate_text(best_text)
            
            # Додаємо поради з валідації до загальних рекомендацій
            if result['validation'].get('recommendations'):
                result['recommendations'].extend(result['validation']['recommendations'])
            
            # Логування попереджень якщо якість низька
            if not result['validation']['valid']:
                logger.warning(f"⚠️ Текст не пройшов валідацію (якість: {result['validation']['quality']})")
                issues = result['validation'].get('issues', [])
                if issues:
                    logger.warning(f"  Проблеми: {', '.join(issues)}")

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


class TextValidator:
    """
    Валідація якості OCR тексту.
    Виявляє проблеми з розпізнаванням та пропонує виправлення.
    """
    
    # Німецькі спеціальні символи
    GERMAN_CHARS = set('äöüÄÖÜß')
    
    # Кириличні символи (українська, російська)
    CYRILLIC_CHARS = set('абвгдеєжзийклмнопрстуфхцчшщьюяїіёАБВГДЕЄЖЗИЙКЛМНОПРСТУФХЦЧШЩЬЮЯЇІЁ')
    
    # Патерни "сміття" (garbage text)
    GARBAGE_PATTERNS = [
        r'[a-z]{20,}',  # Дуже довгі "слова" з малих літер (20+)
        r'[A-Z]{15,}',  # Дуже довгі "слова" з великих літер (15+)
        r'[0-9]{25,}',  # Дуже довгі числа (25+)
        r'[^a-zA-Z0-9äöüÄÖÜß\s\.\,\-\(\)\§]{15,}',  # 15+ спецсимволів підряд (але не пробіли)
        r'(.)\1{8,}',  # Повторення символу 8+ разів
    ]
    
    # Очікувані німецькі слова для Jobcenter листів
    EXPECTED_WORDS = {
        'jobcenter', 'einladung', 'termin', 'gespräch', 'kunde',
        'nummer', 'kundennummer', 'bg', 'nummer', 'datum', 'uhrzeit',
        'raum', 'kontakt', 'frau', 'herr', 'mit freundlichen grüßen'
    }
    
    # Німецькі слова які можуть бути довгими (не вважати сміттям)
    LONG_GERMAN_WORDS = {
        'rechtsfolgenbelehrung', 'mitwirkungspflichten', 'bewerbungsunterlagen',
        'sozialgesetzbuch', 'arbeitsagentur', 'nebenkostenabrechnung',
        'meldebescheinigung', 'personalausweis', 'arbeitsbescheinigung'
    }
    
    @classmethod
    def validate_text(cls, text: str) -> Dict:
        """
        Перевірка якості OCR тексту.
        
        Args:
            text: Розпізнаний текст
            
        Returns:
            Dict з результатами валідації
        """
        if not text or len(text.strip()) < 10:
            return {
                'valid': False,
                'quality_score': 0,
                'quality': 'poor',
                'issues': ['Текст занадто короткий'],
                'recommendations': ['Спробуйте зробити фото ще раз']
            }
        
        text_lower = text.lower()
        issues = []
        score = 100
        
        # 0. 🔴 ПЕРЕВІРКА НА КИРИЛИЦЮ (критично для німецьких документів)
        has_cyrillic = bool(cls.CYRILLIC_CHARS & set(text_lower))
        has_german_chars = bool(cls.GERMAN_CHARS & set(text_lower))
        
        if has_cyrillic and not has_german_chars:
            # Це український/російський текст, а не німецький
            return {
                'valid': False,
                'quality_score': 20,
                'quality': 'poor',
                'issues': [
                    '🔴 Знайдено кирилицю в німецькому тексті',
                    'Схоже це український/російський текст, а не німецький'
                ],
                'has_cyrillic': True,
                'has_german_chars': False,
                'recommendations': [
                    '📸 Зробіть фото кращої якості',
                    '🔤 Переконайтесь що документ німецькою мовою',
                    '💡 Використовуйте поради з OCR_TIPS_UA.md'
                ]
            }
        
        # 1. Перевірка на німецькі символи
        if not has_german_chars:
            issues.append('Відсутні німецькі символи (ä, ö, ü, ß)')
            score -= 15
        
        # 2. Перевірка на garbage текст
        garbage_matches = []
        for pattern in cls.GARBAGE_PATTERNS:
            matches = re.findall(pattern, text_lower)
            if matches:
                # Фільтруємо довгі німецькі слова
                filtered = [
                    m for m in matches
                    if m.strip() and m.strip() not in cls.LONG_GERMAN_WORDS
                ]
                if filtered:
                    garbage_matches.extend(filtered[:3])
        
        if garbage_matches:
            issues.append(f'Знайдено "сміття": {", ".join(garbage_matches[:3])}')
            score -= 20
        
        # 3. Перевірка очікуваних слів
        found_expected = [word for word in cls.EXPECTED_WORDS if word in text_lower]
        if len(found_expected) < 3:
            issues.append(f'Мало очікуваних слів ({len(found_expected)} з {len(cls.EXPECTED_WORDS)})')
            score -= 15
        
        # 4. Перевірка на послідовність символів
        char_ratio = len(re.findall(r'[a-zA-ZäöüÄÖÜß]', text)) / len(text) if text else 0
        if char_ratio < 0.6:
            issues.append('Багато не-символьних знаків')
            score -= 10
        
        # 5. Перевірка довжини слів
        words = [w for w in text.split() if len(w) > 1]
        avg_word_length = np.mean([len(w) for w in words]) if words else 0
        if avg_word_length > 15 or avg_word_length < 3:
            issues.append(f'Підозріла середня довжина слів: {avg_word_length:.1f}')
            score -= 10
        
        # 6. 🔍 Перевірка на "кашу" з символів (OCR помилки)
        nonsense_words = []
        vowels = set('aeiouäöüAEIOUÄÖÜ')
        for word in words:
            if len(word) > 5:
                # Слово без голосних або з дивною структурою
                has_vowel = any(c in vowels for c in word)
                if not has_vowel:
                    nonsense_words.append(word)
        
        nonsense_ratio = len(nonsense_words) / len(words) if words else 0
        if nonsense_ratio > 0.3:  # Більше 30% nonsense слів
            issues.append(f'Багато незрозумілих слів ({len(nonsense_words)} слів без голосних)')
            score -= 25
        
        # 7. Перевірка кількості слів
        if len(words) < 5:
            issues.append('Занадто мало слів для аналізу')
            score -= 20
        
        # Визначаємо загальну якість
        quality = 'good' if score >= 80 else 'fair' if score >= 50 else 'poor'
        
        return {
            'valid': score >= 50,
            'quality_score': max(0, score),
            'quality': quality,
            'issues': issues,
            'found_german_chars': has_german_chars,
            'found_expected_words': found_expected,
            'garbage_detected': len(garbage_matches) > 0,
            'nonsense_ratio': nonsense_ratio,
            'recommendations': cls._get_text_recommendations(issues, quality, has_cyrillic)
        }
    
    @classmethod
    def _get_text_recommendations(cls, issues: List[str], quality: str, has_cyrillic: bool = False) -> List[str]:
        """Генерація порад на основі проблем тексту."""
        recommendations = []
        
        # 🔴 КИРИЛИЦЯ - критична помилка
        if has_cyrillic:
            recommendations.append('🔴 **Знайдено кирилицю в тексті!**')
            recommendations.append('   → Схоже це не німецький документ')
            recommendations.append('   → Перевірте що фото містить німецький текст')
            recommendations.append('')
            return recommendations
        
        if quality == 'poor':
            recommendations.append('😕 **Якість тексту низька** - потрібне краще фото')
            recommendations.append('')
        
        if 'Відсутні німецькі символи' in str(issues):
            recommendations.append('🔤 **Немає німецьких літер** (ä, ö, ü, ß)')
            recommendations.append('   → Це дивно для німецького документу')
            recommendations.append('   → Можливо OCR помилився з мовою')
            recommendations.append('')
        
        if 'Знайдено "сміття"' in str(issues):
            recommendations.append('🗑️ **Знайдено "сміття" в тексті**')
            recommendations.append('   → Фото занадто розмите або темне')
            recommendations.append('   → Спробуйте краще освітлення')
            recommendations.append('')
        
        if 'Мало очікуваних слів' in str(issues):
            recommendations.append('📝 **Текст не схожий на німецький документ**')
            recommendations.append('   → Переконайтесь що це Jobcenter лист')
            recommendations.append('   → Спробуйте інший кут зйомки')
            recommendations.append('')
        
        if 'Багато незрозумілих слів' in str(issues):
            recommendations.append('🔤 **Багато незрозумілих слів**')
            recommendations.append('   → OCR погано розпізнав текст')
            recommendations.append('   → Зробіть фото з кращим освітленням')
            recommendations.append('   → Тримайте камеру рівно')
            recommendations.append('')
        
        if 'Занадто мало слів' in str(issues):
            recommendations.append('📄 **Мало тексту для аналізу**')
            recommendations.append('   → Переконайтесь що весь документ в кадрі')
            recommendations.append('   → Спробуйте наблизити камеру')
            recommendations.append('')
        
        if not recommendations:
            recommendations.append('✅ **Якість тексту добра**')
            recommendations.append('   → Можна продовжувати обробку')
        
        return recommendations


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

        # Валідація тексту
        print("\n🔍 ВАЛІДАЦІЯ ТЕКСТУ:")
        validation = TextValidator.validate_text(result['text'])
        print(f"  Якість: {validation['quality']} ({validation['quality_score']}%)")
        print(f"  Валідний: {'✅' if validation['valid'] else '❌'}")
        
        if validation['issues']:
            print(f"\n⚠️ Проблеми:")
            for issue in validation['issues']:
                print(f"  • {issue}")
        
        if validation['recommendations']:
            print(f"\n💡 Поради:")
            for rec in validation['recommendations']:
                print(f"  {rec}")
        
        print("\n" + "="*60)
    else:
        # Тест з прикладом
        print("Тестування TextValidator...")
        
        test_text_good = """
        Ihre Kundennummer: BG123456
        Einladung zum Gespräch
        Termin: Donnerstag, 12.03.2026 um 10:00 Uhr
        Raum Nummer 123
        Kontakt: Frau Müller
        Mit freundlichen Grüßen
        Ihr Jobcenter
        """
        
        test_text_bad = """
        моя довідка: номер клієнта baw homep kniehta
        (bypb nacka jobxam bka3yhte moro)
        шановна пані баве фпісенуе
        """
        
        print("\n✅ Тест хорошого тексту:")
        val_good = TextValidator.validate_text(test_text_good)
        print(f"  Якість: {val_good['quality']} ({val_good['quality_score']}%)")
        print(f"  Валідний: {'✅' if val_good['valid'] else '❌'}")
        
        print("\n❌ Тест поганого тексту:")
        val_bad = TextValidator.validate_text(test_text_bad)
        print(f"  Якість: {val_bad['quality']} ({val_bad['quality_score']}%)")
        print(f"  Валідний: {'✅' if val_bad['valid'] else '❌'}")
        if val_bad['issues']:
            print(f"  Проблеми: {', '.join(val_bad['issues'])}")
