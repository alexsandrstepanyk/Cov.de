#!/usr/bin/env python3
"""
Advanced Translation Module for Gov.de
Покращений переклад з підтримкою кількох сервісів, кешуванням та словником юридичних термінів.
"""

import logging
import json
import hashlib
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime, timedelta
import asyncio

# Імпортуємо кеш
from cache import get_law_cache

logger = logging.getLogger(__name__)

# Шлях до кешу
CACHE_PATH = Path(__file__).parent.parent / "data" / "translation_cache.json"

# Глобальний кеш для перекладів
_translator_cache = None


def _get_cache():
    """Отримує екземпляр кешу для перекладів (лінива ініціалізація)."""
    global _translator_cache
    if _translator_cache is None:
        _translator_cache = get_law_cache()
    return _translator_cache

# Юридичний словник термінів (німецька -> українська -> російська)
LEGAL_DICTIONARY = {
    # Загальні терміни
    'Sehr geehrte Damen und Herren': {
        'uk': 'Шановний(а) одержувач(у)',
        'ru': 'Уважаемый получатель',
        'de': 'Sehr geehrte Damen und Herren'
    },
    'Mit freundlichen Grüßen': {
        'uk': 'З повагою',
        'ru': 'С уважением',
        'de': 'Mit freundlichen Grüßen'
    },
    'Mahnung': {
        'uk': 'Нагадування про сплату',
        'ru': 'Напоминание об оплате',
        'de': 'Mahnung'
    },
    'Rechnung': {
        'uk': 'Рахунок',
        'ru': 'Счет',
        'de': 'Rechnung'
    },
    'Zahlung': {
        'uk': 'Оплата',
        'ru': 'Оплата',
        'de': 'Zahlung'
    },
    'Forderung': {
        'uk': 'Вимога сплати',
        'ru': 'Требование оплаты',
        'de': 'Forderung'
    },
    'Bescheid': {
        'uk': 'Рішення (адміністративне)',
        'ru': 'Решение (административное)',
        'de': 'Bescheid'
    },
    'Widerspruch': {
        'uk': 'Заперечення / Оскарження',
        'ru': 'Возражение / Обжалование',
        'de': 'Widerspruch'
    },
    'Kündigung': {
        'uk': 'Розірвання договору',
        'ru': 'Расторжение договора',
        'de': 'Kündigung'
    },
    'Miete': {
        'uk': 'Орендна плата',
        'ru': 'Арендная плата',
        'de': 'Miete'
    },
    'Nebenkosten': {
        'uk': 'Додаткові витрати',
        'ru': 'Дополнительные расходы',
        'de': 'Nebenkosten'
    },
    'Kaution': {
        'uk': 'Застава',
        'ru': 'Залог',
        'de': 'Kaution'
    },
    'Jobcenter': {
        'uk': 'Центр зайнятості (Jobcenter)',
        'ru': 'Центр занятости (Jobcenter)',
        'de': 'Jobcenter'
    },
    # Додані терміни для кращого перекладу
    'Einladung': {
        'uk': 'Запрошення',
        'ru': 'Приглашение',
        'de': 'Einladung'
    },
    'Kundennummer': {
        'uk': 'Номер клієнта',
        'ru': 'Номер клиента',
        'de': 'Kundennummer'
    },
    'BG-Nummer': {
        'uk': 'BG-номер (номер справи)',
        'ru': 'BG-номер (номер дела)',
        'de': 'BG-Nummer'
    },
    'Gespräch': {
        'uk': 'Співбесіда',
        'ru': 'Собеседование',
        'de': 'Gespräch'
    },
    'Termin': {
        'uk': 'Термін зустрічі',
        'ru': 'Срок встречи',
        'de': 'Termin'
    },
    'Uhr': {
        'uk': 'година',
        'ru': 'час',
        'de': 'Uhr'
    },
    'Raum': {
        'uk': 'Кімната',
        'ru': 'Комната',
        'de': 'Raum'
    },
    'Kontaktperson': {
        'uk': 'Контактна особа',
        'ru': 'Контактное лицо',
        'de': 'Kontaktperson'
    },
    'Mitwirkungspflicht': {
        'uk': "Обов'язок співпраці",
        'ru': 'Обязанность сотрудничества',
        'de': 'Mitwirkungspflicht'
    },
    'Rechtsfolgenbelehrung': {
        'uk': 'Інструкція про правові наслідки',
        'ru': 'Инструкция о правовых последствиях',
        'de': 'Rechtsfolgenbelehrung'
    },
    'Leistungen zur Sicherung des Lebensunterhalts': {
        'uk': 'Допомога для забезпечення життєвих потреб',
        'ru': 'Пособие для обеспечения жизненных потребностей',
        'de': 'Leistungen zur Sicherung des Lebensunterhalts'
    },
    'ärztliche Bescheinigung': {
        'uk': 'Лікарняний лист',
        'ru': 'Больничный лист',
        'de': 'ärztliche Bescheinigung'
    },
    'ohne wichtigen Grund': {
        'uk': 'без важливої причини',
        'ru': 'без важной причины',
        'de': 'ohne wichtigen Grund'
    },
    'Personalausweis': {
        'uk': 'Посвідчення особи',
        'ru': 'Удостоверение личности',
        'de': 'Personalausweis'
    },
    'Reisepass': {
        'uk': 'Закордонний паспорт',
        'ru': 'Заграничный паспорт',
        'de': 'Reisepass'
    },
    'Meldebescheinigung': {
        'uk': 'Свідоцтво про реєстрацію',
        'ru': 'Свидетельство о регистрации',
        'de': 'Meldebescheinigung'
    },
    'Bewerbungsunterlagen': {
        'uk': 'Документи для заявки (резюме)',
        'ru': 'Документы для заявки (резюме)',
        'de': 'Bewerbungsunterlagen'
    },
    'Lebenslauf': {
        'uk': 'Резюме (CV)',
        'ru': 'Резюме (CV)',
        'de': 'Lebenslauf'
    },
    'SGB II': {
        'uk': 'SGB II (Соціальний кодекс II)',
        'ru': 'SGB II (Социальный кодекс II)',
        'de': 'SGB II'
    },
    'SGB III': {
        'uk': 'SGB III (Соціальний кодекс III)',
        'ru': 'SGB III (Социальный кодекс III)',
        'de': 'SGB III'
    },
    'Sozialgesetzbuch': {
        'uk': 'Соціальний кодекс (Sozialgesetzbuch)',
        'ru': 'Социальный кодекс (Sozialgesetzbuch)',
        'de': 'Sozialgesetzbuch'
    },
    'Bürgergeld': {
        'uk': 'Допомога для громадян (Bürgergeld)',
        'ru': 'Пособие для граждан (Bürgergeld)',
        'de': 'Bürgergeld'
    },
    'Arbeitsagentur': {
        'uk': 'Агентство з праці (Arbeitsagentur)',
        'ru': 'Агентство по труду (Arbeitsagentur)',
        'de': 'Arbeitsagentur'
    },
    'Vorsprache': {
        'uk': 'Особиста явка',
        'ru': 'Личная явка',
        'de': 'Vorsprache'
    },
    'Beratungsgespräch': {
        'uk': 'Консультаційна співбесіда',
        'ru': 'Консультационная беседа',
        'de': 'Beratungsgespräch'
    },
    'Teilnahmepflicht': {
        'uk': "Обов'язкова участь",
        'ru': 'Обязательное участие',
        'de': 'Teilnahmepflicht'
    },
    'Sanktion': {
        'uk': 'Санкція (зменшення виплат)',
        'ru': 'Санкция (уменьшение выплат)',
        'de': 'Sanktion'
    },
    'Leistungskürzung': {
        'uk': 'Зменшення виплат',
        'ru': 'Уменьшение выплат',
        'de': 'Leistungskürzung'
    },
    'Frist': {
        'uk': 'Термін (дедлайн)',
        'ru': 'Срок (дедлайн)',
        'de': 'Frist'
    },
    'Datum': {
        'uk': 'Дата',
        'ru': 'Дата',
        'de': 'Datum'
    },
    },
    'Einladung': {
        'uk': 'Запрошення',
        'ru': 'Приглашение',
        'de': 'Einladung'
    },
    'Termin': {
        'uk': 'Термін / Зустріч',
        'ru': 'Срок / Встреча',
        'de': 'Termin'
    },
    'Gespräch': {
        'uk': 'Розмова / Співбесіда',
        'ru': 'Разговор / Собеседование',
        'de': 'Gespräch'
    },
    'Sanktion': {
        'uk': 'Санкція',
        'ru': 'Санкция',
        'de': 'Sanktion'
    },
    'Leistung': {
        'uk': 'Виплата / Допомога',
        'ru': 'Выплата / Помощь',
        'de': 'Leistung'
    },
    'Antrag': {
        'uk': 'Заява',
        'ru': 'Заявление',
        'de': 'Antrag'
    },
    'Genehmigung': {
        'uk': 'Дозвіл',
        'ru': 'Разрешение',
        'de': 'Genehmigung'
    },
    'Finanzamt': {
        'uk': 'Податкова інспекція',
        'ru': 'Налоговая инспекция',
        'de': 'Finanzamt'
    },
    'Steuerbescheid': {
        'uk': 'Податкове рішення',
        'ru': 'Налоговое решение',
        'de': 'Steuerbescheid'
    },
    'Nachzahlung': {
        'uk': 'Доплата',
        'ru': 'Доплата',
        'de': 'Nachzahlung'
    },
    'Gericht': {
        'uk': 'Суд',
        'ru': 'Суд',
        'de': 'Gericht'
    },
    'Urteil': {
        'uk': 'Судове рішення',
        'ru': 'Судебное решение',
        'de': 'Urteil'
    },
    'Gerichtsvollzieher': {
        'uk': 'Судовий виконавець',
        'ru': 'Судебный исполнитель',
        'de': 'Gerichtsvollzieher'
    },
    'Vollstreckung': {
        'uk': 'Примусове виконання',
        'ru': 'Принудительное исполнение',
        'de': 'Vollstreckung'
    },
    'Pfändung': {
        'uk': 'Арешт майна',
        'ru': 'Арест имущества',
        'de': 'Pfändung'
    },
    'Versicherung': {
        'uk': 'Страхування',
        'ru': 'Страхование',
        'de': 'Versicherung'
    },
    'Krankenkasse': {
        'uk': 'Лікарняна каса',
        'ru': 'Больничная касса',
        'de': 'Krankenkasse'
    },
    'Beitrag': {
        'uk': 'Внесок',
        'ru': 'Взнос',
        'de': 'Beitrag'
    },
    'Vertrag': {
        'uk': 'Договір',
        'ru': 'Договор',
        'de': 'Vertrag'
    },
    'Frist': {
        'uk': 'Строк / Термін',
        'ru': 'Срок',
        'de': 'Frist'
    },
    'innerhalb': {
        'uk': 'протягом',
        'ru': 'в течение',
        'de': 'innerhalb'
    },
    'Euro': {
        'uk': 'євро',
        'ru': 'евро',
        'de': 'Euro'
    },
    'überweisen': {
        'uk': 'переказати',
        'ru': 'перевести',
        'de': 'überweisen'
    },
    'Konto': {
        'uk': 'Рахунок',
        'ru': 'Счет',
        'de': 'Konto'
    },
    'IBAN': {
        'uk': 'IBAN (рахунок)',
        'ru': 'IBAN (счет)',
        'de': 'IBAN'
    },
    'BGB': {
        'uk': 'Цивільний кодекс Німеччини (BGB)',
        'ru': 'Гражданский кодекс Германии (BGB)',
        'de': 'BGB'
    },
    'SGB': {
        'uk': 'Соціальний кодекс (SGB)',
        'ru': 'Социальный кодекс (SGB)',
        'de': 'SGB'
    },
    '§': {
        'uk': 'параграф',
        'ru': 'параграф',
        'de': '§'
    }
}

# Фрази для замін після перекладу
POST_TRANSLATION_FIXES = {
    'uk': {
        'дорогие дамы и господа': 'Шановний(а) одержувач(у)',
        'уважаемые дамы и господа': 'Шановний(а) одержувач(у)',
        'искренне ваш': 'З повагою',
        'с наилучшими пожеланиями': 'З повагою',
        'напоминание': 'Нагадування про сплату',
        'требование': 'Вимога сплати',
        'увольнение': 'Розірвання договору',
        'аренда': 'Орендна плата',
        'налог': 'Податок',
        'суд': 'Суд',
        'штраф': 'Штрафні санкції',
    },
    'ru': {
        'шановний': 'Уважаемый',
        'з повагою': 'С уважением',
        'нагадування': 'Напоминание',
        'вимога': 'Требование',
        'розірвання': 'Расторжение',
        'оренда': 'Аренда',
        'податок': 'Налог',
    }
}


class AdvancedTranslator:
    """
    Клас для розширеного перекладу з підтримкою кількох сервісів.
    """
    
    def __init__(self):
        self.services = {}
        self.cache = {}
        self._init_services()
        self._load_cache()
    
    def _init_services(self):
        """Ініціалізація сервісів перекладу."""
        # Google Translate через deep-translator
        # (інші сервіси ініціалізуються нижче)
        pass
        
        # DeepL (якщо доступний)
        try:
            import deepl
            # Потрібен API ключ
            deepl_key = None  # os.getenv('DEEPL_API_KEY')
            if deepl_key:
                self.services['deepl'] = deepl.Translator(deepl_key)
                logger.info("✅ DeepL API ініціалізовано")
            else:
                logger.info("⚠️ DeepL API ключ не надано")
        except Exception as e:
            logger.info(f"ℹ️ DeepL недоступний: {e}")
        
        # LibreTranslate (безкоштовний, відкритий API)
        try:
            import requests
            self.services['libretranslate'] = {
                'url': 'https://libretranslate.com/translate',
                'session': requests.Session()
            }
            logger.info("✅ LibreTranslate ініціалізовано")
        except Exception as e:
            logger.info(f"ℹ️ LibreTranslate недоступний: {e}")
        
        # deep-translator (Google Translate)
        try:
            from deep_translator import GoogleTranslator
            GoogleTranslator(source='de', target='en').translate('test')
            logger.info("✅ deep-translator (Google) ініціалізовано")
        except Exception as e:
            logger.warning(f"⚠️ deep-translator недоступний: {e}")
    
    def _load_cache(self):
        """Завантаження кешу перекладів."""
        try:
            if CACHE_PATH.exists():
                with open(CACHE_PATH, 'r', encoding='utf-8') as f:
                    self.cache = json.load(f)
                logger.info(f"✅ Завантажено кеш перекладів ({len(self.cache)} записів)")
        except Exception as e:
            logger.warning(f"⚠️ Не вдалося завантажити кеш: {e}")
            self.cache = {}
    
    def _save_cache(self):
        """Збереження кешу перекладів."""
        try:
            CACHE_PATH.parent.mkdir(parents=True, exist_ok=True)
            with open(CACHE_PATH, 'w', encoding='utf-8') as f:
                json.dump(self.cache, f, ensure_ascii=False, indent=2)
            logger.info(f"✅ Збережено кеш перекладів ({len(self.cache)} записів)")
        except Exception as e:
            logger.error(f"❌ Не вдалося зберегти кеш: {e}")
    
    def _get_cache_key(self, text: str, src: str, dest: str) -> str:
        """Отримання ключа для кешу."""
        key_str = f"{src}:{dest}:{text}"
        return hashlib.md5(key_str.encode('utf-8')).hexdigest()
    
    def _is_cache_valid(self, entry: Dict) -> bool:
        """Перевірка чи кеш валідний (не старіше 7 днів)."""
        try:
            cached_time = datetime.fromisoformat(entry['timestamp'])
            return datetime.now() - cached_time < timedelta(days=7)
        except:
            return False
    
    def translate_with_dictionary(self, text: str, src: str, dest: str) -> Tuple[str, bool]:
        """
        Переклад з використанням юридичного словника.

        Args:
            text: Текст для перекладу
            src: Мова оригіналу
            dest: Мова перекладу

        Returns:
            (перекладений текст, чи застосовувався словник)
        """
        if src != 'de' or dest not in ['uk', 'ru']:
            return text, False
        
        # Перевіряємо кеш
        cache = _get_cache()
        cache_key = f"dict:{src}:{dest}:{hashlib.md5(text.encode()).hexdigest()}"
        cached = cache.cache.get(cache_key)
        if cached is not None:
            logger.debug(f"Кеш хіт словника для тексту довжиною {len(text)}")
            return cached.get('translation', text), cached.get('applied', False)

        result = text
        applied = False

        # Заміна термінів зі словника (спочатку довші фрази)
        sorted_terms = sorted(LEGAL_DICTIONARY.keys(), key=len, reverse=True)

        for de_term in sorted_terms:
            if de_term in result:
                translations = LEGAL_DICTIONARY[de_term]
                translation = translations.get(dest, de_term)
                result = result.replace(de_term, translation)
                applied = True
                logger.debug(f"Замінено термін: {de_term} → {translation}")

        # Зберігаємо в кеш
        cache.cache.set(cache_key, {'translation': result, 'applied': applied}, ttl=7200)

        return result, applied
    
    def apply_post_translation_fixes(self, text: str, dest: str) -> str:
        """
        Застосування виправлень після перекладу.
        
        Args:
            text: Перекладений текст
            dest: Мова перекладу
            
        Returns:
            Виправлений текст
        """
        if dest not in POST_TRANSLATION_FIXES:
            return text
        
        result = text.lower()
        
        for wrong, correct in POST_TRANSLATION_FIXES[dest].items():
            result = result.replace(wrong, correct)
        
        # Capitalize first letter
        if result:
            result = result[0].upper() + result[1:]
        
        return result
    
    async def translate_with_google(self, text: str, src: str, dest: str) -> Optional[str]:
        """Переклад через Google Translate (deep-translator)."""
        try:
            from deep_translator import GoogleTranslator
            
            # Маппінг мов для deep-translator
            lang_map = {
                'de': 'de',
                'en': 'en',
                'uk': 'uk',
                'ru': 'ru'
            }
            
            translator = GoogleTranslator(source=src, target=dest)
            result = translator.translate(text)
            return result
        except Exception as e:
            logger.error(f"Google Translate (deep-translator) помилка: {e}")
            return None
    
    async def translate_with_libre(self, text: str, src: str, dest: str) -> Optional[str]:
        """Переклад через LibreTranslate."""
        if 'libretranslate' not in self.services:
            return None
        
        try:
            service = self.services['libretranslate']
            
            # Маппінг мов
            lang_map = {
                'de': 'de',
                'en': 'en',
                'uk': 'uk',
                'ru': 'ru',
                'fr': 'fr',
                'es': 'es'
            }
            
            payload = {
                'q': text,
                'source': lang_map.get(src, 'en'),
                'target': lang_map.get(dest, 'en'),
                'format': 'text'
            }
            
            response = service['session'].post(
                service['url'],
                json=payload,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json().get('translatedText', '')
            else:
                logger.error(f"LibreTranslate error: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"LibreTranslate помилка: {e}")
            return None
    
    async def translate(self, text: str, src: str = 'de', dest: str = 'uk',
                       use_dictionary: bool = True, use_cache: bool = True) -> Dict:
        """
        Основний метод перекладу з використанням всіх доступних сервісів.

        Args:
            text: Текст для перекладу
            src: Мова оригіналу
            dest: Мова перекладу
            use_dictionary: Чи використовувати юридичний словник
            use_cache: Чи використовувати кеш

        Returns:
            Dict з результатами
        """
        result = {
            'text': '',
            'service': 'none',
            'confidence': 0,
            'from_cache': False,
            'dictionary_applied': False
        }

        # Перевірка кешу (новий LRU кеш)
        if use_cache:
            cache = _get_cache()
            cache_key = f"translate:{src}:{dest}:{hashlib.md5(text.encode()).hexdigest()}"
            cached_translation = cache.get_translation(text)
            if cached_translation is not None:
                result['text'] = cached_translation
                result['service'] = 'cache'
                result['from_cache'] = True
                result['confidence'] = 1.0
                logger.info(f"✅ Переклад з кешу: {len(text)} символів")
                return result

        # Перевірка старого кешу (для сумісності)
        if use_cache:
            cache_key = self._get_cache_key(text, src, dest)
            if cache_key in self.cache:
                cache_entry = self.cache[cache_key]
                if self._is_cache_valid(cache_entry):
                    result['text'] = cache_entry['translation']
                    result['service'] = 'cache'
                    result['from_cache'] = True
                    result['confidence'] = 1.0
                    logger.info(f"✅ Переклад з кешу: {len(text)} символів")
                    return result

        # Спроба перекладу всіма сервісами
        translations = {}

        # Google Translate
        google_result = await self.translate_with_google(text, src, dest)
        if google_result:
            translations['googletrans'] = google_result

        # LibreTranslate
        libre_result = await self.translate_with_libre(text, src, dest)
        if libre_result:
            translations['libretranslate'] = libre_result

        # Обираємо кращий результат (найдовший текст)
        if translations:
            best_service = max(translations, key=lambda s: len(translations[s]))
            result['text'] = translations[best_service]
            result['service'] = best_service
            result['confidence'] = len(result['text']) / len(text) if text else 0
            
            logger.info(f"Найкращий сервіс: {best_service} - {len(result['text'])} символів")
        
        # Застосування юридичного словника
        if use_dictionary and result['text'] and src == 'de' and dest in ['uk', 'ru']:
            dictionary_text, dictionary_applied = self.translate_with_dictionary(
                result['text'], src, dest
            )
            if dictionary_applied:
                result['text'] = dictionary_text
                result['dictionary_applied'] = True
                logger.info("✅ Застосовано юридичний словник")
        
        # Пост-обробка
        if result['text']:
            result['text'] = self.apply_post_translation_fixes(result['text'], dest)
        
        # Збереження в кеш (новий LRU кеш + старий для сумісності)
        if use_cache and result['text']:
            # Новий кеш
            cache = _get_cache()
            cache.set_translation(text, result['text'])
            
            # Старий кеш для сумісності
            cache_key = self._get_cache_key(text, src, dest)
            self.cache[cache_key] = {
                'translation': result['text'],
                'timestamp': datetime.now().isoformat(),
                'service': result['service']
            }
            self._save_cache()

        return result
    
    def translate_sync(self, text: str, src: str = 'de', dest: str = 'uk',
                      use_dictionary: bool = True, use_cache: bool = True) -> Dict:
        """
        Синхронна версія перекладу.
        
        Args:
            text: Текст для перекладу
            src: Мова оригіналу
            dest: Мова перекладу
            use_dictionary: Чи використовувати юридичний словник
            use_cache: Чи використовувати кеш
            
        Returns:
            Dict з результатами
        """
        try:
            loop = asyncio.get_event_loop()
        except RuntimeError:
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
        
        return loop.run_until_complete(
            self.translate(text, src, dest, use_dictionary, use_cache)
        )


# Глобальний екземпляр для використання
_translator_instance = None

def get_translator() -> AdvancedTranslator:
    """Отримати глобальний екземпляр перекладача."""
    global _translator_instance
    if _translator_instance is None:
        _translator_instance = AdvancedTranslator()
    return _translator_instance


def translate_text(text: str, src: str = 'de', dest: str = 'uk',
                  use_dictionary: bool = True, use_cache: bool = True) -> Dict:
    """
    Перекласти текст з використанням покращеного перекладача.
    
    Args:
        text: Текст для перекладу
        src: Мова оригіналу
        dest: Мова перекладу
        use_dictionary: Чи використовувати юридичний словник
        use_cache: Чи використовувати кеш
        
    Returns:
        Dict з результатами
    """
    translator = get_translator()
    return translator.translate_sync(text, src, dest, use_dictionary, use_cache)


async def translate_text_async(text: str, src: str = 'de', dest: str = 'uk',
                               use_dictionary: bool = True, use_cache: bool = True) -> Dict:
    """
    Асинхронна версія перекладу.
    
    Args:
        text: Текст для перекладу
        src: Мова оригіналу
        dest: Мова перекладу
        use_dictionary: Чи використовувати юридичний словник
        use_cache: Чи використовувати кеш
        
    Returns:
        Dict з результатами
    """
    translator = get_translator()
    return await translator.translate(text, src, dest, use_dictionary, use_cache)


if __name__ == '__main__':
    # Тестування
    import sys
    
    if len(sys.argv) > 1:
        text = ' '.join(sys.argv[1:])
        
        print("\n" + "="*60)
        print("  ТЕСТУВАННЯ ПЕРЕКЛАДУ")
        print("="*60)
        print(f"\nОригінал (DE):\n{text}\n")
        
        # Українська
        result_uk = translate_text(text, dest='uk')
        print(f"Переклад (UK) - {result_uk['service']}:")
        print(f"  {result_uk['text']}")
        print(f"  Кеш: {result_uk['from_cache']}, Словник: {result_uk['dictionary_applied']}")
        print()
        
        # Російська
        result_ru = translate_text(text, dest='ru')
        print(f"Переклад (RU) - {result_ru['service']}:")
        print(f"  {result_ru['text']}")
        print(f"  Кеш: {result_ru['from_cache']}, Словник: {result_ru['dictionary_applied']}")
        print()
    else:
        # Тестові приклади
        test_texts = [
            "Sehr geehrte Damen und Herren, hiermit mahnen wir Sie zur Zahlung der offenen Forderung.",
            "Mahnung: Zahlung erforderlich innerhalb von 7 Tagen.",
            "Kündigung der Wohnung wegen Eigenbedarf.",
            "Einladung zum Gespräch im Jobcenter am Montag um 10 Uhr."
        ]
        
        print("\n" + "="*60)
        print("  ТЕСТУВАННЯ ПЕРЕКЛАДУ ЮРИДИЧНИХ ТЕРМІНІВ")
        print("="*60)
        
        for text in test_texts:
            print(f"\n🇩🇪 {text}")
            result = translate_text(text, dest='uk')
            print(f"🇺🇦 {result['text']}")
            print(f"   Сервіс: {result['service']}, Словник: {result['dictionary_applied']}")
