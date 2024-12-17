from flask import Flask, request, Response
import os
from flask_talisman import Talisman
import requests
import threading

from . import authenticate

""" different test_config files could be passed in for different testing """
def create_app(test_config=None): # application factory simplifies things for larger apps

    app = Flask(__name__) # ensures app is not globally created so multiple instances of app could be managed
    BACKEND_URL = 'http://localhost:5000'
    app.config.from_mapping( # set default configuration
        SECRET_KEY = os.urandom(32), # securly generating a random key 
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'), # path to database
        SESSION_COOKIE_SECURE = True
    )

    if test_config is None: 
        app.config.from_pyfile('config.py', silent=True) # create the file if DNE
    else:
        app.config.from_mapping(test_config) # load the config file

    def start_reverse_proxy(): # routes client requests to proxy; proxy to server while masking IP
        app.run(debug=True, port=8080)
        
        @app.route('/<path:path>', methods=["GET", "POST", "PUT", "DELETE"])
        def proxy(path):
            url = f"{BACKEND_URL}/{path}"

            if request.method == "GET":
                resp = requests.get(url, headers=request.headers, params=request.args)
            elif request.method == "POST":
                resp = request.get(url, headers=request.headers, data=request.data)
            elif request.method == "PUT":
                resp = request.get(url, headers=request.headers, data=request.data)
            elif request.method == "DELETE":
                resp = request.get(url, headers=request.headers)
            
            return Response(resp.content, status=resp.status_code, headers=resp.headers.items())
        
        proxy_thread = threading.Thread(proxy)
        proxy_thread.start()

    start_reverse_proxy()
    
    try:
        os.makedirs(app.instance_path) # creates directory with instance files like db.py
    except OSError: 
        pass

    Talisman(app) # enforces HTTPS

    from . import db
    db.init_app(app)
    app.register_blueprint(authenticate.bp)

    return app 
