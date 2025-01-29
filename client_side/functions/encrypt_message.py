#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

#from functions.common_functions import encrypt_symmetric_key

def encrypt_message(data_to_send, symmetric_key) -> dict: #session_key no create seassion vai criptografada com a chave publica do servidor
    """
    Criptografa os dados usando uma chave simétrica compartilhada.

    :param data_to_send: Dados que serão criptografados (bytes).
    :param shared_key: Chave simétrica compartilhada (bytes).
    :return: Dicionário contendo os dados criptografados, nonce e tag.
    
    server_public_key = repo_key
    public_key = serialization.load_pem_public_key(server_public_key.encode(), backend=default_backend())   
    server_public_key = public_key
    """
    nonce = os.urandom(12)
    cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce), backend=default_backend())
    encryptor = cipher.encryptor()

    data_to_send = json.dumps(data_to_send)

    encrypted_data = encryptor.update(data_to_send.encode()) + encryptor.finalize()
    tag = encryptor.tag
    #encrypted_symmetric_key = encrypt_symmetric_key(symmetric_key,server_public_key)

    # Retorna os dados criptografados, nonce e tag
    encrypted_message = {
        "encrypted_data": encrypted_data.hex(),
        "nonce": nonce.hex(),
        "tag": tag.hex(),
    }

    return encrypted_message