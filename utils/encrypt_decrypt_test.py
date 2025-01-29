from decrypt_message import decrypt_message
from encrypt_message import encrypt_message
import os

## normal process
msg1 = b"Hello, World!"
AES256_key1 = os.urandom(32)
encrypted_data = encrypt_message(msg1, AES256_key1)
print(f"Encrypted data: {encrypted_data}")
## send encrypted_data

## modificação maliciosa
msg2 = b"Hello, World! 2"
AES256_key2 = os.urandom(32)
encrypted_data2 =  encrypt_message(msg2, AES256_key2)
#encrypted_data['encrypted_data'] = encrypted_data2['encrypted_data']
#print(encrypted_data['encrypted_data'])


## try to decrypt the modified data
try:
    decrypted_data = decrypt_message(encrypted_data2, AES256_key1)
    print(f"Decrypted data: {decrypted_data}")
except Exception as e:
    print("Malicious modification detected!")