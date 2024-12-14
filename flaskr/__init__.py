from flask import Flask
import os
from flask_talisman import Talisman
from proxy import proxy

def start_proxy_server(): # routes client requests to proxy; proxy to server while masking IP
    pass

""" different test_config files could be passed in for different testing """
def create_app(test_config=None): # application factory simplifies things for larger apps 
    app = Flask(__name__) # ensures app is not globally created so multiple instances of app could be managed
    app.config.from_mapping( # set default configuration
        SECRET_KEY = os.urandom(32), # securly generating a random key 
        DATABASE = os.path.join(app.instance_path, 'flaskr.sqlite'), # path to database
        SESSION_COOKIE_SECURE = True
    )

    if test_config is None: 
        app.config.from_pyfile('config.py', silent=True) # create the file if DNE
    else:
        app.config.from_mapping(test_config) # load the config file

    start_proxy_server()
    
    try:
        os.makedirs(app.instance_path) # creates directory with instance files like db.py
    except OSError: # handled so app doesn't crash
        pass

    Talisman(app) # enforces HTTPS

    from . import db, auth
    db.init_app(app)
    app.register_blueprint(auth.bp)

    return app 
