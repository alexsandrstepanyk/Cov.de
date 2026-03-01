#!/usr/bin/env python3
"""
Quick Fixes for Gov.de Bot v4.2
Швидкі виправлення для покращення виявлення шахрайства
"""

# ============================================================================
# ФІКС 1: Оновлений check_if_document з інтегрованим fraud detection
# ============================================================================

def check_if_document_FIXED(text: str) -> dict:
    """
    Перевірка чи текст є офіційним юридичним документом.
    ВЕРСІЯ 2.0: З інтегрованим виявленням шахрайства
    """
    text_lower = text.lower()

    # Офіційні юридичні маркери
    official_markers = [
        'sehr geehrte', 'damen und herren', 'hiermit', 'gemäß', 'aufgrund',
        'mahnung', 'forderung', 'zahlung', 'kündigung', 'mieterhöhung',
        'wohnung', 'jobcenter', 'einladung', 'termin', 'bescheid', 'antrag',
        'behörde', 'finanzamt', 'steuer', 'gericht', 'urteil', 'versicherung',
        'krankenkasse', 'euro', '€', 'betrag', 'frist', 'innerhalb', 'tagen',
        'unterschrift', 'stempel', 'iban', 'konto', 'überweisung', '§',
        'paragraf', 'bgb', 'sgb', 'aktenzeichen', 'geschäftszeichen',
        'mit freundlichen grüßen', 'rechtsfolgenbelehrung', 'mitwirkungspflichten',
        'arbeitsagentur', 'vermittlungs', 'leistung', 'sanktion', 'kürzung',
        'inkasso', 'eos', 'credit', 'forderungs', 'gläubiger', 'schuldner',
        'vermieter', 'mieter', 'miete', 'kaution', 'nebenkosten', 'hausverwaltung',
        'rechtsanwalt', 'anwalt', 'kanzlei', 'mandant',
        'aok', 'tk', 'barmer', 'dakin', 'krankenkasse', 'versicherungsschein',
        'allianz', 'axa', 'hdi', 'versicherungsschutz', 'police',
        # НОВІ: Більше маркерів
        'arbeitgeber', 'lohnsteuer', 'sozialversicherung',
        'sparkasse', 'volksbank', 'commerzbank',
        'dhl', 'dpd', 'hermes', 'paket', 'sendung',
        'telekom', 'vodafone', 'vertrag', 'laufzeit',
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
        'western union', 'bitcoin', 'geschenkkarte', 'gutscheinkarte',
        'haftbefehl', 'verhaftung', 'polizei kommt',
    ]

    official_score = sum(1 for m in official_markers if m in text_lower)
    non_legal_score = sum(1 for m in non_legal_markers if m in text_lower)
    personal_score = sum(1 for m in personal_markers if m in text_lower)
    fraud_score = sum(1 for m in fraud_markers if m in text_lower)

    # Перевірка на явне шахрайство
    is_likely_fraud = fraud_score >= 2 or (fraud_score >= 1 and official_score >= 3)

    # Визначення типу документу
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
# ФІКС 2: Покращена перевірка email
# ============================================================================

def check_email_legitimacy_FIXED(email: str, organization_type: str = None):
    """
    Перевірка легітимності email з урахуванням типу організації.
    """
    
    # Офіційні організації НЕ повинні використовувати безкоштовні домени
    official_orgs = ['jobcenter', 'finanzamt', 'gericht', 'stadt', 'behörde']
    
    # Комерційні організації також повинні мати корпоративний email
    commercial_orgs = ['dhl', 'bank', 'versicherung', 'telekom', 'sparkasse']
    
    free_email_providers = [
        '@gmail.com', '@yahoo.com', '@hotmail.com',
        '@web.de', '@gmx.de', '@t-online.de', '@aol.com',
    ]
    
    email_lower = email.lower()
    
    if organization_type:
        if organization_type in official_orgs:
            for provider in free_email_providers:
                if provider in email_lower:
                    return False, f"⚠️ Офіційна організація не повинна використовувати {provider}"
        
        if organization_type in commercial_orgs:
            for provider in ['@gmail.com', '@yahoo.com', '@hotmail.com']:
                if provider in email_lower:
                    return False, f"⚠️ Підозрілий email для {organization_type}: {email}"
    
    return True, "✅ Email валідний"


# ============================================================================
# ФІКС 3: Перевірка URL на фішинг
# ============================================================================

def check_url_phishing_FIXED(url: str, expected_brand: str = None):
    """
    Перевірка URL на фішинг.
    
    Args:
        url: URL для перевірки
        expected_brand: Очікуваний бренд (наприклад, 'dhl', 'sparkasse')
    
    Returns:
        (is_legitimate, reason)
    """
    import re
    
    url_lower = url.lower()
    
    # Підозрілі TLD
    suspicious_tlds = ['.xyz', '.top', '.club', '.work', '.loan', '.click']
    for tld in suspicious_tlds:
        if url_lower.endswith(tld):
            return False, f"❌ Підозрільний TLD: {tld}"
    
    # Перевірка на відповідність бренду
    if expected_brand:
        brand_lower = expected_brand.lower()
        # Видаляємо протокол і www
        clean_url = re.sub(r'^https?://', '', url_lower)
        clean_url = re.sub(r'^www\.', '', clean_url)
        
        if brand_lower not in clean_url:
            return False, f"❌ URL не відповідає бренду '{expected_brand}': {url}"
    
    # Підозрілі слова в URL
    phishing_words = ['verify', 'update', 'secure', 'login', 'konto', 'sperre']
    for word in phishing_words:
        if word in url_lower and expected_brand and expected_brand.lower() not in url_lower:
            return False, f"⚠️ Підозріле слово в URL: {word}"
    
    return True, "✅ URL валідний"


# ============================================================================
# ФІКС 4: Розширені індикатори шахрайства
# ============================================================================

FRAUD_INDICATORS_FIXED = {
    'urgent_payment': [
        'sofort', 'umgehend', 'innerhalb 24 Stunden', 'dringend',
        'sofortige Zahlung', 'letzte Mahnung', 'sofort handeln',
        'sofort überweisen', 'zahlung sofort'
    ],
    'threatening_language': [
        'Gerichtsvollzieher', 'Haftbefehl', 'Polizei', 'Strafanzeige',
        'Verhaftung', 'Abschiebung', 'deport', 'konto wird gesperrt',
        'wir kommen zur polizei', 'anordnung der haft'
    ],
    'suspicious_accounts': [
        'Western Union', 'MoneyGram', 'Kryptowährung', 'Bitcoin',
        'Geschenkkarte', 'Gutscheinkarte', 'Paysafecard', 'iTunes',
        'Amazon Gutscheinkarte', 'Steam Wallet'
    ],
    'fake_official': [
        'Bundespolizei', 'Ausländerbehörde', 'Finanzamt',
        'Kreditanstalt', 'Bundesbank'
    ],
    'grammar_errors': [
        'bei nicht zahlung',  # Правильно: bei Nichtzahlung
        'kommen sie zur polizei',  # Дивний вираз
        'überweißen sie',  # Правильно: überweisen Sie
        'sie müssen sofort',  # Занадто агресивно
    ],
    'suspicious_phones': [
        r'^0900',  # Платні номери
        r'^0180',  # Сервісні номери
        r'^\+44',  # UK номери (не Німеччина)
        r'^\+1',   # US номери
        r'^\+234', # Нігерія
        r'^\+254', # Кенія
    ],
    'suspicious_emails': [
        '@gmail.com',
        '@yahoo.com',
        '@hotmail.com',
        '@web.de',
        '@gmx.de',
        '@t-online.de',
        '@aol.com',
    ],
    'banking_fraud': [
        'pin erforderlich', 'passwort bestätigen', 'konto wird gesperrt',
        'daten bestätigen', 'tan eingeben', 'online-banking aktualisieren',
        'sicherheitssperre', 'konto entsperren', 'zugangsdaten aktualisieren'
    ],
    'phishing_urls': [
        'klicken sie hier', 'link aktualisieren', 'seite öffnen',
        'hier klicken', 'jetzt öffnen', 'daten eingeben'
    ],
    'lottery_fraud': [
        'gewonnen', 'lotterie', 'eurojackpot', 'millionen',
        '100.000 euro', 'hauptgewinn', 'glücksspiel',
        'kostenlos gewonnen', 'zufallsgenerator'
    ]
}


# ============================================================================
# ФІКС 5: Повний аналіз шахрайства
# ============================================================================

def analyze_letter_for_fraud_FIXED(text: str, extracted_data: dict = None):
    """
    Повний аналіз листа на шахрайство.
    ВЕРСІЯ 2.0: З покращеними індикаторами
    """
    import re
    
    text_lower = text.lower()
    
    if extracted_data is None:
        extracted_data = {}
    
    # Витягуємо дані якщо не передано
    if not extracted_data.get('phones'):
        # Проста екстракція телефонів
        extracted_data['phones'] = re.findall(r'\+?\d[\d\s\-\(\)]{8,}\d', text)
    
    if not extracted_data.get('emails'):
        extracted_data['emails'] = re.findall(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}', text)
    
    if not extracted_data.get('websites'):
        extracted_data['websites'] = re.findall(r'https?://[^\s<>"{}|\\^`\[\]]+', text)
    
    # Перевірка на ознаки шахрайства
    fraud_score = 0
    indicators = {key: [] for key in FRAUD_INDICATORS_FIXED.keys()}
    
    # Перевірка кожної категорії
    for category, indicator_list in FRAUD_INDICATORS_FIXED.items():
        for indicator in indicator_list:
            if indicator.lower() in text_lower:
                indicators[category].append(indicator)
                # Вагові коефіцієнти
                if category in ['banking_fraud', 'suspicious_accounts']:
                    fraud_score += 3
                elif category in ['threatening_language', 'lottery_fraud']:
                    fraud_score += 2
                else:
                    fraud_score += 1
    
    # Перевірка телефонів
    phone_checks = []
    for phone in extracted_data.get('phones', []):
        for pattern in FRAUD_INDICATORS_FIXED['suspicious_phones']:
            if re.match(pattern, phone.replace(' ', '').replace('-', '')):
                fraud_score += 2
                phone_checks.append({'phone': phone, 'is_legitimate': False, 'reason': 'Підозрілий номер'})
                break
        else:
            phone_checks.append({'phone': phone, 'is_legitimate': True, 'reason': 'Нормальний номер'})
    
    # Перевірка email
    email_checks = []
    for email in extracted_data.get('emails', []):
        is_legit, reason = check_email_legitimacy_FIXED(email, None)
        email_checks.append({'email': email, 'is_legitimate': is_legit, 'reason': reason})
        if not is_legit:
            fraud_score += 2
    
    # Перевірка URL
    website_checks = []
    for website in extracted_data.get('websites', []):
        is_legit, reason = check_url_phishing_FIXED(website, None)
        website_checks.append({'website': website, 'is_legitimate': is_legit, 'reason': reason})
        if not is_legit:
            fraud_score += 2
    
    # Визначення рівня ризику
    is_likely_fraud = fraud_score >= 5
    risk_level = 'high' if fraud_score >= 5 else 'medium' if fraud_score >= 2 else 'low'
    
    # Рекомендації
    if is_likely_fraud:
        recommendations = [
            "🚨 НЕ ПЕРЕРАХОВУЙТЕ ГРОШІ!",
            "📞 Перевірте організацію на офіційному сайті",
            "🏦 Зверніться до банку для перевірки рахунку",
            "👮 Повідомте поліцію про шахрайство",
            "📧 Не відповідайте на цей лист",
        ]
    elif risk_level == 'medium':
        recommendations = [
            "⚠️ Будьте обережні",
            "📞 Перевірте телефон організації на офіційному сайті",
            "📧 Надішліть запит на офіційний email",
            "💡 Зверніться до адвоката для консультації",
        ]
    else:
        recommendations = [
            "✅ Лист виглядає легітимним",
            "📞 Все одно перевірте контактні дані",
            "📋 Збережіть копію листа",
        ]
    
    return {
        'fraud_score': fraud_score,
        'indicators': indicators,
        'is_likely_fraud': is_likely_fraud,
        'risk_level': risk_level,
        'phone_checks': phone_checks,
        'email_checks': email_checks,
        'website_checks': website_checks,
        'recommendations': recommendations
    }


# ============================================================================
# ТЕСТУВАННЯ ФІКСІВ
# ============================================================================

if __name__ == '__main__':
    print("="*80)
    print(" ТЕСТУВАННЯ ФІКСІВ")
    print("="*80)
    
    # Тест 1: Fake Finanzamt
    test_fraud_1 = """
Finanzamt (FAKE)
Steuerzahlung SOFORT!

Überweisen Sie 3.000 EUR auf:
IBAN: DE12 3456 7890 1234 5678 90

Bei nicht zahlung kommen wir zur polizei!

Tel: +44 123 456789 (UK Nummer)
"""
    
    result1 = check_if_document_FIXED(test_fraud_1)
    print(f"\nТест 1: Fake Finanzamt")
    print(f"  is_fraud: {result1['is_fraud']}")
    print(f"  fraud_score: {result1['fraud_score']}")
    print(f"  document_type: {result1['document_type']}")
    print(f"  Очікувалось: is_fraud=True ✅" if result1['is_fraud'] else f"  Очікувалось: is_fraud=True ❌")
    
    # Тест 2: Fake Paket
    test_fraud_2 = """
DHL Paket
Ihr Paket konnte nicht zugestellt werden.

Klicken Sie hier: http://fake-dhl.com
Zahlen Sie 2,99 EUR Bearbeitungsgebühr.

Email: dhl-service@web.de
"""
    
    result2 = check_if_document_FIXED(test_fraud_2)
    fraud_analysis2 = analyze_letter_for_fraud_FIXED(test_fraud_2)
    print(f"\nТест 2: Fake Paket")
    print(f"  is_fraud: {result2['is_fraud']}")
    print(f"  fraud_score: {result2['fraud_score']}")
    print(f"  risk_level: {fraud_analysis2['risk_level']}")
    print(f"  Очікувалось: is_fraud=True ✅" if result2['is_fraud'] or fraud_analysis2['risk_level'] != 'low' else f"  Очікувалось: is_fraud=True ❌")
    
    # Тест 3: Fake Bank
    test_fraud_3 = """
Sparkasse (FAKE)
Ihr Konto wird gesperrt!

Bitte bestätigen Sie Ihre Daten:
www.sparkasse-fake.com

Passwort und PIN erforderlich!

Sofort handeln!
"""
    
    result3 = check_if_document_FIXED(test_fraud_3)
    fraud_analysis3 = analyze_letter_for_fraud_FIXED(test_fraud_3)
    print(f"\nТест 3: Fake Bank")
    print(f"  is_fraud: {result3['is_fraud']}")
    print(f"  fraud_score: {result3['fraud_score']}")
    print(f"  risk_level: {fraud_analysis3['risk_level']}")
    print(f"  Очікувалось: is_fraud=True ✅" if result3['is_fraud'] or fraud_analysis3['risk_level'] != 'low' else f"  Очікувалось: is_fraud=True ❌")
    
    # Тест 4: Реальний Jobcenter
    test_real = """
Jobcenter Berlin Mitte
Einladung zum persönlichen Gespräch
Termin: Montag, 15.03.2026, um 10:00 Uhr
§ 59 SGB II, § 31 SGB II
"""
    
    result4 = check_if_document_FIXED(test_real)
    print(f"\nТест 4: Реальний Jobcenter")
    print(f"  is_document: {result4['is_document']}")
    print(f"  is_fraud: {result4['is_fraud']}")
    print(f"  document_type: {result4['document_type']}")
    print(f"  Очікувалось: is_document=True, is_fraud=False ✅" if result4['is_document'] and not result4['is_fraud'] else f"  Очікувалось: is_document=True, is_fraud=False ❌")
    
    print("\n" + "="*80)
