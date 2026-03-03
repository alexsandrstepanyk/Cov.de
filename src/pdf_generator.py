#!/usr/bin/env python3
"""
PDF Generator for German Legal Letters v8.4
Генерація PDF-файлів з німецькими відповідями у форматі DIN 5008

Використовує reportlab для створення професійних PDF-документів
"""

import os
from typing import Dict, Optional
from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import cm, inch
    from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageTemplate, Frame
    from reportlab.pdfgen import canvas
    REPORTLAB_AVAILABLE = True
except Exception as e:
    REPORTLAB_AVAILABLE = False
    print(f"⚠️ reportlab недоступний: {e}")
    print("Встановіть: pip3 install reportlab")


class GermanLetterPDFGenerator:
    """
    Генератор PDF-файлів для німецьких юридичних листів.
    
    Форматування згідно DIN 5008:
    - Відправник: 4.5 cm від верху
    - Отримувач: 8 cm від верху
    - Дата: 8 cm від верху, справа
    - Betreff: 10.5 cm від верху
    - Текст: 11.5 cm від верху
    """
    
    def __init__(self, output_dir: str = 'data/pdf_letters'):
        """
        Ініціалізація генератора.
        
        Args:
            output_dir: Директорія для збереження PDF
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        if not REPORTLAB_AVAILABLE:
            raise ImportError("reportlab не встановлено. Встановіть: pip3 install reportlab")
    
    def generate_pdf(self, analysis: Dict, response_text: str, filename: Optional[str] = None) -> str:
        """
        Генерація PDF-файлу з німецькою відповіддю.
        
        Args:
            analysis: Результат аналізу листа
            response_text: Текст німецької відповіді
            filename: Ім'я файлу (за замовчуванням: letter_YYYYMMDD_HHMMSS.pdf)
            
        Returns:
            Шлях до згенерованого PDF
        """
        # Генерація імені файлу
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'letter_{timestamp}.pdf'
        elif not filename.endswith('.pdf'):
            filename += '.pdf'
        
        output_path = self.output_dir / filename
        
        # Отримання даних з аналізу
        recipient_name = analysis.get('recipient_name', 'Oleksandr Shevchenko')
        recipient_address = analysis.get('recipient_address', 'Müllerstraße 45, Apt. 12')
        recipient_city_full = analysis.get('recipient_city', '13351 Berlin')
        recipient_city = recipient_city_full.split()[-1] if recipient_city_full else 'Berlin'
        recipient_zip = recipient_city_full.split()[0] if recipient_city_full else '13351'
        
        sender_name = analysis.get('sender_name', 'Jobcenter Berlin Mitte')
        sender_address = analysis.get('sender_address', 'Straße der Migration 123')
        sender_city_full = analysis.get('sender_city', '10115 Berlin')
        sender_city = sender_city_full.split()[-1] if sender_city_full else 'Berlin'
        sender_zip = sender_city_full.split()[0] if sender_city_full else '10115'
        
        dates = analysis.get('dates', [])
        letter_date = dates[0] if dates else datetime.now().strftime('%d.%m.%Y')
        customer_number = analysis.get('customer_number', '')
        letter_type = analysis.get('letter_type', 'Schreiben')
        
        # Поточна дата
        current_date = datetime.now().strftime('%d.%m.%Y')
        
        # Створення PDF
        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=A4,
            rightMargin=2.5*cm,
            leftMargin=2.5*cm,
            topMargin=4.5*cm,
            bottomMargin=2.5*cm
        )
        
        # Стилі
        styles = getSampleStyleSheet()
        
        # Стиль для відправника (верхній лівий кут)
        sender_style = ParagraphStyle(
            'Sender',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            spaceAfter=0.5*cm
        )
        
        # Стиль для отримувача
        recipient_style = ParagraphStyle(
            'Recipient',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            spaceAfter=0.5*cm
        )
        
        # Стиль для дати
        date_style = ParagraphStyle(
            'Date',
            parent=styles['Normal'],
            fontSize=10,
            leading=12,
            alignment=TA_RIGHT,
            spaceAfter=1*cm
        )
        
        # Стиль для Betreff
        betreff_style = ParagraphStyle(
            'Betreff',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            fontWeight='bold',
            spaceAfter=0.5*cm
        )
        
        # Стиль для тексту
        text_style = ParagraphStyle(
            'Text',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=0.3*cm
        )
        
        # Стиль для підпису
        signature_style = ParagraphStyle(
            'Signature',
            parent=styles['Normal'],
            fontSize=11,
            leading=14,
            spaceAfter=2*cm
        )
        
        # Форматування тексту відповіді
        formatted_lines = []
        for line in response_text.split('\n'):
            if line.strip():
                formatted_lines.append(Paragraph(line, text_style))
            else:
                formatted_lines.append(Spacer(1, 0.3*cm))
        
        # Побудова документу
        story = []
        
        # Відправник
        sender_text = f"{recipient_name}<br/>{recipient_address}<br/>{recipient_zip} {recipient_city}"
        story.append(Paragraph(sender_text, sender_style))
        story.append(Spacer(1, 1*cm))
        
        # Отримувач
        recipient_text = f"{sender_name}<br/>{sender_address}<br/>{sender_zip} {sender_city}"
        story.append(Paragraph(recipient_text, recipient_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Дата
        date_text = f"{recipient_city}, {current_date}"
        story.append(Paragraph(date_text, date_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Betreff
        betreff_text = f"<b>Betreff:</b> {letter_type} vom {letter_date}"
        if customer_number:
            betreff_text += f"<br/><b>Kundennummer:</b> {customer_number}"
        story.append(Paragraph(betreff_text, betreff_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Привітання
        salutation = "Sehr geehrte Damen und Herren,"
        if sender_name:
            last_name = sender_name.split()[-1]
            if last_name.lower() not in ['damen', 'herren', 'mitte']:
                salutation = f"Sehr geehrte Frau/Herr {last_name},"
        story.append(Paragraph(salutation, text_style))
        story.append(Spacer(1, 0.5*cm))
        
        # Текст відповіді
        story.extend(formatted_lines)
        
        # Підпис
        story.append(Spacer(1, 1*cm))
        story.append(Paragraph("Mit freundlichen Grüßen", signature_style))
        story.append(Spacer(1, 1.5*cm))
        story.append(Paragraph(recipient_name, text_style))
        if customer_number:
            story.append(Paragraph(f"Kundennummer: {customer_number}", text_style))
        
        # Додаткова інформація (внизу)
        story.append(Spacer(1, 2*cm))
        
        # Footer
        footer_style = ParagraphStyle(
            'Footer',
            parent=styles['Normal'],
            fontSize=8,
            leading=10,
            textColor=colors.grey
        )
        
        footer_text = f"Erstellt am {datetime.now().strftime('%d.%m.%Y um %H:%M')} | Gov.de Bot v8.4"
        story.append(Paragraph(footer_text, footer_style))
        
        # Генерація PDF
        doc.build(story)
        
        return str(output_path)
    
    def generate_simple_pdf(self, response_text: str, filename: Optional[str] = None) -> str:
        """
        Проста генерація PDF без форматування DIN 5008.
        
        Args:
            response_text: Текст відповіді
            filename: Ім'я файлу
            
        Returns:
            Шлях до згенерованого PDF
        """
        if filename is None:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f'letter_{timestamp}.pdf'
        elif not filename.endswith('.pdf'):
            filename += '.pdf'
        
        output_path = self.output_dir / filename
        
        # Простий PDF
        c = canvas.Canvas(str(output_path), pagesize=A4)
        width, height = A4
        
        # Відступы
        y = height - 2*cm
        x_left = 2.5*cm
        
        # Текст
        c.setFont("Helvetica", 11)
        for line in response_text.split('\n'):
            if y < 2*cm:  # Якщо досягли низу сторінки
                c.showPage()
                y = height - 2*cm
                c.setFont("Helvetica", 11)
            
            if line.strip():
                c.drawString(x_left, y, line[:80])  # Обмеження довжини рядка
                y -= 14
            else:
                y -= 14  # Пустий рядок
        
        c.save()
        
        return str(output_path)


# Глобальний екземпляр
_pdf_generator = None

def get_pdf_generator() -> GermanLetterPDFGenerator:
    """Отримати або створити генератор PDF."""
    global _pdf_generator
    if _pdf_generator is None:
        _pdf_generator = GermanLetterPDFGenerator()
    return _pdf_generator

def generate_letter_pdf(analysis: Dict, response_text: str, filename: Optional[str] = None) -> str:
    """
    Генерація PDF-файлу з німецькою відповіддю.
    
    Args:
        analysis: Результат аналізу листа
        response_text: Текст німецької відповіді
        filename: Ім'я файлу
        
    Returns:
        Шлях до згенерованого PDF
    """
    generator = get_pdf_generator()
    return generator.generate_pdf(analysis, response_text, filename)

def generate_simple_letter_pdf(response_text: str, filename: Optional[str] = None) -> str:
    """
    Проста генерація PDF.
    
    Args:
        response_text: Текст відповіді
        filename: Ім'я файлу
        
    Returns:
        Шлях до згенерованого PDF
    """
    generator = get_pdf_generator()
    return generator.generate_simple_pdf(response_text, filename)


if __name__ == '__main__':
    # Тестування
    print("="*80)
    print("  📄 PDF GENERATOR TEST v8.4")
    print("="*80)
    
    if not REPORTLAB_AVAILABLE:
        print("❌ reportlab не встановлено!")
        print("Встановіть: pip3 install reportlab")
    else:
        print("✅ reportlab встановлено")
        
        # Тестові дані
        test_analysis = {
            'recipient_name': 'Oleksandr Shevchenko',
            'recipient_address': 'Müllerstraße 45, Apt. 12',
            'recipient_city': '13351 Berlin',
            'sender_name': 'Jobcenter Berlin Mitte',
            'sender_address': 'Straße der Migration 123',
            'sender_city': '10115 Berlin',
            'dates': ['15.02.2026'],
            'customer_number': '123ABC456',
            'letter_type': 'Einladung',
        }
        
        test_response = """hiermit bestätige ich den Empfang Ihres Schreibens vom 15.02.2026.

Ich nehme zur Kenntnis:
- § 59 SGB II
- die genannten Fristen und Termine
- die erforderlichen Unterlagen

Ich werde fristgerecht reagieren und die notwendigen Schritte einleiten.

Für Rückfragen stehe ich Ihnen gerne zur Verfügung."""
        
        try:
            # Генерація PDF
            pdf_path = generate_letter_pdf(test_analysis, test_response, 'test_letter.pdf')
            print(f"\n✅ PDF згенеровано: {pdf_path}")
            print(f"📄 Розмір: {os.path.getsize(pdf_path) / 1024:.1f} KB")
        except Exception as e:
            print(f"\n❌ Помилка: {e}")
