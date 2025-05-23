from pathlib import Path
import sys
aes_dir = Path(__file__).parent.parent
sys.path.append(str(aes_dir))
from flask import Flask, request, jsonify
from aes import AES
import os
from dotenv import load_dotenv
import json

load_dotenv()

key = os.getenv('KEY_AES', '')
key_bytes = bytes.fromhex(key)
aes = AES(key=key_bytes)

DIR_CSV = Path(__file__).parent.parent / 'dump.json'

API_KEY = 'AB_4g1dhJvysdrfR9HPax49hjYh2nv5UhjqbMz5a2RMG1'

app = Flask(__name__)

@app.route('/')
def homepage() :
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

@app.route('/tv', methods=['GET'])
def listar_tv():
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    lista_tv = json.loads(decrypt_json)
    return jsonify([{"id": id, **info} for id, info in lista_tv.get('tv', {}).items()])

@app.route('/tv/<int:id>', methods=['GET'])
def listar_uma_tv(id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    lista_uma_tv = json.loads(decrypt_json)
    tv_dict = lista_uma_tv.get('tv', {})
    tv_info = tv_dict.get(str(id))
    if tv_info is None:
        return jsonify({'error': 'id não encontrado.'}), 401
    return jsonify({"id": str(id), **tv_info})


@app.route('/tv/<int:id>', methods=['PUT'])
def editar_uma_tv(id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    lista_uma_tv = json.loads(decrypt_json)
    response = request.get_json()
    tv_dict = lista_uma_tv.get('tv', {})
    tv_info = tv_dict.get(str(id))
    if tv_info is None:
        return jsonify({'error': 'id não encontrado.'}), 401
    tv_info.update(response)
    return jsonify({"id": str(id), **tv_info})

@app.route('/tv/<int:id>', methods=['DELETE'])
def deletar_uma_tv(id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    lista_uma_tv = json.loads(decrypt_json)
    tv_dict = lista_uma_tv.get('tv', {})
    tv_info = tv_dict.get(str(id))
    if tv_info is None:
        return jsonify({'error': 'id não encontrado.'}), 401
    del tv_info
    return jsonify({'lista_tv': tv_dict})

@app.route('/tv/<int:id>', methods=['POST'])
def criar_uma_tv(id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    lista_uma_tv = json.loads(decrypt_json)
    tv_dict = lista_uma_tv.get('tv', {})
    response = request.get_json()
    for i in tv_dict:
        if str(id) in i:
            return jsonify({'error': 'id já existente.'}), 401
    tv_dict[str(id)] = response
    lista_uma_tv['tv'] = tv_dict
    return jsonify({"id": str(id), **tv_dict})

app.run()