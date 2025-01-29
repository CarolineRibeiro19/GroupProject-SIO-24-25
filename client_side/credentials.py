import logging
import argparse
from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.hashes import SHA256
import os
import sys

# Configurar nível de debug
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

SALT = b"fixed_salt_value"  # Um valor fixo para garantir a derivação consistente da chave privada

def parse_args() -> tuple:
    # Configurar argumentos do comando
    parser = argparse.ArgumentParser()

    parser.add_argument('password', help="Senha para derivar a chave privada")
    parser.add_argument('credentials_file', help="Arquivo para salvar a chave pública")
    parser.add_argument("-v", '--verbose', help="Aumentar verbosidade", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info('Setting log level to DEBUG')
    
    return args.password, args.credentials_file

def derive_private_key(password: str) -> ec.EllipticCurvePrivateKey:
    # Derivar chave privada a partir da senha usando PBKDF2
        try:
            kdf = PBKDF2HMAC(
                algorithm=SHA256(),
                length=32,  # Tamanho da chave para curvas elípticas (32 bytes para SECP256R1)
                salt=SALT,
                iterations=100000,
            )
            key_material = kdf.derive(password.encode('utf-8'))
            private_key = ec.derive_private_key(int.from_bytes(key_material, byteorder="big"), ec.SECP256R1())
            return private_key
        except Exception as e:
            logger.error("Error deriving private key: %s", e)
            sys.exit(-1)  # Erro crítico na geração da chave privada

def gen_subj_credentials(password: str , credentials_file: str ):
    # Gerar e salvar a chave pública no arquivo
    
    private_key = derive_private_key(password)

    try:
        public_key = private_key.public_key()
        public_pem = public_key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        )

        # Salvar a chave pública no arquivo
        with open(credentials_file, "wb") as pub_file:
            pub_file.write(public_pem)

        logger.debug("Saved public key to %s", credentials_file)
    except Exception as e:
        logger.error("Error saving public key: %s", e)
        sys.exit(-1)  # Erro crítico ao salvar a chave pública

def load_subj_credentials(password: str,credentials_file: str):
    # Carregar chave pública do 
    logger.debug("loading subject credentials from file %s with password %s", credentials_file, password)

    private_key = derive_private_key(password)

    try:
        with open(credentials_file, "rb") as pub_file:
            public_pem = pub_file.read()
            public_key = serialization.load_pem_public_key(public_pem)
            return (public_key, private_key)
    except FileNotFoundError:
        logger.error("Credentials file not found: %s", credentials_file)
        sys.exit(1)  # Erro não crítico, mas arquivo ausente
    except Exception as e:
        logger.error("Error loading credentials: %s", e)
        sys.exit(-1)  # Erro crítico ao carregar credenciais


