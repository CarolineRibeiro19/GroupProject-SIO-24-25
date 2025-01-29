#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import os
import sqlite3

from functions.repo_operations import get_public_key, get_username_by_id, load_server_private_key, load_session_from_id, sign_message, verify_session_file, verify_subject_signature
from functions.decrypt_message import decrypt_message

def drop_role(data):

    session_id = data["session_id"]

    if verify_session_file(session_id):

        session_data = load_session_from_id(session_id)
        session_key = session_data.get("symmetric_key")
        session_roles = session_data.get("roles")
        session_key = bytes.fromhex(session_key)

        decrypted_message = decrypt_message(data["encrypted_data"],session_key) 

        data_str = decrypted_message.decode('utf-8')

        # Passo 2: Carregar a string como um dicionário
        data_dict = json.loads(data_str)

        # Passo 3: Acessar o valor da chave "roles"
        role= data_dict["role"]

        try:
            if role in session_roles:
                session_folder = os.path.abspath("sessions")  # Ajuste para absoluto ou relativo
                session_path = os.path.join(session_folder, str(session_id))
                file_path = session_path + ".json"
                
                if not os.path.exists(file_path):
                    raise FileNotFoundError(f"O arquivo {file_path} não existe.")
                
                with open(file_path, "r") as json_file:
                    try:
                        data = json.load(json_file)  
                    except json.JSONDecodeError as e:
                        raise ValueError(f"Erro ao decodificar o JSON em {file_path}: {e}")
        
                data["roles"].remove(role)
                
                with open(file_path, "w") as session_file:
                    json.dump(data, session_file, indent=4)  

                    
                server_private_key =  load_server_private_key()
                signature = sign_message(decrypted_message, server_private_key)
                signature = {"signature": signature.hex()}

                return signature, 201
            
            else:
                return"Error",500

        except Exception as e:
            raise ValueError(f"Erro ao verificar role: {e}")
