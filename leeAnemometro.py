#!/usr/bin/python
"""Lee la velocidad de un anemómetro por Modbus y publica máximos en MQTT."""

import configparser as ConfigParser
import json
import logging
import sys
import time

import minimalmodbus
import paho.mqtt.client as mqttClient
import serial


def on_connect(client, userdata, flags, rc):
    # Registra si el cliente MQTT pudo conectarse al broker.
    if rc == 0:
      #  print("Connected to broker")
        global Connected                #Use global variable
        Connected = True                #Signal connection 
    else:
        print("Connection failed")

def convert_data(VIE):
    # Prepara los campos que se enviarán como mensaje JSON.
    # pull out the data elements into a list  and replace the code with the json field name
    ev=[]
    ev.insert(0,['Planta',planta])
    ev.insert(1,['Inverter',0])
    ev.insert(2,['Linea',0])
    ev.insert(3,['VIE',VIE])
    return (dict(ev))

def main():
    global Connected, planta
    try:
        # Carga la configuración del anemómetro, los logs y la conexión MQTT.
        cfg = ConfigParser.ConfigParser()
        if not cfg.read("config.cfg"):
        #    logger.warning("No existe el archivo de configuracion")
            sys.exit(0)
            
        # Configura dónde guardar los logs y qué nivel de mensajes registrar.
        logging.getLogger()
        # Obtiene del archivo de configuración el directorio de los logs.
        fichero_log=cfg.get("debug","directorio_log")+'VientoLog.log'
        #En el fichero config se puede hacer que saque más o menos logs, poniendo WARNING o ERROR
        if cfg.get("debug", "debug") == 'WARNING':
            logging.basicConfig(filename=fichero_log,
                                level=logging.WARNING, format='%(asctime)s %(message)s')
        else:
            logging.basicConfig(filename=fichero_log,
                                level=logging.ERROR, format='%(asctime)s %(message)s')
        logging.getLogger().addHandler(logging.StreamHandler(sys.stdout))


        # Conecta con el broker y espera la confirmación antes de medir.
        Connected = False   #global variable for the state of the connection
        broker_address= cfg.get("MQTT", "broker_address")
        port = cfg.getint("MQTT", "port")
        user = cfg.get("MQTT", "user")
        password = cfg.get("MQTT", "password")

        intervalo= cfg.getint("viento", "intervalo") #tiempo entre lecturas
        pausa=cfg.getint("viento", "pausa") #tiempo entre envíos

        instrument = minimalmodbus.Instrument(cfg.get("viento", "port"), cfg.getint("viento", "dir_MODBUS"))
        instrument.serial.baudrate = cfg.getint("viento", "baudrate")
        instrument.serial.bytesize = cfg.getint("viento", "bytesize")
        instrument.serial.parity = serial.PARITY_EVEN
        instrument.serial.stopbits = cfg.getint("viento", "stopbits")
        instrument.serial.timeout = cfg.getint("viento", "timeout")
        instrument.debug = cfg.getboolean("viento", "debug")
        instrument.mode = minimalmodbus.MODE_RTU
        instrument.serial.rtscts = cfg.getboolean("viento", "rtscts")
        instrument.handle_local_echo = cfg.getboolean("viento", "echo")


        planta=cfg.get("MQTT", "nombre")
        client = mqttClient.Client(planta+"Anemometro")    #create new instance
        client.username_pw_set(user, password=password)    #set username and password
        client.on_connect= on_connect                      #attach function to callback
        client.connect(broker_address, port=port)          #connect to broker
        client.loop_start()        #start the loop
        while Connected != True:    #Wait for connection
            time.sleep(0.1)
            print("espero")

        # Lee el registro Modbus periódicamente y acumula el máximo medido.
        max=0 #velocidad máxima 
        segundoInicial=time.time() #segundo en el que empieza un nuevo periodo entre envíos
        try:    
            while True:
                try:
                    lectura=instrument.read_register(cfg.getint("viento", "dir_memoria"), 0)  
                    print(f"lectura={lectura}")
                    # Actualiza el máximo si esta lectura lo supera.
                    if lectura>max:
                        max=lectura
                        print(f"max={max}")
                    segundoAhora=time.time()
                    tiempoCiclo=segundoAhora-segundoInicial
                    print(f"tiempociclo= {tiempoCiclo}")
                    # Publica el máximo acumulado cuando termina el intervalo.
                    if tiempoCiclo>=pausa:
                        data = convert_data(max)
                        print(data)
                        resultado=client.publish(planta+"/viento",json.dumps(data),2)
                        if (resultado[0]!=0 and resultado[0]!=4):
                                print("deberia salir")
                                client.disconnect()
                                client.loop_stop()
                                return
                                #sys.exit()
                        # Reinicia el máximo y el inicio del siguiente intervalo.
                        segundoInicial=time.time()  
                        max=0      
                    time.sleep(intervalo)        
                except Exception as e: 
                    print(e)    
        except:
            pass            

    except KeyboardInterrupt:
        client.disconnect()
        client.loop_stop()             
  


if __name__ == "__main__":
    main()