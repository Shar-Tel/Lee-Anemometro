# Anemómetro MQTT / Anemometer MQTT

## Español

### Descripción
Este proyecto recoge la velocidad de un anemómetro conectado por Modbus RTU y publica el valor máximo medido en un broker MQTT. Está pensado para integrarse en sistemas de supervisión, monitorización industrial o telemetría de instalaciones con sensores de viento.

El script principal es `leeAnemometro.py` y usa la librería `minimalmodbus` para leer registros Modbus, `paho-mqtt` para publicar datos y `pyserial` para la comunicación con el puerto serie.

### Funcionalidades
- Lectura de un registro Modbus del anemómetro.
- Conexión automática a un broker MQTT.
- Publicación periódica del máximo de velocidad en un topic MQTT.
- Configuración externa mediante archivo `config.cfg`.
- Registro de eventos y errores en un fichero de log.
- Soporte para la configuración de puerto, velocidad, paridad, timeout y dirección Modbus.

### Requisitos
- Python 3.x
- Acceso al puerto serie donde está conectado el anemómetro
- Broker MQTT accesible en la red
- Librerías Python:
  - `minimalmodbus`
  - `paho-mqtt`
  - `pyserial`

Se pueden instalar con:

```bash
pip install minimalmodbus paho-mqtt pyserial
```

### Configuración
El archivo `config.cfg` incluye la configuración de MQTT, del sensor y del sistema de logs. Un ejemplo típico es el siguiente:

```ini
[MQTT]
nombre = serverName
broker_address = serverIP
port = 1883
user = userName
password = password

[viento]
port = COM6
dir_MODBUS = 244
baudrate = 19200
bytesize = 8
stopbits = 1
timeout = 1
debug = False
rtscts = False
echo = False
dir_memoria = 0000
intervalo = 10
pausa = 300

[debug]
debug = ERROR
directorio_log = ./
```

### Parámetros principales
- `nombre`: nombre del origen o del equipo que publica los datos.
- `broker_address`: dirección IP o hostname del broker MQTT.
- `port`: puerto MQTT (normalmente 1883).
- `dir_MODBUS`: dirección del instrumento Modbus.
- `dir_memoria`: registro a leer en el anemómetro.
- `intervalo`: tiempo entre lecturas internas (en segundos).
- `pausa`: tiempo que define el intervalo de envío del máximo medido (en segundos).
- `directorio_log`: carpeta donde se guarda el fichero de log.

### Ejecución
Desde la carpeta del proyecto:

```bash
python leeAnemometro.py
```

El script se conectará al broker MQTT, espera confirmación, y cada vez que se cumple el periodo de `pausa` publicará el máximo acumulado con el formato JSON:

```json
{
  "Planta": "serverName",
  "Inverter": 0,
  "Linea": 0,
  "VIE": 123
}
```

La publicación se hace en el topic:

```text
serverName/viento
```

### Cómo funciona
1. El programa carga la configuración desde `config.cfg`.
2. Inicializa el cliente MQTT.
3. Conecta con el broker.
4. Lee el registro Modbus del anemómetro.
5. Mantiene el máximo del periodo.
6. Cuando el tiempo definido por `pausa` llega, publica ese valor máximo en MQTT.
7. Reinicia el contador y vuelve a medir.

### Consideraciones
- Asegúrate de que el puerto COM o dispositivo serie es correcto.
- Verifica que el anemómetro y el sensor usen la misma configuración Modbus.
- Revisa la configuración del broker y las credenciales MQTT.
- El valor de `dir_memoria` debe ajustarse al registro real del fabricante.

### Estructura del proyecto
- `leeAnemometro.py`: script principal.
- `config.cfg`: configuración del sistema.
- `README.md`: documentación del proyecto.

---

## English

### Description
This project reads the wind speed from an anemometer connected through Modbus RTU and publishes the maximum measured value to an MQTT broker. It is designed for monitoring systems, industrial supervision, or telemetry installations using wind sensors.

The main script is `leeAnemometro.py`. It uses `minimalmodbus` to read Modbus registers, `paho-mqtt` to publish data, and `pyserial` for serial communication.

### Features
- Reads a Modbus register from the anemometer.
- Automatically connects to an MQTT broker.
- Periodically publishes the maximum speed measured on an MQTT topic.
- External configuration through `config.cfg`.
- Event and error logging to a log file.
- Support for COM port, baud rate, parity, timeout, and Modbus address settings.

### Requirements
- Python 3.x
- Access to the serial port where the anemometer is connected
- MQTT broker accessible on the network
- Python libraries:
  - `minimalmodbus`
  - `paho-mqtt`
  - `pyserial`

Install them with:

```bash
pip install minimalmodbus paho-mqtt pyserial
```

### Configuration
The file `config.cfg` contains the MQTT, sensor, and logging settings. A typical configuration looks like this:

```ini
[MQTT]
nombre = serverName
broker_address = serverIP
port = 1883
user = userName
password = password

[viento]
port = COM6
dir_MODBUS = 244
baudrate = 19200
bytesize = 8
stopbits = 1
timeout = 1
debug = False
rtscts = False
echo = False
dir_memoria = 0000
intervalo = 10
pausa = 300

[debug]
debug = ERROR
directorio_log = ./
```

### Main parameters
- `nombre`: name of the device or source publishing the data.
- `broker_address`: IP address or hostname of the MQTT broker.
- `port`: MQTT port (usually 1883).
- `dir_MODBUS`: Modbus device address.
- `dir_memoria`: register to read from the anemometer.
- `intervalo`: delay between internal readings (in seconds).
- `pausa`: time after which the maximum measured value is sent (in seconds).
- `directorio_log`: folder where the log file is written.

### Execution
From the project folder:

```bash
python leeAnemometro.py
```

The script connects to the MQTT broker, waits for confirmation, and when the `pausa` period ends it publishes the accumulated maximum in JSON format:

```json
{
  "Planta": "serverName",
  "Inverter": 0,
  "Linea": 0,
  "VIE": 123
}
```

The data is published to the topic:

```text
serverName/viento
```

### How it works
1. The program loads the settings from `config.cfg`.
2. Initializes the MQTT client.
3. Connects to the broker.
4. Reads the Modbus register from the anemometer.
5. Keeps the maximum value for the current period.
6. When the `pausa` time is reached, it publishes the maximum value to MQTT.
7. Resets the counter and continues measuring.

### Notes
- Make sure the COM port or serial device is correct.
- Verify that the anemometer and the sensor use the same Modbus configuration.
- Check the MQTT broker address and credentials.
- The `dir_memoria` value must match the actual register defined by the manufacturer.

### Project structure
- `leeAnemometro.py`: main script.
- `config.cfg`: system configuration.
- `README.md`: project documentation.
