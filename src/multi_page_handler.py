#!/usr/bin/env python3
"""
Multi-page Document Handler for Gov.de
Обробка багатосторінкових документів
"""

import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler

logger = logging.getLogger(__name__)


async def handle_multi_page_photo(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, file_path: str, lang: str) -> tuple:
    """
    Обробка фото для багатосторінкового документу.
    
    Returns:
        (page_text, pages_count, success)
    """
    from advanced_ocr import recognize_image
    
    try:
        ocr_result = recognize_image(file_path, lang='deu+eng')
        page_text = ocr_result['text']
        logger.info(f"Advanced OCR: витягнуто {len(page_text)} символів")
        
        if not page_text.strip():
            return None, 0, False
        
        # Зберігаємо фото та текст
        if 'letter_photos' not in context.user_data:
            context.user_data['letter_photos'] = []
            context.user_data['letter_text'] = ''
        
        context.user_data['letter_photos'].append(file_path)
        page_num = len(context.user_data['letter_photos'])
        context.user_data['letter_text'] += f"\n\n--- СТОРІНКА {page_num} ---\n\n{page_text}"
        
        logger.info(f"Збережено сторінку {page_num}: {len(page_text)} символів")
        
        return page_text, page_num, True
        
    except Exception as e:
        logger.error(f"Помилка OCR: {e}")
        return None, 0, False


def get_multi_page_keyboard():
    """Отримати клавіатуру для багатосторінкового режиму."""
    return [['✅ Все, аналізуй'], ['📄 Надіслати ще сторінку']]


async def ask_for_more_pages(update: Update, pages_count: int, page_text: str):
    """Запитати чи є ще сторінки."""
    keyboard = get_multi_page_keyboard()
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    
    await update.message.reply_text(
        f"✅ **Сторінку {pages_count} розпізнано!**\n\n"
        f"📝 Знайдено тексту: {len(page_text)} символів\n\n"
        f"📄 **Є ще сторінки?**\n"
        f"• Натисніть \"📄 Надіслати ще сторінку\" щоб додати\n"
        f"• Натисніть \"✅ Все, аналізуй\" щоб завершити",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )


async def finalize_multi_page(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """
    Завершення збору багатосторінкового документу.
    
    Returns:
        (text, pages_count) або (None, 0) при помилці
    """
    text = context.user_data.get('letter_text', '')
    pages_count = len(context.user_data.get('letter_photos', []))
    
    if not text.strip():
        return None, 0
    
    # Повідомлення про початок аналізу
    if pages_count > 1:
        await update.message.reply_text(
            f"⏳ **Аналіз {pages_count} сторінок**, зачекайте...\n\n"
            f"📊 Об'єднаний текст: {len(text)} символів",
            parse_mode='Markdown'
        )
    else:
        await update.message.reply_text("⏳ Аналіз листа, зачекайте...")
    
    logger.info(f"Фінальний аналіз: {pages_count} сторінок, {len(text)} символів")
    
    # Очищаємо тимчасові дані
    context.user_data['letter_photos'] = []
    
    return text, pages_count
