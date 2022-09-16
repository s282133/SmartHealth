
#!!!!IMPORTANTEEEE CAMBIA IL NOME DELL'IPADDRESS NEL CONFIG!!!

from gettext import Catalog
import json                     
import time
import cherrypy
import requests



from functionsOnCatalogue import *
from customExceptions import *

#from jinja2 import Template
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton

class FrontEnd:
    exposed=True
    
    def __init__(self, catalog_address):
        self.catalog_address=catalog_address
        
    
    def GET(self,*uri,**params):

# start : apertura pagina html per registrazione dottore 
        if uri[0] == "registrazione_dottore":
          
      
            self.telegramID = int(params["chat_ID"])
            filename = 'doctors.html'
            f1 = open(filename)
            fileContent = f1.read()      
            f1.close() 
            return fileContent
            
        # elif uri[0] == "login_dottore":
        #     filename = 'login_dottore.html'
        #     f2= open(filename)
        #     fileContent2 = f2.read()      
        #     f2.close() 
        #     return fileContent2
            
        
           
    
# registrazione_paziente : apertura pagina html per registrazione paziente
        elif uri[0] == "registrazione_paziente": 
            self.telegramID= int(params["chat_ID"]) 
            filename = 'patients.html'
            f3 = open(filename)
            fileContent = f3.read()      
            f3.close()
            return fileContent
        
        
        elif uri[0] == "tabella_pazienti": 
            resp = requests.get(f"{self.catalog_address}/{uri[0]}?chat_ID={self.telegramID}")
            return resp
        
    def POST(self,*uri,**params):
        
        #print(self.telegramID)  DEBUG
        body = json.loads(cherrypy.request.body.read())
        resp = requests.post(f"{self.catalog_address}/{uri[0]}?chat_ID={self.telegramID}", json=body)
        # qualsiasi sia l'uri lo manda direttamente al MainServer, così non bisogna modificarlo
        return resp
        
        
if __name__=="__main__":
    
   # attivazione microservizio per ottenere l'host del server
    frontend_service = http_getServiceByName("FrontEnd")
    server_host = frontend_service["host"]
    server_port =frontend_service["port"]
    # PROVARE QUESTO SE CON L'IP ADDRESS NON FUNZIONA
    
    # localhost=get_localhost()
    # ipAddress, port=get_host_and_port()
    # catalog_address= f"http://{localhost}:{port}"
    
    ipAddress, port=get_host_and_port()
    catalog_address= f"http://{ipAddress}:{port}"

    cherrypy.tree.mount(FrontEnd(catalog_address),'/')
    conf={
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tools.sessions.on':True
        }
    }

    cherrypy.tree.mount(FrontEnd(catalog_address),'/',conf)
    cherrypy.config.update({'server.socket_host': server_host ,  
                            'server.socket_port': server_port})
                            
    cherrypy.engine.start() 
    cherrypy.engine.block() 