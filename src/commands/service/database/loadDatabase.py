from tinydb import TinyDB, Query
from pprint import pprint
import csv
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
items = TinyDB(os.path.join(script_dir, 'data/output/items.json'))
players = TinyDB(os.path.join(script_dir, 'data/output/players.json'))


def populatePlayerTable():
    players.insert({
            "first": "Nix",
            "last": "Cantor",
            "id": 239517576781234177,
            "balance": 110739,
            "rolls": {
                "str": "-1",
                "dex": "4",
                "con": "1",
                "wis": "2",
                "int": "0",
                "char": "5",
                "prof": "3",
                "stealth": "1d20 + dex + prof"
            },
            "inventory": {}
        })


def populateItemsTable():
    counter = 0
    # ARMOR
    with open('./src/data/csv/armor.csv') as armorFile:
        rows = csv.reader(armorFile, delimiter=',')
        x = 0
        for data in rows:
            if x != 0:
                try:
                    entry = {
                        'name': data[0].strip(),
                        'id': counter,
                        'searchable': ''.join(data[0].split()).lower(),
                        'cost': data[1].strip(),
                        'weight': data[2].strip(),
                        'type': 'armor',
                        'properties': {
                            'type': data[3].strip(),
                            'ac': data[4].strip(),
                            'stealthDisadvantage': data[5].strip() == 'd',
                            'strengthRequirement': 0 if data[6].strip() == '-' else int(data[6].strip())
                        }
                    }
                except:
                    print(f'Missing or invalid item data from armor.csv, line {x}.')
                    print(data)
                else:
                    items.insert(entry)
                    counter +=1
            x += 1

    # WEAPONS
    with open('./src/data/csv/weapons.csv') as weaponFile:
        rows = csv.reader(weaponFile, delimiter=',')
        damage = {
            'b': 'bludgeoning',
            'p': 'piercing',
            's': 'slashing',
            '-': '-'
        }
        x = 0
        for data in rows:
            if x != 0:
                try:
                    entry = {
                        'name': data[0].strip(),
                        'id': counter,
                        'searchable': ''.join(data[0].split()).lower(),
                        'cost': data[1].strip(),
                        'weight': data[2].strip(),
                        'type': 'weapon',
                        'properties': {
                            'damage': data[3].strip(),
                            'versatileDamage': data[4].strip() if data[4].strip() != '-' else data[3].strip(),
                            'damageType': damage[data[5].strip()],
                            'range': data[6].strip(),
                            'properties': data[7].split('*')
                        }
                    }
                except:
                    print(f'Missing or invalid item data from weapons.csv, line {x}.')
                    print(data)
                else:
                    items.insert(entry)
                    counter += 1
            x += 1
    # GEAR
    with open('./src/data/csv/gear.csv') as gearFile:
        rows = csv.reader(gearFile, delimiter=',')
        x = 0
        for data in rows:
            if x != 0:
                try:
                    entry = {
                        'name': data[0].strip(),
                        'id': counter,
                        'searchable': ''.join(data[0].split()).lower(),
                        'cost': data[1].strip(),
                        'weight': data[2].strip(),
                        'type': 'gear',
                        'properties': {}
                    }
                except:
                    print(f'Missing or invalid item data from gear.csv, line {x}.')
                    print(data)
                else:
                    items.insert(entry)
                    counter += 1
            x += 1
            
if __name__ == '__main__':
    # populateItemsTable()
    populatePlayerTable()