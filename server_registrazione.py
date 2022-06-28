# SERVER PER LA REGISTRAZIONE DEL PAZIENTE E DEL DOTTORE 
# Il server permette al medico di registrarsi per la prima volta o di inserire un paziente nella sua lista  iscrivendolo

import json                     
import time
import telepot
import cherrypy
import socket
# from MyMQTT import *
from time import sleep
from collections import UserList
from telepot.loop import MessageLoop
import requests
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

import sys, os
sys.path.insert(0, os.path.abspath('..'))

from PageHTML import *
from commons.MyMQTT import *

class Registrazione(object):
    exposed=True
    def GET(self,*uri,**params):
        
        # apertura pagina html per registrazione dottore
        if uri[0] == "start": 
            self.telegramID = params["chat_ID"]
            filename = 'PageHTML\\doctors.html'
            f1 = open(filename)
            fileContent = f1.read()      
            f1.close()
            return fileContent

        # apertura pagina html per registrazione paziente
        if uri[0] == "registrazione_paziente": 

            # macaddress
            try:
                r = requests.get("http://192.168.1.254:8080/macaddress", verify=False, timeout=5)
                self.macaddress = r.text
            except requests.exceptions.RequestException as e:  # This is the correct syntax
                #raise SystemExit(e)
                self.macaddress = "b8:27:eb:81:80:64"
                #print(requests.status_codes)
                #return "Collegare il raspberry"

            self.doctortelegramID = params["chat_ID"]
            filename = 'PageHTML\\patients.html'
            f2 = open(filename)
            fileContent = f2.read()      
            f2.close()
            return fileContent

        # apertura tabella con dati iniziali
        if uri[0] == "tabella": 

            filename = 'CatalogueAndSettings\\catalog.json'
            f4 = open(filename)
            self.catalog = json.load(f4)
            self.lista = self.catalog["doctorList"]
            doctor_number = 0
            for doctorObject in self.lista:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"] 
                if self.doctortelegramID == telegramID: 
                    break
                doctor_number += 1
            self.lista = self.catalog["doctorList"][doctor_number] 
            return json.dumps(self.lista) 

    # aggiungere un dottore alla lista di dottori al SUBMIT
    def POST(self,*uri,**params):

        if uri[0] == "doctors": 
            
            body = cherrypy.request.body.read() 
            self.record = json.loads(body)

            doctor = {
                "doctorID": 0,
                "doctorName": self.record["doctorName"],
                "doctorSurname": self.record["doctorSurname"],
                "doctorMail": self.record["doctorMail"],
                "lastUpdate": time.strftime("%Y-%m-%d"),
                "connectedDevice": {
                    "telegramID": self.telegramID
                },
                "patientList": [],
                "devicesList":[]
            }

            #self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            self.dictionary = json.load(open('CatalogueAndSettings\\catalog.json'))

            # inserisco ID del dottore
            self.LastDoctorID = self.dictionary["LastDoctorID"]
            doctor["doctorID"] = self.LastDoctorID + 1
            self.dictionary["LastDoctorID"] = self.LastDoctorID + 1

            # inserisco il dottore nella lista
            self.dictionary['doctorList'].append(doctor) 
            # PROBLEMA (02-06-2022) : se parto dal catalog.json vuoto, non riesco a salvare il dottore

            # salvo il catalogo aggiornato
            with open('CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            return json.dumps(self.dictionary)


        #Chiamata post fatta dal raspberry per ottenere il suo macaddresse il suo ipaddress
        if uri[0] == "ipaddress": 

            body = cherrypy.request.body.read() 
            self.raspberry = json.loads(body)

            catalog_fn = 'CatalogueAndSettings\\catalog.json'
            self.catalog = json.load(open(catalog_fn))
            self.doctorlist = self.catalog["doctorList"]
            
            macaddress = self.raspberry["macaddress"]
            ipaddress  = self.raspberry["ipaddress"]

            bool_modificato=False
            for doctorObject in self.doctorlist:
                devicesList = doctorObject["devicesList"]
                for deviceObject in devicesList:
                    macAddress = deviceObject["macAddress"] 
                    if  macaddress == macAddress:
                        deviceObject["ipAddress"] = ipaddress
                        bool_modificato=True

            if bool_modificato:
                with open('CatalogueAndSettings\\catalog.json', "w") as f:
                    json.dump(self.dictionary, f, indent=2)
            return "ok"


        #Chiamata post per registrare il paziente
        if uri[0] == "patients": 

            body = cherrypy.request.body.read() 
            self.record = json.loads(body)

            channel={
                "api_key":"OEUWTU8AH5MOIMKZ",
                "name":"lillo",
                "Field 1":"heart rate",
                "Field 2":"pressure_high",
                "Field 3":"glycemia",    
                "Field 4":"pressure_low",            
                "Field 5":"peso" 
                }   
            # r=requests.post("https://api.thingspeak.com/channels.json",channel)
            
            # print(f"Questo è il channel: {r.json()}")
            # self.dicty=r.json()
            # self.api_key_w=self.dicty["api_keys"][0]
            # self.api_keys_write=self.api_key_w["api_key"]
            # self.api_keys_read = self.dicty["api_keys"][1]["api_key"]
            # chennel_id=self.dicty["id"]
            chennel_id="123"
            self.api_keys_write="abc"
            self.api_keys_read="def"

            patient = {
                "patientID": 0,
                "patientName": self.record["patientName"],
                "patientSurname": self.record["patientSurname"],
                "personalData": {
                    "taxIDcode": self.record["taxIDcode"],
                    "userEmail": self.record["userEmail"],
                    "pregnancyDayOne": self.record["pregnancyDayOne"]
                },
                "connectedDevice": {
                    "deviceName": self.record["deviceName"],
                    "onlineSince": -1,
                    "mesureType": [
                    "Heart Rate",
                    "Pressure",
                    "Temperature",
                    "Glycemia"
                    ],
                    "telegramID": 0,        
                    "thingspeakInfo": {
                    "channel": chennel_id,
                    "apikeys": [
                          self.api_keys_write,
                          self.api_keys_read
                    ]
                    }
                }
                }    

            #self.dictionary = json.load(open('C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json'))
            self.dictionary = json.load(open('CatalogueAndSettings\\catalog.json'))

            self.LastPatientID = self.dictionary["LastPatientID"]
            patient["patientID"] = self.LastPatientID + 1
            self.dictionary["LastPatientID"] = self.LastPatientID + 1

            # ricerca del giusto dottore tramite telegram ID già presente nel catalogo e quello da cui si è ricevuto il messaggio per la registrazione 
            doctor_number = self.findDoctorwithtelegramID(self.doctortelegramID)
            self.dictionary['doctorList'][doctor_number]['patientList'].append(patient)

            # aggiunta del device contemporaneamente al paziente
            device = {
                "deviceName": self.record["deviceName"],
                "patientID": patient["patientID"],
                "ipAddress": "0.0.0.0",
                "macAddress": self.macaddress,
                "measureType": [
                    "Temperature",
                    "Battito cardiaco",
                    "Pressione",
                    "Glicemia"
                ],
                "availableServices": [
                    "MQTT"
                ],
                "servicesDetails": [
                    {
                    "serviceType": "MQTT",
                    "topic": [
                        "/MySmartHealth/1/sensors/body"
                    ]
                    }
                ],
                "lastUpdate": time.strftime("%Y-%m-%d")
            }

            self.dictionary['doctorList'][doctor_number]['devicesList'].append(device)

            #with open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\catalog.json", "w") as f:
            with open('CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            self.lista = self.dictionary["doctorList"][doctor_number]  
            return json.dumps(self.lista) 


    def findDoctorwithtelegramID(self, doctortelegramID):
        doctor_number = 0
        self.lista = self.dictionary["doctorList"]
        for doctorObject in self.lista:
            connectedDevice = doctorObject["connectedDevice"]
            telegramID = connectedDevice["telegramID"] 
            if doctortelegramID == telegramID: 
                break
            doctor_number += 1
            print(f"{doctor_number} belongs to {telegramID}")
        return doctor_number


# Inviare pagine html per la registrazione al messaggio inviato da un dottore
class EchoBot():
    exposed=True
    def __init__(self, token):
        self.tokenBot = token
        self.bot = telepot.Bot(self.tokenBot)
        MessageLoop(self.bot, {'chat': self.on_chat_message}).run_as_thread()
    def on_chat_message(self, msg):
        content_type, chat_type, chat_ID = telepot.glance(msg)
        self.bot.sendMessage(chat_ID, str(chat_ID))
   

if __name__=="__main__":

    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.connect(("8.8.8.8", 80))
    ipaddress = s.getsockname()[0]
    s.close() 

    # Server per la registrazione
    cherrypy.tree.mount(Registrazione(),'/')
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }
    cherrypy.server.socket_host = ipaddress
    cherrypy.tree.mount(Registrazione(),'/',conf)
    cherrypy.config.update(conf)
    cherrypy.engine.start() 
    cherrypy.engine.block() 

    # Telegram per inviare le pagine html per la registrazione
    #conf = json.load(open("C:\\Users\\Giulia\\Desktop\\Progetto IoT condiviso\\CatalogueAndSettings\\settings.json"))
    
    # anto commented here
    # cur_path = os.path.dirname(__file__)
    # new_path = os.path.relpath('..\\CatalogueAndSettings\\settings.json', cur_path)
    # conf = json.load(open(new_path,'settings.json'))
    # end comment

    #conf_file = 'CatalogueAndSettings\\settings.json' #non ci andrebbe settingDoctorTelegram?
    conf_file = 'CatalogueAndSettings\\catalog.json' 
    conf = json.load(open(conf_file))
    token = conf["telegramToken"]
    bot=EchoBot(token)
    print("Bot started ...")
    while True:
        time.sleep(3)


