# SERVER PER LA REGISTRAZIONE DEL PAZIENTE E DEL DOTTORE 
# Il server permette al medico di registrarsi per la prima volta o di inserire un paziente nella sua lista  iscrivendolo

import json                     
import time
import telepot
import cherrypy
import socket
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
            self.telegramID = int(params["chat_ID"])
            filename = 'PageHTML\\doctors.html'
            f1 = open(filename)
            fileContent = f1.read()      
            f1.close()
            return fileContent

        # apertura pagina html per registrazione paziente
        if uri[0] == "registrazione_paziente": 

            self.doctortelegramID = int(params["chat_ID"])
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

        if uri[0] == "lista_pazienti":

            filename = 'CatalogueAndSettings\\catalog.json'
            f4 = open(filename)
            self.catalog = json.load(f4)
            self.lista_pazienti = []
            self.lista = self.catalog["doctorList"]
            for doctorObject in self.lista:
                self.patientList = doctorObject["patientList"]
                for patientObject in self.patientList:
                    self.patientID = patientObject["patientID"]
                    idRegistratoSuRaspberry = patientObject["idRegistratoSuRaspberry"]
                    if idRegistratoSuRaspberry == "no":
                        self.lista_pazienti.append(self.patientID)
            return json.dumps(self.lista_pazienti)

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
            r=requests.post("https://api.thingspeak.com/channels.json",channel)
            
            print(f"Questo è il channel: {r.json()}")
            # self.dicty=r.json()
            # self.api_key_w=self.dicty["api_keys"][0]
            # self.api_keys_write=self.api_key_w["api_key"]
            # self.api_keys_read = self.dicty["api_keys"][1]["api_key"]
            # channel_id=self.dicty["id"]
            channel_id="123"
            self.api_keys_write="abc"
            self.api_keys_read="def"

            self.dictionary = json.load(open('CatalogueAndSettings\\catalog.json'))
            self.LastPatientID = self.dictionary["LastPatientID"]
            self.NewPatientID = self.LastPatientID + 1
            self.dictionary["LastPatientID"] = self.NewPatientID

            if self.RegistraPatientIdSuRaspberry( self.NewPatientID ):
                registratoSuRaspberry = "yes"
            else:
                registratoSuRaspberry = "no"
        
            patient = {
                "patientID": self.NewPatientID,
                "patientName": self.record["patientName"],
                "patientSurname": self.record["patientSurname"],
                "personalData": {
                    "taxIDcode": self.record["taxIDcode"],
                    "userEmail": self.record["userEmail"],
                    "pregnancyDayOne": self.record["pregnancyDayOne"]
                },
                "idRegistratoSuRaspberry": registratoSuRaspberry,
                "connectedDevice": {
                    "deviceName": self.record["deviceName"],
                    "onlineSince": -1,
                    "telegramID": 0,        
                    "thingspeakInfo": {
                    "channel": channel_id,
                    "apikeys": [
                          self.api_keys_write,
                          self.api_keys_read
                    ]
                    }
                }
                }    

            # ricerca del giusto dottore tramite telegram ID già presente nel catalogo e quello da cui si è ricevuto il messaggio per la registrazione 
            trovatoDottore = False
            doctor_number = 0
            dictionary = json.load(open('CatalogueAndSettings\\catalog.json'))
            lista = dictionary["doctorList"]
            for doctorObject in lista:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"] 
                if self.doctortelegramID == telegramID: 
                    trovatoDottore = True
                    break
                doctor_number += 1

            if not trovatoDottore:
                messaggio = f"Dottore non trovato con il telegram ID {self.doctortelegramID}"
                print(messaggio)
                return messaggio
            
            self.dictionary['doctorList'][doctor_number]['patientList'].append(patient)

            # aggiunta del device contemporaneamente al paziente
            device = {
                "deviceName": self.record["deviceName"],
                "patientID": patient["patientID"],
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
            with open('CatalogueAndSettings\\catalog.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            self.lista = self.dictionary["doctorList"][doctor_number]  
            return json.dumps(self.lista) 


    def RegistraPatientIdSuRaspberry( self, NewPatientID ):
        patient = { "ClientID": NewPatientID}   
        try:
            r = requests.post(f'http://{ipAddressRaspberry}:8080/updatepatientid', json.dumps(patient), timeout=5) 
            #r = requests.post(f'http://192.168.1.253:8080/updatepatientid', json.dumps(patient), timeout=5) 
            return True
        except:
            return False


if __name__=="__main__":

    conf_file = 'CatalogueAndSettings\\settings.json' 
    conf = json.load(open(conf_file))
    ipAddressServerRegistrazione = conf["ipAddressServerRegistrazione"]
    ipAddressRaspberry = conf["ipAddressRaspberry"]
    doctortelegramToken = conf["doctortelegramToken"]

    if ipAddressServerRegistrazione == "":
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ipAddressServerRegistrazione = s.getsockname()[0]
        s.close()  

    # Server per la registrazione
    cherrypy.tree.mount(Registrazione(),'/')
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }
    cherrypy.server.socket_host = ipAddressServerRegistrazione
    cherrypy.tree.mount(Registrazione(),'/',conf)
    cherrypy.config.update(conf)
    cherrypy.engine.start() 
    cherrypy.engine.block() 

