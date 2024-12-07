import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
import skimage as ski
import flaskr.AES256 as AES256

bp = Blueprint('auth', __name__, url_prefix='/') # all html files in templates, no subfolders

""" Compares if user's face input matches stored value of face closely """ 
def face_match(db_face, input_face):
    return True

@bp.route('/register', methods=('GET', 'POST')) 
def register(): # for new user
    if request.method == 'POST': # to sign up
        full_name = request.args['full_name']
        password = request.args['password']
        phone = request.args['phone_number']
        email = request.args['email']
        face = request.args['face_image']

        db = get_db()
        error = None

        if not full_name or not password or not not phone or not email or not face: 
            error = "Please fill out all fields"

        if error is None:
            try: 
                sqlite_insert = """ INSERT INTO data 
                                (full_name, pass, phone, email, face_embedding, encryption_key, iv) 
                                VALUES (?, ?, ?, ?, ?, ?, ?); """
                hashed_password = generate_password_hash(password) # generating a hashed password
                
                # use AES 256 to ecrypt user face data
                key, iv = AES256.generate_key()
                cipher = AES256.generate_cipher(key, iv)
                encrypted_face = AES256.encrypt(cipher, face)

                data_tuple = (full_name, hashed_password, phone, email, encrypted_face, key, iv) 
                db.execute(sqlite_insert, data_tuple) # adding user to database
                db.commit()
            except db.IntegrityError as e:
                print(e)
                error = f"{full_name} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        else:
            flash(error)
    
    return(render_template("register.html"))


@bp.route("/login", methods=['GET', 'POST'])
def login(): 
    if request.method == 'POST':
        full_name = request.args['full_name']
        password = request.args['password']
        face = request.args['face_image']

        db = get_db()
        error = None

        if not full_name or not password or not face: 
            error = "Please fill out all fields"

        if error is not None:
            flash(error)

        # check if inputted values match database values
        db.execute("SELECT * FROM users WHERE full_name = ?", (full_name,))
        user = db.fetchone()
        
        if user is None:
            error = f"{full_name} has not registered."
        elif not check_password_hash(user['pass'], password):
            error = f"Invalid password"
        elif not face_match(user['face'], face): 
            error = f"Face does not match"

        if error is None:
            session.clear() # clearing cookies
            session['user_id'] = user['id']
            return redirect(url_for("account.home")) # fillout this view later
        
        flash(error)

    return render_template("/login.html")

@bp.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id") # getting user_id from the dictionry session (stored as a cookie)
    if user_id is None: # if user not found in session (not logged in, session expired/cleared/corrupted)
        g.user = None # no user logged in
    else:
        command =  "SELECT * FROM users WHERE id = ?"
        g.user = get_db().execute(command, (user_id,)).fetchone() # getting user data based on id


@bp.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear() # clearing cookies
    return redirect(url_for("auth.login")) # redirecting to login page

