import sqlite3
import json
from functions.decrypt_message import decrypt_message
from functions.repo_operations import (
    check_document_permission,
    get_username_by_id,
    load_session_from_id,
    verify_session_file,
    load_server_private_key,
    sign_message,
)

def delete_doc(data, permission = "DOC_DELETE"):
    session_id = data.get("session_id")

    if verify_session_file(session_id):

        # Carrega os dados da sessão
        session_data = load_session_from_id(session_id)
        session_org_id = session_data.get("organization_id")
        session_org_id = json.dumps(session_org_id)
        session_org_id = session_org_id[1]
        session_roles = session_data.get("roles")
        session_key = session_data.get("symmetric_key")
        session_user = get_username_by_id(session_data.get("user_id"))

        # Descriptografa os dados
        session_key = bytes.fromhex(session_key)
        decrypted_message = decrypt_message(data["encrypted_data"], session_key)
        data_str = decrypted_message.decode("utf-8")
        data_dict = json.loads(data_str)
        document_name = data_dict.get("document_name")

        if not document_name:
            return {"error": "Document name not provided"}, 400

        # Verifica permissões
        if check_document_permission(document_name, session_roles, permission, session_org_id):

            # Conecta ao banco de dados
            conn = sqlite3.connect("repository.db")
            cursor = conn.cursor()

            try:
                # Obtém o documento e verifica se ele existe
                cursor.execute(
                    "SELECT file_handle FROM documents WHERE name = ? AND organization_id = ?",
                    (document_name, session_org_id),
                )
                row = cursor.fetchone()

                if not row:
                    return {"error": "Document not found"}, 404

                file_handle = row[0]

                # Realiza a exclusão lógica do documento
                cursor.execute(
                    """
                    UPDATE documents
                    SET file_handle = NULL, deleter = ?
                    WHERE name = ? AND organization_id = ?
                    """,
                    (session_user, document_name, session_org_id),
                )
                conn.commit()
                server_private_key = load_server_private_key()
                signature = sign_message(document_name.encode(), server_private_key)
                return {"file_handle": file_handle, "signature": signature.hex()}, 201

            except Exception as e:
                return {"error": f"Database error: {e}"}, 500
            finally:
                conn.close()

            
        return {"error": "Permission denied"}, 403
    
    return {"error": "Invalid session file"}, 400
        

    

    