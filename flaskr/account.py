from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from flaskr.db import get_db
import http.client
import json

account = Blueprint('account', __name__, url_prefix='/')

@account.route("/home", methods=['GET', 'POST'])
def home(): 
    pass

