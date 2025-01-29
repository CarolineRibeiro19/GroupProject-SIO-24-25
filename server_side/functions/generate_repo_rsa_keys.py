import logging
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization
from repo_operations import load_server_private_key, load_server_public_key

# configurar nível de debug
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

PRIV_KEY = './keys/repo_priv_key.pem'
PUB_KEY = './keys/repo_pub_key.pem'


def gen_rsa_credentials(password) -> tuple:

    logger.debug("generating subject credentials for password %s", password)

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
    with open(PRIV_KEY, 'wb') as pem_out:
        pem_out.write(priv_pem)

    with open(PUB_KEY, 'wb') as pem_out:
        pem_out.write(pub_pem)
        
    logger.debug("saved public and private credentials in keys folder")

    return (pub_key, priv_key)


def main(): #exemplo de uso
    password = "password"

    #1st generate the credentials and get values
    pub_key, priv_key = gen_rsa_credentials(password)
    print("Public Key:", pub_key)
    print("Private Key:", priv_key)

    #load private key and generate pub key
    loaded_pub_key = load_server_public_key()
    loaded_priv_key = load_server_private_key(password)
    print("Public Key: %s", loaded_pub_key)
    print("Private Key: %s", loaded_priv_key)

if __name__ == "__main__":
    main()