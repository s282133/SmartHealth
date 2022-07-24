import json
import requests
import time

def http_getServiceByName(parServiceName):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/service_by_name?service_name={parServiceName}') 

    if r.status_code == 200:
        return r.json()
    else:
        return None


def http_getApiByName(parServiceName,parApiName):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/api_by_name?service_name={parServiceName}&api_name={parApiName}') 

    if r.status_code == 200:
        return r.json()
    else:
        return None


def http_getMonitoringStateFromClientID(patient_ID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/monitoring_state?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_retrievePregnancyDayOne(patient_ID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/pregnancy_state?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_getNameFromClientID(patient_ID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/get_name_from_id?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_findDoctorTelegramIdFromPatientId(parPatientID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/get_telegram_from_id?patient_id={parPatientID}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None


def http_setMonitorinStatefromClientID(patient_ID, monitoring):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/set_monitoring_by_id?patient_id={patient_ID}&monitoring={monitoring}') 

    if r.status_code == 200:
        return (r.text == "OK")
    else:
        return None


def http_findPatient(chat_ID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/find_patient_by_chat_id?chat_id={chat_ID}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None


def http_retrieveTSWriteAPIfromClientID(patient_ID):

    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]

    # interroga il server serverRegistation che ha le funzionalità GET e l'accesso al catalogo 
    r = requests.get(f'http://{ipAddress}:{port}/get_ts_from_id?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) #parPatient da passare come stringa
    return local_topic


def getWeek(dayOne):
    print(f"dayone = {dayOne}")
    currTime = time.strftime("%Y-%m-%d")
    currY = currTime.split("-")[0]
    currM = currTime.split("-")[1]
    currD = currTime.split("-")[2]
    #print(f"currY: {currY}, currM: {currM}, currD: {currD}")
    currDays = int(currY)*365 + int(currM)*30 + int(currD)
    #print(f"DataAnalysisBlock: current day is {currDays}")

    #print(f"DataAnalysisBlock: clientID : {self.clientID}" )      
    #print(f"DataAnalysisBlock: dayOne : {dayOne}")
    dayoneY = str(dayOne).split("-")[0]
    dayoneM = str(dayOne).split("-")[1]
    dayoneD = str(dayOne).split("-")[2]
    #print(f"dayoneY: {dayoneY}, dayoneM: {dayoneM}, dayoneD: {dayoneD}")
    dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
    #print(f"dayoneDays of {self.clientID} is {dayoneDays}")

    elapsedDays = currDays - dayoneDays
    week = int(elapsedDays / 7)
    return week

    
def setOnlineSinceFromClientID(patient_ID):
    filename = 'CatalogueAndSettings\\ServicesAndResourcesCatalogue.json'
    filepointer = open(filename)
    dictionaryCatalog = json.load(filepointer)
    docList=dictionaryCatalog["resources"]
    for _doctors in docList:
        patientList=_doctors["patientList"] 
        for _patients in patientList: 
            if patient_ID == _patients["patientID"]:
                _patients["connectedDevice"]["onlineSince"] = -1
                filepointer.close()
                with open('CatalogueAndSettings\\ServicesAndResourcesCatalogue.json', "w") as f:
                    json.dump(dictionaryCatalog, f, indent=2)