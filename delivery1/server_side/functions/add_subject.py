#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sqlite3
import sys
import json

from functions.create_table_if_not_exists import create_table_if_not_exists

def add_subject(organization_id, username, name, email, public_key):
    #connect to the database
    conn = sqlite3.connect('repository.db')
    create_table_if_not_exists(conn)
    cursor = conn.cursor()

    try:
        cursor.execute("""
            INSERT INTO subjects (organization_id, username, full_name, email, public_key, status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (organization_id, username, name, email, public_key, "active"))

        #confirm and close the connection
        conn.commit()
        return "Subject added successfully", 201
    except sqlite3.IntegrityError as e:
        return "Subject already added to this organization", 409
    except Exception as e:
        return f"Database error: {e}", 500
    finally:
        conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 6:
        print("Usage: rep_add_subject <session file> <username> <name> <email> <credentials file>")
        sys.exit(-1)
    
    _, organization_id, username, name, email, public_key = sys.argv

    add_subject(organization_id, username, name, email, public_key)