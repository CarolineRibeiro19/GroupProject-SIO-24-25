import json
import logging
import time
import os
from hashlib import sha3_224

from Crypto.Util.Padding import pad
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.Cipher import AES

#set debug level
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.DEBUG)

###CIPHER CBC
def cipherCBC(key:bytes, plaintext: bytes, iv: bytes) -> bytes:
    #TODO add verification
    cipher = Cipher(
        algorithm = algorithms.AES128(key),
        mode = modes.CBC(iv)
    )
    encryptor = cipher.encryptor()
    logging.debug("plaintext: %s", plaintext)
    ciphertext = encryptor.update(pad(plaintext, AES.block_size)) + encryptor.finalize()
    logging.debug("ciphertext: %s", ciphertext)

    
    metadata = {
        'alg': {
            'name': 'AES-128',
            'keysize': 128,
            'mode': 'CBC',
            'iv': iv.hex(),
            'hash': 'sha3-224'
        },
        'key': key.hex()
    }

    return ciphertext, metadata


def save_ciphertext(ciphertext: bytes, file_digest: str) -> None:
    path = f'{file_digest}'
    logger.debug('saving %s', path)
    with open(path, 'wb') as f:
        f.write(ciphertext)

def save_metadata(file_name, file_digest, restricted_metadata: dict) -> None:
    path = f'documents.json'
      
    with open(path, 'r') as f:
        metadata_list = json.load(f)

    metadata = {
        'document_handle': len(metadata_list['documents']), #number of documents
        'name': os.path.basename(file_name),
        'create_date': time.time(),
        'creator': "person",
        'file_handle': file_digest,
        'acl': [],
        'deleter': None,
        'restricted_metadata' : restricted_metadata
    }
    metadata_list['documents'].append(metadata)

    with open(path, 'w') as f:
        f.write(json.dumps(metadata_list, indent=4))

def encrypt_file(file_name: str, key:bytes, iv: bytes) -> None:
    logger.debug("encrypting file %s", file_name)
    #open file
    with open(file_name, 'rb') as f:
        plaintext = f.read()
        logger.debug("data: %s", plaintext)
        
    #generate digest

    #encrypt plaintext
    ciphertext, restricted_metadata = cipherCBC(key, plaintext, iv)
    file_digest = sha3_224(ciphertext).hexdigest()
    logger.debug("ciphertext: %s", ciphertext)

    return restricted_metadata, file_digest, ciphertext
