import time
import cherrypy
import json
import requests

#if __name__ == "__main__":

class temperatureSensorClass():
    
    def getTemperature(self):
        done=False
        while not done:
            time.sleep(3)

            r = requests.get('http://127.0.0.1:8080/temperature') 
            # per raspberry: decommenta la prossima riga e commenta la precedente
            # r = requests.get('http://192.168.1.254:8080/'+st_parametro) #collegarsi al programma che è in esecuzione su quell'indirizzo ip attraverso una chiamata get

            j_temp = r.json() 

            vett = j_temp['e']
            primo = vett[0]
            temp = float(primo['v'])

            print('Temperatura ' + str(cont) + ': ' + str(temp))



