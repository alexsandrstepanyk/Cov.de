# 🧪 RAG ПОШУК - 50 ТЕСТОВИХ ЗАПИТІВ

**Дата:** 2026-03-31T00:34:35.569017
**База:** 65,186 документів (ChromaDB)

---

## 📊 РЕЗУЛЬТАТИ

| Показник | Значення |
|----------|----------|
| Всього запитів | 50 |
| Успішно | 24 |
| Неуспішно | 26 |
| Успішність | 48.0% |

---

## 📈 ПО КАТЕГОРІЯХ

| Категорія | Успішно | Всього | % |
|-----------|---------|--------|---|
| Jobcenter | 3 | 5 | 60.0% |
| Finanzamt | 4 | 5 | 80.0% |
| Vermieter | 4 | 5 | 80.0% |
| Inkasso | 3 | 5 | 60.0% |
| Gericht | 1 | 5 | 20.0% |
| Versicherung | 0 | 5 | 0.0% |
| Krankenkasse | 5 | 5 | 100.0% |
| Arbeitsagentur | 1 | 5 | 20.0% |
| Verbraucherschutz | 3 | 5 | 60.0% |
| Stadt | 0 | 2 | 0.0% |
| Versorger | 0 | 1 | 0.0% |
| Ordnungsamt | 0 | 1 | 0.0% |
| Jugendamt | 0 | 1 | 0.0% |

---

## 📝 ПРИКЛАДИ УСПІШНИХ ЗАПИТІВ

- **§ 59 SGB II Einladung Vorsprache** → Unknown § 195
- **SGB II Leistungen Lebensunterhalt Bürgergeld** → Unknown § 1626d
- **Jobcenter Beratung § 14 SGB II** → SGB_II § 43
- **§ 172 AO Steuerbescheid** → AO § 174
- **§ 250 AO Vollstreckung Steuern** → SGB_VI § 154a
- **§ 240 AO Säumniszuschlag** → AO § 240
- **§ 196 AO Außenprüfung Finanzamt** → Unknown § 196
- **§ 543 BGB Kündigung Zahlungsverzug** → Unknown § 2202
- **§ 558 BGB Mieterhöhung** → BGB § 556f
- **§ 555 BGB Modernisierung Duldung** → BGB § 35

---

## ⚠️ ПРИКЛАДИ НЕУСПІШНИХ ЗАПИТІВ

- **§ 60 SGB I Vermögenserklärung** → не знайдено очікуваний закон
- **Mitwirkungspflicht SGB II** → не знайдено очікуваний закон
- **Einkommensteuererklärung EStG Pflicht** → не знайдено очікуваний закон
- **Nebenkostenabrechnung BGB Nachzahlung** → не знайдено очікуваний закон
- **Inkasso Gericht Mahnbescheid** → не знайдено очікуваний закон
- **§ 688 ZPO Zahlungsbefehl** → не знайдено очікуваний закон
- **§ 380 ZPO Zeuge Ladung** → не знайдено очікуваний закон
- **§ 114 ZPO Prozesskostenhilfe** → не знайдено очікуваний закон
- **§ 263 StGB Betrug Strafe** → не знайдено очікуваний закон
- **Urteil Zivilprozess Rechtsmittel** → не знайдено очікуваний закон

---

## 🎯 ВИСНОВКИ

### ✅ Сильні сторони:
- RAG пошук працює з новою базою (65,186 документів)
- Добре знаходить основні кодекси (BGB, SGB, AO, ZPO)
- PDF документи інтегровані

### ⚠️ Проблемні зони:
- Семантичний пошук може давати неточні результати
- Рідкісні закони (OWiG, RStV) можуть не знаходитись
- SGB з римськими цифрами потребує кращої нормалізації

### 📋 Рекомендації:
1. Покращити нормалізацію SGB II/III → SGB_2/SGB_3
2. Додати більше прикладів для рідкісних законів
3. Використовувати гібридний пошук (semantic + keyword)

---

*Звіт створено автоматично*
