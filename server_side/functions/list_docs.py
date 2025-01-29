from datetime import datetime
from flask import Flask, json, request, jsonify
import sqlite3
from functions.decrypt_message import decrypt_message
from functions.repo_operations import (
    load_session_from_id,
    verify_session_file,
    load_server_private_key,
    sign_message,
)


def list_documents(data):
    session_id = data.get("session_id")
    username = None
    date_filter = None

    if not verify_session_file(session_id):
        return {"error": "Invalid session file"}, 400

    # Carrega os dados da sessão
    session_data = load_session_from_id(session_id)
    session_org_id = session_data.get("organization_id")
    session_key = session_data.get("symmetric_key")
    session_org_id = json.dumps(session_org_id)
    session_org_id =session_org_id[1]

    # Verifica se há dados criptografados
    if "encrypted_data" in data:
        session_key = bytes.fromhex(session_key)
        decrypted_message = decrypt_message(data["encrypted_data"], session_key)
        data_str = decrypted_message.decode("utf-8")
        data_dict = json.loads(data_str)
        username = data_dict.get("username")
        date_filter = data_dict.get("date")

    # Conecta ao banco de dados
    conn = sqlite3.connect("repository.db")
    cursor = conn.cursor()

    try:
        # Query base para buscar documentos
        query = "SELECT name, creation_date FROM documents WHERE organization_id = ?"
        params = [session_org_id]

        # Adiciona filtros, se fornecidos
        if username:
            query += " AND creator = ?"
            params.append(username)

        if date_filter:
            try:
                date_type, target_date = date_filter.split(" ")
                target_date = datetime.strptime(target_date, "%d-%m-%Y").strftime("%Y-%m-%d")

                if date_type == "nt":  # Newer than
                    query += " AND creation_date > ?"
                elif date_type == "ot":  # Older than
                    query += " AND creation_date < ?"
                elif date_type == "et":  # Equal to
                    query += " AND creation_date = ?"
                else:
                    return {"error": "Invalid date filter type"}, 400
                params.append(target_date)

            except ValueError:
                return {"error": "Invalid date format. Use DD-MM-YYYY"}, 400

        # Executa a query
        cursor.execute(query, params)
        documents = [{"name": row[0], "creation_date": row[1]} for row in cursor.fetchall()]

        # Assina a resposta
        server_private_key = load_server_private_key()
        if username != None or date_filter != None:
            if username != None and date_filter == None:
                signature_data = username.encode()
            elif username == None and date_filter != None:
                signature_data = date_filter.encode()
            else:
                data = {"username": username, "date_filter": date_filter}
                signature_data = json.dumps(data).encode()
        else:
            signature_data = session_id.encode()

        signature = sign_message(signature_data, server_private_key)

        return {"signature": signature.hex(), "documents": documents}, 201
    
    except Exception as e:
        return {"error": f"Database error: {e}"}, 500

    finally:
        conn.close()
