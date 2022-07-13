# TelegramBot gestisce il bot del dottore
# abilitando i comandi disponibili e mandando messaggi di allerta

import time
import json
import telepot
from gettext import Catalog

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class DoctorBot:
    def __init__(self, data_analisys_obj):

        # Gestione servizi MQTT
        resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
        catalog = json.load(open(resouce_filename))
        services = catalog["services"]

        mqtt_service = getServiceByName(services,"MQTT_analysis")
        if mqtt_service == None:
            print("Servizio registrazione non trovato")
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        mqtt_base_topic = mqtt_service["base_topic"]

        # Gestione servizi telegram
        TelegramDoctor_service = getServiceByName(services,"TelegramDoctor")
        if TelegramDoctor_service == None:
            print("Servizio registrazione non trovato")
        doctorTelegramToken = TelegramDoctor_service["doctorTelegramToken"]

        # Creazione bot
        self.bot = telepot.Bot(doctorTelegramToken)
        self.client = MyMQTT("telegramBot", mqtt_broker, mqtt_port, None)
        self.client.start()
        self.mqttTopic = mqtt_base_topic
        self.data_analisys_obj = data_analisys_obj
        self.previous_message="previous_message"
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
     
        MessageLoop(self.bot, {'chat': self.on_chat_message,
                'callback_query': self.on_callback_query}).run_as_thread()


    def send_alert(self,telegramID,messaggio,cmd_on,cmd_off): 
        buttons = [[InlineKeyboardButton(text=f'MONITORING 🟡',    callback_data=cmd_on), 
                   InlineKeyboardButton(text=f'NOT MONITORING ⚪', callback_data=cmd_off)]]
        self.cmd_on=cmd_on
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.bot.sendMessage(telegramID, text=messaggio, reply_markup=keyboard)


    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            
            # Gestione Servizi di registrazione dottore
            conf_file = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json' 
            conf = json.load(open(conf_file))
            services = conf["services"]
            registration_service = getServiceByName(services,"Registration")
            if registration_service == None:
                print("Servizio registrazione non trovato")

            registration_ipAddress = registration_service["host"]
            registration_port = registration_service["port"]
            api_start = getApiByName(registration_service["APIs"],"start") 
            registration_uri = api_start["uri"]

            #da cambiare con jinja
            registration_uri = registration_uri.replace("{{chat_ID}}", str(chat_ID))

            uri = f"http://{registration_ipAddress}:{registration_port}/{registration_uri}"
            self.bot.sendMessage(chat_ID, text=f"Create a personal doctor account at this link: {uri}")


        if message == "/registrazione_paziente": 

            # Gestione Servizi di registrazione paziente
            conf_file = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json' 
            conf = json.load(open(conf_file))
            services = conf["services"]
            registration_service = getServiceByName(services,"Registration")
            if registration_service == None:
                print("Servizio registrazione non trovato")

            patient_registration_ipAddress = registration_service["host"]
            patient_registration_port = registration_service["port"]
            api_start = getApiByName(registration_service["APIs"],"registrazione_paziente") 
            patient_registration_uri = api_start["uri"]

            #da cambiare con jinja
            patient_registration_uri = patient_registration_uri.replace("{{chat_ID}}", str(chat_ID))

            uri = f"http://{patient_registration_ipAddress}:{patient_registration_port}/{patient_registration_uri}"
            self.bot.sendMessage(chat_ID, text=f"Sign in a new patient at this link: {uri}")

        if message == "/accesso_dati": 
            self.bot.sendMessage(chat_ID, text='Access to data at this link: ')


    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
                
        MonitoringID = self.cmd_on.split(" ")[2]
        monitoring = self.cmd_on.split(" ")[1]
        
        top = f"{self.mqttTopic}/{MonitoringID}/monitoring"   
        message =  {"status": monitoring}
        self.data_analisys_obj.myPublish(top, message)
        print(f"{message}")
        self.bot.sendMessage(chat_ID, text=f"Monitoring {monitoring}")
 