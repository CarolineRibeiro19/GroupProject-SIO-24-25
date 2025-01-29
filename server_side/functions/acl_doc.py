import sqlite3
import json
from functions.decrypt_message import decrypt_message
from functions.repo_operations import (
    load_session_from_id,
    verify_session_file,
    load_server_private_key,
    sign_message,
    check_document_permission,
)

def modify_document_acl(data):
    session_id = data.get("session_id")

    if not verify_session_file(session_id):
        return {"error": "Invalid session file"}, 400

    session_data = load_session_from_id(session_id)
    session_org_id = session_data.get("organization_id")
    session_org_id = json.dumps(session_org_id)
    session_org_id = session_org_id[1]
    session_roles = session_data.get("roles")
    session_key = session_data.get("symmetric_key")

    session_key = bytes.fromhex(session_key)
    decrypted_message = decrypt_message(data["encrypted_data"], session_key)
    data_dict = json.loads(decrypted_message.decode("utf-8"))

    document_name = data_dict.get("document_name")
    operation = data_dict.get("operation")
    role = data_dict.get("role")
    permission = data_dict.get("permission")

    if not document_name or not operation or not role or not permission:
        return {"error": "Missing required fields"}, 400

    if not check_document_permission(document_name, session_roles, "DOC_ACL", session_org_id):
        return {"error": "Permission denied"}, 403

    conn = sqlite3.connect("repository.db")
    cursor = conn.cursor()

    try:
        cursor.execute(
            "SELECT acl FROM documents WHERE name = ? AND organization_id = ?",
            (document_name, session_org_id),
        )
        row = cursor.fetchone()

        if not row:
            return {"error": "Document not found"}, 404

        acl = json.loads(row[0])

        if role not in acl:
            acl[role] = []

        if operation == "+":
            if permission not in acl[role]:
                acl[role].append(permission)
        elif operation == "-":
            if permission in acl[role]:
                acl[role].remove(permission)
        else:
            return {"error": "Invalid operation"}, 400

        cursor.execute(
            "UPDATE documents SET acl = ? WHERE name = ? AND organization_id = ?",
            (json.dumps(acl), document_name, session_org_id),
        )
        conn.commit()

        server_private_key = load_server_private_key()
        signature_data = json.dumps(data_dict).encode()
        signature = sign_message(signature_data, server_private_key)

        return {"signature": signature.hex()}, 200

    except Exception as e:
        return {"error": f"Database error: {e}"}, 500

    finally:
        conn.close()
