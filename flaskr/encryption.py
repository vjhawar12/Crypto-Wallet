from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
import sys
import db as database

def encrypt(text):
    text = text.encode()
    aes_key = get_random_bytes(16)
    cipher = AES.new(aes_key, AES.MODE_GCM) # GCM mode better for larger strings like emails
    ciphertext, tag = cipher.encrypt_and_digest(text)
    assert len(cipher.nonce) == 15
    return ciphertext, tag, cipher.nonce

def decrypt():
    pass