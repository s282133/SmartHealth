# TelegramBot gestisce il client_bot del dottore
# abilitando i comandi disponibili e mandando messaggi di allerta

import time
import json
import telepot
from gettext import Catalog

from commons.MyMQTT import *
from commons.functionsOnCatalogue import *
from commons.customExceptions import *

from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class DoctorBot:
    def __init__(self):

        # Gestione servizi MQTT
        mqtt_service = http_getServiceByName("MQTT_analysis")
        try:
            mqtt_broker = mqtt_service["broker"]
            mqtt_port = mqtt_service["port"]
            self.mqtt_base_topic = mqtt_service["base_topic"]
        except TypeError:
            print("MQTT_analysis could not be initialized [ERR 1].")
        try:
            mqtt_api_monitoring = get_api_from_service_and_name(mqtt_service,"monitoring_on") 

            self.mqtt_topic_monitoring  = mqtt_api_monitoring["topic"]
        except TypeError:
            print("MQTT_analysis could not be initialized [ERR 2].")
        except KeyError:
            print("MQTT_analysis could not be initialized [ERR 3].")
        except:
            print("MQTT_analysis could not be initialized [ERR 4].")
        mqtt_api_alert = get_api_from_service_and_name(mqtt_service,"receive_alert") 


        mqtt_topic_alert = mqtt_api_alert["topic"]
        self.local_topic_alert = mqtt_topic_alert.replace("{{base_topic}}", self.mqtt_base_topic)
        # Oggetto mqtt
        self.mqtt_client = MyMQTT(None, mqtt_broker, mqtt_port, self)
        # Gestione servizi telegram
        try:
            TelegramDoctor_service = http_getServiceByName("TelegramDoctor")
            doctorTelegramToken = TelegramDoctor_service["doctorTelegramToken"]
        except TypeError:
            print("TelegramDoctor could not be initialized [ERR 5].")
        except KeyError:
            print("TelegramDoctor could not be initialized [ERR 6].")
        except:
            print("TelegramDoctor could not be initialized [ERR 7].")
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
            
            registration_service = http_getServiceByName("ResourceService")
            try:
                registration_ipAddress  = registration_service["host"]
                registration_port       = registration_service["port"]
            except:
                print("Registration - error [ERR 8].")
                
            try:    
                api_registrazione_dottore = get_api_from_service_and_name( registration_service, "registrazione_dottore" )
               
                registration_uri = api_registrazione_dottore["uri"]
            except:
                print("Registration - error [ERR 9].")

            registration_uri = registration_uri.replace("{{chat_ID}}", str(chat_ID))

            uri = f"http://{registration_ipAddress}:{registration_port}/{registration_uri}"
            self.client_bot.sendMessage(chat_ID, text=f"Create a personal doctor account at this link: {uri}")

        elif message == "/registrazione_paziente": 

            registration_service = http_getServiceByName("ResourceService")
            try:
                patient_registration_ipAddress = registration_service["host"]
                patient_registration_port = registration_service["port"]
            except:
                print("Registration - error [ERR 10].")
           
            try:
                api_start = get_api_from_service_and_name(registration_service,"registrazione_paziente") 

                patient_registration_uri = api_start["uri"]
            except:
                print("Registration - error [ERR 11].")

            patient_registration_uri = str(patient_registration_uri).replace("{{chat_ID}}", str(chat_ID))

            uri = f"http://{patient_registration_ipAddress}:{patient_registration_port}/{patient_registration_uri}"
            self.client_bot.sendMessage(chat_ID, text=f"Sign in a new patient at this link: {uri}")

        elif message == "/accesso_dati": 

            accesso_dati_service = http_getServiceByName("NodeRed")
            try:
                accesso_dati_ipAddress = accesso_dati_service["host"]
                accesso_dati_port = accesso_dati_service["port"]
            except:
                print("Accesso dati - error [ERR 10].")
           
            try:
                api_accesso_dati = get_api_from_service_and_name(accesso_dati_service,"accesso_dati") 

                accesso_dati_uri = api_accesso_dati["uri"]
            except:
                print("Accesso dati - error [ERR 11].")

            uri = f"http://{accesso_dati_ipAddress}:{accesso_dati_port}/{accesso_dati_uri}"
            self.client_bot.sendMessage(chat_ID, text=f'Access to data at this link: {uri}')
        

        else:
            self.client_bot.sendMessage(chat_ID, text="* Send /start to log in;\n* Send /registrazione_paziente to submit a new patient;\n* Send /accesso_dati to monitor patients' data.") 


    def on_callback_query(self, messaggio):
        query_ID , chat_ID , query_data = telepot.glance(messaggio,flavor='callback_query')
        payload = self.__message.copy()
        payload['e'][0]['v'] = query_data
        payload['e'][0]['t'] = time.time()
                
        patientID = query_data.split(" ")[2]
        monitoring_state = query_data.split(" ")[1]

        patient_name = http_getNameFromClientID(patientID)
        
        local_topic_monitoring = getTopicByParameters(self.mqtt_topic_monitoring, self.mqtt_base_topic, str(patientID))
        message =  {"status": monitoring_state}
        self.mqtt_client.myPublish(local_topic_monitoring, message)
        print(f"{message}")

        self.client_bot.sendMessage(chat_ID, text=f"Monitoring {monitoring_state} ({patient_name} - ID: {patientID})")
 

if __name__=="__main__":

    mybot_dr = DoctorBot()
    mybot_dr.start()

    while True:
        time.sleep(1)