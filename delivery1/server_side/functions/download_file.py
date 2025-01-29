#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import json
from flask import jsonify, send_from_directory

def download_file(app,filehandler):
    
    directory = os.path.join(app.root_path, 'files')  # Diretório onde os arquivos estão armazenados
    try:
        return send_from_directory(directory, filehandler, as_attachment=True)
    except FileNotFoundError:
        return jsonify({"error": "File not found"}), 404