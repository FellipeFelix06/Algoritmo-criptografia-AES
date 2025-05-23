from aes import AES
from dotenv import load_dotenv
from pathlib import Path
import os

load_dotenv()


if __name__ == '__main__':
    DIR_CSV = Path(__file__).parent / 'data.json'
    DIR_DUMP = Path(__file__).parent / 'dump.json'
    key = os.getenv('KEY_AES', '')
    key_bytes = bytes.fromhex(key)
    aes = AES(key=key_bytes)

    with open(DIR_CSV, 'rb') as file:
        data = file.read()

    with open(DIR_DUMP, 'w') as file:
        data_new = aes.encrypt(data).hex()
        file.write(data_new)