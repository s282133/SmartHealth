import json
import sys, os
import json
sys.path.insert(0, os.path.abspath('..'))
import time

def retrievePregnancyDayOne(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    # dictionaryCatalog=json.load(open(filename,'r'))
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                data= _patients["personalData"] 
                filepointer.close()    
                return data["pregnancyDayOne"]
    return None
                

def retrieveOnlineSince(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                device=_patients["connectedDevice"]
                filepointer.close()
                return device["onlineSince"]
    return None


def retrieveTSReadAPIfromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                connectedDevice = _patients["connectedDevice"]
                #print(f"connectedDevice: {connectedDevice}")
                thingspeakInfo = connectedDevice["thingspeakInfo"]
                #print(f"thingspeakInfo: {thingspeakInfo}")                
                api_keys = list(thingspeakInfo["apikeys"])
                #print(f"api_keys: {api_keys}")  
                filepointer.close()                 
                return api_keys[1]
    return None


def retrieveTSWriteAPIfromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                #data= _patients["connectedDevice"]["thingspeakInfo"]["apikeys"][0]
                connectedDevice = _patients["connectedDevice"]
                #print(f"connectedDevice: {connectedDevice}")
                thingspeakInfo = connectedDevice["thingspeakInfo"]
                #p(f"thingspeakInfo: {thingspeakInfo}")                
                api_keys = list(thingspeakInfo["apikeys"])
                #print(f"api_keys: {api_keys}")        
                filepointer.close()          
                return api_keys[0]
    return None


def findDoctorIDwithtelegramID(doctortelegramID):
    dictionary = json.load(open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json','r'))
    lista = dictionary["resources"]
    for doctorObject in lista:
        connectedDevice = doctorObject["connectedDevice"]
        telegramID = connectedDevice["telegramID"] 
        if doctortelegramID == telegramID: 
            doctorID = doctorObject["doctorID"] 
            return doctorID
    return None


def findPatient(chat_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    f = open(filename)
    catalog = json.load(f)

    lista = catalog["resources"]
    for doctorObject in lista:
        patientList = doctorObject["patientList"]
        for userObject in patientList:
            connectedDevice = userObject["connectedDevice"] 
            telegramID = connectedDevice["telegramID"]
            if  chat_ID == telegramID:
                patientID = userObject["patientID"] 
                return patientID   
    return None


def findDoctorTelegramIdFromPatientId(parPatientID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    catalog = json.load(filepointer)

    lista = catalog["resources"]
    for doctorObject in lista:
        patientList = doctorObject["patientList"]
        for userObject in patientList:
            patientID = userObject["patientID"] 
            if  patientID == parPatientID:
                connectedDevice = doctorObject["connectedDevice"]
                telegramID = connectedDevice["telegramID"]
                return telegramID    
    return None
    

def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) #parPatient da passare come stringa
    return local_topic


def getNameFromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                patientName=_patients["patientName"]
                patientSurname=_patients["patientSurname"]
                filepointer.close()
                return f"{patientName} {patientSurname}"
    return None


def getMonitoringStateFromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename, 'r')
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                monitoring=_patients["monitoring"]
                filepointer.close()
                return monitoring
    return None


def setMonitorinStatefromClientID(patient_ID, monitoring):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename)
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                _patients["monitoring"] = monitoring
                filepointer.close()
                with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                    json.dump(dictionaryCatalog, f, indent=2)
                return True    
    return False
         

def main_getServiceByName(parServiceName):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    dictionaryCatalog = json.load(open(filename))
    services = dictionaryCatalog["services"]

    first_or_default = next((x for x in services if x["service_name"]==parServiceName), None)
    return first_or_default 


def main_getApiByServiceAndName(parAPIs,parApiName):
    first_or_default = next((x for x in parAPIs if x["functionality_name"]==parApiName), None)
    return first_or_default 


def main_getApiByName(parServiceName,parApiName):
    mqtt_service = main_getServiceByName(parServiceName)
    if mqtt_service != None:
        api = mqtt_service["APIs"]
        first_or_default = next((x for x in api if x["functionality_name"]==parApiName), None)
        return first_or_default 
    else: 
        return None
