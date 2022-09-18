from ipaddress import ip_address
import json
import requests
import time

# Questa raccolta di funzioni http permette (con le chiamate request.get, post, put e delete 
# di interrogare il MainServer che ha le funzionalità GET e l'accesso al catalogo 

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

# prende dal config.json l'ipadress e la porta del MainServer
def get_host_and_port():
    filename = 'config.json'
    dictionaryCatalog = json.load(open(filename))
    ipAddress = dictionaryCatalog["ipAddress"]
    port = dictionaryCatalog["port"]
    return ipAddress, port

# prende il localhost dal catalogo
def http_get_localhost():                       
    TelegramDoctor, ipAddress, port = get_service_host_and_port("TelegramDoctor")    
    return ipAddress

# trova lo user localhost dal catalogo
def http_get_user_localhost():
    TelegramDocBotService, ipAddress, port = get_service_host_and_port("ResourceService")
    monitoring_state_api = get_api_from_service_and_name( TelegramDocBotService, "get_user_localhost" )
    local_uri = monitoring_state_api["uri"]
    r = requests.get(f'http://{ipAddress}:{port}/{local_uri}') 
    if r.status_code == 200:
        return r.text
    else:
        return None

# cerca gli host e le porte dei servizi in base al nome
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


def get_service_host_and_port(parServiceName):
    Service = http_getServiceByName(parServiceName)
    ipAddress   = Service["host"]
    port        = Service["port"]
    return Service, ipAddress, port

# prende lo stato di monitoraggio on/off dal patientID
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

# trova il telegramID del dottore corrispondente a partire dal patientID
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

    r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    if r.status_code != 200:
        r = requests.get(f'http://{ipAddress}:{port}/{local_final_uri}',timeout=5) 

    # ipAddress, port = get_host_and_port()
    # r = requests.get(f'http://{ipAddress}:{port}/set_monitoring_by_id?patient_id={patient_ID}&monitoring={monitoring}') 

    if r.status_code == 200:
        return (r.text == "OK")
    else:
        return None

# trova il paziente dal suo telegramID
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

# trova la WRITE API di Thingspeak dal patientID
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


def http_delete_ex_patients():

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "delete_ex_patients" )

    local_uri = api["uri"]

    r = requests.delete(f'http://{ipAddress}:{port}/{local_uri}') 
     # requests.get(f'http://{ipAddress}:{port}/delete_ex_patients')  


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

    uri = api["uri"]
    local_uri = uri.replace("{{patient_ID}}", str(parPatientID)) 

    r = requests.put(f'http://{ipAddress}:{port}/{local_uri}') 

    # ipAddress, port = get_host_and_port()
    # r = requests.put(f'http://{ipAddress}:{port}/set_patient_in_monitoring?patient_id={parPatientID}') 

# aggiorna il telegramID del paziente appena si iscrive
def http_Update_PatientTelegramID(chat_ID, message):

    ResourceService, ipAddress, port = get_service_host_and_port("ResourceService")
    api = get_api_from_service_and_name( ResourceService, "update_chat_id" )

    uri = api["uri"]
    local_uri = uri.replace("{{chat_ID}}", str(chat_ID)) 
    local_final_uri = local_uri.replace("{{message}}", str(message)) 

    r = requests.put(f'http://{ipAddress}:{port}/{local_final_uri}') 

    #r = requests.get(f'http://{ipAddress}:{port}/update_telegram_id?patient_id={message}&chat_id={chat_ID}') 

    if r.text == "OK":
        return True
    else:
        return False


def getTopicByParameters(parTopic, parBaseTopic, parPatientID):
    #"topic_temperature": "{{base_topic}}/{{patientID}}/temperature",
    local_topic = parTopic.replace("{{base_topic}}", parBaseTopic)
    local_topic = local_topic.replace("{{patientID}}", str(parPatientID)) #parPatient da passare come stringa
    return local_topic


def get_api_from_service_and_name( parService, parApiName ):
    APIs = parService["APIs"]
    api_found = next((x for x in APIs if x["functionality_name"]==parApiName), None)
    return api_found


# esiste una copia identica in ServerFunctions
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


