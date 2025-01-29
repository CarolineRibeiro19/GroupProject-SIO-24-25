import os
import sys
import argparse
import logging
import json

logging.basicConfig(format='%(levelname)s\t- %(message)s')
logger = logging.getLogger()
logger.setLevel(logging.INFO)

def load_state():
    logger.debug('load_state()')
    state = {}
    # Define um diretório ~/.sio no diretório inicial do usuário.
    state_dir = os.path.join(os.path.expanduser('~'), '.sio')
    state_file = os.path.join(state_dir, 'state.json')

    logger.debug('State folder: ' + state_dir)
    logger.debug('State file: ' + state_file)
    
    # Lê o arquivo state.json deste diretório, caso ele exista, carregando seu conteúdo como um dicionário state.
    if os.path.exists(state_file):
        logger.debug('Loading state')
        with open(state_file,'r') as f:
            state = json.loads(f.read())

    # Retorna um estado vazio ({}) caso o arquivo não exista.
    if state is None:
        state = {}

    return state

def parse_env(state):
    # Caso REP_ADDRESS esteja definida, é atribuída ao estado.
    if 'REP_ADDRESS' in os.environ:
        state['REP_ADDRESS'] = os.getenv('REP_ADDRESS')
        logger.debug('Setting REP_ADDRESS from Environment to: ' + state['REP_ADDRESS'])

    # Se REP_PUB_KEY aponta para um arquivo, o conteúdo deste arquivo é lido e armazenado no estado.
    if 'REP_PUB_KEY' in os.environ:
        rep_pub_key = os.getenv('REP_PUB_KEY')
        logger.debug('Loading REP_PUB_KEY from: ' + state['REP_PUB_KEY'])
        if os.path.exists(rep_pub_key):
            with open(rep_pub_key, 'r') as f:
                state['REP_PUB_KEY'] = f.read()
                logger.debug('Loaded REP_PUB_KEY from Environment')
    return state

def save(state):
    # Define o diretório e o arquivo de estado.
    state_dir = os.path.join(os.path.expanduser('~'), '.sio')
    state_file = os.path.join(state_dir, 'state.json')

    # Cria o diretório ~/.sio se ele não existir.
    if not os.path.exists(state_dir):
      logger.debug('Creating state folder')
      os.mkdir(state_dir)

    # Escreve o estado no arquivo state.json.
    with open(state_file, 'w') as f:
        f.write(json.dumps(state, indent=4))

def increase_verbose(verbose):
    # Aumenta o nível de verbosidade do log se verbose for True.
    if verbose:
        logger.setLevel(logging.DEBUG)
        logger.info('Setting log level to DEBUG')

def get_param_state(key, repo, state):
    try:
        # Verifica e carrega a chave do repositório se fornecida.
        if key:
            if not os.path.exists(key[0]) or not os.path.isfile(key[0]):
                logger.error(f'Key file not found or invalid: {key[0]}')
                sys.exit(-1)

            with open(key[0], 'r') as f:
                state['REP_PUB_KEY'] = f.read()
                logger.info('Overriding REP_PUB_KEY from command line')

        # Verifica e carrega o endereço do repositório se fornecido.
        if repo:
            state['REP_ADDRESS'] = repo[0]
            logger.info('Overriding REP_ADDRESS from command line')
            
        logger.debug('State repo_address: ' + state['REP_ADDRESS'])
        logger.debug('State key: ' + state['REP_PUB_KEY'])
    except Exception as e:
        logger.error("Error, repository key and address not found, try setting the REPOSITORY_KEY and REPOSITORY_ADDRESS environment variables or using the -k and -r options")
        logger.error(f'Error setting state: {e}')
        sys.exit(-1)

    return state