import logging

# configurar nível de debug
logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

#save public key to file
def save_pub_key(credentials_file, pub):
    with open(credentials_file, 'w') as f:
        f.write(f"{hex(pub.x) + hex(pub.y % 2)[2:]}\n")
        logger.debug(f"Chave pública salva em {credentials_file}")

#load public key from file
def load_pub_key(credentials_file):
    with open(credentials_file, 'r') as f:
        pub_key = f.readline().strip()
        logger.debug(f"Chave pública carregada de {credentials_file}")
        return pub_key