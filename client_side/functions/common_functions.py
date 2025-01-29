import base64
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa, ec, utils
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from tinyec import registry 
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import serialization
from .encrypt_message import encrypt_message
from .decrypt_message import decrypt_message
import re

import secrets 
import hashlib
from tinyec import registry 
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from .encrypt_message import encrypt_message
from .decrypt_message import decrypt_message

import secrets 
import hashlib
import os
import json

#busca id da sessão e chave simétrica a partir do arquivo de sessão
def get_session_data(session_file):
    # Carrega a chave simétrica a partir do arquivo de sessão
    with open(session_file, "r") as session_file:
        data = json.load(session_file)
    return data["session_id"], bytes.fromhex(data["symmetric_key"])

# Função para assinar uma mensagem com ECC
# receive parameters in hex string / return in hex string
def sign_message(password: str, message: str) -> str:
    private_key, pub = generate_key_pair(password)
    
    signature = private_key.sign(
        message.encode(),
        ec.ECDSA(hashes.SHA256())
    )
    return signature.hex()

#verify ECC user signature
def verify_subject_signature(public_key, data, signature) -> bool:
    # Hash dos dados antes de verificar
    print("SIGNATURE:", signature, type(signature))
    digest = hashes.Hash(hashes.SHA256())
    digest.update(data.encode())
    hashed_data = digest.finalize()

    try:
        public_key.verify(
            signature,
            hashed_data,
            ec.ECDSA(Prehashed(hashes.SHA256()))
        )
        return True
    except Exception:
        print("Invalid signature")
        return False

# Função para gerar um par de chaves ECC a partir de uma senha
def generate_key_pair(password):
    private_key = ec.derive_private_key(
        int.from_bytes(password.encode(), byteorder="big"),
        ec.BrainpoolP256R1()
    )
    public_key = private_key.public_key()
    return private_key, public_key

#serialize ECC public key
def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

#save ECC public key to file
def save_pub_key(credentials_file, public_key):
    serialized_public = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    with open(credentials_file, 'w') as f:
        f.write(serialized_public.decode())

#load ECC public key from file
def load_pub_key(credentials_file):
    with open(credentials_file, 'r') as f:
        serialized_public = f.read()
    loaded_public_key = serialization.load_pem_public_key(
        serialized_public.encode()
    )
    return loaded_public_key
    
#função para verificar uma assinatura RSA
def verify_repository_signature(message, signature, public_key):

    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        return True
    except InvalidSignature:
        return False

# Função para gerar uma chave simétrica
def generate_symmetric_key():
    # Gera uma chave AES de 256 bits para comunicação segura
    return os.urandom(32)

# Encripta a chave simétrica usando a chave pública do servidor
def encrypt_symmetric_key(symmetric_key, server_public_key):
    ciphertext = server_public_key.encrypt(
        symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return ciphertext

# função para encriptar uma mensagem sem sessão
def encrypt_no_session_message(data_to_send,repo_pub_key):

    server_public_key = serialization.load_pem_public_key(repo_pub_key.encode(), backend=default_backend())   

    symmetric_key = generate_symmetric_key()
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    data_to_send = json.dumps(data_to_send)

    encrypted_data = encryptor.update(data_to_send.encode()) + encryptor.finalize()
    tag = encryptor.tag
    encrypted_symmetric_key = encrypt_symmetric_key(symmetric_key,server_public_key)

    encrypted_message = {
        "encrypted_key": encrypted_symmetric_key.hex(),
        "encrypted_data": encrypted_data.hex(),
        "nonce": nonce.hex(),
        "tag": tag.hex(),
    }

    return encrypted_message, symmetric_key

#função para encriptar uma mensagem normal, ou seja, com sessão
def encrypt_normal_message(data, session_file):
    # carrega chave e id da sessão
    session_data = get_session_data(session_file)
    session_key = session_data[1]
    session_id = session_data[0]
    # encripta a mensagem + adiciona o id da sessão
    encrypted_message = encrypt_message(data, session_key)
    encrypted_message.update({"session_id": session_id})
    return encrypted_message

#função para desencriptar uma mensagem normal, ou seja, com sessão
def decrypt_normal_message(data, session_file): #TODO testar
    # carrega chave e id da sessão
    session_data = get_session_data(session_file)
    session_key = session_data[1]
    session_id = session_data[0]
    # desencripta a mensagem
    decrypted_message = decrypt_message(data, session_key)
    # verifica se o id da sessão é o mesmo que o recebido
    if decrypted_message["session_id"] != session_id:
        raise ValueError("Session ID mismatch")
    return

def is_valid_email(email):
    """Verifica se o e-mail é válido usando uma expressão regular."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return re.match(email_regex, email) is not None