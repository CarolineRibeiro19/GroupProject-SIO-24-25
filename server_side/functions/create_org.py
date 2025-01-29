#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import json

import sqlite3
from functions.create_table_if_not_exists import create_table_if_not_exists
from functions.repo_operations import load_server_private_key, decrypt_symmetric_key
from functions.decrypt_message import decrypt_message

def create_org(data, server_private_key_password="password"):

    server_private_key = load_server_private_key()
    symmetric_key = decrypt_symmetric_key(data["encrypted_key"], server_private_key)
    decrypted_data = decrypt_message(data, symmetric_key)
    decrypted_json_data = json.loads(decrypted_data)

    organization = decrypted_json_data["organization"]
    username = decrypted_json_data["username"]
    name = decrypted_json_data["name"]
    email = decrypted_json_data["email"]
    public_key = decrypted_json_data["public_key"]

    # Conexão com a base de dados
    conn = sqlite3.connect('repository.db')
    cursor = conn.cursor()
    print("Connected to SQLite")

    try:
        # Garantir que a tabela exista
        create_table_if_not_exists(conn)

        # Inserir a organização
        cursor.execute("""
            INSERT INTO organizations (organization_name, acl)
            VALUES (?, ?)
            """, (organization, json.dumps({
                "roles": {
                    "manager": {
                        "status": "up",
                        "subjects": [username],
                        "permissions": ["DOC_ACL","DOC_READ","DOC_DELETE","DOC_ACL","DOC_READ","DOC_DELETE","ROLE_ACL","SUBJECT_NEW","SUBJECT_DOWN","SUBJECT_UP","DOC_NEW","ROLE_NEW","ROLE_DOWN","ROLE_UP","ROLE_MOD"]
                    }
                }
            })))
        
        # Obter o id da organização que acabou de ser criada
        organization_id = cursor.lastrowid 
 
        # Inserir o criador na tabela de subjects com o papel de manager
        cursor.execute("""
            INSERT INTO subjects (organization_id, username, full_name, email, public_key, status)
            VALUES(?, ?, ?, ?, ?, ?)
        """, (organization_id, username, name, email, public_key, "up"))

        print("Subject added as a manager")

        # Confirma a transação
        conn.commit()
        return "Organization created successfully", 201
    
    except sqlite3.IntegrityError as e:
        return "Organization already exists", 409
    
    except Exception as e:
        return f"Database error: {e}", 500
    
    finally:
        conn.close()