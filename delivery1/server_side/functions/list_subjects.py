import sqlite3
import sys
import json
from functions.create_table_if_not_exists import create_table_if_not_exists

def list_subjects(organization_id):

    print("organization_id: ", organization_id)
    #connect to database
    conn = sqlite3.connect('repository.db')

    #grants that table exists
    create_table_if_not_exists(conn)

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT username, full_name FROM subjects WHERE organization_id = ?", (organization_id,))
        subjects = [{"username": row[0], "name": row[1]} for row in cursor.fetchall()]
        return subjects, 200
    except sqlite3.Error as e:
        print("Erro na base de dados")
        return {"error": f"Database error: {e}"}, 500
    finally:
        conn.close()