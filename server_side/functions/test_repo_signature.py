from repo_operations import verify_repository_signature, sign_message, load_server_private_key, load_server_public_key

def main():
    repo_master_key = "password"
    private_key = load_server_private_key(repo_master_key)
    message1 = b"Hello, world!"
    signature = sign_message(message1, private_key)

    print(signature)
    
    message2 = b"Hellasdfo, world!"
    public_key = load_server_public_key()
    verify_repository_signature(message2, signature, public_key)

if __name__ == "__main__":
    main()