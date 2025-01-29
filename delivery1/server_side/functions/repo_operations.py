import json
import sqlite3
import uuid
import time
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from functions.create_table_if_not_exists import create_table_if_not_exists

DATABASE = 'repository.db'

# Função para carregar a chave privada do servidor
def load_server_private_key(server_private_key_password="password"):
    try:
        with open("keys/server_private_key.pem", "rb") as private_key_file:
            return serialization.load_pem_private_key(
                private_key_file.read(),
                password=server_private_key_password.encode(),
                backend=default_backend()
            )
    except Exception as e:
        raise ValueError(f"Error loading the server's private key: {e}")

# Função para descriptografar a chave simétrica usando a chave privada do servidor
def decrypt_symmetric_key(encrypted_symmetric_key, private_key):
    try:
        if isinstance(encrypted_symmetric_key, str):
            encrypted_symmetric_key = bytes.fromhex(encrypted_symmetric_key)
        return private_key.decrypt(
            encrypted_symmetric_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None
            )
        )
    except Exception as e:
        raise ValueError(f"Error decrypting the symmetric key: {e}")

# Função para descriptografar dados com AES-GCM
def decrypt_data(encrypted_data, symmetric_key, nonce, tag):
    try:
        cipher = Cipher(algorithms.AES(symmetric_key), modes.GCM(nonce, tag), backend=default_backend())
        decryptor = cipher.decryptor()
        decrypted_data = decryptor.update(encrypted_data) + decryptor.finalize()
        json_data = json.loads(decrypted_data.decode())
        return json_data
    except Exception as e:
        raise ValueError(f"Error decrypting the data: {e}")

# Função para assinar mensagens com a chave privada do servidor
def sign_message(message, private_key):
    try:
        return private_key.sign(
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
    except Exception as e:
        raise ValueError(f"Error signing the message: {e}")

def get_user_id(username):
    #connect to database
    conn = sqlite3.connect(DATABASE)
    #grants that table exists
    create_table_if_not_exists(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT id FROM users
                        WHERE username = ?""",
                        (username,))
        data = cursor.fetchone()
        return data[0]
    except sqlite3.Error as e:
        return {"error": f"Database error: {e}"}, 500
    except Exception as e:
        return {"error": f"Error: {e}"}, 500
    finally:
        conn.close()

# Função principal para criação de sessão
def create_session(data, server_private_key_password="password"):

    try:
        # Verificar campos obrigatórios
        required_fields = ["encrypted_key", "encrypted_data", "nonce", "tag", "rsa_public_key"]
        for field in required_fields:
            if field not in data:
                raise KeyError(f"Required field missing: '{field}'")

        # Carregar a chave privada do servidor
        private_key = load_server_private_key(server_private_key_password)

        # Descriptografar a chave simétrica com a chave privada do servidor
        encrypted_symmetric_key = data["encrypted_key"]
        symmetric_key = decrypt_symmetric_key(encrypted_symmetric_key, private_key)

        # Descriptografar dados com a chave simétrica
        encrypted_data = bytes.fromhex(data["encrypted_data"])
        nonce = bytes.fromhex(data["nonce"])
        tag = bytes.fromhex(data["tag"])
        decrypted_data = decrypt_data(encrypted_data, symmetric_key, nonce, tag)
        print("Data received and decrypted:", decrypted_data)

        # Assinar uma mensagem de confirmação
        message = b"Session established"
        signature = sign_message(message, private_key)

        # Gerar um ID de sessão (UUID)
        session_id = str(uuid.uuid4())

        # Salvar o ID da sessão no arquivo
        #session_file_path = data.get("session_file")
        session_file_path = "sessions/" + session_id + ".json"

        session_data = json.dumps({
            "session_id": session_id,
            "user_id": get_user_id(decrypted_data['username']),
            "symmetric_key": symmetric_key.hex(),
            "timestamp": time.time(),
            "organization_id": decrypted_data['organization'],
            "user_pub_key": data['rsa_public_key']
        })

        with open(session_file_path, "w") as session_file:
            session_file.write(session_data)
            
        return {"message": message.decode(), "signature": signature.hex(), "session_id": session_id}, 201

    except KeyError as ke:
        return {"error": str(ke)}, 400
    except ValueError as ve:
        return {"error": str(ve)}, 400
    except Exception as e:
        return {"error": str(e)}, 500








