def test_padding(data, block_size=16):
    padding_len = block_size - (len(data) % block_size)
    pad = bytes([padding_len] * padding_len)
    return data + pad

def test_unpadding(data):
    padding_len = data[-1]
    if padding_len < 1 or padding_len > 16:
        raise ValueError('#1')
    if data[-padding_len:] != bytes([padding_len] * padding_len):
        raise ValueError('#2')
    return data[:-padding_len]

def test_addroundkey(data, key):
    result = [x ^ y for x, y in zip(data, key)]
    return result

def test_subbytes(data, sbox):
    result = [sbox[(b >> 4) & 0x0F][b & 0x0F] for b in data]
    return result

def test_campo_finito(a, b):
    acumulador = 0
    for i in range(8):
        if b & 1:
            acumulador ^= a
        mais_significativo = a & 0x80
        a = (a << 1) & 0xFF
        if mais_significativo:
            a ^= 0x1B
        b >>= 1
    return acumulador

sbox = [
    [0x63, 0x7C, 0x77, 0x7B, 0xF2],
    [0xCA, 0x82, 0xC9, 0x7D, 0xFA],
]

matriz = [
    [0x02, 0x03, 0x01, 0x01],
    [0x01, 0x02, 0x03, 0x01],
    [0x01, 0x01, 0x02, 0x03],
    [0x03, 0x01, 0x01, 0x02],
]

data = b'1'
key = b'3'

a = 4 # 1000 = binário
b = 7 # 1100 = binário # 1000 &

variavel = test_padding(data)
variavel = test_addroundkey(variavel, key)
variavel = test_subbytes(variavel, sbox)

matriz_transposta = list(zip(*matriz))

resultado = []

for coluna in matriz_transposta:
    for c in coluna:
        for j in variavel:
            resultado.append(test_campo_finito(j, c))
print(resultado)