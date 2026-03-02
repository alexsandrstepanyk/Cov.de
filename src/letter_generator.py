#!/usr/bin/env python3
"""
Letter Generator Module v1.1
Генерація німецьких відповідей у форматі DIN 5008
з автоматичним витягуванням даних та fallback шаблонами
"""

import re
from typing import Dict, Optional, List
from datetime import datetime

# Імпорт fallback шаблонів
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from fallback_templates import (
    generate_fallback_response,
    should_use_fallback,
    detect_situation_by_keywords
)


class LetterGenerator:
    """
    Генерація офіційних листів німецькою мовою.
    
    Автоматично витягує:
    - Відправника (організацію)
    - Отримувача (користувача)
    - Контактну особу (Frau/Herr)
    - Дати, номери, посилання
    
    Генерує відповідь у форматі DIN 5008:
    - Правильне розташування адрес
    - Персоналізоване звертання
    - Професійна структура
    """
    
    def __init__(self):
        """Ініціалізація генератора."""
        pass
    
    # ========================================================================
    # EXTRACTION - Витягування даних
    # ========================================================================
    
    def extract_all_data(self, text: str) -> Dict:
        """
        Витягнути всі дані з листа.
        
        Args:
            text: Текст листа
            
        Returns:
            Dict з усіма даними
        """
        return {
            'sender': self.extract_sender(text),
            'recipient': self.extract_recipient(text),
            'contact_person': self.extract_contact_person(text),
            'contact_info': self.extract_contact_info(text),
            'reference': self.extract_reference(text),
            'dates': self.extract_dates(text),
            'amounts': self.extract_amounts(text),
        }
    
    def extract_sender(self, text: str) -> Dict:
        """
        Витягнути відправника (організацію).
        
        Args:
            text: Текст листа
            
        Returns:
            Dict з даними відправника
        """
        # Перша адреса в листі (зазвичай організація)
        # Більш простий патерн
        lines = text.split('\n')
        
        # Шукаємо перші 3-4 рядки (організація)
        org_name = ''
        org_address = ''
        org_city = ''
        
        for i, line in enumerate(lines[:6]):
            line = line.strip()
            if not line:
                continue
                
            # Перший рядок - назва
            if not org_name and len(line) > 3:
                org_name = line
            # Другий рядок - вулиця
            elif not org_address and ('straße' in line.lower() or 'str.' in line.lower() or re.search(r'\d+', line)):
                org_address = line
            # Третій рядок - місто (ZIP код)
            elif not org_city and re.search(r'\d{4,5}', line):
                org_city = line
                break
        
        return {
            'name': org_name,
            'address': org_address,
            'city': org_city,
        }
    
    def _extract_first_org_name(self, text: str) -> str:
        """Витягнути назву першої організації."""
        # Jobcenter, Finanzamt тощо
        org_patterns = [
            r'(Jobcenter\s+[A-Z][a-z]+)',
            r'(Finanzamt\s+[A-Z][a-z]+)',
            r'([A-Z][a-z]+\s+(?:GmbH|AG|KG))',
            r'(Inkasso\s+[A-Z][a-z]+)',
        ]
        
        for pattern in org_patterns:
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        
        return ''
    
    def extract_recipient(self, text: str) -> Dict:
        """
        Витягнути отримувача (користувача).
        
        Args:
            text: Текст листа
            
        Returns:
            Dict з даними отримувача
        """
        # Отримувач (після Herrn/Frau)
        lines = text.split('\n')
        
        recipient_name = ''
        recipient_address = ''
        recipient_city = ''
        
        found_herrn_frau = False
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Шукаємо Herrn/Frau
            if not found_herrn_frau and ('Herrn' in line or 'Frau' in line):
                found_herrn_frau = True
                continue
            
            if found_herrn_frau:
                if not recipient_name and len(line) > 3:
                    recipient_name = line
                elif not recipient_address and ('straße' in line.lower() or 'str.' in line.lower() or re.search(r'\d+', line)):
                    recipient_address = line
                elif not recipient_city and re.search(r'\d{4,5}', line):
                    recipient_city = line
                    break
        
        return {
            'name': recipient_name,
            'address': recipient_address,
            'city': recipient_city,
        }
    
    def extract_contact_person(self, text: str) -> Dict:
        """
        Витягнути контактну особу (Frau/Herr з підпису).
        """
        # Шукаємо в кінці листа (підпис)
        end_section = text[-800:] if len(text) > 800 else text
        
        # Фільтр службових слів які НЕ є іменами
        IGNORE_PATTERNS = [
            r'\bIm Auftrag\b', r'\bi\.A\.\b', r'\bi\.V\.\b', r'\bi\.B\.\b',
            r'\bBeraterin\b', r'\bSachbearbeiterin\b', r'\bGeschäftsleitung\b',
            r'\bnamens der Geschäftsleitung\b',
            r'\bin Vollmacht\b', r'\bin Vertretung\b', r'\bDer Leiter\b',
            r'\bDie Leiterin\b', r'\bTeamleiter\b', r'\bAbteilungsleiter\b',
        ]
        
        # Видаляємо службові слова (але залишаємо Mit freundlichen Grüßen для орієнтира)
        for pattern in IGNORE_PATTERNS:
            end_section = re.sub(pattern, '', end_section, flags=re.IGNORECASE)
        
        # Шукаємо ім'я після "Mit freundlichen Grüßen"
        match = re.search(r'Mit freundlichen Grüßen\s*\n*\s*([A-Z][a-z]+\s+[A-Z][a-z]+)', end_section, re.IGNORECASE)
        if match:
            name_parts = match.group(1).split()
            if len(name_parts) >= 2:
                # Визначаємо стать за іменем
                female_names = ['Maria', 'Petra', 'Anna', 'Sabine', 'Monika', 'Claudia', 'Andrea', 'Ute', 'Gabriele', 'Birgit']
                firstname = name_parts[0]
                gender = 'female' if firstname in female_names else 'male'
                return {
                    'firstname': firstname,
                    'lastname': name_parts[-1],
                    'gender': gender,
                    'title': None,
                }
        
        # Жінка (альтернативний патерн)
        frau_match = re.search(r'Frau\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)', end_section, re.IGNORECASE)
        if frau_match:
            return {
                'firstname': frau_match.group(1),
                'lastname': frau_match.group(2),
                'gender': 'female',
                'title': None,
            }
        
        # Чоловік з титулом
        herr_title_match = re.search(r'Herr\s+(Dr\.|Prof\.)\s+([A-Z][a-z]+)', end_section, re.IGNORECASE)
        if herr_title_match:
            return {
                'firstname': None,
                'lastname': herr_title_match.group(2),
                'gender': 'male',
                'title': herr_title_match.group(1),
            }
        
        # Чоловік без титулу
        herr_match = re.search(r'Herr\s+([A-Z][a-z]+)\s+([A-Z][a-z]+)', end_section, re.IGNORECASE)
        if herr_match:
            return {
                'firstname': herr_match.group(1),
                'lastname': herr_match.group(2),
                'gender': 'male',
                'title': None,
            }
        
        return {}
    
    def extract_contact_info(self, text: str) -> Dict:
        """Витягнути контактну інформацію."""
        contact = {}
        
        # Телефон
        phone_match = re.search(r'(?:Telefon|Tel\.?)[:\s]*(\+?\d[\d\s\-/]+)', text)
        if phone_match:
            contact['phone'] = phone_match.group(1).strip()
        
        # Email
        email_match = re.search(r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if email_match:
            contact['email'] = email_match.group(1).strip()
        
        # Вебсайт
        website_match = re.search(r'(www\.[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})', text)
        if website_match:
            contact['website'] = website_match.group(1).strip()
        
        return contact
    
    def extract_reference(self, text: str) -> Dict:
        """Витягнути реквізити (номер справи, клієнта тощо)."""
        ref = {}
        
        patterns = {
            'kundennummer': r'(?:Kundennummer|Kunden-Nr\.?)[:\s]*([A-Z0-9\-/]+)',
            'aktenzeichen': r'(?:Aktenzeichen|Az\.?|Akz\.)[:\s]*([A-Z0-9\-/]+)',
            'forderungsnummer': r'(?:Forderungsnummer|Forderung-Nr\.?)[:\s]*([A-Z0-9\-/]+)',
            'geschäftszeichen': r'(?:Geschäftszeichen|Gesch.-Z.\s*|GZ)[:\s]*([A-Z0-9\-/]+)',
            'steuernummer': r'(?:Steuernummer|St.-Nr\.?)[:\s]*([A-Z0-9\-/]+)',
        }
        
        for key, pattern in patterns.items():
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                ref[key] = match.group(1).strip()
        
        return ref
    
    def extract_dates(self, text: str) -> List[str]:
        """Витягнути всі дати."""
        pattern = r'(\d{1,2}\.\d{1,2}\.\d{2,4})'
        return re.findall(pattern, text)
    
    def extract_amounts(self, text: str) -> List[Dict]:
        """Витягнути грошові суми."""
        amounts = []
        
        # EUR, €
        pattern = r'(\d+[.,\s]?\d*)\s*(?:euro|EUR|€)'
        matches = re.findall(pattern, text, re.IGNORECASE)
        
        for match in matches:
            amount_str = match[0].replace(',', '.').replace(' ', '')
            try:
                amount = float(amount_str)
                amounts.append({
                    'value': amount,
                    'currency': 'EUR',
                    'original': match[0]
                })
            except:
                pass
        
        return amounts
    
    # ========================================================================
    # GENERATION - Генерація листа
    # ========================================================================
    
    def generate_letter(self, data: Dict, response_text: str, response_type: str = 'general') -> str:
        """
        Згенерувати лист у форматі DIN 5008.
        
        Args:
            data: Дані з extract_all_data()
            response_text: Текст відповіді (з improved_response_generator)
            response_type: Тип відповіді (jobcenter, inkasso тощо)
            
        Returns:
            Згенерований лист
        """
        # Шапка (відправник - користувач)
        user_name = data.get('recipient', {}).get('name', '[Ваше ім\'я]')
        user_address = data.get('recipient', {}).get('address', '[Ваша адреса]')
        user_city = data.get('recipient', {}).get('city', '[Ваше місто]')
        
        sender_block = f"{user_name}\n{user_address}\n{user_city}"
        
        # Отримувач (організація)
        org_name = data.get('sender', {}).get('name', '[Організація]')
        org_address = data.get('sender', {}).get('address', '[Адреса]')
        org_city = data.get('sender', {}).get('city', '[Місто]')
        
        recipient_block = f"\n{org_name}\n{org_address}\n{org_city}"
        
        # Дата
        today = datetime.now().strftime('%d.%m.%Y')
        city = user_city.split()[-1] if user_city else ''
        date_line = f"\n{city}, {today}"
        
        # Тема
        dates = data.get('dates', [])
        ref_date = dates[0] if dates else '[Datum]'
        ref_number = data.get('reference', {}).get('kundennummer', '')
        
        betreff = self.generate_betreff(response_type, ref_date, ref_number)
        
        # Звертання
        contact = data.get('contact_person', {})
        salutation = self.generate_salutation(contact)
        
        # Тіло листа (вже готове з improved_response_generator)
        body = response_text
        
        # Підпис
        closing = "\n\nMit freundlichen Grüßen\n\n"
        signature = user_name
        
        # Збірка всього
        letter = (
            f"{sender_block}\n"
            f"{recipient_block}\n"
            f"{date_line}\n\n"
            f"{betreff}\n\n"
            f"{salutation}\n\n"
            f"{body}\n"
            f"{closing}"
            f"{signature}"
        )
        
        return letter
    
    def generate_salutation(self, contact: Dict) -> str:
        """
        Згенерувати правильне звертання.
        
        Args:
            contact: Dict з extract_contact_person()
            
        Returns:
            Рядок зі звертанням
        """
        if not contact:
            return "Sehr geehrte Damen und Herren,"
        
        if contact.get('gender') == 'female':
            if contact.get('title'):
                return f"Sehr geehrte Frau {contact['title']} {contact['lastname']},"
            else:
                return f"Sehr geehrte Frau {contact['lastname']},"
        
        elif contact.get('gender') == 'male':
            if contact.get('title'):
                return f"Sehr geehrter Herr {contact['title']} {contact['lastname']},"
            else:
                return f"Sehr geehrter Herr {contact['lastname']},"
        
        return "Sehr geehrte Damen und Herren,"
    
    def generate_betreff(self, response_type: str, date: str, ref_number: str = '') -> str:
        """
        Згенерувати тему листа.
        
        Args:
            response_type: Тип відповіді
            date: Дата з листа
            ref_number: Номер справи/клієнта
            
        Returns:
            Рядок з темою
        """
        templates = {
            'jobcenter': f"Ihre Einladung vom {date}",
            'jobcenter_einladung': f"Ihre Einladung vom {date}",
            'jobcenter_bescheid': f"Ihr Bescheid vom {date}",
            'inkasso': f"Ihre Forderung vom {date} - {ref_number}" if ref_number else f"Ihre Forderung vom {date}",
            'vermieter': f"Ihre Mieterhöhung vom {date}",
            'finanzamt': f"Ihr Steuerbescheid vom {date}",
            'gericht': f"Ihre Ladung vom {date}",
            'krankenkasse': f"Ihr Schreiben vom {date}",
            'versicherung': f"Ihre Police vom {date}",
        }
        
        return templates.get(response_type, f"Ihr Schreiben vom {date}")


# ============================================================================
# ГОЛОВНА ФУНКЦІЯ
# ============================================================================

def generate_german_letter(text: str, response_de: str, response_type: str = 'general') -> str:
    """
    Згенерувати німецький лист з автоматичним заповненням.

    Args:
        text: Оригінальний текст листа
        response_de: Відповідь німецькою (з improved_response_generator)
        response_type: Тип відповіді

    Returns:
        Згенерований лист у форматі DIN 5008
    """
    generator = LetterGenerator()
    data = generator.extract_all_data(text)
    letter = generator.generate_letter(data, response_de, response_type)

    return letter


def generate_german_letter_with_fallback(text: str, response_type: str = 'general',
                                         sender_name: str = None) -> str:
    """
    Згенерувати німецький лист з fallback підтримкою.
    
    Спочатку намагається згенерувати повну відповідь,
    якщо не виходить - використовує fallback шаблон.
    
    Args:
        text: Оригінальний текст листа
        response_type: Тип відповіді
        sender_name: Ім'я відправника
        
    Returns:
        Згенерований лист у форматі DIN 5008
    """
    # Перевіряємо чи потрібен fallback
    if should_use_fallback(text):
        # Використовуємо fallback шаблон
        fallback_result = generate_fallback_response(
            text=text,
            org_key=response_type,
            lang='de',
            sender_name=sender_name or '[Ihr Name]'
        )
        return fallback_result['response']
    
    # Спроба згенерувати повну відповідь
    try:
        from improved_response_generator import generate_response_smart_improved
        response_de, _ = generate_response_smart_improved(text, 'de')
        
        # Перевіряємо чи відповідь достатньої довжини
        if len(response_de) < 150:
            raise ValueError("Відповідь занадто коротка")
        
        return generate_german_letter(text, response_de, response_type)
    
    except Exception:
        # Fallback при помилці
        fallback_result = generate_fallback_response(
            text=text,
            org_key=response_type,
            lang='de',
            sender_name=sender_name or '[Ihr Name]'
        )
        return fallback_result['response']


if __name__ == '__main__':
    # Тестування
    test_text = '''Jobcenter Berlin Mitte
Straße der Migration 123
10115 Berlin

Herrn
Oleksandr Shevchenko
Müllerstraße 45, Apt. 12
13351 Berlin

Berlin, 15.02.2026

Einladung zum persönlichen Gespräch

Sehr geehrter Herr Shevchenko,

Termin: Montag, 12.03.2026, um 10:00 Uhr

Mit freundlichen Grüßen
Maria Schmidt
Beraterin'''

    test_response = '''📋 BESTÄTIGUNG DES EMPFANGS DER EINLADUNG

Ich habe Ihre Einladung zum Gespräch erhalten und bestätige meine Teilnahme.

✅ ICH BESTÄTIGE MEINE TEILNAHME:
📅 Datum: 12.03.2026
⏰ Uhrzeit: 10:00'''

    generator = LetterGenerator()
    data = generator.extract_all_data(test_text)
    
    print("📊 ВИТЯГНУТІ ДАНІ:")
    print(f"Відправник: {data['sender']}")
    print(f"Отримувач: {data['recipient']}")
    print(f"Контактна особа: {data['contact_person']}")
    print(f"\n📝 ЗГЕНЕРОВАНИЙ ЛИСТ:")
    print("="*60)
    
    letter = generator.generate_letter(data, test_response, 'jobcenter')
    print(letter)
