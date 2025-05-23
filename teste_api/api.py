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

@app.route('/<produto>', methods=['GET'])
def listar_tudo(produto):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    listar_tudo = json.loads(decrypt_json)
    return jsonify([{"id": id, **info} for id, info in listar_tudo.get(produto, {}).items()])

@app.route('/<produto>/<int:id>', methods=['GET'])
def listar_um(produto, id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    listar_tudo = json.loads(decrypt_json)
    celular_dict = listar_tudo.get(produto, {})
    celular_info = celular_dict.get(str(id))
    if celular_info is None:
        return jsonify({'error': 'id inválido'}), 401
    return jsonify({"id": str(id), **celular_info})

@app.route('/<produto>/<int:id>', methods=['PUT'])
def editar_um(produto, id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    listar_tudo = json.loads(decrypt_json)
    response = request.get_json()
    produto_dict = listar_tudo.get(produto, {})
    produto_info = produto_dict.get(str(id))
    if produto_info is None:
        return jsonify({'error': 'id inválido'}), 401
    produto_info.update(response)
    return jsonify({"id": str(id), **produto_info})

@app.route('/<produto>/<int:id>', methods=['DELETE'])
def deletar_um(produto, id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    listar_tudo = json.loads(decrypt_json)
    produto_dict = listar_tudo.get(produto, {})
    produto_info = produto_dict.get(str(id))
    if produto_info is None:
        return jsonify({'error': 'id inválido'}), 401
    del produto_info
    return jsonify({'lista_tv': produto_dict})

@app.route('/<produto>/<int:id>', methods=['POST'])
def criar_um(produto, id):
    erro = check_token()
    if erro:
        return erro
    decrypt_json = decrypt()
    listar_tudo = json.loads(decrypt_json)
    produto_dict = listar_tudo.get(produto, {})
    response = request.get_json()
    for i in produto_dict:
        if str(id) in i:
            return jsonify({'error': 'id já existente.'}), 401
    produto_dict[str(id)] = response
    listar_tudo[produto] = produto_dict
    return jsonify({"id": str(id), **produto_dict})

app.run()