from common_functions import generate_key_pair, sign_message, verify_signature

def main():
    # Solicitar senha do usuário
    password_a = input("Digite a senha para o usuário A: ")

    # Gerar chave secreta e pub a partir da senha
    priv, pub = generate_key_pair(password_a)
    
    # Exemplo de uso
    # assinatura
    message1 = "Esta é uma mensagem secreta"
    signature = sign_message(priv, message1)
    print("Assinatura:", signature)

    # verificação (depois de decriptar a msg)
    message2 = "Esta é uma mensagem secreta"
    is_valid = verify_signature(pub, message2, signature)
    print("Assinatura válida:", is_valid)


if __name__ == "__main__":
    main()
