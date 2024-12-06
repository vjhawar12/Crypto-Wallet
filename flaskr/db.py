import sqlite3
from datetime import datetime # to work with various dates and times
import click
from flask import current_app, g
import numpy as np
import cv2


def get_db(): # ensures only single database connection per request
    if 'db' not in g: # if database has not been created
        g.db = sqlite3.connect(
            current_app.config['DATABASE'], # load database
            detect_types = sqlite3.PARSE_DECLTYPES, # parse some datatypes as python objects
        )
        g.db.row_factory = sqlite3.Row # allows for accessing columns by name

    return g.db


def close_db(e=None):
    db = g.pop('db', None) # retrieving the db object and removing it from g

    if db is not None:
        db.close()

def init_db():
    db = get_db()

    with current_app.open_resource('schema.sql') as f: 
        db.executescript(f.read().decode('utf8'))

def blob_to_image(blob): # converting binary data from SQL to image data so python can check if user's face matches
    return cv2.imdecode( # decodes array into color imag
        np.frombuffer(blob, np.uint8), # converts raw binary data to numpy array
        cv2.IMREAD_COLOR 
    ) 

@click.command("init-db") # decorator to define 'init-db' CLI 
def init_db_command():
    init_db()
    click.echo("Initialized database")

def init_app(app): # calls close db and init db given an instance of app
    app.teardown_appcontext(close_db)
    app.cli.add_command(init_db_command)


sqlite3.register_converter(
    'BLOB', blob_to_image
)

