from api import app #modulo principal que se usa para la entrada wsgi

if __name__=='__main__':
    app.run(host='0.0.0.0', debug=False, threaded=True, port=6000)