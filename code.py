# import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging


#########################
# Creazione file di log #
#########################

logging.basicConfig(
    level=logging.DEBUG,
    format='[ %(asctime)s ] - -  %(levelname)s: %(name)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    filename='chatbot.log',
    filemode='w'
)
console = logging.StreamHandler()
console.setLevel(logging.INFO)
logging.getLogger('').addHandler(console)


##############################################################
# Definizione dei comportamenti del chatbot tramite funzioni #
##############################################################

def command_1(bot, update):
    """La funzione che incapsula il primo comportamento"""
    update.message.reply_text("command_1")
    logging.info('{} {} {}'.format("command_1", bot, update))


def command_2(bot, update):
    """La funzione che incapsula il secondo comportamento"""
    update.message.reply_text("command_2")
    logging.info('{} {} {}'.format("command_2", bot, update))


def welcome(bot, update):
    """La funzione con cui dare il benvenuto all'utente"""
    update.message.reply_text("welcome")
    logging.info('{} {} {}'.format("welcome", bot, update))


def help_me(bot, update):
    """La funzione con cui spiegare all'utente cosa può fare"""
    update.message.reply_text("help")
    logging.info('{} {} {}'.format("help", bot, update))


def dialog(bot, update):
    """La funzione che risponde al linguaggio naturale inserito dall'utente"""
    update.message.reply_text("dialog")
    logging.info('{} {} {}'.format("dialog", bot, update))


def error(bot, update, error):
    """La funzione che gestisce le eventuali situazioni di errore"""
    update.message.reply_text("error")
    logging.warning('{} {} {} {}'.format("dialog", bot, update, error))


#########################
# Creazione del chatbot #
#########################

# N.B.(1): La procedura di creazione va effettuata tramite @BotFather via app Telegram.
#          Utilizzare il token restituito da @BotFather per collegare l'istanza del chatbot ai comportamenti desiderati.

TELEGRAM_BOT_TOKEN = '722180203:AAEBCSejdIlWJbUNv0CLsaa3M6FY0Q0SV7U'

# N.B.(2): Il token viene copiato in chiaro nel sorgente per motivi di tempo e per fini dimostrativi.
#          In caso di applicazioni reali è caldamente consigliata l'adozione di adeguate misure di sicurezza.


#########################################
# Collegamento e avviamento del chatbot #
#########################################


def start():
    """Avvia il chatbot Telegram"""

    # Istanziare l'EventHandler del chatbot creato passandogli il codice identificativo.
    updater = Updater(TELEGRAM_BOT_TOKEN)

    # # Più opportuno salvare il token come variabile d'ambiente e caricarne il valore trasparentemente:
    # updater = Updater(os.environ.get('TELEGRAM_BOT_TOKEN'))

    # Ottenere il dispatcher di eventi.
    dp = updater.dispatcher

    # Associare al dispatcher i comportamenti del chatbot:
    # # Comandi (risposte a necessità utente)
    dp.add_handler(CommandHandler("start", welcome))
    dp.add_handler(CommandHandler("help", help_me))

    dp.add_handler(CommandHandler("command_1", command_1))
    dp.add_handler(CommandHandler("command_2", command_2))

    # # Comprensione del linguaggio naturale (dialogo con utente)
    dp.add_handler(MessageHandler(Filters.text, dialog))

    # # Errori (notificare errori nell'utilizzo o occorsi)
    dp.add_error_handler(error)

    # Start the Bot
    print("Running...")
    updater.start_polling()

    # Mantenere attivo il chatbot finchè il processo non viene interrotto.
    updater.idle()


if __name__ == "__main__":
    logging.info('Bot avviato')
    start()
    logging.info('Bot spento')
