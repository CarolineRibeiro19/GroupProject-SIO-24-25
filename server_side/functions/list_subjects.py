#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import json
from functions.create_table_if_not_exists import create_table_if_not_exists
from functions.decrypt_message import decrypt_message
from functions.repo_operations import load_server_private_key, load_session_from_id, sign_message, verify_session_file


def list_subjects(data):
    session_id = data["session_id"]
    username = None

    if verify_session_file(session_id):
        # Carrega os dados da sessão
        session_data = load_session_from_id(session_id)
        session_org_id = session_data.get("organization_id")
        session_key = session_data.get("symmetric_key")
        session_org_id = json.dumps(session_org_id)
        session_org_id = session_org_id[1]

        # Descriptografa os dados, se fornecidos
        if "encrypted_data" in data:
            session_key = bytes.fromhex(session_key)
            decrypted_message = decrypt_message(data["encrypted_data"], session_key)
            data_str = decrypted_message.decode('utf-8')
            data_dict = json.loads(data_str)
            username = data_dict

        # Conecta ao banco de dados
        conn = sqlite3.connect('repository.db')
        create_table_if_not_exists(conn)
        cursor = conn.cursor()

        try:
            if username !=  None:
                # Consulta para um único usuário
                cursor.execute(
                    "SELECT username,full_name, status FROM subjects WHERE organization_id = ? AND username = ?",
                    (session_org_id, username)
                )
                row = cursor.fetchone()
                if row:
                    subject = {"username": row[0], "name": row[1],"status": row[2]}
                    server_private_key = load_server_private_key()
                    username = username.encode()
                    signature = sign_message(username, server_private_key)
                    return {"signature": signature.hex(), "subject": subject}, 201
                else:
                    return {"error": "User not found or not in the same organization"}, 404
            else:
                # Consulta para todos os usuários da organização
                cursor.execute(
                    "SELECT username, full_name, status FROM subjects WHERE organization_id = ?",
                    (session_org_id,)
                )
                subjects = [{"username": row[0],"name": row[1], "status": row[2]} for row in cursor.fetchall()]
                server_private_key = load_server_private_key()
                session_id = session_id.encode()
                signature = sign_message(session_id, server_private_key)
                return {"signature": signature.hex(), "subjects": subjects}, 201

        except Exception as e:
            return {"error": f"Database error: {e}"}, 500

        finally:
            conn.close()

    else:
        return {"error": "Invalid session file"}, 400
