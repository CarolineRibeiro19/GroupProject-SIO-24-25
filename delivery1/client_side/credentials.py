import logging
import argparse
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

# configurar nível de debug
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def parse_args() -> tuple:
    # configurar argumentos do comando
    parser = argparse.ArgumentParser()

    parser.add_argument('password', help="Senha para criptografar a chave privada")
    parser.add_argument('credentials_file', help="Arquivo para salvar as credenciais")
    parser.add_argument("-v", '--verbose', help="Aumentar verbosidade", action="store_true")

    args = parser.parse_args()
    if args.verbose:
        logger.setLevel(logging.DEBUG)
        logger.info('Setting log level to DEBUG')
    
    return args.password, args.credentials_file

def gen_subj_credentials(password, credentials_file) -> tuple:

    logger.debug("generating subject credentials for password %s and file %s", password, credentials_file)

    priv_key = rsa.generate_private_key(
        public_exponent=65537, key_size=1024
    )

    # serializar chave privada
    priv_pem = priv_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.BestAvailableEncryption(bytes(password, 'utf-8'))
    )
    logger.debug("generated private credentials")
        
    # gerar chave pública
    pub_key = priv_key.public_key()
    pub_pem = pub_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.PKCS1
    )
    logger.debug("generated public credentials")

    # salvar chaves no arquivo
    with open(credentials_file, 'wb') as pem_out:
        pem_out.write(priv_pem)
        pem_out.write(pub_pem)
        
    logger.debug("saved public and private credentials in %s", credentials_file)

    return (pub_key, priv_key)

def load_subj_credentials(password: str, credentials_file: str) -> tuple:
    # carregar credenciais do arquivo
    logger.debug("loading subject credentials from file %s with password %s", credentials_file, password)

    # ler dados do arquivo
    with open(credentials_file, 'rb') as pem_in:
        pem_data = pem_in.read()
        
    # carregar chave privada
    priv_key = serialization.load_pem_private_key(
        pem_data,
        password=bytes(password, 'utf-8')
    )
    logger.debug("loaded private credentials")

    # obter chave pública da chave privada
    pub_key = priv_key.public_key()
    logger.debug("loaded public credentials")

    return (pub_key, priv_key)
