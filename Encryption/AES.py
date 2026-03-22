__author__ = "Noam"

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives import padding
from cryptography.hazmat.backends import default_backend
import os

def generate_key():
    key = os.urandom(16)
    return key

def pad_massage(message):
    padder = padding.PKCS7(128).padder()
    padded_message = padder.update(message) + padder.finalize()
    return padded_message

def encrypt(padded_message, key):
    iv = os.urandom(16)
    cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
    encryptor = cipher.encryptor()
    cipher_text = encryptor.update(padded_message) + encryptor.finalize()

    return iv + cipher_text

def decrypt(key, encrypted_message):
    iv = encrypted_message[:16]
    cipher_text = encrypted_message[16:]

    decryptor = Cipher(algorithms.AES(key),modes.CBC(iv),backend=default_backend()).decryptor()

    decrypted_padded_message = decryptor.update(cipher_text) + decryptor.finalize()
    unpadder = padding.PKCS7(128).unpadder()
    message = unpadder.update(decrypted_padded_message) + unpadder.finalize()

    return message
