import json
from pathlib import Path

DIR_JSON = Path(__file__).parent / 'data.json'

with open(DIR_JSON, 'r') as file:
    d = json.load(file)
    for id, info in d['tv'].items():
        print(id, info)