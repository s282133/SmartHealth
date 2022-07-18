# TelegramBot gestisce il bot del paziente
# abilitando i comandi disponibili 

import json
import telepot
from gettext import Catalog

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

#from unicodedata import name
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class PatientBot:
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
        mqtt_base_topic = mqtt_service["base_topic"]

        # Oggetto mqtt
        self.mqtt_client = MyMQTT(None, mqtt_broker, mqtt_port, self)
        
        # Gestione servizi telegram
        TelegramClient_service = getServiceByName(services,"TelegramClient")
        if TelegramClient_service == None:
            print("Servizio registrazione non trovato")
        patientTelegramToken = TelegramClient_service["patientTelegramToken"]
        
        # Creazione bot
        self.bot = telepot.Bot(patientTelegramToken)
        self.client = MyMQTT("telegramBot", mqtt_broker, mqtt_port, None)
        self.client.start()
        self.mqttTopic = mqtt_base_topic
        self.previous_message="previous_message"
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
       
        MessageLoop(self.bot, {'chat': self.on_chat_patient_message,
                'callback_query': self.on_callback_query}).run_as_thread()

    def start(self):
        self.mqtt_client.start()


    def on_chat_patient_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            self.bot.sendMessage(chat_ID, text="Bot successfully started, send your patientID given you by doctor")
            self.previous_message="/start"
        
        elif  self.previous_message == "/start" and int(message) < 0:
            self.bot.sendMessage(chat_ID, text=f"Your patientID is not possible") 
            self.previous_message="" 
        elif self.previous_message == "/start" and int(message) > 0:
            self.bot.sendMessage(chat_ID, text=f"Your patientID is: {message}")                 
            self.Update_PatientTelegramID(chat_ID,message)
            self.previous_message=""

        elif message == "/help":
            self.bot.sendMessage(chat_ID, text="You can send /start to log in\n You can send /peso toregister your weight\n You can send /survey to complete a survey") 
            self.previous_message="/help"

        elif message == "/survey":
            self.bot.sendMessage(chat_ID, text="You can complete the survey at this link: https://docs.google.com/forms/d/e/1FAIpQLSfLxw1y52kB5xNp6WcHAw0xQ1x2s3ViyXvWUGNDzlVtAdzWIA/viewform")
            self.previous_message="/survey"

        elif message == "/peso": 
            self.bot.sendMessage(chat_ID, text="Please send your weight in kg")
            self.previous_message="/peso"
        
        elif self.previous_message == "/peso":        
            
            # if(int(message) < 0 or (int(message) > 100)):
            #     self.bot.sendMessage(chat_ID, text=f"Your weight is not possible")  
            # else:
            #     self.bot.sendMessage(chat_ID, text=f"Your weight is: {message} Kg")
            #     print (f"Chat ID: {chat_ID}")
            #     self.patientID = findPatient(chat_ID)
                
            #     if self.patientID == 0:
            #         print("Paziente non trovato")
            #         exit
                
            #     topic=f"{self.mqttTopic}/{self.patientID}/peso" 
            #     peso =  {"status": message}
            #     self.mqtt_client.myPublish(topic, peso)
            #     print("published")
            #     self.previous_message=""
            try:
                int_weight = int(message)
                if(int_weight < 0 or int_weight > 100):
                    raise InvalidWeightException
                print (f"Chat ID: {chat_ID}")
                self.patientID = findPatient(chat_ID)             
                if self.patientID == 0:
                    print("Paziente non trovato")
                    raise PatientNotFoundException 
                topic=f"{self.mqttTopic}/{self.patientID}/peso" 
                peso =  {"status": message}
                self.mqtt_client.myPublish(topic, peso)
                print("Weight published.")               
                self.previous_message=""
                self.bot.sendMessage(chat_ID, text=f"OK! Weight submitted correctly.\nYour weight is {int_weight} Kg")                
            except:
                print("[WEIGHT] something went wrong with weight submission.")
                self.bot.sendMessage(chat_ID, text=f"Weight submission failed.\nTry again, push /peso")
            

    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')


    def Update_PatientTelegramID (self,chat_ID, message):
            filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
            f = open(filename)
            self.catalog = json.load(f)
            self.lista = self.catalog["resources"]
            for doctorObject in self.lista:
                patientList = doctorObject["patientList"]
                for patientObject in patientList:
                    patientID = patientObject["patientID"]
                    if patientID == int(message):
                        connectedDevice = patientObject["connectedDevice"]
                        connectedDevice["telegramID"]=chat_ID
                        #print(f"{chat_ID}")
            with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                json.dump(self.catalog, f,indent=2)

class Error(Exception):
    pass

class InvalidWeightException(Error):
    """Raised when weight is < 0 or > 100"""
    pass

class PatientNotFoundException(Error):
    """Raised when the patient is not found"""
    pass

if __name__ == "__main__":
    
    mybot_pz=PatientBot()
    mybot_pz.start()

    while True:
        time.sleep(10)
