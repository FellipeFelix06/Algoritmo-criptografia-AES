#type: ignore
from s_box.sbox import s_box
from s_box.inv_sbox import inv_sbox
from matriz_fixa.matriz import m_mixcolumns
from matriz_fixa.matriz import inv_mixcolumns

MSG = 'olá Mundo!'
MSG_BYTES = bytes(MSG, 'utf-8')

class AES:
    def __init__(self, key: bytes) -> None:
        if len(key) not in (16, 24, 32): # se o tamanho da chave não for 16, 24 ou 32 levanta um erro
            raise ValueError("tamanho da chave inválido. apenas 16, 24 ou 32 bytes.")
        self.key = key

    def pcks7_pad(self, data: bytes, tamanho_bloco=16):
        tamanho_pad = tamanho_bloco - (len(data) % tamanho_bloco) # quantos bytes são necessários para completar 16 bytes
        pad = bytes([tamanho_pad] * tamanho_pad) # multiplica pelo o total que falta
        return data + pad

    def pcks7_unpad(self, data: bytes):
        tamanho_pad = data[-1]
        if tamanho_pad < 1 or tamanho_pad > 16:
            raise ValueError('padding inválido')
        if data[-tamanho_pad:] != bytes([tamanho_pad] * tamanho_pad):
            raise ValueError('padding inválido #2')
        return data[:-tamanho_pad]
    
    def addroundkey(self, bloco, round_key):
        result = bytes([b ^ k for b, k in zip(bloco, round_key)]) # para cada byte no bloco e na key é feito um xor
        return result
    
    def subbytes(self, data):
        result = [s_box[(b >> 4) & 0x0F][b & 0x0F] for b in data] # b >> 4 desloca os mais significativos & 0x0F garante que são os 4 ultimos, isso fa
        # a divisão no meio dos 8 bits
        return result
    
    def campo_finito(self, a, b):
        p = 0
        for i in range(8):
            if b & 1: # se o bit menos significativo for 1
                p ^= a # faz xor com a e acumula em p
            menos_sigf = a & 0x80 # verifica se o bit 7 é 1
            a = (a << 1) & 0xFF # desloca um bit a esquerda
            if menos_sigf:
                a ^= 0x1B # se passar dos 8 bits faz o xor
            b >>= 1 # desloca 1 bita para a direita
        return p 
    
    def encrypt(self, plaintext: bytes) -> bytes:
        rounds = 10 if len(self.key) == 16 else 12 if len(self.key) == 24 else 14
        texto_com_pad = self.pcks7_pad(plaintext)
        texto_cifrado = b''
        
        for i in range(0, len(texto_com_pad), 16):
            bloco = texto_com_pad[i:i+16] # itera para cada byte no texto com padding

            estado = list(bloco) # cada byte é jogado em uma lista
            for rodada in range(rounds):
                # addroundkey
                estado = self.addroundkey(estado, round_key=self.key)
                # subbytes
                estado = self.subbytes(estado)

                matriz = [estado[i:i + 4] for i in range(0, 16, 4)] # organiza o estado (que é uma lista) em uma matriz 4x4
                # shiftrows
                for i in range(1, 4):
                    matriz[i] = matriz[i][i:] + matriz[i][:i] # faz o shiftrows matiz = [a, b, c, d] matriz[2][:2] = [A, B] (o ultimo indice não é inclusivo)

                # mixcolumns
                if rodada != rounds - 1:
                    transposta = list(zip(*matriz)) # transposição cada coluna vira linha
                    nova_transposta = []
                    for coluna in transposta: # iterar cada indice
                        nova_coluna = []
                        for linha in m_mixcolumns: # itera cada indice da matriz fixa
                            val = 0
                            for i, byte in zip(linha, coluna): # itera cada indice da linha da matriz fixa e da coluna da matriz transposta
                                val ^= self.campo_finito(byte, i) # calculo do campo finito
                            nova_coluna.append(val)
                        nova_transposta.append(nova_coluna)

                    matriz = [list(linha) for linha in zip(*nova_transposta)] # volta a matriz normal linha x coluna

                estado = [byte for linha in matriz for byte in linha]

            texto_cifrado += bytes(estado)
        return texto_cifrado

    def decrypt(self, ciphertext: bytes):
        texto_decifrado = b''
        rounds = 10 if len(self.key) == 16 else 12 if len(self.key) == 24 else 14

        for i in range(0, len(ciphertext), 16):
            bloco = ciphertext[i:i+16] # itera cada byte do texto cifrado em um bloco de 16 bytes

            estado = list(bloco) # transforma o bloco em uma lista linear

            matriz = [estado[i:i + 4] for i in range(0, 16, 4)] # organiza a lista em uma matriz 4x4

            for rodada in reversed(range(rounds)):
                # invshftRows
                for i in range(1, 4):
                    matriz[i] = matriz[i][-i:] + matriz[i][:-i] # faz o shiftrows invertendo as posições

                # invsubbytes
                for r in range(4): # itera cada linha "row"
                    for c in range(4): # itera cada coluna "column"
                        b = matriz[r][c] # btye da linha[r] x coluna[c]
                        matriz[r][c] = inv_sbox[(b >> 4) & 0x0F][b & 0x0F]
                        
                # addroundkey
                for r in range(4):
                    for c in range(4):
                        matriz[r][c] ^= self.key[r * 4 + c] # entenda isso como linha = 1, coluna = 1: 1 * 4 + 1 = indice 5 

                # invmixcolumns
                if rodada != 0:
                    transposta = list(zip(*matriz))
                    nova_transposta = []
                    for coluna in transposta:
                        nova_coluna = []
                        for linha in inv_mixcolumns:
                            val = 0
                            for i, byte in zip(linha, coluna):
                                val ^= self.campo_finito(byte, i)
                            nova_coluna.append(val)
                        nova_transposta.append(nova_coluna)

                    matriz = [list(linha) for linha in zip(*nova_transposta)]

            bloco_decifrado = []
            for linha in matriz:
                bloco_decifrado.extend(linha) # volta como uma lista linear

            texto_decifrado += bytes(bloco_decifrado)

        return self.pcks7_unpad(texto_decifrado)

if __name__ == '__main__':
    aes_new = AES(key=b'ThisIsA16ByteKey')
    cipher = aes_new.encrypt(MSG_BYTES, )
    decipher = aes_new.decrypt(cipher)
    print("Texto original:", MSG)
    print('Texto criptografado:', cipher.hex())
    print("Texto descriptografado:", decipher.decode('utf-8'))