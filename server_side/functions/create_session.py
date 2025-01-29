from .repo_operations import decrypt_symmetric_key, load_server_private_key, sign_message, get_public_key, verify_subject_signature, get_user_id, get_org_id, create_table_if_not_exists
from functions.decrypt_message import decrypt_message
import json
import uuid
import sqlite3
import time

# Função principal para criação de sessão
def create_session(data, server_private_key_password="password"): #mudar esse server key password
    
    try:
        # recover the server private key
        server_private_key = load_server_private_key()
        # Decrypt the symmetric key in data
        symmetric_key = decrypt_symmetric_key(data["encrypted_key"], server_private_key)
        # Decrypt the data with the symmetric key
        decrypted_data = decrypt_message(data, symmetric_key)

        decrypted_json_data = json.loads(decrypted_data)

        # Verificar se a organização existe e está associada ao usuário
        conn = sqlite3.connect('repository.db')
        create_table_if_not_exists(conn)
        cursor = conn.cursor()
        
        cursor.execute("SELECT id FROM subjects WHERE username = ?", (decrypted_json_data["username"],))
        
        subject_data = cursor.fetchone()

        if not subject_data:
            return {"error": "Subject not found"}, 403
        # Verificar se o usuário está associado à organização
       
        # Buscar o ID da organização com base no nome fornecido
        cursor.execute("SELECT id FROM organizations WHERE organization_name = ?", (decrypted_json_data["organization"],))
        organization_data = cursor.fetchone()

        # Verificar se a organização existe
        if not organization_data:
            return {"error": "Organization not found."}, 404
        
        org_id = organization_data[0]

        # Obter o ID da organização a partir do banco de dados
        organization_id_from_db = organization_data[0]

        # Verificar se o usuário está associado à organização
        if organization_id_from_db != org_id:
            return {"error": "User not associated with the specified organization."}, 403
    
        public_key_subj = get_public_key(decrypted_json_data["username"])
    
        message = b"Session not established"
        # Gerar um ID de sessão (UUID)
        session_id = str(uuid.uuid4())
        #verificar assinatura do usuário
        signature_ok = verify_subject_signature(public_key=public_key_subj, signature=data["signature"], message=data["encrypted_data"])
        if not signature_ok:
            return {"error": "Invalid signature"}, 403
        else:
            print("VERIFIED")
            # Assinar uma mensagem de confirmação
            message = b"Session established" #TODO use UNIX pattern

            # Salvar o ID da sessão no arquivo
            session_file_path = "sessions/" + session_id + ".json"

            session_data = json.dumps({
                "user_id": get_user_id(decrypted_json_data['username']),
                "symmetric_key": symmetric_key.hex(),
                "organization_id": get_org_id(decrypted_json_data['username']),
                "timeout": time.time() + 3600  # 1 hora de timeout
            })

            with open(session_file_path, "w") as session_file:
                session_file.write(session_data)
        
        signature = sign_message(message=message, private_key=server_private_key)
        return {"message": message.decode(), "signature": signature.hex(), "session_id": session_id}, 201
    except KeyError as ke:
        return {"error": str(ke)}, 400
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500
    