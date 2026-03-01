#!/usr/bin/env python3
"""
Client Bot v4.0 - Повна Інтеграція
Всі функції для client_bot.py
"""

import re
import logging
from typing import Dict, List

logger = logging.getLogger('client_bot')


# ============================================================================
# 1. ПЕРЕВІРКА ЧИ ЦЕ ОФІЦІЙНИЙ ДОКУМЕНТ
# ============================================================================

def check_if_document(text: str) -> Dict:
    """
    Перевірка чи текст є офіційним юридичним документом.
    ВЕРСІЯ 2.0: З інтегрованим виявленням шахрайства
    """
    text_lower = text.lower()

    # Офіційні юридичні маркери (РОЗШИРЕНО)
    official_markers = [
        'sehr geehrte', 'damen und herren', 'hiermit', 'gemäß', 'aufgrund',
        'mahnung', 'forderung', 'zahlung', 'kündigung', 'mieterhöhung',
        'wohnung', 'jobcenter', 'einladung', 'termin', 'bescheid', 'antrag',
        'behörde', 'finanzamt', 'steuer', 'gericht', 'urteil', 'versicherung',
        'krankenkasse', 'euro', '€', 'betrag', 'frist', 'innerhalb', 'tagen',
        'unterschrift', 'stempel', 'iban', 'konto', 'überweisung', '§',
        'paragraf', 'bgb', 'sgb', 'aktenzeichen', 'geschäftszeichen',
        'mit freundlichen grüßen', 'rechtsfolgenbelehrung', 'mitwirkungspflichten',
        # Додаткові маркери
        'arbeitsagentur', 'vermittlungs', 'leistung', 'sanktion', 'kürzung',
        'inkasso', 'eos', 'credit', 'forderungs', 'gläubiger', 'schuldner',
        'vermieter', 'mieter', 'miete', 'kaution', 'nebenkosten', 'hausverwaltung',
        'rechtsanwalt', 'anwalt', 'kanzlei', 'mandant',
        'aok', 'tk', 'barmer', 'dakin', 'krankenkasse', 'versicherungsschein',
        'allianz', 'axa', 'hdi', 'versicherungsschutz',
        # НОВІ: Більше маркерів для кращої класифікації
        'arbeitgeber', 'lohnsteuer', 'sozialversicherung', 'minijob',
        'sparkasse', 'volksbank', 'commerzbank', 'girokonto',
        'dhl', 'dpd', 'hermes', 'gls', 'paket', 'sendung', 'sendungsnummer',
        'telekom', 'vodafone', 'o2', 'vertrag', 'laufzeit',
        # ПОЛІЦІЯ ТА ПРАВООХОРОННІ ОРГАНИ
        'polizei', 'staatsanwaltschaft', 'kriminalpolizei', 'bundespolizei',
        'landeskriminalamt', 'mordkommission', 'verkehrsunfall', 'strafanzeige',
        'haftbefehl', 'durchsuchungsbeschluss', 'vorladung', 'zeuge', 'beschuldigter',
        'strafgesetzbuch', 'strafprozessordnung', 'ordnungswidrigkeitengesetz'
    ]

    # Не-юридичні документи
    non_legal_markers = [
        'service', 'werkstatt', 'ölwechsel', 'inspektion', 'reparatur',
        'kilometerstand', 'tüv', 'hauptuntersuchung', 'fahrzeug', 'auto',
        'motor', 'getriebe', 'bremsen', 'reifen', 'batterie', 'filter',
        'scheckheft', 'serviceheft', 'garantie', 'werkstatthandbuch',
        'bedienungsanleitung', 'gebrauchsanweisung', 'produktbeschreibung',
        'like', 'share', 'subscribe', 'click', 'link in bio', 'lol', 'rofl',
        'sale', 'discount', 'offer', 'buy now', 'limited', 'special',
        'follow', 'follower', 'promo', 'coupon'
    ]

    # Особисті маркери
    personal_markers = [
        'familie', 'geburtstag', 'feier', 'urlaub', 'ferien', 'reise',
        'essen', 'restaurant', 'cafe', 'selfie', 'foto', 'bild', 'schön',
        'toll', 'super', 'liebe', 'grüße', 'kuss'
    ]

    # НОВІ: Маркери шахрайства
    fraud_markers = [
        'sofort überweisen', 'sofort handeln', 'sofortige Zahlung',
        'konto wird gesperrt', 'pin erforderlich', 'passwort bestätigen',
        'gewonnen', 'lotterie', '100.000 euro', 'kostenlos',
        'klicken sie hier', 'link aktualisieren',
        'western union', 'bitcoin', 'geschenkkarte', 'gutscheinkarte', 'paysafecard',
        'haftbefehl wird beantragt', 'polizei kommt zu ihnen', 'zur polizei kommen',
        'dhl paket', 'paket konnte nicht zugestellt werden',
        'sparkasse fake', 'konto entsperren',
        'bundespolizei fake', 'finanzamt fake',
    ]

    official_score = sum(1 for m in official_markers if m in text_lower)
    non_legal_score = sum(1 for m in non_legal_markers if m in text_lower)
    personal_score = sum(1 for m in personal_markers if m in text_lower)
    fraud_score = sum(1 for m in fraud_markers if m in text_lower)
    
    # Бонус для довгих документів (>3000 символів)
    length_bonus = 2 if len(text) > 3000 else 0
    official_score += length_bonus

    # Перевірка на явне шахрайство
    is_likely_fraud = fraud_score >= 2 or (fraud_score >= 1 and official_score >= 5)

    # Визначення типу документу (з пріоритетом fraud)
    if is_likely_fraud:
        document_type = 'fraud'
        is_legal_document = False
    elif official_score >= 3 and non_legal_score < 2:
        document_type = 'legal_letter'
        is_legal_document = True
    elif non_legal_score >= 3:
        document_type = 'service_document'
        is_legal_document = False
    elif personal_score > 2 and official_score < 2:
        document_type = 'personal'
        is_legal_document = False
    elif len(text) < 50 or (personal_score > official_score):
        document_type = 'image'
        is_legal_document = False
    else:
        document_type = 'unknown'
        is_legal_document = False

    return {
        'is_document': is_legal_document,
        'is_legal_letter': is_legal_document,
        'is_service_document': not is_legal_document and non_legal_score >= 3,
        'is_receipt': 'rechnung' in text_lower or 'quittung' in text_lower or 'bon' in text_lower,
        'is_image': len(text) < 50 or (personal_score > official_score),
        'is_banner': non_legal_score > 5 and official_score == 0,
        'is_meme': non_legal_score > 2 and official_score == 0,
        'is_personal': personal_score > 2 and official_score < 2,
        'is_fraud': is_likely_fraud,
        'document_type': document_type,
        'official_score': official_score,
        'non_legal_score': non_legal_score,
        'personal_score': personal_score,
        'fraud_score': fraud_score,
        'text_length': len(text)
    }


# ============================================================================
# 2. ОТРИМАННЯ ОПИСУ ПАРАГРАФУ
# ============================================================================

def get_paragraph_description(paragraph: str, lang: str = 'uk') -> str:
    """Отримати опис параграфу."""
    descriptions = {
        'BGB § 241': {
            'uk': 'Обов\'язки зі зобов\'язання: Кожна сторона зобов\'язана виконувати умови договору',
            'de': 'Pflichten aus dem Schuldverhältnis: Jede Partei ist zur Erfüllung der Vertragsbedingungen verpflichtet',
            'ru': 'Обязанности из обязательства'
        },
        'BGB § 286': {
            'uk': 'Прострочення боржника: Боржник перебуває у простроченні після отримання письмового нагадування',
            'de': 'Verzug des Schuldners: Der Schuldner gerät nach Erhalt einer Mahnung in Verzug',
            'ru': 'Просрочка должника'
        },
        'BGB § 288': {
            'uk': 'Проценти у простроченні: 5% річних для споживачів',
            'de': 'Verzugszinsen: 5% p.a. für Verbraucher',
            'ru': 'Проценты в просрочке'
        },
        'BGB § 194': {
            'uk': 'Строк позовної давності: Загальний строк становить 3 роки',
            'de': 'Verjährungsfrist: Die regelmäßige Verjährungsfrist beträgt 3 Jahre',
            'ru': 'Срок исковой давности'
        },
        'BGB § 535': {
            'uk': 'Обов\'язки орендодавця: Утримувати житло в придатному стані',
            'de': 'Pflichten des Vermieters: Erhaltung der Wohnung in geeignetem Zustand',
            'ru': 'Обязанности арендодателя'
        },
        'BGB § 558': {
            'uk': 'Підвищення оренди: До місцевої порівняльної оренди, макс. 20% за 3 роки',
            'de': 'Mieterhöhung: Bis zur ortsüblichen Vergleichsmiete, max. 20% in 3 Jahren',
            'ru': 'Повышение аренды'
        },
        'BGB § 543': {
            'uk': 'Позачергове розірвання: Можливе при несплаті 2+ місяців',
            'de': 'Außerordentliche Kündigung: Möglich bei 2+ Monaten Nichtzahlung',
            'ru': 'Внесрочное расторжение'
        },
        'BGB § 573': {
            'uk': 'Розірвання орендодавцем: Тільки за обґрунтованих причин',
            'de': 'Kündigung durch den Vermieter: Nur aus berechtigten Gründen',
            'ru': 'Расторжение арендодателем'
        },
        '§ 59 SGB II': {
            'uk': 'Обов\'язок явки: Зобов\'язані з\'являтися на всі запрошення Jobcenter',
            'de': 'Meldepflicht: Müssen zu allen Einladungen des Jobcenters erscheinen',
            'ru': 'Обязанность явки'
        },
        '§ 31 SGB II': {
            'uk': 'Наслідки неявки: Зменшення виплат на 30% протягом 12 тижнів',
            'de': 'Leistungskürzung um 30% für 12 Wochen bei unentschuldigtem Fehlen',
            'ru': 'Уменьшение выплат на 30%'
        },
        '§ 32 SGB II': {
            'uk': 'Повне припинення виплат: При повторному порушенні',
            'de': 'Vollständige Einstellung der Leistung bei Wiederholung',
            'ru': 'Полное прекращение выплат'
        },
        '§ 309 SGB III': {
            'uk': 'Офіційні запрошення: Обов\'язкові документи від біржі праці',
            'de': 'Offizielle Einladungen: Pflichtdokumente der Arbeitsagentur',
            'ru': 'Официальные приглашения'
        },
        'VwVfG § 35': {
            'uk': 'Адміністративний акт: Повинен бути письмовим',
            'de': 'Verwaltungsakt: Muss schriftlich sein',
            'ru': 'Административный акт'
        },
        'VwGO § 42': {
            'uk': 'Право на оскарження: Можна оскаржити рішення',
            'de': 'Klagerecht: Kann angefochten werden',
            'ru': 'Право на обжалование'
        }
    }

    para_key = paragraph.split(' (')[0] if ' (' in paragraph else paragraph
    if para_key in descriptions:
        return descriptions[para_key].get(lang, descriptions[para_key]['uk'])
    return f"[{para_key}]"


# ============================================================================
# 3. СТВОРЕННЯ ПРОСТОГО АНАЛІЗУ З ЗАКОНАМИ ТА НАСЛІДКАМИ
# ============================================================================

def create_simple_analysis(text: str, law_info: Dict, lang: str) -> str:
    """Створення швидкого аналізу з законами та наслідками."""
    import re
    
    analysis = ""
    text_lower = text.lower()
    
    # Заголовки
    titles = {
        'uk': {
            'found': "✅ ЗНАЙДЕНО В ЛИСТІ",
            'laws': "📚 ЗАСТОСОВНІ ЗАКОНИ",
            'consequences': "⚠️ НАСЛІДКИ НЕВИКОНАННЯ",
            'de': "🇩🇪 DEUTSCHE VERSION"
        },
        'ru': {
            'found': "✅ НАЙДЕНО В ПИСЬМЕ",
            'laws': "📚 ПРИМЕНИМЫЕ ЗАКОНЫ",
            'consequences': "⚠️ ПОСЛЕДСТВИЯ НЕВЫПОЛНЕНИЯ",
            'de': "🇩🇪 DEUTSCHE VERSION"
        },
        'de': {
            'found': "✅ GEFUNDEN IM BRIEF",
            'laws': "📚 ANWENDBARE GESETZE",
            'consequences': "⚠️ FOLGEN BEI NICHTBEACHTUNG",
            'de': "🇩🇪 DEUTSCHE VERSION"
        }
    }
    
    t = titles.get(lang, titles['uk'])
    
    # 1. Знайдені елементи
    analysis += f"{t['found']}:\n\n"
    
    # Грошові суми
    money = re.findall(r'(\d+[,\.\s]?\d*)\s*(euro|EUR|€)', text_lower)
    for amount, _ in money[:3]:
        analysis += f"  💰 **Сума:** {amount} EUR\n"
    
    # Дати
    dates = re.findall(r'(\d{1,2}\.\s*\d{1,2}\.\s*\d{2,4})', text)
    for date in dates[:3]:
        analysis += f"  📅 **Дата:** {date}\n"
    
    # Час
    times = re.findall(r'(\d{1,2}:\d{2})', text)
    for time in times[:2]:
        analysis += f"  ⏰ **Час:** {time}\n"
    
    # Терміни
    if '7 tagen' in text_lower:
        analysis += f"  ⏳ **Термін:** 7 днів\n"
    elif '14 tagen' in text_lower:
        analysis += f"  ⏳ **Термін:** 14 днів\n"
    
    analysis += "\n"
    
    # 2. Закони
    analysis += f"{t['laws']}:\n\n"
    
    paragraphs = law_info.get('paragraphs', [])
    for para in paragraphs[:5]:
        para_desc = get_paragraph_description(para, lang)
        analysis += f"  📖 **{para}**\n"
        analysis += f"     _{para_desc}_\n\n"
    
    # 3. Наслідки
    consequences = law_info.get('consequences', '')
    if not consequences:
        org = law_info.get('organization', '').lower()
        if 'jobcenter' in org or 'arbeitsagentur' in org:
            consequences = (
                "⚠️ **При неявці без поважної причини:**\n"
                "• Зменшення виплат на 30% протягом 12 тижнів (§ 31 SGB II)\n"
                "• Повне припинення виплат при повторному порушенні (§ 32 SGB II)\n"
                "• Хворобу потрібно підтвердити лікарською довідкою протягом 3 днів\n"
                "• Запрошення є офіційним обов'язковим документом (§ 309 SGB III)"
            )
        elif 'inkasso' in org or 'forderung' in org:
            consequences = (
                "⚠️ **При несплаті боргу:**\n"
                "• Нараховується пеня 5% річних (§ 288 BGB)\n"
                "• Можливі судові витрати (Gerichtskosten)\n"
                "• Примусове стягнення через судового виконавця (Gerichtsvollzieher)\n"
                "• Від'ємна кредитна історія (Schufa)"
            )
        elif 'vermieter' in org or 'miete' in org:
            consequences = (
                "⚠️ **При порушенні умов оренди:**\n"
                "• Можливе підвищення оренди до 20% за 3 роки (§ 558 BGB)\n"
                "• При несплаті 2+ місяців — виселення (§ 543 BGB)\n"
                "• Орендодавець може розірвати договір (§ 573 BGB)"
            )
        else:
            consequences = (
                "📋 **Наслідки залежать від типу листа.**\n"
                "Рекомендується звернутися до фахівця.\n\n"
                "📞 **Безкоштовна правова допомога:**\n"
                "• Telefonseelsorge: 0800 111 0 111"
            )
    
    analysis += f"{t['consequences']}:\n\n{consequences}\n\n"
    
    # 4. Німецька версія
    analysis += f"\n━━━━━━━━━━━━━━━━━━━━\n\n"
    analysis += f"{t['de']}:\n\n"
    
    org = law_info.get('organization', 'N/A')
    situation = law_info.get('situation', 'N/A')
    
    analysis += f"🏢 **Organisation:** {org}\n"
    analysis += f"📋 **Situation:** {situation}\n\n"
    analysis += f"{t['laws']}:\n\n"
    
    for para in paragraphs[:5]:
        para_desc = get_paragraph_description(para, 'de')
        analysis += f"  📖 **{para}**\n"
        analysis += f"     _{para_desc}_\n\n"
    
    # Німецькі наслідки
    analysis += f"\n{t['consequences']}:\n\n"
    if 'jobcenter' in org.lower():
        analysis += (
            "⚠️ **Bei Nichtteilnahme:**\n"
            "• Leistungskürzung um 30% für 12 Wochen (§ 31 SGB II)\n"
            "• Vollständige Einstellung bei Wiederholung (§ 32 SGB II)\n"
            "• Krankheit muss innerhalb von 3 Tagen attestiert werden"
        )
    elif 'inkasso' in org.lower():
        analysis += (
            "⚠️ **Bei Nichtzahlung:**\n"
            "• Säumniszuschlag 5% p.a. (§ 288 BGB)\n"
            "• Gerichtskosten möglich\n"
            "• Zwangsvollstreckung durch Gerichtsvollzieher"
        )
    else:
        analysis += "📋 Folgen hängen vom Brieftyp ab."
    
    return analysis


# ============================================================================
# 4. ГЕНЕРАЦІЯ РОЗГОРНУТОЇ ВІДПОВІДІ З ЗАКОНАМИ
# ============================================================================

def generate_detailed_response(text: str, law_info: Dict, lang: str) -> str:
    """Генерація розгорнутої відповіді з посиланнями на закони."""
    
    org = law_info.get('organization', '').lower()
    situation = law_info.get('situation', '').lower()
    
    # Jobcenter запрошення
    if 'jobcenter' in org or 'arbeitsagentur' in org:
        if lang == 'uk':
            return f'''Шановний(а) одержувач(у),

📋 **Підтвердження отримання запрошення**

Я отримав(ла) ваше запрошення на співбесіду та підтверджую свою участь.

📅 **Деталі зустрічі:**
• Дата: [вкажіть дату з листа]
• Час: [вкажіть час з листа]
• Місце: Jobcenter [назва]

⚖️ **ПРАВОВЕ ПІДҐРУНТЯ:**

Згідно з **§ 59 SGB II** (Обов'язок явки):
• Отримувачі допомоги зобов'язані з'являтися на всі запрошення Jobcenter

Згідно з **§ 309 SGB III** (Офіційні запрошення):
• Запрошення біржі праці є офіційними обов'язковими документами

⚠️ **Усвідомлюю наслідки:**
• При неявці виплати можуть бути зменшені на 30% (§ 31 SGB II)
• При повторному порушенні виплати можуть бути повністю припинені (§ 32 SGB II)

📎 **Документи які візьму з собою:**
• Посвідчення особи або паспорт
• Актуальне свідоцтво про реєстрацію
• Оновлене резюме (CV)

З повагою,
[Ваше ім'я]
[Номер клієнта]'''
        
        elif lang == 'de':
            return f'''Sehr geehrte Damen und Herren,

📋 **Bestätigung des Eingangs der Einladung**

Ich habe Ihre Einladung zum Gespräch erhalten und bestätige meine Teilnahme.

📅 **Termindetails:**
• Datum: [Datum aus dem Brief]
• Uhrzeit: [Uhrzeit aus dem Brief]
• Ort: Jobcenter [Name]

⚖️ **RECHTSGRUNDLAGE:**

Gemäß **§ 59 SGB II** (Meldepflicht):
• Leistungsempfänger müssen zu allen Jobcenter-Einladungen erscheinen

Gemäß **§ 309 SGB III** (Offizielle Einladungen):
• Einladungen der Arbeitsagentur sind offizielle Pflichtdokumente

⚠️ **Ich bin mir der Folgen bewusst:**
• Bei Nichtteilnahme kann die Leistung um 30% gekürzt werden (§ 31 SGB II)
• Bei Wiederholung kann die Leistung vollständig eingestellt werden (§ 32 SGB II)

📎 **Mitgebrachte Unterlagen:**
• Personalausweis oder Reisepass
• Aktuelle Meldebescheinigung
• Aktualisierter Lebenslauf (CV)

Mit freundlichen Grüßen
[Ihr Name]
[Kundennummer]'''
    
    # Борговий лист (Inkasso)
    elif 'inkasso' in org or 'forderung' in situation or 'mahnung' in situation:
        if lang == 'uk':
            return f'''Шановний(а) одержувач(у),

📋 **Щодо вашої вимоги сплати боргу № {law_info.get("reference", "N/A")}**

Я отримав(ла) ваше повідомлення щодо вимоги сплати боргу в розмірі {law_info.get("amount", "N/A")}.

⚖️ **ПРАВОВЕ ПІДҐРУНТЯ:**

Згідно з **BGB § 286** (Прострочення боржника):
• Боржник перебуває у простроченні тільки після отримання письмового нагадування

Згідно з **BGB § 288** (Проценти у простроченні):
• Для споживачів процентна ставка становить 5% річних

Згідно з **BGB § 194** (Строк позовної давності):
• Загальний строк позовної давності становить 3 роки

📋 **МОЯ ПОЗИЦІЯ:**

[Оберіть відповідний варіант:]
□ Я визнаю борг і пропоную розстрочку на {law_info.get("installment_months", "6")} місяців
□ Я заперечую проти вимоги та вимагаю доказів боргу
□ Я вже сплатив(ла) борг (додаю квитанцію про сплату)

💡 **ПРОПОЗИЦІЯ:**
• Готовий(а) обговорити умови сплати
• Прошу надати детальну розбивку боргу (основна сума, проценти, витрати)
• Прошу призупинити нарахування процентів на час переговорів

⚠️ **ЗАСТЕРЕЖЕННЯ:**
• Будь ласка, утримайтесь від судових кроків до завершення переговорів
• Всі листи надсилайте письмово на мою адресу

З повагою,
[Ваше ім'я]
[Ваша адреса]
[Ваш телефон]
[Ваш email]'''

        elif lang == 'de':
            return f'''Sehr geehrte Damen und Herren,

📋 **Bezüglich Ihrer Forderung Nr. {law_info.get("reference", "N/A")}**

Ich habe Ihre Forderung über {law_info.get("amount", "N/A")} EUR erhalten.

⚖️ **RECHTSGRUNDLAGE:**

Gemäß **BGB § 286** (Verzug des Schuldners):
• Der Schuldner gerät erst nach Erhalt einer schriftlichen Mahnung in Verzug

Gemäß **BGB § 288** (Verzugszinsen):
• Für Verbraucher beträgt der Verzugszinssatz 5% p.a.

Gemäß **BGB § 194** (Verjährungsfrist):
• Die regelmäßige Verjährungsfrist beträgt 3 Jahre

📋 **MEINE POSITION:**

[Bitte wählen Sie eine Option:]
□ Ich erkenne die Forderung an und schlage eine Ratenzahlung vor
□ Ich widerspreche der Forderung und fordere Nachweise
□ Ich habe die Forderung bereits bezahlt (Beleg liegt bei)

💡 **VORSCHLAG:**
• Ich bin bereit, die Zahlungsbedingungen zu verhandeln
• Bitte senden Sie mir eine detaillierte Aufstellung (Hauptforderung, Zinsen, Kosten)
• Bitte setzen Sie die Zinsberechnung während der Verhandlungen aus

⚠️ **HINWEIS:**
• Bitte sehen Sie von gerichtlichen Schritten bis zum Abschluss der Verhandlungen ab
• Bitte senden Sie alle Schreiben schriftlich an meine Adresse

Mit freundlichen Grüßen
[Ihr Name]
[Ihre Adresse]
[Ihr Telefon]
[Ihre E-Mail]'''
    
    # Відповідь для орендодавця (Vermieter/Mieterhöhung)
    elif 'vermieter' in org or 'miete' in situation or 'mieterhöhung' in situation:
        if lang == 'uk':
            return f'''Шановний(а) орендодавче(у),

📋 **Щодо підвищення орендної плати**

Я отримав(ла) ваше повідомлення про підвищення орендної плати з {law_info.get("current_rent", "450,00")} EUR до {law_info.get("new_rent", "550,00")} EUR.

⚖️ **ПРАВОВЕ ПІДҐРУНТЯ:**

Згідно з **BGB § 558** (Підвищення оренди):
• Оренда може бути підвищена до місцевої порівняльної оренди
• Максимальне підвищення: 20% протягом 3 років

Згідно з **BGB § 558 Abs. 3** (Обмеження підвищення):
• Підвищення на {law_info.get("increase_percent", "22,2")}% перевищує допустимий ліміт

📋 **МОЯ ПОЗИЦІЯ:**

□ Я заперечую проти підвищення на {law_info.get("increase_percent", "22,2")}%
□ Прошу надати обґрунтування з Mietspiegel Berlin 2026
□ Готовий(а) обговорити помірне підвищення (до 20%)

💡 **ПРОПОЗИЦІЯ:**
• Прошу зменшити підвищення до 18% ({law_info.get("proposed_rent", "531,00")} EUR)
• Готовий(а) підписати додаткову угоду до орендного договору
• Прошу відкласти підвищення до {law_info.get("proposed_date", "01.06.2026")}

⚠️ **ЗАСТЕРЕЖЕННЯ:**
• Зберігаю за собою право на оскарження у разі незгоди
• Прошу підтвердити отримання цього листа

З повагою,
[Ваше ім'я]
[Ваша адреса]
[Ваш телефон]'''

        elif lang == 'de':
            return f'''Sehr geehrte(r) Vermieter(in),

📋 **Bezüglich der Mieterhöhung**

Ich habe Ihr Schreiben zur Mieterhöhung von {law_info.get("current_rent", "450,00")} EUR auf {law_info.get("new_rent", "550,00")} EUR erhalten.

⚖️ **RECHTSGRUNDLAGE:**

Gemäß **BGB § 558** (Mieterhöhung):
• Die Miete kann bis zur ortsüblichen Vergleichsmiete erhöht werden
• Maximale Erhöhung: 20% innerhalb von 3 Jahren

Gemäß **BGB § 558 Abs. 3** (Begrenzung der Erhöhung):
• Die Erhöhung um {law_info.get("increase_percent", "22,2")}% überschreitet die zulässige Grenze

📋 **MEINE POSITION:**

□ Ich widerspreche der Erhöhung um {law_info.get("increase_percent", "22,2")}%
□ Bitte senden Sie mir eine Begründung aus dem Mietspiegel Berlin 2026
□ Ich bin bereit, eine moderate Erhöhung (bis 20%) zu besprechen

💡 **VORSCHLAG:**
• Bitte reduzieren Sie die Erhöhung auf 18% ({law_info.get("proposed_rent", "531,00")} EUR)
• Ich bin bereit, eine Zusatzvereinbarung zum Mietvertrag zu unterzeichnen
• Bitte verschieben Sie die Erhöhung bis zum {law_info.get("proposed_date", "01.06.2026")}

⚠️ **HINWEIS:**
• Ich behalte mir das Recht auf Widerspruch vor
• Bitte bestätigen Sie den Erhalt dieses Schreibens

Mit freundlichen Grüßen
[Ihr Name]
[Ihre Adresse]
[Ihr Telefon]'''

    # Відповідь за замовчуванням
    else:
        if lang == 'uk':
            response = f'''Шановний(а) одержувач(у),

📋 **Щодо вашого листа**

Я отримав(ла) ваш лист та опрацьовую його.

⚖️ **ЗАСТОСОВНІ ЗАКОНИ:**

'''
            paragraphs = law_info.get('paragraphs', [])
            for para in paragraphs[:3]:
                para_desc = get_paragraph_description(para, 'uk')
                response += f"• **{para}** - {para_desc}\n"

            response += f'''
📋 **НАСТУПНІ КРОКИ:**

Я розгляну ваше повідомлення та надам відповідь найближчим часом.

З повагою,
[Ваше ім'я]'''
            return response
        else:
            return f'''Sehr geehrte Damen und Herren,

📋 **Bezüglich Ihres Schreibens**

Ich habe Ihr Schreiben erhalten und bearbeite es.

⚖️ **ANWENDBARE GESETZE:**

''' + '\n'.join([f"• **{p}**" for p in law_info.get('paragraphs', [])[:3]]) + f'''

📋 **NÄCHSTE SCHRITTE:**

Ich werde Ihr Schreiben prüfen und bald antworten.

Mit freundlichen Grüßen
[Ihr Name]'''


# ============================================================================
# 5. ОБРОБКА БАГАТОСТОРІНКОВИХ ДОКУМЕНТІВ
# ============================================================================

async def handle_multi_page_photo(update, context, file_path: str, chat_id: int) -> tuple:
    """
    Обробка фото для багатосторінкового документу.
    Returns: (page_text, pages_count, success)
    """
    from advanced_ocr import recognize_image
    
    try:
        ocr_result = recognize_image(file_path, lang='deu+eng')
        page_text = ocr_result['text']
        
        if not page_text.strip():
            return None, 0, False
        
        # Зберігаємо фото та текст
        if 'letter_photos' not in context.user_data:
            context.user_data['letter_photos'] = []
            context.user_data['letter_text'] = ''
        
        context.user_data['letter_photos'].append(file_path)
        page_num = len(context.user_data['letter_photos'])
        context.user_data['letter_text'] += f"\n\n--- СТОРІНКА {page_num} ---\n\n{page_text}"
        
        return page_text, page_num, True
        
    except Exception as e:
        return None, 0, False


def get_multi_page_keyboard():
    """Отримати клавіатуру для багатосторінкового режиму."""
    from telegram import ReplyKeyboardMarkup
    keyboard = [['✅ Все, аналізуй'], ['📄 Надіслати ще сторінку']]
    return ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
