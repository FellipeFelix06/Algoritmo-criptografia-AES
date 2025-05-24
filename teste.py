texto_com_pad = '1234567891234567'

for i in range(0, len(texto_com_pad), 16):
    estado = list(texto_com_pad[i:i+16])

print(estado)