from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from os import urandom

# generate key, encrypt data as BLOB, store data in sqlite3 db, decrypt

def generate_key():
    key = urandom(32) # the 32 byte key used for encryption and decryption
    iv = urandom(16) # the 16 byte initialization vector used to randomize the encryption
    
    return key, iv
    
    
def generate_cipher(key, iv):
    cipher = Cipher(algorithms.AES(key), modes.CTR(iv), backend=default_backend()) # CTR > CBC for Binary Large Object files due to size 
    return cipher


def encrypt(cipher, face_data):
    encryptor = cipher.encryptor()
    encrypted = encryptor.update(face_data) + encryptor.finalize()
    return encrypted


def decrypt(cipher, encrypted):
    decryptor = cipher.decryptor()
    decrypted_data = decryptor.update(encrypted) + decryptor.finalize()
    return decrypted_data



