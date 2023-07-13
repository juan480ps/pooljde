from flask import Flask
from flask_restful import Api
from logging.config import dictConfig

dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': 'pooljde %(levelname)s %(filename)s(%(lineno)d) %(funcName)s(): %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'DEBUG',
        'handlers': ['wsgi']
    }
})

app = Flask(__name__)

app.config.from_pyfile('config.py')

api_key = app.config.get('API_KEY')

api = Api(app)

from api.resources.conn import Conn

api.add_resource(Conn, '/api/jdedb')

@app.route("/", methods = ['POST', 'GET'])
def hello():
    return "Pagina de prueba"