# import os
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import ParseMode
import logging
from keras.models import model_from_json
import numpy as np
import tensorflow as tf
from bs4 import BeautifulSoup
from requests import get
from unidecode import unidecode
import re
import uuid

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


def get_program():
    def parse_orario(event):
        return re.split(r"[-]\s", event)

    def parse_speaker(event):
        parts = re.split(r"[-\(\)]", event)
        return [x.strip() for x in parts if x]

    def format_dict(event, p_dict):
        sp_h = ["speaker", "azienda", "tema"]
        last_day = list(p_dict.keys())[-1]

        if event.startswith("Eventi collaterali"):
            return

        try:  # orario
            int(event[0])
            p_dict[last_day][event] = {}

        except ValueError:  # speaker
            last_event = list(p_dict[last_day].keys())[-1]
            speaker_parts = parse_speaker(event)
            p_dict[last_day][last_event][uuid.uuid4().hex] = {x: y for x, y in zip(sp_h, speaker_parts)}

    def organize_program(p_dict):
        by_day_prog = {}
        by_topic_prog = {}

        for day in p_dict:
            by_day_prog[day] = {}

            for slot in p_dict[day]:
                by_day_prog[day][slot] = []
                slot_parts = parse_orario(slot)

                for id_e in p_dict[day][slot]:
                    formatted_event = " - ".join(list(p_dict[day][slot][id_e].values()))
                    formatted_short = " - ".join(list(p_dict[day][slot][id_e].values())[:-1])
                    by_day_prog[day][slot].append(formatted_event)

                    if "tema" in p_dict[day][slot][id_e].keys():
                        current_topic = p_dict[day][slot][id_e]["tema"]

                        if not current_topic in by_topic_prog.keys():
                            by_topic_prog[current_topic] = []
                        by_topic_prog[current_topic].append(
                            "[{day}, {time}] {ev}".format(day=day, time=slot_parts[0].strip(), ev=formatted_short))

        return by_day_prog, by_topic_prog

    program_dict = {}
    url = "http://www.imolaprogramma.it/imola-programma-2018/"
    response = get(url)
    soup = BeautifulSoup(response.text, 'html.parser')

    program = soup.find('div', class_='et_pb_row et_pb_row_15')

    day1 = program.find('div', class_='et_pb_column et_pb_column_1_2 et_pb_column_39')
    day2 = program.find('div', class_='et_pb_column et_pb_column_1_2 et_pb_column_40')

    program = [day1, day2]

    program = [
        [unidecode(x.replace("–", "-"))
         for x in [day.find('h3').text] + [x.text.strip() for x in day.find_all('p')]
         if x]
        for day in program
    ]

    for day in program:
        program_dict[day[0]] = {}
        for event in day[1:]:
            format_dict(event, program_dict)

    return organize_program(program_dict)


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
- Ottieni il programma ristretto di Imola Programma 2018 con il comando /short_program
- Ottieni il programma integrale di Imola Programma 2018 con il comando /full_program
- Ottieni i talk di Imola Programma 2018 ordinati per categoria con il comando /topics

- In linguaggio naturale:
    - Chiedi quanta energia consumerà il tuo impianto industriale
    - Ottieni informazioni sulla temperatura del tuo macchinario
"""
    )
    logging.info('{} ha chiesto le info di utilizzo'.format(
        update.message.chat.first_name
    ))


def program_short(bot, update):
    global by_day_program
    s = ""
    for day in by_day_program:
        s += "*{}*".format(day)
        for slot in by_day_program[day]:
            s += "\n{}".format(slot)
        s += "\n\n"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=s,
        parse_mode=ParseMode.MARKDOWN
    )
    logging.info('{} ha chiesto il programma 2018 (short)'.format(
        update.message.chat.first_name
    ))


def program_full(bot, update):
    global by_day_program
    s = ""
    for day in by_day_program:
        s += "*{}*".format(day)
        for slot in by_day_program[day]:
            s += "\n\n_{}_\n\n".format(slot)
            s += "{}".format("\n".join(by_day_program[day][slot]))
        s += "\n\n"
    bot.send_message(
        chat_id=update.message.chat_id,
        text=s,
        parse_mode=ParseMode.MARKDOWN
    )
    logging.info('{} ha chiesto il programma 2018 (full)'.format(
        update.message.chat.first_name
    ))


def program_topics(bot, update):
    global by_topic_program
    s = ""
    for topic in by_topic_program:
        s += "*{}*\n{}\n\n".format(topic, "\n".join(by_topic_program[topic]))

    bot.send_message(
        chat_id=update.message.chat_id,
        text=s,
        parse_mode=ParseMode.MARKDOWN
    )
    logging.info('{} ha chiesto il programma 2018 (topic)'.format(
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

TELEGRAM_BOT_TOKEN = '892891556:AAHbizfizrP3GyPF5k5NBf--JugxdoKdvzE'

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
    dp.add_handler(CommandHandler("short_program", program_short))
    dp.add_handler(CommandHandler("full_program", program_full))
    dp.add_handler(CommandHandler("topics", program_topics))
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


by_day_program, by_topic_program = get_program()

if __name__ == "__main__":
    logging.info('Bot avviato')
    start()
    logging.info('Bot spento')
