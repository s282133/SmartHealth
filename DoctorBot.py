# TelegramBot gestisce il client_bot del dottore
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
    def __init__(self):

        # Gestione servizi MQTT
        resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
        catalog = json.load(open(resouce_filename))
        services = catalog["services"]

        mqtt_service = getServiceByName(services,"MQTT_analysis")
        if mqtt_service == None:
            print("Servizio registrazione non trovato")
        mqtt_broker = mqtt_service["broker"]
        mqtt_port = mqtt_service["port"]
        self.mqtt_base_topic = mqtt_service["base_topic"]
        mqtt_api_monitoring = getApiByName(mqtt_service["APIs"],"monitoring_on") 
        self.mqtt_topic_monitoring  = mqtt_api_monitoring["topic"]

        mqtt_api_alert = getApiByName(mqtt_service["APIs"],"receive_alert") 
        mqtt_topic_alert = mqtt_api_alert["topic"]
        self.local_topic_alert = mqtt_topic_alert.replace("{{base_topic}}", self.mqtt_base_topic)

        # Oggetto mqtt
        self.mqtt_client = MyMQTT(None, mqtt_broker, mqtt_port, self)

        # Gestione servizi telegram
        TelegramDoctor_service = getServiceByName(services,"TelegramDoctor")
        if TelegramDoctor_service == None:
            print("Servizio registrazione non trovato")
        doctorTelegramToken = TelegramDoctor_service["doctorTelegramToken"]

        # Creazione client_bot
        self.client_bot = telepot.Bot(doctorTelegramToken)
        self.client_mqtt = MyMQTT("telegramBot", mqtt_broker, mqtt_port, None)
        self.client_mqtt.start()
        self.previous_message="previous_message"
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
     
        MessageLoop(self.client_bot, {'chat': self.on_chat_message,
                'callback_query': self.on_callback_query}).run_as_thread()


    def start(self):
        self.mqtt_client.start()
        self.mqtt_client.mySubscribe(self.local_topic_alert)


    def notify(self, topic, msg):

        print(f"Il topic è: {topic}")
        msg_json = json.loads(msg)
        
        telegramID = msg_json["telegramID"]
        messaggio = msg_json["Messaggio"]
        cmd_on = msg_json["CmdOn"]
        cmd_off = msg_json["CmdOff"]

        self.send_alert(telegramID,messaggio,cmd_on,cmd_off)


       
    def send_alert(self,telegramID,messaggio,cmd_on,cmd_off): 
        buttons = [[InlineKeyboardButton(text=f'MONITORING 🟡',    callback_data=cmd_on), 
                   InlineKeyboardButton(text=f'NOT MONITORING ⚪', callback_data=cmd_off)]]
        keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
        self.client_bot.sendMessage(telegramID, text=messaggio, reply_markup=keyboard)


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
            self.client_bot.sendMessage(chat_ID, text=f"Create a personal doctor account at this link: {uri}")


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
            self.client_bot.sendMessage(chat_ID, text=f"Sign in a new patient at this link: {uri}")

        if message == "/accesso_dati": 
            self.client_bot.sendMessage(chat_ID, text='Access to data at this link: ')


    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
                
        MonitoringID = query_data.split(" ")[2]
        monitoring = query_data.split(" ")[1]
         
        local_topic_monitoring = getTopicByParameters(self.mqtt_topic_monitoring, self.mqtt_base_topic, str(MonitoringID))
        message =  {"status": monitoring}
        self.mqtt_client.myPublish(local_topic_monitoring, message)
        print(f"{message}")

        self.client_bot.sendMessage(chat_ID, text=f"Monitoring {monitoring}")
 

if __name__=="__main__":

    mybot_dr = DoctorBot()
    mybot_dr.start()

    while True:
        time.sleep(1)