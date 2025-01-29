import sqlite3
import sys
import json
from functions.create_table_if_not_exists import create_table_if_not_exists

def list_orgs():
    #connect to database
    conn = sqlite3.connect('repository.db')

    #grants that table exists
    create_table_if_not_exists(conn)

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, organization_name FROM organizations")
        organizations = [{"id": row[0], "organization_name": row[1]} for row in cursor.fetchall()]
        return organizations, 200
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    finally:
        conn.close()

if __name__ == '__main__':
    list_orgs()