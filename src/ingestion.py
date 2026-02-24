#!/usr/bin/env python3
"""
Letter Ingestion Module
Обробка вхідних листів: текст, PDF, зображення (OCR).
"""

import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)

def load_letter(file_path: str) -> str:
    """
    Завантаження тексту листа з файлу.
    
    Args:
        file_path: Шлях до файлу
    
    Returns:
        Текст листа
    
    Raises:
        ValueError: Якщо не вдалося завантажити файл
    """
    path = Path(file_path)
    suffix = path.suffix.lower()
    
    logger.info(f"Завантаження файлу: {file_path} (suffix: {suffix})")
    
    # Спроба PDF
    if suffix == '.pdf':
        try:
            from pdfminer.high_level import extract_text
            text = extract_text(str(path))
            if text and text.strip():
                logger.info(f"PDF завантажено: {len(text)} символів")
                return text
        except Exception as e:
            logger.warning(f"PDF extraction failed: {e}")
    
    # Спроба текстового файлу
    if suffix in ['.txt', '.md', '']:
        try:
            with open(path, 'r', encoding='utf-8') as f:
                text = f.read()
            if text and text.strip():
                logger.info(f"Текст завантажено: {len(text)} символів")
                return text
        except UnicodeDecodeError:
            # Спроба з іншою кодувкою
            try:
                with open(path, 'r', encoding='latin-1') as f:
                    text = f.read()
                if text and text.strip():
                    logger.info(f"Текст завантажено (latin-1): {len(text)} символів")
                    return text
            except Exception as e:
                logger.warning(f"Текст не завантажено: {e}")
    
    # Спроба OCR для зображень
    if suffix in ['.jpg', '.jpeg', '.png', '.bmp', '.tiff', '.gif']:
        try:
            import pytesseract
            from PIL import Image
            img = Image.open(str(path))
            text = pytesseract.image_to_string(img, lang='deu+eng')
            if text and text.strip():
                logger.info(f"OCR виконано: {len(text)} символів")
                return text
        except Exception as e:
            logger.warning(f"OCR failed: {e}")
    
    # Спроба OCR для PDF (якщо pdfminer не спрацював)
    if suffix == '.pdf':
        try:
            import pytesseract
            from PIL import Image
            import pdf2image
            
            # Конвертація PDF у зображення
            images = pdf2image.convert_from_path(str(path))
            text = ""
            for img in images:
                text += pytesseract.image_to_string(img, lang='deu+eng')
            
            if text and text.strip():
                logger.info(f"PDF OCR виконано: {len(text)} символів")
                return text
        except ImportError:
            logger.warning("pdf2image не встановлено")
        except Exception as e:
            logger.warning(f"PDF OCR failed: {e}")
    
    # Фолбек: спроба читати як текст
    try:
        with open(path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()
        if content and content.strip():
            logger.info(f"Фолбек: завантажено {len(content)} символів")
            return content
    except Exception as e:
        logger.error(f"Фолбек не спрацював: {e}")
    
    raise ValueError(f"Не вдалося завантажити файл: {path.name}")

def preprocess_text(text: str) -> str:
    """
    Базова попередня обробка тексту.
    
    Args:
        text: Вхідний текст
    
    Returns:
        Оброблений текст
    """
    # Видалення зайвих пробілів
    text = ' '.join(text.split())
    
    # Видалення спецсимволів на початку/кінці речень
    import re
    text = re.sub(r'\s+([,.:;!?])', r'\1', text)
    
    # Нормалізація нових рядків
    text = text.replace('\r\n', '\n').replace('\r', '\n')
    
    # Видалення більше 2 нових рядків підряд
    text = re.sub(r'\n{3,}', '\n\n', text)
    
    logger.info(f"Текст оброблено: {len(text)} символів")
    return text

def extract_text_from_bytes(data: bytes, content_type: str) -> str:
    """
    Витягування тексту з байтів.
    
    Args:
        data: Байти файлу
        content_type: MIME тип
    
    Returns:
        Текст
    """
    import tempfile
    
    with tempfile.NamedTemporaryFile(delete=False, suffix='.tmp') as f:
        f.write(data)
        temp_path = f.name
    
    try:
        # Визначення типу файлу
        if 'pdf' in content_type:
            suffix = '.pdf'
        elif 'image' in content_type:
            suffix = '.jpg'
        else:
            suffix = '.txt'
        
        # Перейменування для правильного визначення
        new_path = temp_path + suffix
        os.rename(temp_path, new_path)
        
        return load_letter(new_path)
    finally:
        # Видалення тимчасових файлів
        try:
            os.unlink(temp_path)
        except:
            pass
        try:
            os.unlink(new_path)
        except:
            pass
