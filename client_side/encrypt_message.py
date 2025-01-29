#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
import os

def encrypt_message(data_to_send, symmetric_key) -> dict: #session_key no create seassion vai criptografada com a chave publica do servidor

    data_to_send = json.dumps(data_to_send).encode('utf-8')
    
    # Gera um nonce único para esta operação de criptografia
    nonce = os.urandom(12)  # Recomendado para AES-GCM

    # Configura o cifrador com AES no modo GCM
    cipher = Cipher(
        algorithms.AES(symmetric_key),
        modes.GCM(nonce),
        backend=default_backend()
    )
    encryptor = cipher.encryptor()

    # Criptografa os dados
    encrypted_data = encryptor.update(data_to_send) + encryptor.finalize()
    tag = encryptor.tag

    # Retorna os dados criptografados, nonce e tag
    encrypted_message = {
        "encrypted_data": encrypted_data.hex(),
        "nonce": nonce.hex(),
        "tag": tag.hex(),
    }

    return encrypted_message