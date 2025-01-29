# manipulation of documents in the database
import sqlite3
import sys
import json
from flask import jsonify

#from functions.create_table_if_not_exists import create_table_docs

from functions.create_table_if_not_exists import create_table_docs


DATABASE = 'repository.db'

def add_doc(name, file_handle, alg, key, organization_id):
    print("TYPE OF ALG: ", type(alg))
    alg = json.dumps(alg)
    print("TYPE OF ALG: ", type(alg))
    #connect to the database
    conn = sqlite3.connect(DATABASE)
    create_table_docs(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO documents (name, file_handle, alg, key, organization_id)
            VALUES (?, ?, ?, ?, ?) """,
            (name, file_handle, alg, key, organization_id))

        #gets the id of the organization that was just created
        #id = cursor.lastrowid 

        #confirm and close the connection
        conn.commit()
        return "Document created successfully", 201
    except sqlite3.IntegrityError as e:
        return "Integrity error", 409
    except Exception as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()



def list_docs(app, organization_id):
    #connect to database
    conn = sqlite3.connect(DATABASE)
    #grants that table exists
    create_table_docs(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""SELECT name FROM documents
                       WHERE organization_id = ?""",
                       (organization_id,))
        data = cursor.fetchall()
        return json.dumps(data), 200
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    except Exception as e:
        return {"error": f"Error: {e}"}, 500
    finally:
        conn.close()


def find_org(session_id):
    #open file named session_id
    try:
        with open(f"sessions/{session_id}.json", "r") as f:
            session = json.load(f)
            return session['organization_id']
    except Exception as e:
        raise Exception(f"Error: {e}")



if __name__ == '__main__':
    org = find_org(sys.argv[1])
    print(list_docs(org))
    
    result = add_doc(
        name = "exemplo.pdf",
        file_handle= "f0105d5ff773f0572c455b7de54ddaefc61b40749f5f9fc262f02832",
        alg = json.dumps({ 'name': "AES-128",
            'keysize': 128,
            'mode': "CBC",
            'iv': "aad1583cd91365e3bb2f0c3430d065bb",
            'hash': "sha3-224" }),
        key= "0700d603a1c514e46b6191ba430a3a0c",
        organization_id = 0
    )
    print(result)

    print(list_docs(org))

"""
    "documents": [
        {
            "document_handle": 0,
            "name": "files/exemplo.pdf",
            "create_date": 1731450002.8484697,
            "creator": "person",
            "file_handle": "f0105d5ff773f0572c455b7de54ddaefc61b40749f5f9fc262f02832",
            "acl": [],
            "deleter": null,
            "restricted_metadata": {
                "alg": {
                    "name": "AES-128",
                    "keysize": 128,
                    "mode": "CBC",
                    "iv": "aad1583cd91365e3bb2f0c3430d065bb",
                    "hash": "sha3-224"
                },
                "key": "0700d603a1c514e46b6191ba430a3a0c"
            }
        },
        """