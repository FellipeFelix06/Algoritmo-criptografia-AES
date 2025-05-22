from sbox.sbox import sbox
from sbox.sbox import inv_sbox
from mixcolumns.mixcolumns import mixcolumns
from mixcolumns.mixcolumns import inv_mixcolumns
from key_expansion.key_expansion import KeyExpansion

class AES:
    def __init__(self, key: bytes) -> None:
        if len(key) not in (16, 24, 32):
            raise ValueError("tamanho da chave inválido. apenas 16, 24 ou 32 bytes.")
        self.key = key
        self.key_exp = KeyExpansion(key).keyexpansion()

    def pcks7_pad(self, data: bytes, tamanho_bloco=16):
        tamanho_pad = tamanho_bloco - (len(data) % tamanho_bloco)
        pad = bytes([tamanho_pad] * tamanho_pad)
        return data + pad

    def pcks7_unpad(self, data: bytes):
        tamanho_pad = data[-1]
        if tamanho_pad < 1 or tamanho_pad > 16:
            raise ValueError('padding inválido')
        if data[-tamanho_pad:] != bytes([tamanho_pad] * tamanho_pad):
            raise ValueError('padding inválido #2')
        return data[:-tamanho_pad]
    
    def addroundkey(self, bloco, round_key):
        result = bytes([b ^ k for b, k in zip(bloco, round_key)])
        return result
    
    def subbytes(self, data):
        result = [sbox[(b >> 4) & 0x0F][b & 0x0F] for b in data]
        return result
    
    def shiftrows(self, matriz):
        for i in range(1, 4):
            matriz[i] = matriz[i][i:] + matriz[i][:i]
        return matriz
    
    def mixcolumns(self, matriz, matriz_mix):
        nova_matriz = []

        for coluna_transposta in matriz:
            nova_coluna = []
            for linha_mixcolumns in matriz_mix:
                acumulador = 0
                for i, j in zip(linha_mixcolumns, coluna_transposta):
                    acumulador ^= self.campo_finito(j, i)
                nova_coluna.append(acumulador)
            nova_matriz.append(nova_coluna)

        return nova_matriz
    
    def invshiftrows(self, matriz):
        for i in range(1, 4):
            matriz[i] = matriz[i][-i:] + matriz[i][:-i]
        return matriz
    
    def invsubbytes(self, matriz):
        for r in range(4):
            for c in range(4):
                b = matriz[r][c]
                matriz[r][c] = inv_sbox[(b >> 4) & 0x0F][b & 0x0F]
        return matriz

    def campo_finito(self, a, b):
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
    
    def encrypt(self, plaintext: bytes) -> bytes:
        rounds = 10 if len(self.key) == 16 else 12 if len(self.key) == 24 else 14
        texto_com_pad = self.pcks7_pad(plaintext)
        texto_cifrado = b''

        for i in range(0, len(texto_com_pad), 16):
            estado = list(texto_com_pad[i:i+16])

            estado = self.addroundkey(estado, self.key_exp[0])

            for rodada in range(1, rounds):
                estado = self.subbytes(estado)

                matriz = [list(estado[i:i + 4]) for i in range(0, 16, 4)] # monta a matriz

                matriz = self.shiftrows(matriz)

                transposta = list(zip(*matriz))

                nova_transposta = self.mixcolumns(transposta, mixcolumns)

                matriz = [list(linha) for linha in zip(*nova_transposta)]
                estado = [byte for linha in matriz for byte in linha]
                estado = self.addroundkey(estado, self.key_exp[rodada])

            # rodada final

            estado = self.subbytes(estado)

            matriz = [list(estado[i:i + 4]) for i in range(0, 16, 4)]

            matriz = self.shiftrows(matriz)

            estado = [byte for linha in matriz for byte in linha]
            estado = self.addroundkey(estado, self.key_exp[rounds])

            texto_cifrado += bytes(estado)

        return texto_cifrado
    
    def decrypt(self, ciphertext: bytes) -> bytes:
        texto_decifrado = b''
        rounds = 10 if len(self.key) == 16 else 12 if len(self.key) == 24 else 14

        for i in range(0, len(ciphertext), 16):
            estado = list(ciphertext[i:i+16])

            estado = self.addroundkey(estado, self.key_exp[rounds])

            for rodada in reversed(range(1, rounds)):
                matriz = [list(estado[i:i + 4]) for i in range(0, 16, 4)]
                
                matriz = self.invshiftrows(matriz)

                matriz = self.invsubbytes(matriz)

                estado = [byte for linha in matriz for byte in linha]
                estado = self.addroundkey(estado, self.key_exp[rodada])

                matriz = [list(estado[i:i + 4]) for i in range(0, 16, 4)]

                transposta = list(zip(*matriz))
                nova_transposta = self.mixcolumns(transposta, inv_mixcolumns)
                
                matriz = [list(linha) for linha in zip(*nova_transposta)]

                estado = [byte for linha in matriz for byte in linha]

            # Última rodada (sem InvMixColumns)
            matriz = [estado[i:i + 4] for i in range(0, 16, 4)]

            matriz = self.invshiftrows(matriz)

            matriz = self.invsubbytes(matriz)

            estado = [byte for linha in matriz for byte in linha]
            estado = self.addroundkey(estado, self.key_exp[0])

            texto_decifrado += bytes(estado)

        return self.pcks7_unpad(texto_decifrado)