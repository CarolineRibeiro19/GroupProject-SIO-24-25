from credentials import gen_subj_credentials, load_subj_credentials

password = "password"
file_name = "test_files/credentials.pem"


#1st generate the credentials and get values
pub_key, priv_key = gen_subj_credentials(password, file_name)
print("Public Key:", pub_key)
print("Private Key:", priv_key)


#load keys together
loaded_pub_key, loaded_priv_key = load_subj_credentials(password, file_name)
print("Public Key: %s", loaded_pub_key)
print("Private Key: %s", loaded_priv_key)

