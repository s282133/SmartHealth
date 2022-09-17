# Il MainServer contiene tutte le funzioni GET, PUT, POST che servono per la gestione del catalogo in remoto

from gettext import Catalog                          
import json                     
import time
import cherrypy
import requests


from MyMQTT import *
from ServerFunctions import *
from customExceptions import *

#from jinja2 import Template
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class Registrazione(object):
    exposed=True
    
    def __init__(self):
        pass                      
    def GET(self,*uri,**params):

# get_raspberry_parameters: mandare al raspberry il servizio da utilizzare
        if uri[0] == "get_raspberry_parameters":
        
            try:
                mqtt_service = main_getServiceByName("MQTT_analysis")
                mqtt_broker = mqtt_service["broker"]
                mqtt_port = mqtt_service["port"]
                mqtt_base_topic = mqtt_service["base_topic"]

                if mqtt_service == None:
                    raise ServiceUnavailableException
                else:
                    try:
                        api_updatepatient = main_getApiByServiceAndName(mqtt_service["APIs"],"temp_raspberry") 
                        if(api_updatepatient == None):
                            raise ApiUnavailableException
                        topic = api_updatepatient["topic"]

                        # da cambiare con jinja
                        #"{{base_topic}}/{{patientID}}/temp_raspberry"
                        local_topic = topic.replace("{{base_topic}}", mqtt_base_topic)
                        
                        #print(f"topic template: {topic}, local_topic : {local_topic}")
                        #local_topic = Template.render()
                        # boh non mi stampa il topic, non so

                        mqtt_service = {
                            "broker": mqtt_broker,
                            "port": mqtt_port,
                            "topic": local_topic
                        }
                        
                        return json.dumps(mqtt_service) 

                    except ApiUnavailableException:
                        print("MainServer - error [ERR 4]")
                        exit(4)

            except ServiceUnavailableException:
                print("MainServer - error [ERR 5]")
                exit(5)
            except: 
                print("MainServer - error [ERR 6]")
                exit(6)
      
        elif uri[0] == "get_user_localhost":
            catalog = openCatalogue()
            localhost = catalog["user_localhost"]
            return localhost

# service_by_name: restituisce il servizio dal nome del servizio
        elif uri[0] == "service_by_name":
            try:
                service_name = params["service_name"]

                resouce_filename = 'ServicesAndResourcesCatalogue.json'

                catalog = json.load(open(resouce_filename))
                #time.sleep(1)
                services = catalog["services"]

                service = next((x for x in services if x["service_name"]==service_name), None)

                if service != None:
                    return json.dumps(service)
                else:
                    raise cherrypy.HTTPError(500, "Service not found")
            except Exception as inst:
                # print(type(inst))    
                # print(inst.args)     
                print(inst)          
                raise cherrypy.HTTPError(500, "Service not found exception")        


# api_by_name: restituisce l'api dando il nome dle servizio e quello dell'api
        elif uri[0] == "api_by_name":
            service_name = params["service_name"]
            api_name = params["api_name"]
            api = main_getApiByName(service_name,api_name)
            if api != None:
                return json.dumps(api)
            else:
                raise cherrypy.HTTPError(500, "Api not found")


# monitoring_state: restituisce lo stato di monitoraggio in cui è il paziente (on o off) 
        elif uri[0] == "monitoring_state":
            patient_ID = params["patient_id"]
            MonitoringState = getMonitoringStateFromClientID(patient_ID)
            if MonitoringState != None:
                return MonitoringState
            else:
                raise cherrypy.HTTPError(500, "Monitoring State not found")


# pregnancy_state: restituisce il dayOne di gravidanza 
        elif uri[0] == "pregnancy_state":
            patient_ID = params["patient_id"]
            dayOne = retrievePregnancyDayOne(patient_ID)
            if dayOne != None:
                return dayOne
            else:
                raise cherrypy.HTTPError(500, "Pregnancy State not found")
            
            
# # get_registrazion_confirm: restituisce se il dottore è presente o meno
#         elif uri[0] == "get_registrazion_confirm":
#             chat_ID = params["chat_ID"]
#             trovato = get_registrazion_confirm_from_chat_ID(chat_ID)
#             print(f"trovato: {trovato}")
#             return int(trovato)


# get_name_from_id: restituisce il nome del paziente dal suo ID 
        elif uri[0] == "get_name_from_id":
            patient_ID = params["patient_id"]
            name = getNameFromClientID(patient_ID)
            if name != None:
                return name
            else:
                raise cherrypy.HTTPError(500, "Name not found")


# get_telegram_from_id: restituisce il telegram ID del dottore dall'ID del paziente  
        elif uri[0] == "get_telegram_from_id":
            patient_ID = params["patient_id"]
            telegram_id = findDoctorTelegramIdFromPatientId(patient_ID)
            if telegram_id != None:
                return str(telegram_id)
            else:
                raise cherrypy.HTTPError(500, "Telegram ID not found")
          

# set_monitoring_by_id: restituisce il monitoring del paziente dal suo ID 
        elif uri[0] == "set_monitoring_by_id":
            try:
                patient_ID = params["patient_id"]
                monitoring = params["monitoring"]

                success = setMonitorinStatefromClientID(patient_ID, monitoring)
                if success:
                    return "OK"
                else:
                    raise cherrypy.HTTPError(500, "Patient not found")
            except Exception as inst:
                # print(type(inst))    
                # print(inst.args)     
                print(inst)          
                raise cherrypy.HTTPError(500, "Service not found exception")        


# find_patient_by_chat_id: restituisce il paziente dal suo ID 
        elif uri[0] == "find_patient_by_chat_id":
            chat_ID = params["chat_id"]
            patient_ID = findPatientFromChatID(chat_ID)
            if patient_ID != None:
                return str(patient_ID)
            else:
                raise cherrypy.HTTPError(500, "Patient not found")


# get_ts_from_id: restituisce l'API di scrittura di thingspeak del paziente dal suo ID 
        elif uri[0] == "get_ts_from_id":
            patient_ID = params["patient_id"]
            print(f"patient_ID: {patient_ID}")
            api_keys = retrieveTSWriteAPIfromClientID(patient_ID)
            
            if patient_ID != None:
                return api_keys
            else:
                raise cherrypy.HTTPError(500, "Patient not found")

        elif uri[0] == "get_ts_patientIDs_channelIDs":
            dict = getListsOfTSinfo()
            return dict


# get_lista_pazienti_simulati: restituisce lista dei pazienti con raspberry simulati per l'invio delle temperature
        elif uri[0] == "get_lista_pazienti_simulati":
            lista_pazienti = get_lista_pazienti_simulati()
            return lista_pazienti

# da cancellare se facciamo il delete
# contolla_scadenza_week: controllo sulla week
        elif uri[0] == "contolla_scadenza_week":
            contolla_scadenza_week()            


# lista_pazienti_da_monitorare: restituisce lista dei pazienti
        elif uri[0] == "lista_pazienti_da_monitorare":
            try:
                lista_pazienti_da_monitorare = get_lista_pazienti_da_monitorare()
                return lista_pazienti_da_monitorare
            except:
                raise cherrypy.HTTPError(500, "List of patients unavailable")

# paziente della tabella a partire dal telegramID del medico
        elif uri[0] == "tabella_pazienti":
            self.doctortelegramID=int(params['chat_ID'])
            tab_pazienti=get_patient_from_doctortelegram_id(self.doctortelegramID)
            return tab_pazienti
    
    def PUT(self,*uri,**params):

# aggiorna i pazienti a stato di monitoraggio (da -1 a monitorato)       
        if uri[0] == "set_patient_in_monitoring": 
            patient_ID = params["patient_id"]
            set_lista_pazienti_in_monitoring(patient_ID)


# update_telegram_id: aggiorna il telegram ID dopo che il paziente ha risposto al messaggio /start
        elif uri[0] == "update_telegram_id":
            chat_id = params["chat_id"]
            patient_id = params["patient_id"]

            filename = 'ServicesAndResourcesCatalogue.json'
            f = open(filename)
            self.catalog = json.load(f)
            self.lista = self.catalog["resources"]
            for doctorObject in self.lista:
                patientList = doctorObject["patientList"]
                for patientObject in patientList:
                    patientID = patientObject["patientID"]
                    if patientID == int(patient_id):
                        connectedDevice = patientObject["connectedDevice"]
                        connectedDevice["telegramID"]=chat_id
                        with open('ServicesAndResourcesCatalogue.json', "w") as f:
                            json.dump(self.catalog, f,indent=2)
                        return "OK"
            return "Paziente non trovato"
        
        

    def POST(self,*uri,**params):
        
# doctors: aggiungere un dottore alla lista di dottori al SUBMIT
        if uri[0] == "doctors": 
            
            body = cherrypy.request.body.read() 
            self.record = json.loads(body)
            self.telegramID = int(params["chat_ID"]) #lo leggo dal FrontEND
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

            self.dictionary = json.load(open('ServicesAndResourcesCatalogue.json'))

            self.LastDoctorID = self.dictionary["resourceState"]["LastDoctorID"]
            doctor["doctorID"] = self.LastDoctorID + 1
            self.dictionary["resourceState"]["LastDoctorID"] = self.LastDoctorID + 1

            self.dictionary["resources"].append(doctor) 
            # PROBLEMA (02-06-2022) : se parto dal catalog.json vuoto, non riesco a salvare il dottore

            with open('ServicesAndResourcesCatalogue.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            return json.dumps(self.dictionary)


# patients: aggiungere un paziente alla lista dei pazienti al SUBMIT
        if uri[0] == "patients": 

            body = cherrypy.request.body.read() 
            self.record = json.loads(body)
            self.telegramID = int(params["chat_ID"]) #lo leggo dal FrontEND   
            #prova
            self.dictionary = json.load(open('ServicesAndResourcesCatalogue.json'))
            self.LastPatientID = self.dictionary["resourceState"]["LastPatientID"]                                                        
            # nameChannel = self.record["patientName"] + " " + self.record["patientSurname"]
            nameChannel=self.LastPatientID+1

            ## ATTENZIONE: mettere api key in settings!
            channel={
                "api_key":"OEUWTU8AH5MOIMKZ",
                "name": nameChannel,
                "field1": "heart rate",
                "field2": "pressure_high",
                "field3": "glycemia",    
                "field4": "pressure_low",            
                "field5": "peso",
                "field6": "temperature",
                "public_flag":True
                }   
            # r=requests.post("https://api.thingspeak.com/channels.json",channel)
            api=main_getApiByName("Thingspeak","create_channel_thingspeak")
            local_uri=api["uri"]
            print(f"localuri:{local_uri}")
            #r=requests.post("https://api.thingspeak.com/channels.json",channel)
            r=requests.post(local_uri,channel)

            print(f"Questo è il channel: {r.json()}")
            self.dicty=r.json()
            self.api_key_w=self.dicty["api_keys"][0]
            self.api_keys_write=self.api_key_w["api_key"]
            self.api_keys_read = self.dicty["api_keys"][1]["api_key"]
            channel_id=self.dicty["id"]

            self.dictionary = json.load(open('ServicesAndResourcesCatalogue.json'))
            self.LastPatientID = self.dictionary["resourceState"]["LastPatientID"]
    
            self.NewPatientID = self.LastPatientID + 1
            self.dictionary["resourceState"]["LastPatientID"] = self.NewPatientID

            self.returnCode = 0
            result = self.RegistraPatientIdSuRaspberry( self.NewPatientID )
            if result == 1:
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
                "state": "attivo",
                "monitoring": "off",
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

            # ATTENZIONE: ricerca del giusto dottore tramite telegram ID DA TRASFORMARE in funzione  

            ## ATTENZIONE: qui ci vuole un try except (DoctorNotFoundException)

            trovatoDottore = False
            doctor_number = 0
            dictionary = json.load(open('ServicesAndResourcesCatalogue.json'))
            lista = dictionary["resources"]
            for doctorObject in lista:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID1 = connectedDevice["telegramID"] # modificato
                if self.telegramID == telegramID1: 
                    trovatoDottore = True
                    break
                doctor_number += 1

            if not trovatoDottore:
                messaggio = f"Dottore non trovato con il telegram ID {self.telegramID}"
                print(messaggio)
                return messaggio
            
            self.dictionary["resources"][doctor_number]['patientList'].append(patient)

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
                    "raspberry_mqtt",
                    "raspberry_rest"
                ],
                "activeService": "application_to_raspberry",
                "activeProtocol": "mqtt",
                "lastUpdate": time.strftime("%Y-%m-%d")
            }

            self.dictionary["resources"][doctor_number]['devicesList'].append(device)
            with open('ServicesAndResourcesCatalogue.json', "w") as f:
                json.dump(self.dictionary, f, indent=2)
            self.lista = self.dictionary["resources"][doctor_number]  
            return json.dumps(self.lista) 

    def DELETE(self,*uri,**params):
        
        if uri[0] == "delete_ex_patients":
            delete_ex_patients()   

    def RegistraPatientIdSuRaspberry( self, NewPatientID ):
        json_post = rasp_json.replace("{{NewPatientID}}",str(NewPatientID),1)
        try:
            uri = f'http://{rasp_ipAddress}:{rasp_port}/{rasp_uri}'
            r = requests.post(uri, json_post, timeout=5) 
            if r.text == 'OK':
                return 1
            else:    
                return 0
        except: return -1
        
    



if __name__=="__main__":

    ## ATTENZIONE: qui ci vuole un try except per il servizio non trovato (ServiceUnavailableException)
    
    # attivazione microservizio per la registrazione dei parametri per il raspberry 
    PatientRegistrationOnRaspberry = main_getServiceByName("PatientRegistrationOnRaspberry")
    if PatientRegistrationOnRaspberry == None:
        print("Service not found")
        exit(-1)

    rasp_ipAddress  = PatientRegistrationOnRaspberry["host"]
    rasp_port       = PatientRegistrationOnRaspberry["port"]

    try:
        api_updatepatient = main_getApiByServiceAndName(PatientRegistrationOnRaspberry["APIs"],"updatepatient") 
        rasp_uri    = api_updatepatient["uri"]
        rasp_json   = api_updatepatient["json_post"]


        # attivazione microservizio per ottenere l'host del server
        try:
            catalog = openCatalogue()
            server_host = catalog["server_host"]
            server_port = catalog["server_port"]
               
            resetCatalog() #mette -1 a tutto

            cherrypy.tree.mount(Registrazione(),'/')
            conf={
                '/':{
                    'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
                    'tools.sessions.on':True
                }
            }
            cherrypy.server.socket_host = server_host
            cherrypy.server.socket_port = server_port
            cherrypy.tree.mount(Registrazione(),'/',conf)
            cherrypy.config.update({'server.socket_host': server_host ,  
                            'server.socket_port': server_port })
            cherrypy.engine.start() 
            cherrypy.engine.block() 
        except:
            print("Catalogue could not be opened")
            exit(-2)
    except:
        print("Service not found")
        exit(-3)
