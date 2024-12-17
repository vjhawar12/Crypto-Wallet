import functools
from flask import Blueprint, flash, g, redirect, render_template, request, session, url_for
from werkzeug.security import check_password_hash, generate_password_hash
from flaskr.db import get_db
from flaskr.account import account
from flaskr.encryption import encrypt, decrypt
from bitcoinlib.wallets import Wallet
from web3 import Web3
from eth_account import Account
import secrets
from solders.keypair import Keypair

auth = Blueprint('auth', __name__, url_prefix='/') # all html files in templates, no subfolders

@auth.route('/register', methods=('GET', 'POST')) 
def register(): # for new user
    if request.method == 'POST': # to sign up
        full_name = request.args['full_name']
        password = request.args['password']
        email = request.args['email']

        db = get_db()
        error = None

        if not full_name or not password or not email: 
            error = "Please fill out all fields"

        if error is None:
            try: 
                sqlite_insert = """ INSERT INTO data (full_name, pass, email, nonce, tag) VALUES (?, ?, ?, ?, ?); """
               
                hashed_password = generate_password_hash(password) # generating a hashed password
                encrypted = encrypt(email) # encrypting email securely
                email = encrypted[0]
                tag = encrypted[1]
                nonce = encrypted[2]

                data_tuple = (full_name, hashed_password, email, nonce, tag) 
                db.execute(sqlite_insert, data_tuple) # adding user to database
                db.commit()

                # Creating Bitcoin wallet
                btc_wallet = Wallet.create("Bitcoin wallet 1")
                btc_key = btc_wallet.get_key()
                btc_address = btc_key.address

                # creating Ethereum wallet
                eth_priv = secrets.token_hex(32) # creating random text string
                eth_private_key = '0x' + eth_priv
                eth_acct = Account.from_key(eth_private_key)
                eth_address = eth_acct.address

                # creating Solana wallet
                sol_private_key = secrets.token_hex(32)
                kp = Keypair().from_base58_string(sol_private_key)
                sol_address = kp.pubkey # solana address

                # fake user balances
                BTC_balance = 0.05
                ETH_balance = 0.10
                SOL_balance = 0.01

                user_id = db.execute(""" FROM wallet SELECT last_insert_rowid() """ ).fetchone()[0] # getting new user's id

                # inserting wallet info into database
                sqlite_insert = """ INSERT INTO wallet (user_id, BTC_balance, ETH_balance, SOL_balance) VALUES (?, ?, ?, ?) """
                data = (user_id, BTC_balance, ETH_balance, SOL_balance)
                db.execute(sqlite_insert, data)
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

        db = get_db()
        error = None

        if not full_name or not password: 
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

