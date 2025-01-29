import json
import os
import sqlite3
import hashlib
import time
from tinyec import registry 
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.backends import default_backend
from functions.create_table_if_not_exists import create_table_if_not_exists, create_table_docs
from cryptography.hazmat.primitives.asymmetric import ec, utils
from cryptography.hazmat.primitives.asymmetric.utils import Prehashed
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend
from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.backends import default_backend

DATABASE = 'repository.db'

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

#deserialize ECC public key
def deserialize_public_key(serialized_public_key):
    return serialization.load_pem_public_key(
        serialized_public_key
    )

# Função para obter o ID do usuário a partir do username
def get_user_id(username):
    #connect to database
    conn = sqlite3.connect(DATABASE)
    #grants that table exists
    create_table_if_not_exists(conn)
    cursor = conn.cursor()
    try:
        cursor.execute("""SELECT id FROM subjects
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

# Função para obter a chave pública de um usuário a partir do username
def get_public_key(username):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(DATABASE)  # Substitua 'database.db' pelo seu banco de dados real
    cursor = conn.cursor()

    # Consultar a chave pública para o nome de usuário fornecido
    cursor.execute("SELECT public_key FROM subjects WHERE username = ?", (username,))
    result = cursor.fetchone()

    # Fechar a conexão com o banco de dados
    conn.close()

    # Verificar se a chave pública foi encontrada
    if result is None:
        raise ValueError(f"Public key for username {username} not found.")
    
    # A chave pública está armazenada no banco de dados em formato PEM
    public_key_pem = result[0]
    
    # Carregar a chave pública a partir do PEM
    public_key = serialization.load_pem_public_key(public_key_pem.encode())

    return public_key

# Função para obter o ID da organização a partir do nome de usuário
def get_org_id(username):
    # Conectar ao banco de dados SQLite
    conn = sqlite3.connect(DATABASE)  # Substitua 'database.db' pelo seu banco de dados real
    cursor = conn.cursor()

    # Consultar a chave pública para o nome de usuário fornecido
    cursor.execute("SELECT organization_id FROM subjects WHERE username = ?", (username,))
    result = cursor.fetchone()

    # Fechar a conexão com o banco de dados
    conn.close()

    # Verificar se a chave pública foi encontrada
    if result is None:
        raise ValueError(f"Organization ID for username {username} not found.")

    return result

#serialize ECC public key
def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

#verify ECC user signature
#receive parameters in hex format
def verify_subject_signature(public_key: str, message: str, signature) -> bool:
    # Hash dos dados antes de verificar
    signature = bytes.fromhex(signature)
    message = message.encode()
    try:
    ##to remmber: message e signature são bytes
        public_key.verify(signature, message, ec.ECDSA(hashes.SHA256()))
        print("Assinatura verificada com sucesso")
        return True
    except Exception:
        print("Invalid signature")
        return False
    
#verify RSA signature
def verify_repository_signature(message, signature, public_key):
    try:
        public_key.verify(
            signature,
            message,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )
        print("Assinatura verificada com sucesso")
        return 0
    except InvalidSignature:
        print("Assinatura inválida")
        return -1
    
# Função para descomprimir uma chave pública ECC
def decompress(compressed_key):
    x = int(compressed_key[:64], 16)
    y = int(compressed_key[64:], 16)
    return registry.get_curve('brainpoolP256r1').point(x, y)

# Função para decriptar a chave simétrica com a chave privada do servidor
def decrypt_symmetric_key(encrypted_symmetric_key, server_private_key):
    encrypted_symmetric_key = bytes.fromhex(encrypted_symmetric_key)
    plaintext = server_private_key.decrypt(
        encrypted_symmetric_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None
        )
    )
    return plaintext

# Função para carregar a chave privada do servidor
def load_server_private_key(PRIV_KEY = 'keys/repo_priv_key.pem', repo_master_key = "password"):
    with open(PRIV_KEY, "rb") as private_key_file:
        return serialization.load_pem_private_key(
            private_key_file.read(),
            password=repo_master_key.encode(),
            backend=default_backend()
        )

# Função para carregar a chave pública do servidor
def load_server_public_key(PUB_KEY = 'keys/repo_pub_key.pem'):
    with open(PUB_KEY, 'rb') as key_file:
        pub_key = serialization.load_pem_public_key(
            key_file.read()
        )
    #print(pub_key)
    return pub_key

def verify_session_file(session_id):
    # Caminho absoluto para a pasta de sessões
    session_folder = os.path.abspath("sessions")  # Ajuste para absoluto ou relativo
    session_path = os.path.join(session_folder, str(session_id))
    session_path = session_path + ".json"

    try:
        # Verifica se o arquivo de sessão existe
        if not os.path.isfile(session_path):
            print(f"Arquivo de sessão {session_path} não encontrado.")
            return False

        # Abre e lê o conteúdo do arquivo JSON
        with open(session_path, "r", encoding="utf-8") as file:
            session_data = json.load(file)

        timeout = session_data.get("timeout", 3600)  # Timeout padrão de 1 hora

        # Verifica se a sessão expirou
        current_time = time.time()
        if current_time > timeout:
            print(f"Sessão expirou. Removendo o arquivo: {session_path}")
            os.remove(session_path)  # Remove o arquivo expirado
            return False

        return True

    except FileNotFoundError:
        print("Arquivo de sessão não encontrado.")
        return False

    except json.JSONDecodeError:
        print(f"Erro ao decodificar o JSON no arquivo {session_path}.")
        return False

    except Exception as e:
        raise ValueError(f"Erro ao verificar a sessão: {e}")



def load_session_from_id(session_id):
    # Caminho absoluto para a pasta de sessões
    session_folder = os.path.abspath("sessions")  # Ajuste para absoluto ou relativo
    session_path = os.path.join(session_folder, str(session_id))
    session_path = session_path + ".json"

    # Verifica se o arquivo existe
    if not os.path.isfile(session_path):
        raise FileNotFoundError(f"Arquivo {session_id} não encontrado na pasta {session_path}")

    # Abre e carrega o conteúdo do arquivo JSON
    with open(session_path, "r", encoding="utf-8") as file:
        data = json.load(file)  # Carrega o JSON como um dicionário
        return data
    

def check_permission_user(roles,org_id, username, permission):
    
    org_id = org_id[1]

    try:
        connection = sqlite3.connect("repository.db")
        cursor = connection.cursor()

        # Garantir que a tabela exista
        create_table_if_not_exists(connection)

        # Obter o ACL da organização
        cursor.execute(
            """
            SELECT acl
            FROM organizations
            WHERE id= ?
            """,
            (org_id,)
        )
        org_data = cursor.fetchone()

        if not org_data:
            raise ValueError("Organização não encontrada.")
        
        acl = json.loads(org_data[0])

        # Verificar permissões nos roles do ACL
        for role in roles:
            if "roles" in acl and role in acl["roles"]:
                data = acl["roles"]
                if username in data.get(role, {}).get("subjects", []):
                    if permission in data.get(role, {}).get("permissions", []):
                        return True

        return False

    except Exception as e:
        raise ValueError(f"Erro ao verificar permissão: {e}")

    finally:
        connection.close()

import sqlite3
import json

def check_document_permission(document_name, roles, permission, organization_id):
    conn = sqlite3.connect("test_repository.db")
    cursor = conn.cursor()

    try:
        # Obtém o ACL do documento
        cursor.execute(
            "SELECT acl FROM documents WHERE name = ? AND organization_id = ?",
            (document_name, organization_id),
        )
        row = cursor.fetchone()

        if not row:
            return False  # Documento não encontrado

        # Carrega o ACL como JSON
        acl = json.loads(row[0])

        # Verifica se o role existe no ACL
        for role in roles:
            # Verifica se a permission está associada ao role
            return permission in acl[role]

        return False  # Role não encontrado no ACL

    except Exception as e:
        print(f"Database error: {e}")
        return False

    finally:
        conn.close()

def get_username_by_id( user_id):
    
    try:
        # Conecta ao banco de dados
        connection = sqlite3.connect("repository.db")
        cursor = connection.cursor()

        # Executa a consulta
        cursor.execute("SELECT username FROM subjects WHERE id = ?", (user_id,))
        result = cursor.fetchone()

        # Fecha a conexão
        connection.close()

        # Retorna o nome do usuário se encontrado
        return result[0] if result else None
    except sqlite3.Error as e:
        print(f"Erro ao acessar o banco de dados: {e}")
        return None
    

def add_doc(name, file_handle, alg, key, organization_id):
    #connect to the database
    conn = sqlite3.connect(DATABASE)
    create_table_docs(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO documents (name, file_handle, alg, key, organization_id)
            VALUES (?, ?, ?, ?, ?) """,
            (name, file_handle, alg, key, organization_id[0]))

        #confirm and close the connection
        conn.commit()
        return "Document created successfully", 201
    except sqlite3.IntegrityError as e:
        return "Integrity error", 409
    except Exception as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()