import json, logging, db.pool, psycopg2, base64, api
from flask_restful import Resource
from flask import request
from db.db_config_pstgr import postgresqlConfig
from functools import wraps

logging.basicConfig(level = logging.DEBUG)
connpost = psycopg2.connect(postgresqlConfig)

class APIKeyManager:
    @staticmethod
    def validate_api_key(api_key):
        return api_key == api.api_key

def require_api_key(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            params = data['params']
            api_key = params['apikey']
            if not api_key or not api_key == api.api_key:
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

def require_token(func):
    @wraps(func)
    def decorated_function(*args, **kwargs):
        try:
            data = request.get_json()
            params = data['params']
            token = params['token']
            if not token:
                return {'codigo': -1005, 'descripcion': 'Token requerido', 'objetoJson' : [], 'arrayJson': []}
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

class Conn(Resource):
    @require_api_key
    @require_token
    def post(self):        
        logging.debug("Entro POST ")
        objetoJson = []
        arrayJson = []
        try:     
            logging.debug("HTTP REQUEST HEADERS: "+str(request.headers))
            logging.debug("HTTP REQUEST DATA: "+str(request.data))
            data = request.get_json(force=True)            
            logging.info('@REQUEST POST '+json.dumps(data))            
            operation = data['operation']
            params = data['params']
            query = params['query']            
            cur = connpost.cursor()
            cursor = db.pool.getCursorJDE()            
            decoded_query = base64.b64decode(query).decode("utf-8")            
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
                    objetoJson = []
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
            logging.debug(e)
            logging.info("Peticion finalizada con error", exc_info=True)
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1001
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            connpost.rollback()
        finally:
            cursor.connection.commit()
            cursor.close()
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': objetoJson, 'arrayJson': arrayJson }        
        query = f"INSERT INTO public.log (codigo, descripcion, objetojson, arrayjson) VALUES({codigo}, '{descripcion}', '{json.dumps(objetoJson)}', '{json.dumps(arrayJson)}'); "        
        cur.execute(query)
        connpost.commit()
        cur.close()        
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))        
        return respuesta