from s_box.sbox import s_box
from rcon.rcon_tabela import rcon

class KeyExpansion():

    def __init__(self, key: bytes) -> None:
        self.key = key

    def rot_byte(self, data):
        return data[1:] + data[:1]
    
    def sub_byte(self, data, sbox):
        return [sbox[(b >> 4) & 0x0F][b & 0x0F] for b in data]
    
    def xor_byte(self, a, b):
        return [x ^ y for x, y in zip(a, b)]
    
    def keyexpansion(self):
        bloco = [list(self.key[i:i+4]) for i in range(0, 16, 4)]

        for i in range(4, 44):
            palavra_temp = bloco[i - 1]
            if i % 4 == 0:
                palavra_temp = self.rot_byte(palavra_temp)
                palavra_temp = self.sub_byte(palavra_temp, s_box)
                palavra_temp = self.xor_byte(palavra_temp, rcon[i // 4])

            novos_bytes = self.xor_byte(bloco[i - 4], palavra_temp)
            bloco.append(novos_bytes)

        return [sum(bloco[i:i+4], []) for i in range(0, 44, 4)]