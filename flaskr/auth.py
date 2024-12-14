import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.account import account
import flaskr.AES256 as AES256
import face_recognition
from PIL import Image
from io import BytesIO
from bitcoinlib.wallets import Wallet

auth = Blueprint('auth', __name__, url_prefix='/') # all html files in templates, no subfolders

""" Computes distance between input face and stored face and checks if distance within tolerance """ 
# db_face is BLOB and input face is jpg
def face_match(known_face, input_face, tolerance=0.6): # less than 0.6 tolerance is too strict
    known_data = Image.open(BytesIO(known_face)) # converts blob to file object 
    known_image_file = known_data.save("f.jpg", format='jpg') # converts file to jpg file
    
    known_image_file_array = face_recognition.load_image_file(known_image_file)
    input_image_file_array = face_recognition.load_image_file(input_face)

    known_image_encoding = face_recognition.face_encodings(known_image_file_array)[0]
    input_image_file_encoding = face_recognition.face_encodings(input_image_file_array)[0]

    face_distance = face_recognition.face_distance(known_image_encoding, input_image_file_encoding)
    return face_distance <= tolerance

@auth.route('/register', methods=('GET', 'POST')) 
def register(): # for new user
    if request.method == 'POST': # to sign up
        full_name = request.args['full_name']
        password = request.args['password']
        email = request.args['email']
        face = request.args['face_image']

        db = get_db()
        error = None

        if not full_name or not password or not email or not face: 
            error = "Please fill out all fields"

        if error is None:
            try: 
                sqlite_insert = """ INSERT INTO data 
                                (full_name, pass, email, face_embedding, encryption_key, iv) 
                                VALUES (?, ?, ?, ?, ?, ?); """
               
                hashed_password = generate_password_hash(password) # generating a hashed password
                hashed_email = generate_password_hash(email) # generating a hashed email
                # use AES 256 to ecrypt user face data
                key, iv = AES256.generate_key()
                cipher = AES256.generate_cipher(key, iv)
                encrypted_face = AES256.encrypt(cipher, face)

                data_tuple = (full_name, hashed_password, hashed_email, encrypted_face, key, iv) 
                db.execute(sqlite_insert, data_tuple) # adding user to database
                db.commit()

                # generate wallet address
                w = Wallet.create("Wallet 1")
                key1 = w.get_key()
                public_key = key1.public_hex    
                private_key = key1.private_hex
                sqlite_insert = """ INSERT INTO wallet (public_key, private_key) VALUES (?, ?) """
                data_tuple = (public_key, private_key)
                db.execute(sqlite_insert, data_tuple)
                db.commit()

            except db.IntegrityError as e:
                print(e)
                error = f"{full_name} is already registered."
            else:
                return redirect(url_for("auth.login"))
            
        else:
            flash(error)
    
    return(render_template("register.html"))


@auth.route("/login", methods=['GET', 'POST'])
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
        elif not face_match(AES256.decrypt(user['face']), face): 
            error = f"Face does not match"

        if error is None:
            session.clear() # clearing cookies
            session['user_id'] = user['id']
            return redirect(url_for("account.home")) # fillout this view later
        
        flash(error)

    return render_template("/login.html")

@auth.before_app_request
def load_logged_in_user():
    user_id = session.get("user_id") # getting user_id from the dictionry session (stored as a cookie)
    if user_id is None: # if user not found in session (not logged in, session expired/cleared/corrupted)
        g.user = None # no user logged in
    else:
        command =  "SELECT * FROM users WHERE id = ?"
        g.user = get_db().execute(command, (user_id,)).fetchone() # getting user data based on id

def login_required(view): # takes each view and makes sure user is logged in before routing there
    @functools.wraps(view) 
    def wrapped_view(**kwargs):
        if g.user is None:
            return redirect(url_for('auth.login'))
        
        return view(**kwargs)
    return wrapped_view


@auth.route("/logout", methods=['GET', 'POST'])
def logout():
    session.clear() # clearing cookies
    return redirect(url_for("auth.login")) # redirecting to login page

