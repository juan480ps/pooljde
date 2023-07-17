import logging.config, yaml
from flask import Flask
from flask_restful import Api

file = open('config/log/logging.yml', 'r')
data = yaml.safe_load(file)
file.close()
logging.config.dictConfig(data)

app = Flask(__name__)
app.config.from_pyfile('config.py')
api_key = app.config.get('API_KEY')
api = Api(app)

from api.resources.conn import Conn

api.add_resource(Conn, '/api/jdedb')

@app.route("/", methods = ['POST', 'GET'])
def hello():
    return "Pagina de prueba"