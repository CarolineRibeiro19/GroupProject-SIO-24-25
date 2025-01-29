#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from functions.repo_operations import get_username_by_id, load_server_private_key, load_session_from_id, sign_message, verify_session_file, verify_subject_signature

def list_roles(data):

    session_id = data["session_id"]

    
    if verify_session_file(session_id):

        session_data = load_session_from_id(session_id)
        session_roles=  session_data.get("roles")

        server_private_key =  load_server_private_key()
        signature = sign_message(session_id.encode(), server_private_key)
        signature = {"signature": signature.hex(), "roles" : session_roles }

        return signature, 201
    else:
        return "Invalid session file", 400


                

