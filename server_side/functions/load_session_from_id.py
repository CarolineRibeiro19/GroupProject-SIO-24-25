import json
import os


def load_session_from_id(sessions, session_id):
    """
    Carrega os dados da sessão a partir de um ID de sessão.

    :param session_folder: Caminho para a pasta contendo os arquivos de sessão (str).
    :param session_id: ID da sessão a ser procurada (str).
    :return: Dados da sessão (dict) ou None se não encontrado.
    """
    try:
        for filename in os.listdir(sessions):
            file_path = os.path.join(sessions, filename)
            if os.path.isfile(file_path):
                with open(file_path, "r") as file:
                    session_data = json.load(file)
                    if session_data.get("session_id") == session_id:
                        return session_data
        return None
    except Exception as e:
        raise ValueError(f"Erro ao carregar sessão: {e}")