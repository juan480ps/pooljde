import json, logging, config.db.pool as db, base64, api
from flask_restful import Resource
from flask import request
from functools import wraps
from utils.result_set_to_page import ArrayResultSetToPage

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
            codigo = -1003
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
            codigo = -1003
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
            page_number = params.get('page_number') if params.get('page_number') is not None else api.DEFAULT_PAGE_NUMBER
            page_size = params.get('page_size') if params.get('page_size') is not None else api.DEFAULT_PAGE_SIZE #al llamar el metodo get no es obligatorio enviar la key desde el ws por ende no da error si no tiene            
            cursor = db.getCursorJDE() # # se abre cursor JDE
            decoded_query = base64.b64decode(query).decode("utf-8") # se decodifica el query recibido del json en base64            
            decoded_query = ArrayResultSetToPage.convert_query_to_page(decoded_query, page_number, page_size)            
            if operation.lower() == "select": # se valida la operacion a realizar
                logging.debug(str(decoded_query))  #logging de prueba
                cursor.execute(str(decoded_query)) #se ejecuta el query decodificado
                column_names = cursor.description
                results = []
                fila = 1
                while fila <= page_size:
                    row = cursor.fetchone()
                    fila = fila + 1
                    if row is None:
                        break
                    row_dict = {}                    
                    for i, column in enumerate(column_names):
                        column_name = column[0]
                        value = row[i]
                        value = str(value)
                        row_dict[column_name] = value
                    results.append(row_dict)                
                row = cursor.fetchone() # vemos si despues de la pagina existe un registro
                if row is None:
                    has_more_pages = False
                else:
                    has_more_pages = True
                if results: # se valida si el select tuvo resultados
                    array_to_page = ArrayResultSetToPage(results, has_more_pages, page_number, page_size)
                    array_to_page = array_to_page.to_json()                    
                    objetoJson = array_to_page['objetoJson']  
                    arrayJson = array_to_page.get('arrayJson')['rows']
                    descripcion = 'OK'
                    codigo = 1000
                else:
                    descripcion = 'No encontrado'
                    codigo = -1001
            elif operation.lower() == "update" or operation.lower() == "delete" or operation.lower() == "insert": # se valida si el tipo de operacion es distinto a select
                cursor.execute(str(decoded_query))  #se ejecuta el query decodificado
                rowcount = cursor.rowcount # se obtiene la cantidad de filas afectadas
                descripcion = 'OK'
                codigo = 1000
                objetoJson = [str(rowcount) + " Filas afectadas"]
            else:
                descripcion = 'Operación no válida'
                codigo = -1002
        except KeyError as e : 
            descripcion = 'No se encuentra el parametro: ' + str(e)
            codigo = -1003
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
        except Exception as e:
            descripcion = str(e)
            codigo = -1000
            logging.debug(e)
            logging.error("Peticion finalizada con error; " + descripcion + " " + str(codigo), exc_info=True)
        finally:
            cursor.connection.commit()# se hace commit de todas las operaciones
            cursor.close()# se cierra el cursor
        respuesta = {'codigo': codigo, 'descripcion': descripcion, 'objetoJson': objetoJson, 'arrayJson': arrayJson }
        logging.info('@REQUEST GET ' + request.full_path + ' @RESPONSE ' + json.dumps(respuesta))
        return respuesta