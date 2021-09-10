import os
import tabula
import pandas as pd
import numpy as np
import shutil
import nums_from_string
import time
import logging
import configparser
import sys
from time import strftime
import logging.handlers
import logging.config
import os
import fitz  # PyMuPDF
import io
from PIL import Image
import re

import Calidad_Encapsulado
import Sushi_Encapsulado

config_obj = configparser.ConfigParser()
config_file = os.path.join(os.path.dirname(__file__), 'configCalidad_Sushi.ini')
config_obj.read(config_file)

username = str(config_obj.get('host', 'username'))
password = str(config_obj.get('host', 'password'))
rutaEntradaCalidad = str(config_obj.get('rutas', 'rutaEntradaCalidad'))
rutaSalidaCalidad = str(config_obj.get('rutas', 'rutaSalidaCalidad'))
rutaArchivoCalidad = str(config_obj.get('rutas', 'rutaArchivoCalidad'))
rutaEntradaCalidad = str(config_obj.get('rutas', 'rutaEntradaCalidad'))
rutaCalidad = str(config_obj.get('rutas', 'rutaCalidad'))
centro_bloque = str(config_obj.get('rutas', 'centro_bloque'))
rutaEntradaSushi = str(config_obj.get('rutas', 'rutaEntradaSushi'))
rutaSalidaSushi = str(config_obj.get('rutas', 'rutaSalidaSushi'))
rutaArchivoSushi = str(config_obj.get('rutas', 'rutaArchivoSushi'))
rutaSalidaImagenesSushi = str(config_obj.get('rutas', 'rutaSalidaImagenesSushi'))
rutaSushi = str(config_obj.get('rutas', 'rutaSushi'))
rutaCalidad = str(config_obj.get('rutas', 'rutaCalidad'))
regtiendas = str(config_obj.get('rutas', 'regtiendas'))


logCalidad = str(config_obj.get('logData', 'logCalidad'))
logSushi = str(config_obj.get('logData', 'logSushi'))

start_time = time.time()
timenow = time.strftime("%d-%b-%Y  %H_%M_%S")


llamada_calidad()

wait(10)


llamada_sushi()


tiempoTranscurrido = time.time() - start_time
totaltime = time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
time.strftime("%H:%M:%S", time.gmtime(tiempoTranscurrido))
logging.info('Fichero creado correctamente: ' + timenow)
logging.info('Tiempo de proceso transcurrido: ' + totaltime)
logging.shutdown()
