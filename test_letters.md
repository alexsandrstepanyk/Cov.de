# Тестові листи для Gov.de Bot

## 📋 Колекція тестових листів німецькою мовою

---

## 1. Jobcenter (Запрошення)

```
Bundesagentur für Arbeit
Jobcenter Berlin-Mitte

Sehr geehrte Frau Müller,

hiermit laden wir Sie zu einem persönlichen Gespräch ein.

Termin: 15.03.2024 um 10:00 Uhr
Ort: Jobcenter Berlin-Mitte, Straße der Migration 45, 10115 Berlin
Ansprechpartner: Herr Schmidt, Raum 3.12

Bitte bringen Sie folgende Unterlagen mit:
- Personalausweis oder Reisepass
- Aktueller Lebenslauf
- Bewerbungsnachweise der letzten 4 Wochen
- Mietbescheinigung

Gemäß § 59 SGB II sind Sie verpflichtet, zu dem Termin zu erscheinen. 
Bei unentschuldigtem Fehlen können Leistungen nach § 31 SGB II gekürzt werden.

Mit freundlichen Grüßen
Ihr Jobcenter Team

Kundennummer: 123BG456
```

**Очікуваний результат:**
- Тип: employment
- Ризик: LOW ✅
- Закони: § 59 SGB II, § 31 SGB II

---

## 2. Inkasso (Шахрайський лист)

```
FAKE Inkasso GmbH
Forderungsmanagement

Sehr geehrte Dame und Herren,

letzte Mahnung!

Sie schulden uns sofort 2.500 Euro!

Überweisen Sie das Geld innerhalb 24 Stunden auf:
Western Union MTCN: 1234567890

Bei nicht Zahlung kommt Polizei und macht Haftbefehl!
Sie müssen ins Gefängnis für 3 Jahre!

Bitcoin Wallet: 1A2B3C4D5E6F7G8H9I

Rufen Sie an: 0900-999888 (2€/Minute)
Email: urgent@gmail.com

Dringend! Sofort!

Mit freundlichen Grüßen
Inkasso Team
```

**Очікуваний результат:**
- Тип: debt_collection
- Ризик: HIGH 🚨
- Ознаки шахрайства: Western Union, Bitcoin, 0900 номер, загрози

---

## 3. Finanzamt (Податкова)

```
Finanzamt München
Steuerabteilung

Sehr geehrter Herr Kowalenko,

wir beziehen uns auf Ihre Einkommensteuererklärung 2023.

Nach Prüfung ergibt sich eine Steuernachzahlung in Höhe von 450,00 Euro.

Bitte überweisen Sie den Betrag bis zum 30.04.2024 auf folgendes Konto:

Finanzamt München
IBAN: DE89 3704 0044 0532 0130 00
BIC: COBADEFFXXX
Verwendungszweck: Steuernummer 123/456/7890

Bei Fragen stehen wir Ihnen gerne zur Verfügung.

Telefon: 089 123456-0
Email: poststelle@finanzamt-muenchen.de

Mit freundlichen Grüßen
Ihr Finanzamt
```

**Очікуваний результат:**
- Тип: administrative
- Ризик: LOW ✅
- Офіційний .de домен

---

## 4. Vermieter (Орендодавець - підвищення оренди)

```
Herrn Wolfgang Müller
Vermieter

Sehr geehrte Familie Kowalenko,

hiermit kündige ich eine Mieterhöhung gemäß § 558 BGB an.

Die neue Miete beträgt ab 01.05.2024:
- Kaltmiete: 650 Euro (vorher 550 Euro)
- Nebenkosten: 150 Euro
- Gesamtmiete: 800 Euro

Begründung: Die ortsübliche Vergleichsmiete liegt bei 12 Euro/qm.

Sie haben der Erhöhung bis zum 30.04.2024 zuzustimmen.

Mit freundlichen Grüßen
Wolfgang Müller

Telefon: 0171 1234567
Email: w.mueller@web.de
```

**Очікуваний результат:**
- Тип: tenancy
- Ризик: LOW-MEDIUM ⚠️
- Закони: § 558 BGB

---

## 5. Falsche Polizei (Шахрай від імені поліції)

```
BUNDESPOLIZEI ZENTRALE
Kriminalpolizei

SEHR GEEHRTE DAME UND HERREN,

SIE MÜSSEN SOFORT 5000 EURO ÜBERWEISEN!

Gegen Sie läuft ein Strafverfahren wegen Geldwäsche.

Bei nicht Zahlung:
- Haftbefehl wird ausgestellt
- Sie werden verhaftet
- Abschiebung in die Ukraine

Überweisen Sie auf:
Kontonummer: 1234567890
BLZ: 10020030

Oder Paysafecard Code: 1234-5678-9012-3456

Rufen Sie an: +44 20 1234567 (UK Nummer!)
Email: polizei.bundes@gmail.com

DRINGEND! 24 STUNDEN!

Mit freundlichen Grüßen
Kommissar Müller
```

**Очікуваний результат:**
- Тип: administrative
- Ризик: HIGH 🚨
- Ознаки: +44 номер, gmail, Paysafecard, загрози

---

## 6. Gericht (Суд - офіційний)

```
Amtsgericht Berlin-Charlottenburg
Gerichtstraße 123
10585 Berlin

Beschluss

In dem Verfahren betreffend die Mietsache
Kowalenko ./. Müller

hat das Gericht am 20.02.2024 entschieden:

Der Mietvertrag wird zum 31.05.2024 gekündigt.

Rechtsmittelbelehrung:
Gegen diesen Beschluss kann innerhalb eines Monats
Widerspruch eingelegt werden.

Geschäftszeichen: 12 C 345/24

Telefon: 030 9018-0
Email: poststelle@agch-gericht-berlin.de
Internet: www.gericht-berlin.de
```

**Очікуваний результат:**
- Тип: administrative
- Ризик: LOW ✅
- Офіційний .de домен, суд

---

## 7. Stromversorger (Комунальні послуги)

```
Stadtwerke Berlin GmbH
Energieversorgung

Sehr geehrter Kunde,

hiermit mahnen wir Sie zur Zahlung der offenen Stromrechnung.

Rechnungsnummer: SW-2024-12345
Offener Betrag: 234,56 Euro
Fälligkeitsdatum: 01.02.2024

Bitte überweisen Sie den Betrag innerhalb 14 Tagen auf:

Stadtwerke Berlin GmbH
IBAN: DE12 1005 0000 0123 4567 89
BIC: BELADEBEXXX

Bei Nichtzahlung müssen wir leider eine Mahngebühr von 5 Euro berechnen.

Kundenservice: 030 123456-0
Email: kundenservice@stadtwerke-berlin.de

Mit freundlichen Grüßen
Ihre Stadtwerke Berlin
```

**Очікуваний результат:**
- Тип: debt_collection
- Ризик: LOW ✅
- Офіційна компанія

---

## 8. Krankenkasse (Лікарняна каса)

```
AOK Berlin-Brandenburg
Gesundheitskasse

Sehr geehrte Frau Kowalenko,

wir bestätigen den Eingang Ihrer Unterlagen vom 15.02.2024.

Ihre Versichertennummer: A123456789

Wir haben Ihre Daten geprüft. Alles ist in Ordnung.

Ihre Beiträge werden weiterhin monatlich abgebucht.

Bei Fragen:
Telefon: 030 39002-0
Email: service@bb.aok.de
Internet: www.aok.de/bb

Mit freundlichen Grüßen
Ihre AOK Berlin-Brandenburg
```

**Очікуваний результат:**
- Тип: general
- Ризик: LOW ✅
- Офіційна страхова каса

---

## 9. Falsches Paketamt (Шахрайська посилка)

```
Deutsche Post DHL
Paketzentrum

Sehr geehrte Kundin,

Ihr Paket kann nicht zugestellt werden!

Es fallen Zollgebühren in Höhe von 45,90 Euro an.

Bitte bezahlen Sie online:
www.dhl-paket-zoll.com/track123

Oder überweisen Sie:
Deutsche Post Bank
IBAN: DE89 1001 0010 0123 4567 89

Bei nicht Zahlung wird das Paket zurückgeschickt.

Rufen Sie an: 0180-5-123456 (14 Cent/Minute)

Mit freundlichen Grüßen
DHL Team
```

**Очікуваний результат:**
- Тип: debt_collection
- Ризик: MEDIUM-HIGH ⚠️
- Ознаки: 0180 номер, підозрілий сайт

---

## 10. Arbeitgeber (Роботодавець - звільнення)

```
Musterfirma GmbH
Personalabteilung

Sehr geehrter Herr Kowalenko,

hiermit kündigen wir das Arbeitsverhältnis fristgerecht zum 31.03.2024.

Begründung: Betriebliche Gründe erfordern den Abbau von Arbeitsplätzen.

Sie haben Anspruch auf Arbeitslosengeld I.

Bitte melden Sie sich innerhalb 3 Monaten bei der Arbeitsagentur.

Ihr Arbeitszeugnis erhalten Sie separat.

Bei Fragen:
Telefon: 089 987654-0
Email: personal@musterfirma.de

Mit freundlichen Grüßen
Geschäftsführung
Musterfirma GmbH
HRB 123456
```

**Очікуваний результат:**
- Тип: employment
- Ризик: LOW ✅
- Закони: KSchG

---

## 📊 Очікувані результати тестування

| # | Організація | Тип | Ризик | Ознаки |
|---|-------------|-----|-------|--------|
| 1 | Jobcenter | employment | LOW ✅ | Офіційний |
| 2 | FAKE Inkasso | debt_collection | HIGH 🚨 | Western Union, Bitcoin, 0900 |
| 3 | Finanzamt | administrative | LOW ✅ | Офіційний .de |
| 4 | Vermieter | tenancy | LOW | § 558 BGB |
| 5 | Falsche Polizei | administrative | HIGH 🚨 | +44, gmail, Paysafecard |
| 6 | Gericht | administrative | LOW ✅ | Офіційний суд |
| 7 | Stromversorger | debt_collection | LOW ✅ | Офіційна компанія |
| 8 | Krankenkasse | general | LOW ✅ | AOK офіційний |
| 9 | Falsches Paketamt | debt_collection | MEDIUM ⚠️ | 0180 номер |
| 10 | Arbeitgeber | employment | LOW ✅ | HRB номер |

---

## 🧪 Як тестувати:

1. Надіслати кожен лист боту @GovDeClientBot
2. Перевірити чи правильно визначено тип
3. Перевірити рівень ризику
4. Перевірити виявлені ознаки шахрайства

**Очікується:**
- 7 листів LOW ризик (легітимні)
- 1 лист MEDIUM ризик (підозрілий)
- 2 листи HIGH ризик (шахрайство)
