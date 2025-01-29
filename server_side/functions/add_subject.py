#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sqlite3
import sys
import json
from functions.decrypt_message import decrypt_message
from functions.create_table_if_not_exists import create_table_if_not_exists
from functions.repo_operations import check_permission_user, get_username_by_id, load_server_private_key, load_session_from_id, sign_message, verify_session_file, verify_subject_signature
#from utils import decrypt_message

def add_subject(data, permission= "SUBJECT_NEW"):

    session_id = data["session_id"]

    if verify_session_file(session_id):

        session_data = load_session_from_id(session_id)

        session_data = load_session_from_id(session_id)
        session_roles = session_data.get("roles")
        session_org_id = session_data.get("organization_id")
        session_key = session_data.get("symmetric_key")
        session_user_id = session_data.get("user_id")
        session_username = get_username_by_id(session_user_id)
        session_key = bytes.fromhex(session_key)

        decrypted_data = decrypt_message(data["encrypted_data"],session_key) #username, new_name, new_email, credentials_file

        data_str = decrypted_data.decode("utf-8")

        # Carregar o JSON como dicionário
        data_dict = json.loads(data_str)

        new_username = data_dict["username"]
        new_name = data_dict["name"]
        new_email = data_dict["email"]
        public_key_new_user = data_dict["public_key"]
        session_org_id = json.dumps(session_org_id)

        if check_permission_user(session_roles, session_org_id,session_username, permission):

            conn = sqlite3.connect('repository.db')
            create_table_if_not_exists(conn)
            cursor = conn.cursor()

            try:
                cursor.execute("""
                    INSERT INTO subjects (organization_id, username, full_name, email, public_key, status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (session_org_id[1], new_username, new_name, new_email, public_key_new_user, "up"))

                #confirm and close the connection
                conn.commit()

                server_private_key =  load_server_private_key()
                signature = sign_message(decrypted_data, server_private_key)
                signature = {"signature": signature.hex()}

                return signature, 201
            
            except sqlite3.IntegrityError as e:
                return "Subject already added to this organization", 409
            except Exception as e:
                return f"Database error: {e}", 500
            finally:
                conn.close()

            
