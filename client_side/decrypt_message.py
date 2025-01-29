#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend

def decrypt_message(encrypted_payload, symmetric_key):
    """
    Descriptografa os dados usando uma chave simétrica compartilhada.

    :param encrypted_payload: Dicionário contendo dados criptografados, nonce e tag.
    :param shared_key: Chave simétrica compartilhada (bytes).
    :return: Dados descriptografados (bytes).
    """
    try:
        # Recupera os valores do dicionário
        encrypted_data = bytes.fromhex(encrypted_payload["encrypted_data"])
        nonce = bytes.fromhex(encrypted_payload["nonce"])
        tag = bytes.fromhex(encrypted_payload["tag"])

        # Configura o cifrador com AES no modo GCM
        cipher = Cipher(
            algorithms.AES(symmetric_key),
            modes.GCM(nonce, tag),
            backend=default_backend()
        )
        decryptor = cipher.decryptor()

        # Descriptografa os dados
        decrypted_message = decryptor.update(encrypted_data) + decryptor.finalize()

        return decrypted_message
    except Exception as e:
        raise ValueError(f"Erro ao descriptografar os dados: {e}")