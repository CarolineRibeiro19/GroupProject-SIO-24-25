import json
import logging
from hashlib import sha3_224
import argparse
import os

from Crypto.Util.Padding import unpad
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from Crypto.Cipher import AES

# Configurar nível de debug
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Lista de hashes suportados
suported_hash_list = ['sha3-224']

def parse_args() -> tuple:
    parser = argparse.ArgumentParser()

    # Argumentos do script
    parser.add_argument('encrypted_file', help="File to decrypt")
    parser.add_argument('encryption_metadata', help="File with encryption metadata")
    parser.add_argument("-v", '--verbose', help="Increase verbosity", action="store_true")
    parser.add_argument("-b", '--out_bytes', help="Makes the standart output exibit the text in bytes, by default, it will be exibted in string", action="store_true")
    parser.add_argument("-f", '--decrypted_file_name', nargs="?" ,help="Name of the file to save decripted content")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info('Setting log level to DEBUG')
    
    logger.debug("args: %s", args)
    return args.encrypted_file, args.encryption_metadata, args.decrypted_file_name, args.out_bytes

# Função para verificar o hash
def check_hash(hash_expected:str, plaintext:bytes, hash) -> bool:
    if(hash in suported_hash_list):
        logger.debug("hashing plaintext with sha3-224")
        hash_calculated = sha3_224(plaintext).hexdigest()
    else:
        logger.error("unsupported hash algorithm: %s", hash)
        return False
    logger.debug("hash calculated: %s ", hash_calculated)
    logger.debug("hash expected: %s", hash_expected)

    return hash_calculated == hash_expected

# Função para decifrar usando CBC
def decipherCBC(key:bytes, ciphertext:bytes, iv: bytes) -> bytes:
    cipher = Cipher(
        algorithm = algorithms.AES128(key),
        mode = modes.CBC(iv)
    )
    decryptor = cipher.decryptor()
    logging.debug("ciphertext: %s", ciphertext)
    plaintext = unpad(decryptor.update(ciphertext) + decryptor.finalize(), AES.block_size)
    logging.debug("plaintext: %s", plaintext)
    return plaintext

"""
This command sends to the stdout the contents of an encrypted file upon decryption (and integrity control)
with the encryption metadata, that must contain the algorithms used to encrypt its contents and the encryption key.
"""
def decrypt_file(file_handle: str, metadata: str) -> bytes:
    logger.debug("decrypting file %s with metadata %s", file_handle, metadata)
    
    # Abrir arquivo e metadados
    with open(metadata, 'r') as f:
        metadata = json.load(f)
        logger.debug("metadata: %s", metadata)
    with open(file_handle, 'rb') as f:
        ciphertext = f.read()
        #logger.debug("data: %s", ciphertext)
    
    try:
        # Extrair atributos dos metadados
        key = bytes.fromhex(metadata['key'])
        print(key)
        algorithm = metadata['alg']['name']
        print(algorithm)
        mode = metadata['alg']['mode']
        print(mode)
        iv = metadata['alg']['iv']
        print(iv)
        usedHash = metadata['alg']['hash']
        print(usedHash)
    except KeyError as e:
        logger.error("inclomplete or incorrect metadata format: %s", e)
        return None

    # Verificar qual algoritmo usar para descriptografar
    if(algorithm == 'AES-128' and mode == 'CBC'):
        iv = bytes.fromhex(iv)
        plaintext = decipherCBC(key, ciphertext, iv)
        logger.debug("\nRESULT>> %s", plaintext)

        # Verificar integridade
        logger.debug("FILEHANDLES TYPE: %s",type(file_handle))
        integrity = check_hash(os.path.basename(file_handle), plaintext, usedHash)
        logger.debug("integrity %s", integrity)
        if not integrity:
            logger.error("integrity check failed")
            return None

        return plaintext
    
    else:
        logger.error("unsupported algorithm: %s", algorithm)
        return None

# Função para salvar o arquivo descriptografado
def save_file(decripted_file: bytes, file_name: str):
    with open(f'{file_name}', 'wb') as f:
        f.write(decripted_file)