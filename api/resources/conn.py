import json, logging, config.db.pool as db, psycopg2, base64, api
from flask_restful import Resource
from flask import request
from config.db.db_config_pstgr import postgresqlConfig
from functools import wraps

connpost = psycopg2.connect(postgresqlConfig)

def require_api_key(func): #funcion para requerir de forma obligatoria la apikey
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            logging.info("Verificar Api-Key PoolJDE")
            data = request.get_json()
            params = data['params']
            api_key = params['apikey']
            if not api_key or not api_key == api.API_KEY:
                return {'codigo': -1005, 'descripcion': 'Api-Key requerida', 'objetoJson' : [], 'arrayJson': []}
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            return {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': [], 'arrayJson' : {}}
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            return {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': [], 'arrayJson' : {}}
        return func(*args, **kwargs)
    return decorated_function

def require_token(func): #funcion para requerir de forma obligatoria el token
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            logging.info("Verificar Token PoolJDE")
            data = request.get_json()
            params = data['params']
            token = params['token']
            if not token:
                return {'codigo': -1005, 'descripcion': 'Token requerido', 'objetoJson' : [], 'arrayJson': []}
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
            return {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': [], 'arrayJson' : {}}
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
            return {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': [], 'arrayJson' : {}}
        return func(*args, **kwargs)
    return decorated_function

class Conn(Resource):
    @require_api_key #requerimos la apikey
    @require_token # requerimos el token
    def post(self):
        logging.debug("Entro POST PoolJDE")
        objetoJson = {}
        arrayJson = []
        try:
            logging.debug("HTTP REQUEST HEADERS: " + str(request.headers)) #logging de prueba
            logging.debug("HTTP REQUEST DATA: " + str(request.data)) #logging de prueba
            data = request.get_json(force = True) # asignamos a una variable el json de la peticion
            logging.info('@REQUEST POST ' + json.dumps(data)) #logging de prueba
            operation = data['operation'] # se obtiene la key operacion del json
            params = data['params'] # se obtiene la key params del json
            query = params['query'] # se obtiene la key query de params
            cur = connpost.cursor() # se abre cursor postgres interno
            cursor = db.getCursorJDE() # # se abre cursor JDE
            decoded_query = base64.b64decode(query).decode("utf-8") # se decodifica el query recibido del json en base64
            if operation.lower() == "select":
                logging.debug(str(decoded_query))
                cursor.execute(str(decoded_query))
                rows = cursor.fetchall()
                column_names = cursor.description
                results = []
                for row in rows:
                    row_dict = {}
                    for i, column in enumerate(column_names):
                        column_name = column[0]
                        value = row[i]
                        value = str(value)
                        row_dict[column_name] = value
                    results.append(row_dict)
                if results:
                    descripcion = 'OK'
                    codigo = 1000
                    objetoJson = {}
                    arrayJson = results
                else:
                    descripcion = 'No encontrado'
                    codigo = -1001
            elif operation.lower() == "update" or operation.lower() == "delete" or operation.lower() == "insert":
                cursor.execute(str(decoded_query))
                rowcount = cursor.rowcount
                descripcion = 'OK'
                codigo = 1000
                objetoJson = [str(rowcount) + " Filas afectadas"]
            else:
                descripcion = 'Operación no válida'
                codigo = -1002
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
            connpost.rollback()
        finally:
            cursor.connection.commit()
            cursor.close()
            
        try:
            query = f"INSERT INTO testdta.log (codigo, descripcion, objetojson, arrayjson) VALUES({codigo}, '{descripcion}', '{json.dumps(objetoJson)}', '{json.dumps(arrayJson)}'); "
            cur.execute(query)
            connpost.commit()
            cur.close()
        except KeyError as e :
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
            connpost.rollback()
        
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': objetoJson, 'arrayJson': arrayJson }
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta