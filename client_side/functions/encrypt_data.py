from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
import functions.common_functions as cf

def encrypt_data(data_to_send,repo_key):

    server_public_key = repo_key
    public_key = serialization.load_pem_public_key(server_public_key.encode(), backend=default_backend())   
    server_public_key = public_key

    symmetric_key = cf.generate_symmetric_key()
    encrypted_data, tag, nonce = cf.encrypt_data(data_to_send, symmetric_key)
    encrypted_symmetric_key = cf.encrypt_symmetric_key(symmetric_key,server_public_key)

    encrypt_data = {
        "encrypted_key": encrypted_symmetric_key.hex(),
        "encrypted_data": encrypted_data.hex(),
        "nonce": nonce.hex(),
        "tag": tag.hex(),
    }

    return encrypt_data