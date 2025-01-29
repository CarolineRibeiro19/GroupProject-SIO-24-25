import json

def load_session_data(session_file):
    # Carregar os dados da sessão
    with open(session_file, "r") as file:
        session_data = json.load(file)

    # Obter o session_id
    session_id = session_data.get("session_id")
    if not session_id:
        return "Erro: session_id not found."
    session_key = session_data.get("session_key")
    if not session_key:
        return "Error: session_key not found."
    return session_id,session_key