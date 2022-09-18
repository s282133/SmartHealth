from ipaddress import ip_address
import json
import requests
import time

# Questa raccolta di funzioni http permette (con le chiamate request.get, post, put e delete 
# di interrogare il MainServer che ha le funzionalità GET, POST, PUT E DELETE e l'accesso al catalogo.


# restituisce il patientID e il channelID dal canale di Thingspeak
def http_retrieveTSpatientIDsAndChannelIDs():
    
    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "retrieve_TS_patientIDs_channelIDs" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 
    if r.status_code == 200:
        return r.text
    else:
        print("http_retrieveTSpatientIDsAndChannelIDs returned status code different from 200")
        return None

# resituisce dal config.json l'ip_adress e la porta del Catalog
def get_host_and_port():
    filename = 'config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]
    return ipAddress, port

# restituisce lo user localhost nel catalog
def http_get_user_localhost():
    TelegramDocBotService, ipAddress, port = get_service_host_and_port("ResourceService")
    monitoring_state_api = get_api_from_service_and_name( TelegramDocBotService, "get_user_localhost" )
    local_uri = monitoring_state_api["uri"]
    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 
    if r.status_code == 200:
        return r.text
    else:
        return None

# restituisce gli host e le porte dei servizi in base al suo nome
def http_get_host_and_port(parServiceName): 
    filename = 'config.json'
    dictionaryCatalog = json.load(open(filename))
    server_ipAddress    = dictionaryCatalog["ipAddress"]
    server_port         = dictionaryCatalog["port"]

    r = requests.get(f'http://{server_ipAddress}:{server_port}/service_by_name?service_name={parServiceName}') 

    service_parameters = r.json()
    serevice_idAddress  = service_parameters["ipAddress"]
    serevice_port       = service_parameters["port"]

    return serevice_idAddress, serevice_port

# resituisce l'intero servizio dal nome del servizio
def http_getServiceByName(parServiceName):

    ipAddress, port = get_host_and_port() 
    r = requests.get(f'http://{ipAddress}:{port}/service_by_name?service_name={parServiceName}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/service_by_name?service_name={parServiceName}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/service_by_name?service_name={parServiceName}',timeout=5) 

    if r.status_code == 200:
        return r.json()
    else:
        return None

# restuisce il servizio, l'host e la porta dal nome del servizio
def get_service_host_and_port(parServiceName):
    Service = http_getServiceByName(parServiceName)
    ipAddress   = Service["host"]
    port        = Service["port"]
    return Service, ipAddress, port

# restuisce lo stato di monitoraggio on/off dal patientID
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

    if r.status_code == 200:
        return r.text
    else:
        return None

# restuisce il telegramID del dottore a partire dall'ID del paziente
def http_findDoctorTelegramIdFromPatientId(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "find_doctor_telegram_id_from_patient_id" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None

# imposta lo stato del monitoraggio (on/off)
def http_setMonitorinStatefromClientID(patient_ID, monitoring):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "set_monitoring_state_from_client_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 
    local_final_uri = local_uri.replace("{{monitoring}}", monitoring) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    if r.status_code == 200:
        return (r.text == "OK")
    else:
        return None

# restituisce il paziente a partire dal telegramID
def http_findPatientFromChatID(chat_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "find_patient_from_chat_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{chat_ID}}", str(chat_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    if r.status_code == 200:
        return int(r.text)
    else:
        return None

# restituisce la WRITE API di Thingspeak dal patientID
def http_retrieveTSWriteAPIfromClientID(patient_ID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "retrieve_TS_write_API_from_client_ID" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(patient_ID)) 

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 
    
    if r.status_code == 200:
        return r.text
    else:
        return None

# restituisce la lista di pazienti non associati al raspberry per cui dev'essere simulata la temperatura
def http_get_lista_pazienti_simulati():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "get_lista_pazienti_simulati" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 

    if r.status_code == 200:
        return r.json()
    else:
        return None

# elimina i pazienti 
def http_delete_ex_patients():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "delete_ex_patients" )

    local_uri = api["uri"]

    r = requests.delete(f'http://{ipAddress}:{port}/{local_uri}') 

# restituisce la lista pazienti da monitorare 
def http_get_lista_pazienti_da_monitorare():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "lista_pazienti_da_monitorare" )

    local_uri = api["uri"]

    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 
    
    if r.status_code == 200:
        return r.json()
    else:
        return None

# imposta l'onlineSince per iniziare a registrare le misure
def http_set_patient_in_monitoring(parPatientID):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "set_patient_in_monitoring" )

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(parPatientID)) 

    r = requests.put(f'http://{ipAddress}:{port}/{local_uri}') 


# aggiorna il telegramID del paziente appena si iscrive
def http_Update_PatientTelegramID(chat_ID, message):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "update_chat_id" )

    uri = api["uri"]
    local_uri = uri.replace("{{chat_ID}}", str(chat_ID)) 
    local_final_uri = local_uri.replace("{{message}}", str(message)) 

    r = requests.put(f'http://{ipAddress}:{port}/{local_final_uri}') 

    if r.text == "OK":
        return True
    else:
        return False


def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", str(parPatientID)) 
    return local_topic


def get_api_from_service_and_name( parService, parApiName ):
    APIs = parService["APIs"]
    api_found = next((x for x in APIs if x["functionality_name"]==parApiName), None)
    return api_found

# restituisce la settimana di gravidanza
def getWeek(dayOne):
    currTime = time.strftime("%Y-%m-%d")
    currY = currTime.split("-")[0]
    currM = currTime.split("-")[1]
    currD = currTime.split("-")[2]
    currDays = int(currY)*365 + int(currM)*30 + int(currD)
    dayoneY = str(dayOne).split("-")[0]
    dayoneM = str(dayOne).split("-")[1]
    dayoneD = str(dayOne).split("-")[2]
    dayoneDays = (int(dayoneY) * 365) + (int(dayoneM) * 30) + int(dayoneD)
    elapsedDays = currDays - dayoneDays
    week = int(elapsedDays / 7)
    return week


