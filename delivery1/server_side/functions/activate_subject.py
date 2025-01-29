#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sqlite3
import sys


from functions.create_table_if_not_exists import create_table_if_not_exists
from pathlib import Path

# Caminho relativo usando pathlib
path_sessions = '/Users/cacar/Desktop/SIO/sio-2425-project-104170_106093_117450/delivery1/server_side/sessions'

def session_id_exists(path, nome_arquivo):
    
    arquivos = os.listdir(path)

    nome_arquivo = nome_arquivo + ".json"

    if nome_arquivo in arquivos:
        return True
    return False

def activate_subject(session_id, username):

    if session_id_exists(path_sessions,session_id):

        # Conectar ao banco de dados
        conn = sqlite3.connect('repository.db')
        create_table_if_not_exists(conn)
        cursor = conn.cursor()

        try:
            # Atualizar o status do sujeito para 'up'
            cursor.execute("""
                UPDATE subjects
                SET status = ?
                WHERE username = ?
            """, ("up",  username))

            # Confirmar a transação
            conn.commit()

            return "Subject activated successfully", 200
        
        except Exception as e:
            return f"Database error: {e}", 500
        finally:
            conn.close()
    else:
        return "Session expired."
