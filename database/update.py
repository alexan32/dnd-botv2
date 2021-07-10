from tinydb import TinyDB, Query
from difflib import SequenceMatcher
from pprint import pprint
import os

script_dir = os.path.dirname(__file__)
items = TinyDB(os.path.join(script_dir, 'data/output/items.json'))

armor = {
    "name": "Dagger",
    "id": 14,
    "searchable": "dagger",
    "cost": "2gp",
    "weight": "1",
    "type": "weapon",
    "properties": {
        "damage": "1d4",
        "versatileDamage": "1d4",
        "damageType": "piercing",
        "range": "20/60",
        "properties": [
            "finesse",
            "light",
            "thrown"
        ],
        "attackMod": [
            
        ]
    }
}

def build_use_strings(item):
    
    if item['type'] == 'weapon':
        