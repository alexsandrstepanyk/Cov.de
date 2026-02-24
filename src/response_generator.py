#!/usr/bin/env python3
"""
Response Generator Module
Генерація детальних відповідей німецькою та українською мовами.
"""

from typing import Dict
from googletrans import Translator

translator = Translator()

# Детальні шаблони відповідей
RESPONSE_TEMPLATES = {
    'de': {
        'debt_collection': {
            'uk': {
                'subject': 'Щодо вашого повідомлення про сплату боргу',
                'body': '''Шановний одержувач,

📋 Я отримав ваше повідомлення щодо сплати боргу (ваш посилання: [вставити номер]).

🔍 ІНФОРМАЦІЯ:
• Я не заперечую проти існування боргу / Я заперечую проти суми боргу*
• Прошу надати детальну розбивку суми
• Прошу надати копію договору/рахунку

⚖️ ЗАКОНОДАВСТВО:
Згідно з BGB § 286, боржник перебуває у простроченні тільки після отримання письмового нагадування (Mahnung) з вказанням конкретної суми та строку сплати.

Відповідно до BGB § 288, процентна ставка у простроченні становить 5% річних для споживачів.

💡 МОЯ ПРОПОЗИЦІЯ:
• Сплата частинами: [сума] євро на місяць
• Або: Прошу відстрочку до [дата]

Прошу підтвердити отримання цього листа та надати письмову відповідь протягом 14 днів.

З повагою,
[Ваше ім'я]
[Адреса]
[Контакти]

* - оберіть потрібне''',
                'tips': [
                    '📌 Збережіть копію цього листа',
                    '⏰ Відправте рекомендованим листом (Einschreiben)',
                    '💰 Не ігноруйте листи — це може призвести до суду',
                    '⚖️ При сумі понад €200 можливий судовий процес (Mahnbescheid)'
                ]
            },
            'de': {
                'subject': 'Bezug: Ihre Zahlungsaufforderung',
                'body': '''Sehr geehrte Damen und Herren,

📋 ich beziehe mich auf Ihre Zahlungsaufforderung (Ihr Zeichen: [Nummer einfügen]).

🔍 INFORMATION:
• Ich bestreite die Forderung nicht / Ich bestreite die Höhe der Forderung*
• Bitte senden Sie mir eine detaillierte Aufstellung
• Bitte senden Sie mir eine Kopie des Vertrags/der Rechnung

⚖️ RECHTLICHE GRUNDLAGEN:
Gemäß BGB § 286 kommt der Schuldner erst nach Erhalt einer schriftlichen Mahnung mit konkreter Summe und Frist in Verzug.

Gemäß BGB § 288 beträgt der Verzugszinsatz für Verbraucher 5% p.a.

💡 MEIN VORSCHLAG:
• Ratenzahlung: [Betrag] Euro pro Monat
• Oder: Bitte gewähren Sie mir eine Stundung bis [Datum]

Bitte bestätigen Sie den Erhalt dieses Schreibens und senden Sie mir eine schriftliche Antwort innerhalb von 14 Tagen.

Mit freundlichen Grüßen,
[Ihr Name]
[Adresse]
[Kontakte]

* - Bitte wählen Sie das Zutreffende aus''',
                'tips': [
                    '📌 Bewahren Sie eine Kopie dieses Schreibens auf',
                    '⏰ Senden Sie es per Einschreiben',
                    '💰 Ignorieren Sie keine Mahnungen - dies kann zu Gerichtsverfahren führen',
                    '⚖️ Bei Beträgen über €200 ist ein Mahnbescheid möglich'
                ]
            }
        },
        
        'tenancy': {
            'uk': {
                'subject': 'Щодо вашого повідомлення про оренду',
                'body': '''Шановний орендодавцю / Управління будинком,

📋 Я отримав ваше повідомлення щодо [тема: підвищення оренди / ремонт / виселення тощо].

🏠 ІНФОРМАЦІЯ ПРО ОРЕНДУ:
• Адреса: [ваша адреса]
• Договір оренди від: [дата]
• Поточна орендна плата: [сума] євро

⚖️ ЗАКОНОДАВСТВО:
Згідно з BGB § 535, орендодавець зобов'язаний утримувати житло в придатному для проживання стані.

Відповідно до BGB § 558, підвищення оренди можливе тільки до рівня місцевої порівняльної оренди (ortsübliche Vergleichsmiete) і не більше ніж на 20% за 3 роки.

Згідно з BGB § 543, позачергове розірвання договору можливе тільки при серйозних порушеннях (наприклад, несплата оренди протягом 2+ місяців).

💡 МОЯ ПОЗИЦІЯ:
• Я згоден / не згоден* з вашим повідомленням
• Прошу надати обґрунтування та документи
• Пропоную зустріч для обговорення

Прошу надати письмову відповідь протягом 14 днів.

З повагою,
[Ваше ім'я]
[Адреса]
[Контакти]

* - оберіть потрібне''',
                'tips': [
                    '📌 Фотографуйте всі дефекти житла',
                    '⏰ Зберігайте всі листування з орендодавцем',
                    '💰 Орендна плата не повинна перевищувати 30% доходу',
                    '⚖️ Mieterbund (спілка орендарів) надає безкоштовну консультацію'
                ]
            },
            'de': {
                'subject': 'Bezug: Ihre Mitteilung zur Miete',
                'body': '''Sehr geehrte Damen und Herren,

📋 ich beziehe mich auf Ihre Mitteilung bezüglich [Thema: Mieterhöhung / Reparatur / Kündigung etc.].

🏠 MIETINFORMATIONEN:
• Adresse: [Ihre Adresse]
• Mietvertrag vom: [Datum]
• Aktuelle Miete: [Betrag] Euro

⚖️ RECHTLICHE GRUNDLAGEN:
Gemäß BGB § 535 ist der Vermieter verpflichtet, die Mietsache in einem bewohnbaren Zustand zu erhalten.

Gemäß BGB § 558 ist eine Mieterhöhung nur bis zur ortsüblichen Vergleichsmiete und maximal 20% innerhalb von 3 Jahren möglich.

Gemäß BGB § 543 ist eine außerordentliche Kündigung nur bei schwerwiegenden Verstößen möglich (z.B. Mietrückstand von 2+ Monaten).

💡 MEINE POSITION:
• Ich stimme Ihrer Mitteilung zu / Ich widerspreche*
• Bitte senden Sie mir eine Begründung und Unterlagen
• Ich schlage ein persönliches Gespräch vor

Bitte senden Sie mir eine schriftliche Antwort innerhalb von 14 Tagen.

Mit freundlichen Grüßen,
[Ihr Name]
[Adresse]
[Kontakte]

* - Bitte wählen Sie das Zutreffende aus''',
                'tips': [
                    '📌 Fotografieren Sie alle Mängel der Wohnung',
                    '⏰ Bewahren Sie alle Korrespondenzen auf',
                    '💰 Die Miete sollte 30% des Einkommens nicht überschreiten',
                    '⚖️ Der Mieterbund bietet kostenlose Beratung'
                ]
            }
        },
        
        'employment': {
            'uk': {
                'subject': 'Підтвердження явки на Jobcenter',
                'body': '''Шановне Управління Jobcenter,

📋 Підтверджую отримання вашого запрошення на:
• Дата: [дата]
• Час: [час]
• Адреса: [адреса Jobcenter]
• Консультаційна особа: [ім'я, якщо відомо]

✅ ПІДТВЕРДЖУЮ:
Я з'явлюся на призначену зустріч у зазначений час.

⚠️ ВАЖЛИВА ІНФОРМАЦІЯ:
Згідно з § 59 SGB II, отримувачі допомоги зобов'язані з'являтися на запрошення Jobcenter.

Відповідно до § 31-32 SGB II, при відсутності без поважної причини виплати можуть бути:
• Зменшені на 30% протягом 12 тижнів
• Повністю припинені при повторних порушеннях

🩺 У РАЗІ ХВОРОБИ:
Якщо я захворію, я:
1. Негайно повідомлю вас телефоном
2. Надам лікарську довідку (Arbeitsunfähigkeitsbescheinigung) протягом 3 днів

📎 ДОКУМЕНТИ, ЯКІ ВІЗЬМУ З СОБОЮ:
• Паспорт / посвідка особи
• Актуальне резюме (Lebenslauf)
• Докази пошуку роботи (Bewerbungen)
• Інші документи за вашим запитом

З повагою,
[Ваше ім'я]
[Номер клієнта: Kundennummer]
[Адреса]
[Телефон]''',
                'tips': [
                    '📌 Приходьте на 10 хвилин раніше',
                    '⏰ Зберігайте копії всіх документів',
                    '💼 Одягайтеся ділово',
                    '📝 Робіть нотатки під час зустрічі'
                ]
            },
            'de': {
                'subject': 'Terminbestätigung',
                'body': '''Sehr geehrte Damen und Herren vom Jobcenter,

📋 hiermit bestätige ich den Erhalt Ihrer Einladung zum:
• Datum: [Datum]
• Uhrzeit: [Uhrzeit]
• Adresse: [Adresse des Jobcenters]
• Ansprechpartner: [Name, falls bekannt]

✅ BESTÄTIGUNG:
Ich werde zum genannten Termin erscheinen.

⚠️ WICHTIGE INFORMATIONEN:
Gemäß § 59 SGB II sind Leistungsempfänger verpflichtet, den Einladungen des Jobcenters Folge zu leisten.

Gemäß § 31-32 SGB II können bei unentschuldigtem Fehlen die Leistungen:
• Um 30% für 12 Wochen gekürzt werden
• Bei wiederholten Verstößen ganz entfallen

🩺 IM KRANKHEITSFALL:
Falls ich erkranken sollte, werde ich:
1. Sie umgehend telefonisch informieren
2. Eine Arbeitsunfähigkeitsbescheinigung innerhalb von 3 Tagen nachreichen

📎 UNTERLAGEN, DIE ICH MITBRINGE:
• Personalausweis / Reisepass
• Aktueller Lebenslauf
• Bewerbungsnachweise
• Weitere angeforderte Unterlagen

Mit freundlichen Grüßen,
[Ihr Name]
[Kundennummer]
[Adresse]
[Telefon]''',
                'tips': [
                    '📌 Kommen Sie 10 Minuten früher',
                    '⏰ Bewahren Sie Kopien aller Dokumente auf',
                    '💼 Tragen Sie angemessene Kleidung',
                    '📝 Machen Sie Notizen während des Gesprächs'
                ]
            }
        },
        
        'administrative': {
            'uk': {
                'subject': 'Щодо вашого адміністративного повідомлення',
                'body': '''Шановна установо,

📋 Я отримав ваше повідомлення від [дата] щодо [тема].

📎 МОЄ ПРОХАННЯ:
• Прошу надати детальне обґрунтування рішення
• Прошу надати копії всіх документів
• Прошу вказати строк для відповіді/дії

⚖️ ЗАКОНОДАВСТВО:
Згідно з VwVfG § 35, адміністративний акт повинен бути письмовим та обґрунтованим.

Відповідно до VwGO § 42, я маю право на оскарження адміністративного рішення.

💡 МОЇ ПРАВА:
• Право на вислуховування (Anhörung)
• Право на доступ до файлів (Akteneinsicht)
• Право на оскарження (Widerspruch) протягом 1 місяця

Прошу надати письмову відповідь протягом 14 днів.

З повагою,
[Ваше ім'я]
[Адреса]
[Контакти]''',
                'tips': [
                    '📌 Зберігайте всі офіційні листи',
                    '⏰ Строк оскарження — 1 місяць',
                    '⚖️ Rechtsantragsstelle надає безкоштовну допомогу',
                    '📞 Telefonseelsorge: 0800 111 0 111'
                ]
            },
            'de': {
                'subject': 'Bezug: Ihre behördliche Mitteilung',
                'body': '''Sehr geehrte Damen und Herren,

📋 ich beziehe mich auf Ihre Mitteilung vom [Datum] bezüglich [Thema].

📎 MEINE BITTE:
• Bitte senden Sie mir eine detaillierte Begründung der Entscheidung
• Bitte senden Sie mir Kopien aller Unterlagen
• Bitte nennen Sie mir die Frist für Antwort/Handlung

⚖️ RECHTLICHE GRUNDLAGEN:
Gemäß VwVfG § 35 muss ein Verwaltungsakt schriftlich und begründet sein.

Gemäß VwGO § 42 habe ich das Recht, einen Verwaltungsakt anzufechten.

💡 MEINE RECHTE:
• Recht auf Anhörung
• Recht auf Akteneinsicht
• Recht auf Widerspruch innerhalb von 1 Monat

Bitte senden Sie mir eine schriftliche Antwort innerhalb von 14 Tagen.

Mit freundlichen Grüßen,
[Ihr Name]
[Adresse]
[Kontakte]''',
                'tips': [
                    '📌 Bewahren Sie alle behördlichen Schreiben auf',
                    '⏰ Widerspruchsfrist beträgt 1 Monat',
                    '⚖️ Rechtsantragsstelle bietet kostenlose Hilfe',
                    '📞 Telefonseelsorge: 0800 111 0 111'
                ]
            }
        },
        
        'general': {
            'uk': {
                'subject': 'Щодо вашого листа',
                'body': '''Шановний одержувачу,

📋 Я отримав ваш лист від [дата].

❓ ПРОХАННЯ ПРО РОЗ'ЯСНЕННЯ:
Будь ласка, уточніть:
• Яка саме дія потрібна від мене?
• Який строк виконання?
• Які документи потрібно надати?

⚖️ ЗАУВАЖЕННЯ:
Я залишаю за собою право на:
• Отримання детальної інформації
• Консультацію з адвокатом
• Відповідь протягом розумного строку

Прошу надати письмову відповідь протягом 14 днів.

З повагою,
[Ваше ім'я]
[Адреса]
[Контакти]''',
                'tips': [
                    '📌 Не підписуйте документи без розуміння',
                    '⏰ Зберігайте копії всього',
                    '⚖️ При сумнівах звертайтеся до адвоката',
                    '📞 Безкоштовна правова допомога: 0800 111 0 111'
                ]
            },
            'de': {
                'subject': 'Bezug: Ihr Schreiben',
                'body': '''Sehr geehrte Damen und Herren,

📋 ich beziehe mich auf Ihr Schreiben vom [Datum].

❓ BITTE UM KLÄRUNG:
Bitte präzisieren Sie:
• Welche Handlung wird von mir erwartet?
• Welche Frist gilt?
• Welche Unterlagen sind erforderlich?

⚖️ HINWEIS:
Ich behalte mir das Recht vor auf:
• Detaillierte Information
• Anwaltliche Beratung
• Antwort innerhalb einer angemessenen Frist

Bitte senden Sie mir eine schriftliche Antwort innerhalb von 14 Tagen.

Mit freundlichen Grüßen,
[Ihr Name]
[Adresse]
[Kontakte]''',
                'tips': [
                    '📌 Unterschreiben Sie nichts Unverständliches',
                    '⏰ Bewahren Sie Kopien von allem auf',
                    '⚖️ Bei Zweifeln wenden Sie sich an einen Anwalt',
                    '📞 Kostenlose Rechtshilfe: 0800 111 0 111'
                ]
            }
        }
    }
}

# Описи законів
LAW_DESCRIPTIONS = {
    'BGB § 241': 'Обов\'язки зі зобов\'язання: Кожна сторона зобов\'язана виконувати умови договору добросовісно.',
    'BGB § 286': 'Прострочення боржника: Боржник перебуває у простроченні після отримання письмового нагадування.',
    'BGB § 288': 'Проценти у простроченні: 5% річних для споживачів, 9% для бізнесу.',
    'BGB § 433': 'Купівля-продаж: Продавець зобов\'язаний передати товар, покупець — сплатити ціну.',
    'BGB § 488': 'Кредитний договір: Кредитор надає гроші, боржник повертає з процентами.',
    'BGB § 823': 'Відшкодування збитків: Хто заподіяв шкоду, зобов\'язаний її відшкодувати.',
    'BGB § 535': 'Обов\'язки орендодавця: Утримувати житло в придатному стані.',
    'BGB § 536': 'Зниження оренди: При дефектах житла орендна плата може бути зменшена.',
    'BGB § 543': 'Позачергове розірвання: Можливе при серйозних порушеннях.',
    'BGB § 558': 'Підвищення оренди: Тільки до місцевого рівня, максимум 20% за 3 роки.',
    'BGB § 573': 'Розірвання орендодавцем: Тільки за обґрунтованих причин.',
    'BGB § 611': 'Трудовий договір: Роботодавець платить, працівник виконує роботу.',
    'BGB § 620': 'Припинення трудових відносин: Можливе за згодою сторін або з попередженням.',
    'KSchG § 1': 'Захист від звільнення: Звільнення тільки за соціально обґрунтованих причин.',
    'VwVfG § 35': 'Адміністративний акт: Повинен бути письмовим та обґрунтованим.',
    'VwGO § 42': 'Право на оскарження: Кожен може оскаржити адміністративне рішення.',
    '§ 59 SGB II': 'Обов\'язок явки: Отримувачі допомоги зобов\'язані з\'являтися на запрошення.',
    '§ 31-32 SGB II': 'Наслідки неявки: Зменшення виплат на 30% або припинення.',
    '§ 309 SGB III': 'Офіційні запрошення: Запрошення біржі праці є обов\'язковими.'
}

def generate_response(letter_type: str, laws: Dict, language: str, country: str = 'de') -> str:
    """
    Генерація повної відповіді з поясненнями законів та наслідків.
    
    Args:
        letter_type: Тип листа (debt_collection, tenancy, employment, administrative, general)
        laws: Словник з законами та наслідками
        language: Мова відповіді ('uk' або 'de')
        country: Країна ('de' тощо)
    
    Returns:
        Відформатована відповідь
    """
    # Отримання шаблону
    country_templates = RESPONSE_TEMPLATES.get(country, RESPONSE_TEMPLATES['de'])
    template = country_templates.get(letter_type, country_templates['general'])
    
    # Вибір мови
    lang_template = template.get(language, template['uk'])
    
    # Формування відповіді
    response = f"""📝 ШАБЛОН ВІДПОВІДІ:

Тема: {lang_template['subject']}

{lang_template['body']}

━━━━━━━━━━━━━━━━━━━━

💡 КОРИСНІ ПОРАДИ:
{chr(10).join(lang_template['tips'])}

━━━━━━━━━━━━━━━━━━━━

📚 ЗАКОНИ (детальніше):
"""
    
    # Додавання описів законів
    laws_list = laws.get('laws', [])
    for law in laws_list:
        # Видалення дужок для пошуку
        law_key = law.split(' (')[0] if ' (' in law else law
        desc = LAW_DESCRIPTIONS.get(law_key, 'Детальніше у юриста.')
        response += f"\n• {law}\n  → {desc}"
    
    # Додавання наслідків
    consequences = laws.get('consequences', '')
    if consequences:
        response += f"\n\n⚠️ НАСЛІДКИ НЕДОТРИМАННЯ:\n{consequences}"
    
    return response
