import subprocess
import os

def run_command(command):
    """Executa um comando no terminal."""
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"Comando executado com sucesso: {command}")
        print(f"Saída: {result.stdout.strip()}")
        return result.stdout.strip()
    except subprocess.CalledProcessError as e:
        print(f"Erro ao executar o comando: {command}")
        print(f"Erro: {e.stderr.strip()}")
        return None

def create_credentials(password, credentials_file):
    """Cria um arquivo de credenciais usando o comando rep_subject_credentials."""
    command = f"./rep_subject_credentials {password} {credentials_file}"
    run_command(command)

def create_organization(org_name, username, name, email, public_key_file):
    """Cria uma organização usando o comando rep_create_org."""
    command = f"./rep_create_org {org_name} {username} {name} {email} {public_key_file}"
    run_command(command)

#rep_create_session <organization> <username> <password> <credentials file> <session file>

def create_session(org_name, username, password, credentials_file, session_file):
    """Cria uma sessão usando o comando rep_create_session."""
    command = f"./rep_create_session {org_name} {username} {password} {credentials_file} {session_file}"
    run_command(command)

def main():
    # Lista de organizações com dados fixos
    organizations = [
        {"org_name": "Mercadona", "username": "anamercadona", "name": "ana", "email": "ana@mercadona.pt", "password": "12345"},
        {"org_name": "PingoDoce", "username": "joaopingodoce", "name": "joao", "email": "joao@pingodoce.pt", "password": "12345"},
        {"org_name": "Continente", "username": "mariacontinente", "name": "maria", "email": "maria@continente.pt", "password": "12345"},
        {"org_name": "Auchan", "username": "pedroauchan", "name": "pedro", "email": "pedro@auchan.pt", "password": "12345"},
        {"org_name": "Lidl", "username": "catarinalidl", "name": "catarina", "email": "catarina@lidl.pt", "password": "12345"},
    ]


    for org in organizations:
        org_name = org["org_name"]
        username = org["username"]
        name = org["name"]
        email = org["email"]
        password = org["password"]
        credentials_file = f"{org_name}_credentials.pem"

        # Criar credenciais
        create_credentials(password, credentials_file)

        # Criar organização
        create_organization(org_name, username, name, email, credentials_file)

        create_session(org_name, username, password, credentials_file, f"{org_name}_session")



if __name__ == "__main__":
    main()
