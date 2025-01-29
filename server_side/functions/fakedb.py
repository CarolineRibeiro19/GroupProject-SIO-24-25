from create_table_if_not_exists import create_table_if_not_exists, create_table_docs
import sqlite3
import json
import repo_operations
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import ec


# Função para gerar um par de chaves ECC a partir de uma senha
def generate_key_pair(password):
    private_key = ec.derive_private_key(
        int.from_bytes(password.encode(), byteorder="big"),
        ec.BrainpoolP256R1()
    )
    public_key = private_key.public_key()
    return private_key, public_key

#serialize ECC public key
def serialize_public_key(public_key):
    return public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )

# Conexão com a base de dados
conn = sqlite3.connect('repository.db')
cursor = conn.cursor()

create_table_docs(conn)
create_table_if_not_exists(conn)

try:
    # Garantir que a tabela exista
    create_table_if_not_exists(conn)

    # Inserir a organização
    cursor.execute("""
        INSERT INTO organizations (organization_name, acl)
        VALUES (?, ?)
        """, ("UA", json.dumps({
            "roles": {
                "manager": {
                    "status": "up",
                    "subjects": ['antonia'],
                    "permissions": ["ROLE_ACL", "SUBJECT_NEW", "SUBJECT_DOWN", "SUBJECT_UP", "DOC_NEW"]
                },
                "moderator": {
                    "status": "up",
                    "subjects": ['beatriz, carla'],
                    "permissions": ["SUBJECT_NEW", "SUBJECT_DOWN", "SUBJECT_UP", "DOC_NEW"]
                },
                "contributors" : {
                    "status": "down",
                    "subjects": ['daniela, eduarda'],
                    "permissions": ["DOC_NEW"]
                }
            }
        })))
    
    # Obter o id da organização que acabou de ser criada
    organization_id = cursor.lastrowid 

    # Inserir o criador na tabela de subjects com o papel de manager
    cursor.execute("""
        INSERT INTO subjects (organization_id, username, full_name, email, public_key, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (organization_id, "antonia", "Antonia Silva", "antonia@email.com", repo_operations.get_public_key(), "up"))

    # Confirma a transação
    conn.commit()
    print("Organization created successfully")

except Exception as e:
    print(f"Database error: {e}")

finally:
    conn.close()