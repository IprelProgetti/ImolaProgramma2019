# import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
from keras.models import model_from_json
import numpy as np
import tensorflow as tf

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


#########################
# Training rete neurale #
#########################
# from keras.models import Sequential
# from keras.layers import Dense
# from sklearn.model_selection import train_test_split
# import numpy as np
# np.random.seed(7)
#
# # Addestramento con numeri da -3000 a +3000
# ds = np.array([[i, i+1] for i in range(-3000, 3000)])
# X = ds[:, 0]
# y = ds[:, 1]
# X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.33, random_state=42)
#
# # Modello
# model = Sequential()
# model.add(Dense(1, input_dim=1, activation='linear', name="neuron"))
# model.summary()
# model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])
# model.fit(X_train, y_train, epochs=100, batch_size=10, validation_data=(X_test, y_test), verbose=1)
#
# # Salvataggio modello
# model_json = model.to_json()
# with open("model.json", "w") as json_file:
#     json_file.write(model_json)
# # Salvataggio pesi
# model.save_weights("model.h5")

################################
# Caricamento modello allenato #
################################
with open('model.json', 'r') as json_file:
    loaded_model_json = json_file.read()
loaded_model = model_from_json(loaded_model_json)
loaded_model.load_weights("model.h5")

global graph
graph = tf.get_default_graph()
loaded_model.compile(loss='mean_squared_error', optimizer='adam', metrics=['accuracy'])


def predict_successor(nb):
    """
    Dato un numero, predice il suo successivo grazie alla rete neurale.
    :param nb: un numero, float
    :return: nb + 1
    """
    global loaded_model
    with graph.as_default():
        succ = loaded_model.predict(np.array([nb]))[0][0]
    return succ


##############################################################
# Definizione dei comportamenti del chatbot tramite funzioni #
##############################################################

def predict_next(bot, update, args):
    """
    Dato un numero inserito dall'utente, ritorna il suo successore predetto dalla rete neurale.
    """
    global loaded_model
    number = "no_number"
    try:
        # vogliamo un solo numero in ingresso
        if len(args) != 1:
            raise ValueError()

        input = args[0].strip()
        number = float(input)
        succ = predict_successor(number)
        update.message.reply_text("{}".format(succ))
    except ValueError:
        succ = "un errore"
        update.message.reply_text("Per favore inserisci un numero")
    logging.info('{} ha chiesto il successore di {} ottenendo {}'.format(
        update.message.chat.first_name,
        number,
        succ))


def welcome(bot, update):
    """La funzione con cui dare il benvenuto all'utente"""
    update.message.reply_text("Ciao {}, come posso aiutarti?".format(
        update.message.chat.first_name
    ))
    logging.info('{} ha avviato una chat'.format(
        update.message.chat.first_name
    ))


def help_me(bot, update):
    """La funzione con cui spiegare all'utente cosa può fare"""
    update.message.reply_text(
        """
        - Predici il successore di un qualsiasi numero con il comando /predict
        - Chiedi quanta energia consumerà il tuo impianto industriale
        - Ottieni informazioni sulla temperatura del motore del tuo macchinario
        """
    )
    logging.info('{} ha chiesto le info di utilizzo'.format(
        update.message.chat.first_name
    ))


def dialog(bot, update):
    """La funzione che risponde al linguaggio naturale inserito dall'utente"""
    message = update.message.text
    if "energia" in message.lower().strip():
        answer = "{}kW".format(10.6)
    elif "temperatura" in message.lower().strip():
        answer = "{}°C".format(32.5)
    else:
        answer = "Non ho capito, potresti ripetere per favore?"

    update.message.reply_text("{}".format(answer))
    logging.info('{} ha chiesto "{}" ottenendo "{}" come risposta'.format(
        update.message.chat.first_name,
        message,
        answer
    ))


def error(bot, update, error):
    """La funzione che gestisce le eventuali situazioni di errore"""
    update.message.reply_text("error")
    logging.warning("{} ha causato l'errore {}".format(
        update.message.chat.first_name,
        error
    ))


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
    dp.add_handler(CommandHandler("predict", predict_next, pass_args=True))

    # # Comprensione del linguaggio naturale (dialogo con utente)
    dp.add_handler(MessageHandler(Filters.text, dialog))

    # # Errori (notificare errori nell'utilizzo o occorsi)
    dp.add_error_handler(error)

    # Start the Bot
    logging.info("Running...")
    updater.start_polling()

    # Mantenere attivo il chatbot finchè il processo non viene interrotto.
    updater.idle()


if __name__ == "__main__":
    logging.info('Bot avviato')
    start()
    logging.info('Bot spento')
