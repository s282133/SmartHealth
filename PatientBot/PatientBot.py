# PatientBot gestisce il bot del paziente

import json
import telepot
from gettext import Catalog

from MyMQTT import *
from functionsOnCatalogue import *
from customExceptions import *

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class PatientBot:
    def __init__(self):
        
        # Gestione servizi MQTT
        try:
            mqtt_service = http_getServiceByName("MQTT_analysis")
            TelegramClient_service = http_getServiceByName("TelegramClient")
            self.api_send_peso = get_api_from_service_and_name( TelegramClient_service, "send_peso" )
        except:
            print("Patient_Bot could not be initialized [ERR 1]")
        try:
            mqtt_broker = mqtt_service["broker"]
            mqtt_port = mqtt_service["port"]
            mqtt_base_topic = mqtt_service["base_topic"]    
        except:
                print("Patient_Bot could not be initialized [ERR 2]")     
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
                int_message = int(message)      
                if(int_message < 0):
                    raise InvalidPatientID

                # aggiorna il telegramID del paziente
                if http_Update_PatientTelegramID(chat_ID, message):
                    self.bot.sendMessage(chat_ID, text=f"Login procedure successful.\nConfirmed PatientID: {message}")
                else:    
                    self.bot.sendMessage(chat_ID, text=f"Login procedure unsuccessful.\nChoose again /start to insert your PatientID")

                self.previous_message=""   
            except:
                print("[PATIENT_BOT] INVALID PATIENT ID.")
                self.bot.sendMessage(chat_ID, text=f"PatientID not recognized.\nTry the login procedure again: /start") 
                self.previous_message="" 

        # spiegazione dei comandi disponibili
        elif message == "/help":
            self.bot.sendMessage(chat_ID, text="* Send /start to log in;\n* Send /peso to submit your weight;\n* Send /survey to complete a survey about your current health status.") 
            self.previous_message="/help"

        # invio del link al questionario
        elif message == "/survey":

            survey_service = http_getServiceByName("TelegramClient")
            api_survey = get_api_from_service_and_name(survey_service,"send_survey_link_to_patient") 
            survey_uri = api_survey["uri"]
            self.bot.sendMessage(chat_ID, text= f"You can complete the survey at this link: {survey_uri}")
            self.previous_message="/survey"

        # inserimento del peso 
        elif message == "/peso": 
            self.bot.sendMessage(chat_ID, text="Please send your weight in kg")
            self.previous_message="/peso"
        
        elif self.previous_message == "/peso":        
            try:
                int_weight = int(message)
                if(int_weight < 0 or int_weight > 100):
                    raise InvalidWeightException
                self.patientID = http_findPatientFromChatID(chat_ID)             
                if self.patientID == -1:
                    print("Paziente non trovato")
                    raise PatientNotFoundException 

                topic = self.api_send_peso["topic"]
                topic_send_peso = getTopicByParameters(topic, self.mqttTopic, self.patientID)
                peso =  {"status": message}
                
                # pubblicazione del peso
                self.mqtt_client.myPublish(topic_send_peso, peso)
                print("Weight submitted to the system.")               
                self.previous_message=""
                self.bot.sendMessage(chat_ID, text=f"Weight submitted correctly.\nYour weight is {int_weight} Kg")                
            except:
                print("[PATIENT_BOT] something went wrong with weight submission.")
                self.bot.sendMessage(chat_ID, text=f"Weight submission failed.\nTry again, push /peso")

        else:
            self.bot.sendMessage(chat_ID, text="Command not recognized/Message not supported.\nPush /help for a list of commands.")

    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')

if __name__ == "__main__":
    
    mybot_pz=PatientBot()
    mybot_pz.start()

    while True:
        time.sleep(10)
