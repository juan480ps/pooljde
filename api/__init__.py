import logging.config, yaml
from flask import Flask
from flask_restful import Api

file = open('config/log/logging.yml', 'r') # se lee el archivo de configuracion para el logging
data = yaml.safe_load(file)
file.close()
logging.config.dictConfig(data)

app_config_file = open('config/app_config.yaml', 'r')  # se lee el archivo de configuracion para la app. De este archivo se extrae la apikey para poder validar posteriormente
app_config_data = yaml.safe_load(app_config_file)
app_config_file.close()

API_KEY = app_config_data['API_KEY']

app = Flask(__name__)
api = Api(app)

from api.resources.conn import Conn 

api.add_resource(Conn, '/api/jdedb') # url del servicio principal pool

@app.route("/", methods = ['POST', 'GET']) # url de prueba
def hello():
    return "Pagina de prueba"