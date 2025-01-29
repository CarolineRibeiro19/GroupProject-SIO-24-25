import json
import sqlite3
from functions.create_table_if_not_exists import create_table_if_not_exists
from functions.decrypt_message import decrypt_message
from functions.repo_operations import load_server_private_key, load_session_from_id, sign_message, verify_session_file

def list_username_roles(data):

    session_id = data["session_id"]
    
    if verify_session_file(session_id):
        # Carrega os dados da sessão
        session_data = load_session_from_id(session_id)
        session_key = session_data.get("symmetric_key")
        session_key = bytes.fromhex(session_key)
        session_org_id = session_data.get("organization_id")

        # Descriptografa a mensagem
        decrypted_message = decrypt_message(data["encrypted_data"], session_key)
        data_str = decrypted_message.decode('utf-8')
        data_dict = json.loads(data_str)

        # Role passada como argumento
        username = data_dict["username"]
        session_org_id = json.dumps(session_org_id)

        # Conecta ao banco de dados
        conn = sqlite3.connect('repository.db')
        create_table_if_not_exists(conn)
        cursor = conn.cursor()

        try:
            # Recupera o ACL da organização
            cursor.execute("SELECT acl FROM organizations WHERE id = ?", (session_org_id[1],))
            result = cursor.fetchone()

            if result and result[0]:
                current_acl = json.loads(result[0])  # Carrega o JSON existente
                print(current_acl)
            else:
                return {"error": "No ACL found for this organization"}, 404

            # Lista todos os roles em que o username está presente
            roles_with_username = []

            if "roles" in current_acl:
                for role, details in current_acl["roles"].items():
                    if "subjects" in details and username in details["subjects"]:
                        roles_with_username.append(role)
                        
                print(roles_with_username)
                server_private_key =  load_server_private_key()
                signature = sign_message(decrypted_message, server_private_key)
                signature = {"signature": signature.hex(), "subject roles" : roles_with_username }

                return signature, 201
            else:
                return {"error": f"Role '{role}' not found in ACL"}, 404

        except sqlite3.Error as e:
            return {"error": f"Database error: {e}"}, 500
        finally:
            conn.close()
    else:
        return {"error": "Invalid session file"}, 400
