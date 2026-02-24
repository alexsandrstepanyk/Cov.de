"""
Germany Bot for Gov.de
Provides laws for Germany.
"""

LEGAL_DB_DE = {
    'debt_collection': {
        'laws': [
            {'section': 'BGB § 241', 'summary': 'Pflichten aus dem Schuldverhältnis'},
            {'section': 'BGB § 286', 'summary': 'Verzug des Schuldners'},
            {'section': 'BGB § 288', 'summary': 'Verzugszinsen'},
            {'section': 'BGB § 433', 'summary': 'Vertragstypische Pflichten beim Kaufvertrag'},
            {'section': 'BGB § 488', 'summary': 'Vertragstypische Pflichten beim Darlehensvertrag'},
            {'section': 'BGB § 823', 'summary': 'Schadensersatzpflicht'}
        ],
        'consequences': 'Пеня, судовий процес, стягнення боргу, компенсація збитків.'
    },
    'tenancy': {
        'laws': [
            {'section': 'BGB § 535', 'summary': 'Inhalt und Hauptpflichten des Mietvertrags'},
            {'section': 'BGB § 536', 'summary': 'Mietminderung bei Sach- und Rechtsmängeln'},
            {'section': 'BGB § 543', 'summary': 'Außerordentliche fristlose Kündigung'},
            {'section': 'BGB § 573', 'summary': 'Ordentliche Kündigung des Vermieters'}
        ],
        'consequences': 'Виселення, штраф, суд, компенсація.'
    },
    'employment': {
        'laws': [
            {'section': 'BGB § 611', 'summary': 'Dienstvertrag'},
            {'section': 'BGB § 620', 'summary': 'Beendigung des Dienstverhältnisses'},
            {'section': 'KSchG § 1', 'summary': 'Allgemeiner Kündigungsschutz'}
        ],
        'consequences': 'Компенсація, судовий розгляд, звільнення.'
    },
    'administrative': {
        'laws': [
            {'section': 'VwVfG § 35', 'summary': 'Befristung von Verwaltungsakten'},
            {'section': 'VwGO § 42', 'summary': 'Klagebefugnis'}
        ],
        'consequences': 'Штраф, оскарження в суді.'
    },
    'general': {
        'laws': [
            {'section': 'BGB § 241', 'summary': 'Pflichten aus dem Schuldverhältnis'}
        ],
        'consequences': 'Залежно від ситуації, цивільні чи кримінальні наслідки.'
    }
}

def get_relevant_laws_de(letter_type: str):
    return LEGAL_DB_DE.get(letter_type, LEGAL_DB_DE['general'])

# Bot logic
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

async def handle_request(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    letter_type = update.message.text
    laws = get_relevant_laws_de(letter_type)
    await update.message.reply_text(str(laws))

def main():
    application = Application.builder().token("8691230405:AAEPaEM4l2A6kzsxFHnnkY5ICtfLnYZDYJw").build()
    application.add_handler(MessageHandler(filters.TEXT, handle_request))
    application.run_polling()

if __name__ == '__main__':
    main()