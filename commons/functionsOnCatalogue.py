import json
import requests
import time

def get_host_and_port():
    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]
    return ipAddress, port


def http_get_host_and_port(parServiceName):
    # config.json mi dice qual è il server da interrogare
    filename = 'CatalogueAndSettings\\config.json'
    dictionaryCatalog = json.load(open(filename))
    server_ipAddress    = dictionaryCatalog["ipAddress"]
    server_port         = dictionaryCatalog["port"]

    r = requests.get(f'http://{server_ipAddress}:{server_port}/service_by_name?service_name={parServiceName}') 

    service_parameters = r.json()
    serevice_idAddress  = service_parameters["ipAddress"]
    serevice_port       = service_parameters["port"]

    return serevice_idAddress, serevice_port



# Questa raccolta di funzioni http permette (con le chiamate request.get, post e put) 
# di interrogare il MainServer che ha le funzionalità GET e l'accesso al catalogo 

def http_getServiceByName(parServiceName):

    ipAddress, port = get_host_and_port() #presi da config
    r = requests.get(f'http://{ipAddress}:{port}/service_by_name?service_name={parServiceName}') 

    if r.status_code == 200:
        return r.json()
    else:
        return None


def get_service_host_and_port(parServiceName):
    Service = http_getServiceByName(parServiceName)
    ipAddress   = Service["host"]
    port        = Service["port"]
    return Service, ipAddress, port

# da fare anche sugli altri
def http_getMonitoringStateFromClientID(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    monitoring_state_api = get_api_from_service_and_name( ResourceService, "monitoring_state" )

    uri = monitoring_state_api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_retrievePregnancyDayOne(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    pregnancy_state_api = get_api_from_service_and_name( ResourceService, "retrieve_pregnancy_day_one" )

    uri = pregnancy_state_api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/pregnancy_state?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_getNameFromClientID(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "get_name_from_clientID" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/get_name_from_id?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_findDoctorTelegramIdFromPatientId(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "find_doctor_telegram_id_from_patient_id" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/get_telegram_from_id?patient_id={patient_ID}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None


def http_setMonitorinStatefromClientID(patient_ID, monitoring):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "set_monitoring_state_from_client_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 
    local_final_uri = local_uri.replace("{{monitoring}}", monitoring) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/set_monitoring_by_id?patient_id={patient_ID}&monitoring={monitoring}') 

    if r.status_code == 200:
        return (r.text == "OK")
    else:
        return None


def http_findPatientFromChatID(chat_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "find_patient_from_chat_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{chat_ID}}", str(chat_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/find_patient_by_chat_id?chat_id={chat_ID}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None


def http_retrieveTSWriteAPIfromClientID(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "retrieve_TS_write_API_from_client_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/get_ts_from_id?patient_id={patient_ID}') 

    if r.status_code == 200:
        return r.text
    else:
        return None


def http_get_lista_pazienti_simulati():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "get_lista_pazienti_simulati" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 


    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/get_lista_pazienti_simulati') 

    if r.status_code == 200:
        return r.json()
    else:
        return None


def http_contolla_scadenza_week():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "contolla_scadenza_week" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # requests.get(f'http://{ipAddress}:{port}/contolla_scadenza_week') 


def http_get_lista_pazienti_da_monitorare():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "lista_pazienti_da_monitorare" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/lista_pazienti_da_monitorare') 
    
    if r.status_code == 200:
        return r.json()
    else:
        return None


def http_set_patient_in_monitoring(parPatientID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "set_patient_in_monitoring" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.put(f'http://{ipAddress}:{port}/set_patient_in_monitoring?patient_id={parPatientID}') 


def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", parPatientID) #parPatient da passare come stringa
    return local_topic


def get_api_from_service_and_name( parService, parApiName ):
    APIs = parService["APIs"]
    api_found = next((x for x in APIs if x["functionality_name"]==parApiName), None)
    return api_found


# esiste una copia identica in ServerFunctions
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


# da cancellare alla fine, serve solo per inserire il -1 in automatico (quando si debugga è utile)    
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




