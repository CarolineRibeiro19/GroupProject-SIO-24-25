from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.asymmetric import padding, rsa
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os
import json

# Função para gerar uma chave simétrica
def generate_symmetric_key():
    # Gera uma chave AES de 256 bits para comunicação segura
    return os.urandom(32)

def encrypt_data(data, symmetric_key):
    # Encripta dados usando a chave simétrica
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()
    encrypted_data = encryptor.update(data.encode()) + encryptor.finalize()
    return encrypted_data, encryptor.tag, nonce

def encrypt_symmetric_key(symmetric_key, server_public_key):
    # Encripta a chave simétrica usando a chave pública do servidor
    return server_public_key.encrypt(
        symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )

def get_session_data(session_file):
    # Carrega a chave simétrica a partir do arquivo de sessão
    with open(session_file, "r") as session_file:
        data = json.load(session_file)
    return data["session_id"], bytes.fromhex(data["symmetric_key"])