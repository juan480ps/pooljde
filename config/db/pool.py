import cx_Oracle, logging, yaml

config_file = 'config/db/db_config_orcl.yaml' # se lee el archivo config
file = open(config_file, 'r')
config_data = file.read()
file.close()
config = yaml.safe_load(config_data) # se carga la configuracion

username = config['username']
password = config['password']
sdn = f"{config['host']}:{config['port']}/{config['sid']}"

pd_pool = cx_Oracle.SessionPool(username, password, sdn, min = 5, max = 10, increment = 1, threaded = True)# se define el pool de conexiones 

logging.debug("Conectada BD JDE PD") # logging de prueba

def getCursorJDE(): # se define una funcion para abrir conexion y cursor del jde
    con = pd_pool.acquire()
    cur = con.cursor()
    return cur