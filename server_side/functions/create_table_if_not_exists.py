def create_table_if_not_exists(conn):
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS organizations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        organization_name TEXT UNIQUE NOT NULL,
        acl TEXT NOT NULL 
    );
        ''')
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS subjects (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            organization_id INTEGER NOT NULL,
            username TEXT UNIQUE NOT NULL,
            full_name TEXT NOT NULL,
            email TEXT NOT NULL,
            public_key TEXT NOT NULL,
            status TEXT NOT NULL,
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
        );
    """)
    conn.commit()

def create_table_docs(conn):
    cursor = conn.cursor()
    cursor.execute("""
            CREATE TABLE IF NOT EXISTS documents (
            document_handle INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            file_handle TEXT NOT NULL,
                   
            alg TEXT NOT NULL,
            key TEXT NOT NULL,
            creation_date DATE NOT NULL,
            acl TEXT NOT NULL,
                   
            organization_id INTEGER NOT NULL,
            creator TEXT NOT NULL,
            deleter TEXT NOT NULL,
                   
            FOREIGN KEY (creator) REFERENCES subjects(id),
            FOREIGN KEY (deleter) REFERENCES subjects(id),
            FOREIGN KEY (organization_id) REFERENCES organizations(id)
                   
        );
    """)
    conn.commit()


"""
The public metadata must include the following elements:

    document_handle: Document handle for efficient referencing
    name: Document name for name-handle resolution
    create_date: Creation date
    creator: Reference to the subject that created the file
    file_handle: Handle of its file (for uniform file referencing)
    acl: Access control list (ACL)
    deleter: Reference to the subject that deleted the file

The non-public (or restricted) metadata must include the following elements:

    alg: Description of the cryptographic procedures used to protect the file (with encryption and integrity control)
    key: Key used to encrypt the file.

"""