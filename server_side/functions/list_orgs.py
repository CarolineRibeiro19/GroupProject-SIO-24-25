import sqlite3
from .create_table_if_not_exists import create_table_if_not_exists
from .repo_operations import load_server_private_key, sign_message
import json

def list_orgs():
    #connect to database
    conn = sqlite3.connect('repository.db')

    #grants that table exists
    create_table_if_not_exists(conn)

    cursor = conn.cursor()

    try:
        cursor.execute("SELECT id, organization_name FROM organizations")
        organizations = [{"id": row[0], "organization_name": row[1]} for row in cursor.fetchall()]
       
        data = {"organizations": organizations}

        priv_key = load_server_private_key()
        signature = sign_message(json.dumps(data).encode('utf-8'), priv_key)

        data_to_send = {
            "data": data,
            "signature": signature.hex()
        }

        #return data
        return data_to_send, 200

    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    finally:
        conn.close()

if __name__ == '__main__':
    list_orgs()