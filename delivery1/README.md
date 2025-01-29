# Entrega 1

Security of Information and Organizations 2024/25

## componentes:

- 104170 - Júlia Abrantes (julia.abrantes@ua.pt)
- 106093 - Caroline Ribeiro (caroline.ribeiro@ua.pt)
- 117450 - Ellen Sales (ellensales@ua.pt)

Nesta primeira etapa implementamos as funcionalidades básicas do repositório, nomeadamente:

## Comandos locais

### rep_subject_credentials \<password\> \<credentials file\> [-v]

Este comando gera um par de chaves RSA de 1024 bits e a salva a chave privada (PKCS8) e pública (PKCS1), nesta ordem em um ficheiro codificadas como PEM.

> Opcionalmente, pode usar _-v_ para ativar verbose
> TODO Opcionalmente, pode usar _-k <key_size>_ para alterar o tamanho para outro desejado

Dentro do diretório _delivery1/client_side_ utilize o seguinte comando para testar

```console
./rep_subject_credentials password123 test_files/credentials.pem
```

### rep_decrypt_file \<encrypted file\> \<encryption metadata\>

Este comando envia para a stdout a desencriptação de um ficheiro segundo o ficheiro json que guarda o algoritmo e a chave para desencriptação (geralmente, private metadatas).

Para o controle de integridade, o ficheiro é desencriptado e o hash é refeito, caso o hash do output não corresponda ao nome base do ficheiro (que deve ser um método hash suportado), o conteúdo não é enviado para o stdout nem salvo em ficheiro nenhum.

> Opcionalmente, pode usar _-v_ para ativar verbose
> Opcionalmente, pode usar _-f "nome do ficheiro"_ para salvar o ficheiro desencriptado
> Opcionalmente, pode usar -b para enviar o conteúdo para o standart output em bytes (recomendado para binários), o comportamento padrão é em string (recomendado para txt)

Atualmente ferece a possibilidade de desencriptar apenas ficheiros encriptados com AES-128, em modo CBC, e diggests processados com sha3 de 224 bits. para isso o ficheiro de metadados deve ter os seguintes campos:

```json
{
  "key": "00000000000000000000000000000000",
  "alg": {
    "name": "AES-128",
    "mode": "CBC",
    "iv": "00000000000000000000000000000000",
    "hash": "sha3-224"
  }
}
```

Dentro do diretório _delivery1/client_side_ utilize os seguintes comandos para testar

```console
./rep_decrypt_file test_files/f0105d5ff773f0572c455b7de54ddaefc61b40749f5f9fc262f02832 test_files/metadata.json
```

ou

```console
./rep_decrypt_file test_files/f0105d5ff773f0572c455b7de54ddaefc61b40749f5f9fc262f02832 test_files/metadata.json -v -b -f test_files/decrypted_file.pdf >> test_files/decrypted_echo.pdf
```

> TODO: implementar mais opções de encriptação/desencriptação

## Comandos que usam a API anônima

### rep_get_file \<file handle\> [file]

Com este comando o cliente é capaz de buscar o file que quiser dentro da diretório permitido no repositorio desde que saiba o seu filehandler.

> Opcionalmente, pode usar _-v_ para ativar verbose

Dentro do diretório _delivery1/client_side_ utilize o seguinte comando para testar

```console
./rep_get_file example.txt
```

## rep_create_org \<organization\> \<username\> \<name\> \<email\> \<public key file\>

Comando em que o permite o cliente criar uma organização. Ele faz o pedido ao servidor, e o servidor adiciona a organização a base de dados repository.db, a base de dados possui duas tabelas, uma com as organizações e cada associação está associada ao cliente que a criou, através de uma chave estrangeira.

para testar

```console
./rep_create_org UA joaoua joao joao@ua.pt ./test_files/credentials.pem
```

## rep_list_orgs

Comando que permite o cliente receber a lista de organizações da base de dados do repositório. O cliente faz o pedido e o servidor transforma a base de dados em um json e passa-o para o cliente.

```console
./rep_list_orgs
```

## rep_create_session \<organization\> \<username\> \<password\> \<credentials file\> \<session file\>

Comando que permite o cliente criar uma sessão com seu nome, chave pública, id e chave simétrica. O cliente faz o pedido, encripta seus dados com a chave simétrica, encripta a chave pública do servidor com a chave simétrica e envia para o servidor esses dois dados juntamente com o session_file.

O servidor usa sua chave privada para desencriptografar a chave simétrica e usá-la para desencriptografar os dados enviados. O session_file é composto pelo id criado pelo servidor, pelo nome do cliente, pela sua chave pública e a chave simétrica. O session_file só é gerado após a sessão ter sido criada.

para testar

```console
./rep_create_session Mercadona João password test_files/credentials.pem session
```

## Comandos que usam a API autenticada

## rep_list_subjects <session file> [username]

Comando que lista os sujeitos que fazem parte da mesma organização da sessão da session_file. A parte de username opcional não foi ainda implementada.

para testar
```console
./rep_list_subjects  session
```

## Comandos que usam a API autenticada

## rep_list_docs <session file> [-s username] [-d nt/ot/et date]

para testar
```console
./rep_list_docs session
```

## Comandos que usam a API autorizada

## rep_add_subject <session file> <username> <name> <email> <credentials file>

Comando que adiciona um sujeito a organização da session_file a partir das credentials_file.

para testar
```console
./rep_add_subject session username name email@email.pt test_files/credentials.pem
```

## rep_suspend_subject <session file> <username>

Comando que suspende o status de um username na base de dados, muda para down. Não verifica as permições de quem quer suspender.

para testar
```console
./rep_add_subject session joaoua
```

## rep_activate_subject <session file> <username>

Comando que ativa o status de um username na base de dados, muda para up. Não verifica as permições de quem quer ativar.

para testar
```console
./rep_add_subject session joaoua
```

## rep_add_doc <session file> <document name> <file> [-v]

Adiciona os metadados de um novo documento na base de dados

```console
./rep_add_doc test_files/session_file1.txt my_doc.txt test_files/decrypted.txt
```

## rep_list_docs <session file>

Lista os documentos da organização cujo o utilizador tem sessão ativa

```console
./rep_list_docs test_files/session_file1.txt
```


