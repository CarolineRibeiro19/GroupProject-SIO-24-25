#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import os
import sqlite3
import json
from functions.create_table_if_not_exists import create_table_if_not_exists
from functions.decrypt_message import decrypt_message
from functions.repo_operations import check_permission_user, get_public_key, get_username_by_id, load_server_private_key, load_session_from_id, sign_message, verify_session_file, verify_subject_signature


def reactivate_role(data, permission="ROLE_UP"):

    session_id = data["session_id"]

    if verify_session_file(session_id):

        session_data = load_session_from_id(session_id)

        session_roles = session_data.get("roles")
        session_org_id = session_data.get("organization_id")
        session_key = session_data.get("symmetric_key")
        session_user_id = session_data.get("user_id")
        session_username = get_username_by_id(session_user_id)
        session_key = bytes.fromhex(session_key)

        decrypted_message = decrypt_message(data["encrypted_data"],session_key) 

        data_str = decrypted_message.decode('utf-8')

        # Passo 2: Carregar a string como um dicionário
        data_dict = json.loads(data_str)

        # Passo 3: Acessar o valor da chave "roles"
        role= data_dict["role"]

        session_org_id = json.dumps(session_org_id)


        if check_permission_user(session_roles, session_org_id, session_username, permission):

            conn = sqlite3.connect('repository.db')
            create_table_if_not_exists(conn)
            cursor = conn.cursor()
            
            # Seleciona o conteúdo atual de `acl`
            cursor.execute("SELECT acl FROM organizations WHERE id = ?", (session_org_id[1],))
            result = cursor.fetchone()

            if result and result[0]:
                # Carregar o JSON existente de `acl`
                current_acl = json.loads(result[0])
            else:
                return "No ACL found for the organization", 404

            # Verifica se o `role` existe
            if "roles" in current_acl and role in current_acl["roles"]:
                # Atualiza o status do role
                current_acl["roles"][role]["status"] = "up"
            else:
                return f"Role '{role}' not found in ACL", 404

            try:
                # Atualiza o banco de dados com o novo `acl`
                cursor.execute(
                    """
                    UPDATE organizations
                    SET acl = ?
                    WHERE id = ?
                    """,
                    (json.dumps(current_acl), session_org_id[1])
                )    

                # Commit and close the connection
                conn.commit()
                server_private_key =  load_server_private_key()
                signature = sign_message(decrypted_message, server_private_key)
                signature = {"signature": signature.hex()}

                return signature, 201

            except sqlite3.IntegrityError:
                return "Role already exists for this organization", 409

            except Exception as e:
                return f"Database error: {e}", 500

            finally:
                conn.close()
        else:
            return "Permission denied", 403
    else:
        return "Invalid session file", 400