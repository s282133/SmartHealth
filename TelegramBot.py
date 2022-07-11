# TelegramBot gestisce sia il bot del paziente che quello del dottore
# abilitando i comandi disponibili e mandando messaggi di allerta

from gettext import Catalog
import time
import json
import telepot
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from unicodedata import name
from telepot.loop import MessageLoop
# import sys, os
# from pprint import pprint
# sys.path.insert(0, os.path.abspath('..'))
from commons.MyMQTT import *
from commons.functionsOnCatalogue import *

class SwitchBot:
    def __init__(self, token, broker, port, mqttTopic, topic, ipAddressServerRegistrazione, data_analisys_obj):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        self.client = MyMQTT("telegramBot", broker, port, None)
        self.client.start()
        self.topic = topic
        self.mqttTopic = mqttTopic
        self.ipAddressServerRegistrazione = ipAddressServerRegistrazione
        self.data_analisys_obj = data_analisys_obj
        self.previous_message="previous_message"
        self.__message = {'bn': "telegramBot",
                          'e':
                          [
                              {'n': 'switch', 'v': '', 't': '', 'u': 'bool'},
                          ]
                          }
        print(f"self.tokenBot is {self.tokenBot}")
        if self.tokenBot == "5373152293:AAESoB5LMU3JUunXegFryWk484twuniHinE":
            MessageLoop(self.bot, {'chat': self.on_chat_message,
                                'callback_query': self.on_callback_query}).run_as_thread()
            print(f"token if is {self.tokenBot}")
            
        else:
            MessageLoop(self.bot, {'chat': self.on_chat_patient_message,
                    'callback_query': self.on_callback_query}).run_as_thread()
            print(f"token else is {self.tokenBot}")


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
            
            # Gestione Servizi
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

            # Gestione Servizi
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
        self.client.myPublish(self.topic, payload)
        if query_data==f"{self.cmd_on}":
            monitoring = "ON"      
        else:
            monitoring = "OFF"

        mes=messaggio["message"]["text"]
        print(mes)
        self.patientID = int(mes.split(" ")[2])
        print(self.patientID)
        
        top = f"{self.mqttTopic}/{self.patientID}/monitoring"   
        message =  {"status": monitoring}
        self.data_analisys_obj.myPublish(top, message)
        print(f"{message}")
        self.bot.sendMessage(chat_ID, text=f"Monitoring {query_data}")
 
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
            self.bot.sendMessage(chat_ID, text="You can complete the survey at this link: ")
            self.previous_message="/survey"

        elif message == "/peso": 
            self.bot.sendMessage(chat_ID, text="Please send your weight in kg")
            self.previous_message="/peso"
        
        elif self.previous_message == "/peso":
            
            if(int(message) < 0 or (int(message) > 100)):
                self.bot.sendMessage(chat_ID, text=f"Your weight is not possible")  
            else:
                self.bot.sendMessage(chat_ID, text=f"Your weight is: {message} Kg")
                print (f"Chat ID: {chat_ID}")
                self.patientID = findPatient(chat_ID)
                
                if self.patientID == 0:
                    print("Paziente non trovato")
                    exit
                
                topic=f"{self.mqttTopic}/{self.patientID}/peso" 
                peso =  {"status": message}
                self.data_analisys_obj.myPublish(topic, peso)
                print("published")
                self.previous_message=""

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
                        print(f"{chat_ID}")
            with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                json.dump(self.catalog, f,indent=2)
    
                              


