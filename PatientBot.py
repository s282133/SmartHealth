# TelegramBot gestisce il bot del paziente
# abilitando i comandi disponibili 

import json
import telepot
from gettext import Catalog

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *
from commons.customExceptions import *

#from unicodedata import name
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class PatientBot:
    def __init__(self):
        
        # Gestione servizi MQTT
        resouce_filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
        catalog = json.load(open(resouce_filename))
        services = catalog["services"]

        try:
            mqtt_service = getServiceByName(services,"MQTT_analysis")
            TelegramClient_service = getServiceByName(services,"TelegramClient")
            if mqtt_service == None or TelegramClient_service == None:
                raise ServiceUnavailableException
            else:
                mqtt_broker = mqtt_service["broker"]
                mqtt_port = mqtt_service["port"]
                mqtt_base_topic = mqtt_service["base_topic"]         
                # Oggetto mqtt
                self.mqtt_client = MyMQTT(None, mqtt_broker, mqtt_port, self)           
                # Gestione servizi telegram
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
        except:
            print("[PATIENT_BOT] Uno o più servizi non trovati")


    def start(self):
        self.mqtt_client.start()


    def on_chat_patient_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        message = msg['text']

        if message == "/start": 
            self.bot.sendMessage(chat_ID, text="BOT successfully started!\nSend the patientID provided by the doctor to login.")
            self.previous_message="/start"
        
        elif  self.previous_message == "/start":
            try:
                int_message = int(message)      # patientID dato dal medico
                if(int_message < 0):
                    raise InvalidPatientID
                self.bot.sendMessage(chat_ID, text=f"Login procedure successful.\nConfirmed PatientID: {message}")                 
                self.Update_PatientTelegramID(chat_ID,message)
                self.previous_message=""   
            except:
                print("[PATIENT_BOT] INVALID PATIENT ID.")
                self.bot.sendMessage(chat_ID, text=f"PatientID not recognized.\nTry the login procedure again: /start") 
                self.previous_message="" 

        elif message == "/help":
            self.bot.sendMessage(chat_ID, text="* Send /start to log in;\n* Send /peso to submit your weight;\n* Send /survey to complete a survey about your current health status.") 
            self.previous_message="/help"

        elif message == "/survey":
            self.bot.sendMessage(chat_ID, text="You can complete the survey at this link: https://docs.google.com/forms/d/e/1FAIpQLSfLxw1y52kB5xNp6WcHAw0xQ1x2s3ViyXvWUGNDzlVtAdzWIA/viewform")
            self.previous_message="/survey"

        elif message == "/peso": 
            self.bot.sendMessage(chat_ID, text="Please send your weight in kg")
            self.previous_message="/peso"
        
        elif self.previous_message == "/peso":        
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
                self.bot.sendMessage(chat_ID, text=f"Weight submitted correctly.\nYour weight is {int_weight} Kg")                
            except:
                print("[PATIENT_BOT] something went wrong with weight submission.")
                self.bot.sendMessage(chat_ID, text=f"Weight submission failed.\nTry again, push /peso")

        else:
            self.bot.sendMessage(chat_ID, text="Command not recognized/Message not supported.\nPush /help for a list of commands.")

    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')


    def Update_PatientTelegramID (self,chat_ID, message):
            # try except (InvalidChatIdException)
            try:
                filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
                f = open(filename)
                self.catalog = json.load(f)
                self.lista = self.catalog["resources"]
                found = 0
                for doctorObject in self.lista:
                    patientList = doctorObject["patientList"]
                    for patientObject in patientList:
                        patientID = patientObject["patientID"]
                        if patientID == int(message):
                            found = 1
                            connectedDevice = patientObject["connectedDevice"]
                            connectedDevice["telegramID"]=chat_ID
                            #print(f"{chat_ID}")
                if found == 0:
                    raise PatientNotFoundException
                else:
                    found = 0       # lo rimetto com'era
                    with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                        json.dump(self.catalog, f,indent=2)
            except:
                print("[PATIENT_BOT] Patient not found")


if __name__ == "__main__":
    
    mybot_pz=PatientBot()
    mybot_pz.start()

    while True:
        time.sleep(10)
