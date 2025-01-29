#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import base64
import json
import os
import sqlite3

from functions.decrypt_message import decrypt_message
from functions.repo_operations import get_username_by_id, load_server_private_key, load_session_from_id, sign_message, verify_session_file, verify_subject_signature

def assume_role(data):
    
    try:
        session_id = data["session_id"]

        # Verifica se o arquivo da sessão é válido
        if not verify_session_file(session_id):
            return {"error": "Invalid or expired session"}, 403

        session_data = load_session_from_id(session_id)
        session_org_id = session_data.get("organization_id")
        session_key = session_data.get("symmetric_key")
        session_user_id = session_data.get("user_id")
        session_username = get_username_by_id(session_user_id)
        session_key = bytes.fromhex(session_key)
            
        decrypted_message = decrypt_message(data["encrypted_data"],session_key) 

        data_str = decrypted_message.decode('utf-8')
        data_dict = json.loads(data_str)
        role = data_dict["role"]

        try:
            connection = sqlite3.connect("repository.db")
            cursor = connection.cursor()

            session_org_id = json.dumps(session_org_id)

            # Obter o ACL da organização
            cursor.execute(
                """
                SELECT acl
                FROM organizations
                WHERE id = ?
                """,
                (session_org_id[1],)
            )
            org_data = cursor.fetchone()


            if not org_data:
                return {"error": "Organization not found"}, 404
            
            acl = json.loads(org_data[0])

            if "roles" not in acl or role not in acl["roles"]:
                return {"error": "Role not available in ACL"}, 403
            
             # Verificar permissão do usuário
            if session_username not in acl["roles"][role].get("subjects", []):
                return {"error": "User not authorized for this role"}, 403
            
            # Atualizar roles na sessão
            session_file_path = os.path.join(os.path.abspath("sessions"), f"{session_id}.json")
            if not os.path.exists(session_file_path):
                return {"error": f"Session file not found: {session_file_path}"}, 404

            with open(session_file_path, "r") as session_file:
                session_data = json.load(session_file)

            session_data.setdefault("roles", []).append(role)

            with open(session_file_path, "r") as session_file:
                session_data = json.load(session_file)

            # Verificar duplicação de roles
            if role not in session_data.setdefault("roles", []):
                session_data["roles"].append(role)
            else:
                return {"error": f"Role '{role}' already assigned to session"}, 200

            with open(session_file_path, "w") as session_file:
                json.dump(session_data, session_file, indent=4)

            # Assinar mensagem de retorno
            server_private_key = load_server_private_key()
            signature = sign_message(decrypted_message, server_private_key)

            return {"signature": signature.hex()}, 201

        except sqlite3.Error as db_error:
            return {"error": f"Database error: {str(db_error)}"}, 500
        except (FileNotFoundError, json.JSONDecodeError) as e:
            return {"error": f"Session file error: {str(e)}"}, 500
        finally:
            connection.close()

    except KeyError as ke:
        return {"error": f"Key missing in request: {ke}"}, 400
    except Exception as e:
        return {"error": f"Internal server error: {e}"}, 500