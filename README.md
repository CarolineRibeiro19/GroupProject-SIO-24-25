# **Security of Information and Organizations 2024/2025**  

## **Componentes do Projeto**
-  Júlia Abrantes ([julia.abrantes@ua.pt](mailto:julia.abrantes@ua.pt))  
-  Caroline Ribeiro ([caroline.ribeiro@ua.pt](mailto:caroline.ribeiro@ua.pt))  
-  Ellen Sales ([ellensales@ua.pt](mailto:ellensales@ua.pt))  

---

## **Descrição**
Nesta etapa, tivemos que melhorar o que foi feito para a entrega anterior. Todas as funções foram **refatoradas** para atender os requisitos.

---

## **Comandos Implementados**

### **Comandos Locais**
#### **rep_subject_credentials**  
**Descrição:**  
Este comando gera um par de chaves ECC que serão utilizadas pelo cliente para autenticação e assinatura. A chave pública é gravada no `<credentials file>`, e a chave privada é protegida por meio da `<password>`.

**Para testar**  
```bash
./rep_subject_credentials 12345 credentials.pem 
```

#### **rep_decrypt_file**   


**Para testar**  
```bash
./rep_decrypt_file 
```

### **API Anónima**

#### **rep_create_org**   

Cria uma organização na base de dados e adiciona o subject como manager, também adiciona o subject a base de dados de subjects. 

**Para testar**  
```bash
./rep_create_org UA manager_ua jose jose@ua.pt credentials.pem
```


#### **rep_list_orgs**   
Lista todas as organizações da base de dados.

**Para testar**  
```bash
./rep_list_orgs
```

#### **rep_create_session**   
Cria uma sessão, mas apenas se o usuario estiver associado à organização e as credenciais estiverem corretas.

**Para testar**  
```bash
./rep_create_session UA jose 12345 credentials.pem jose_session
```

#### **rep_get_file**   

**Para testar**  
```bash
./rep_get_file
```

### **API Autenticada**

#### **rep_assume_role**   

Assume a devida role na session file se o subject estiver inserido na devida role da ACL da organização.

**Para testar**  
```bash
./rep_assume_role jose_session manager
```


#### **rep_drop_role** 

Remove a role da session file se estiver ativa.

**Para testar**  
```bash
./rep_drop_role jose_session manager
```

#### **rep_list_roles**   

Lista as roles da sessão ativa.

**Para testar**  
```bash
./rep_list_roles jose_session manager
```


#### **rep_list_subjects**   

Lista os subjects da organização que está na sessão ativa, indicando se estão "up" ou "down".

**Para testar**  
```bash
./rep_list_subjects jose_session
```

#### **rep_list_role_subjects** 

Lista os sujeitos de uma role na organização que a sessão está ativa. 

**Para testar**  
```bash
./rep_list_role_subjects jose_session manager
```

#### **rep_list_subject_roles**   

Lista as roles de um dado subject que está na organização da sessão ativa.

**Para testar**  
```bash
./rep_list_subject_roles jose_session manager_ua
```

#### **rep_list_role_permissions**   

Lista as permissões de uma dada role na organização que a sessão está ativa.

**Para testar**  
```bash
./rep_list_role_permissions jose_session manager
```

#### **rep_list_permission_roles**   

Lista as roles que possuem dada permissão na organização em que a sessão está ativa.

**Para testar**  
```bash
./rep_list_permission_roles jose_session DOC_NEW
```

#### **rep_list_docs**   
Lista os documentos da organização que o user tem uma sessão ativa. Com -s filtra os documentos criados pelo username que está no parâmetro e com -d filtra pela data com a opão de newer than (nt), older than (ot) e equal to (et). 

**Para testar**  
```bash
./rep_list_docs jose_session [-s username] [-d nt/ot/et date]
```

### **API Autorizada**

#### **rep_add_subject**   

Adiciona o subject à organização se o usuário da sessão ativa tiver a devida permissão

**Para testar**  

antes precisa adicionar o credentials
```bash
./rep_subject_credentials 12345 other_credentials.pem 
```

```bash
./rep_add_subject jose_session maria_ua maria maria@ua.pt other_credentials.pem
```

#### **rep_suspend_subject** 

Suspende o subject na organização ativa se o usuário da sessão ativa tiver a devida permissão

**Para testar**  
```bash
./rep_suspend_subject jose_session maria_ua
```

#### **rep_activate_subject**   
Ativa o subject na organização ativa se o usuário da sessão ativa tiver a devida permissão

**Para testar**  
```bash
./rep_activate_subject jose_session maria_ua
```


#### **rep_add_role**   
Adiciona o role ao subject na organização ativa se o usuário da sessão ativa tiver a devida permissão

**Para testar**  
```bash
./rep_add_role jose_session viewer
```

#### **rep_suspend_role**   
Suspende uma role da organização da sessão ativa se o usuario da sessão tiver a devida permissão

**Para testar**  
```bash
./rep_suspend_role jose_session viewer
``` 

#### **rep_reactivate_role**  
Reativa uma role da organização da sessão ativa se o usuario da sessão tiver a devida permissão


**Para testar**  
```bash
./rep_reactivate_role jose_session viewer
``` 

#### **rep_add_permission**  
No primeiro caso, adiciona uma dada role a um usuário se o usuário fizer parte da organização da sessão ativa e se o usuário da sessão ativa tiver a devida permissão.
No segundo caso, adiciona uma permissão a uma role da ACL da organização da sessão ativa se o usuario tiver a devida permissão.
**Para testar**  
1) 
```bash
./rep_add_permission jose_session viewer maria_ua
``` 
2) 
```bash
./rep_add_permission jose_session viewer DOC_READ
```

#### **rep_remove_permission**   
No primeiro caso,remove uma dada role a um usuário se o usuário fizer parte da organização da sessão ativa e se o usuário da sessão ativa tiver a devida permissão.
No segundo caso, remove uma permissão a uma role da ACL da organização da sessão ativa se o usuario tiver a devida permissão.

**Para testar** 
1)
```bash
./rep_remove_permission jose_session viewer maria_ua
``` 
2)
```bash
./rep_remove_permission jose_session viewer DOC_READ
``` 

#### **rep_add_doc**   

**Para testar**  
```bash
./rep_add_doc files/jose_session juliaDocument files/jose_session
``` 

#### **rep_get_doc_metadata**   

**Para testar**  
```bash
./rep_get_doc_metadata
``` 


#### **rep_get_doc_file**   

**Para testar**  
```bash
./rep_get_doc_file
``` 

#### **rep_delete_doc**   
Põe o file_handle do metadado do document como NULL e retorna o file_handle que foi apagado. É preciso que o role do user da sessão tenha como permissão o DOC_DELETE.

**Para testar**  
```bash
./rep_delete_doc jose_session <document name>
``` 


#### **rep_acl_doc**   
Adiciona (+) ou remove (-) permissão de um role de um documento. É preciso que o role do user da sessão tenha a permissão DOC_ACL para o respetivo documento.

**Para testar**  
1)
```bash
./rep_acl_doc jose_session <document name> + viewer DOC_DELETE
```
2)
```bash
./rep_acl_doc jose_session <document name> - viewer DOC_DELETE
```

