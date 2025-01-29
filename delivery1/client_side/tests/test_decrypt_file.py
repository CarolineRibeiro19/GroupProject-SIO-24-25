from decipher import decrypt_file
import json

with open('../server_side/documents.json', 'r') as f:
    metadata = json.load(f)

file_handle = '8e08fdd0ca74b6a299a88f3d69c19c782f13532ec8f675e06366bd10'


#isto será feito no lado do servidor quando o cliente pedir para baixar o ficheiro
for i in range(len(metadata['documents'])):
    if metadata['documents'][i]['file_handle'] == file_handle:
        #write restricted metadata to file 'metadata.json'
        with open('metadata.json', 'w') as f:
            f.write(json.dumps(metadata['documents'][i]['restricted_metadata'], indent=4))
        break


decrypt_file(file_handle, 'metadata.json')