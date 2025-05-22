from pathlib import Path
import sys
aes_dir = Path(__file__).parent.parent
sys.path.append(str(aes_dir))
import pandas as pd
from flask import Flask, request, jsonify
import base64
from aes import AES
import os
from io import StringIO
from dotenv import load_dotenv

load_dotenv()

key = os.getenv('KEY_AES', '')
key_bytes = bytes.fromhex(key)
aes = AES(key=key_bytes)

DIR_CSV = Path(__file__).parent.parent / 'dump.csv'

API_KEY = 'AB_4g1dhJvysdrfR9HPax49hjYh2nv5UhjqbMz5a2RMG1'

app = Flask(__name__)

@app.route('/')
def homepage():
    home = {
        'message': 'API is running',
        'status': 'OK'
    }
    return jsonify(home)

def check_token():
    auth_header = request.headers.get('Authorization')

    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({'error': 'Unauthorizad'}), 401
    
    token = auth_header.split(' ', 1)[1]

    if token != API_KEY:
        return jsonify({'error', 'Invalid API Key'}), 403

def decrypt():
    with open(DIR_CSV, 'r') as file:
        cipher = file.read()
        cipher_bytes = bytes.fromhex(cipher)
        return aes.decrypt(cipher_bytes).decode('utf-8')

@app.route('/dados', methods=['GET'])
def dadosvendas():
    erro = check_token()
    if erro:
        return erro
    decrypt_csv = decrypt()
    tabela = pd.read_csv(StringIO(decrypt_csv))
    vendas = tabela['Vendas'].tolist()
    return jsonify({'vendas': vendas})

app.run()