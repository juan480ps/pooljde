import cx_Oracle, logging, yaml

config_file = 'config/db/db_config_orcl.yaml'
file = open(config_file, 'r')
config_data = file.read()
file.close()
config = yaml.safe_load(config_data)

username = config['username']
password = config['password']
sdn = f"{config['host']}:{config['port']}/{config['sid']}"

pd_pool = cx_Oracle.SessionPool(username, password, sdn, min = 2, max = 2, increment = 1, threaded = True)

logging.debug("Conectada BD JDE PD")

def getCursorJDE():
    con = pd_pool.acquire()
    cur = con.cursor()
    return cur