from tinydb import TinyDB, Query
from difflib import SequenceMatcher
from pprint import pprint
import json
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
items = TinyDB(os.path.join(script_dir, 'data/items.json'))
characters = TinyDB(os.path.join(script_dir, 'data/characters.json'))
users = TinyDB(os.path.join(script_dir, 'data/users.json'))
Row = Query()

with open(os.path.join(script_dir, "models/user.json")) as f:
    model_user = json.load(f)
with open(os.path.join(script_dir, "models/character.json")) as f:
    model_character = json.load(f)
with open(os.path.join(script_dir, "models/item.json")) as f:
    model_item = json.load(f)


class SearchResult:

    def __init__(self, similarityIndex, id, name=None):
        self.similarityIndex = similarityIndex
        self.id = id
        self.name = name

    def item(self):
        return items.get(Row.id == self.id)


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

def sort_by_similarity_index(e):
    return e.similarityIndex

# USER DATA -----------------------------------------------

def create_user(userId):
    user = model_user.copy()
    user['id'] = int(userId)
    users.insert(user)
    return user

def get_user_by_id( userId):
    return users.get(Row.id == int(userId))

# PLAYER DATA ---------------------------------------------------

def get_character_by_id( id):
    return characters.get(Row.id == int(id))


def get_character_by_name( firstName):
    return characters.get(Row.first == firstName)


def update_character( id, changedValues={}):
    print(f"changed values: {changedValues}")
    print(f"id: {id}")
    characters.update(changedValues, Row.id == int(id))


def search_character_inventory( id, itemName):
    searchString = ''.join(itemName.split()).lower()
    character = get_character_by_id(id)
    results = []
    for key in character['inventory'].keys():
        entry = character['inventory'][key]
        similarityIndex = similarity(searchString, entry['searchable'])
        id = entry.get('id')
        if similarityIndex == 1.0:
            results = [SearchResult(similarityIndex, id)]
            break
        elif similarityIndex > 0.5:
            results.append(SearchResult(similarityIndex, id))
    results.sort(key=sort_by_similarity_index)
    return results


def search_character_inventory_best_match( id, itemName):
    results = search_character_inventory(id, itemName)
    if len(results) == 0:
        return None
    bestMatch = results[0]
    for result in results:
        if result.similarityIndex > bestMatch.similarityIndex:
            bestMatch = result
    return bestMatch


def update_character_inventory( characterId, itemId, quantity=1):
    numberRemoved = 0
    newQuantity = 0
    
    itemId = str(itemId)
    
    character = get_character_by_id(characterId)
    inventory = character['inventory']
    item = inventory.get(itemId)
    print(f'item exists in characters inventory? {item != None}')

    # Remove item
    if quantity < 0 and item != None:
        item['quantity'] += quantity
        numberRemoved = quantity
        newQuantity = item['quantity']
        if item['quantity'] <= 0:
            numberRemoved = quantity - item['quantity']
            newQuantity = 0
            del inventory[itemId]
        update_character(characterId, {'inventory': inventory})

    # Add item
    elif quantity > 0:
        # Item doesn't exist yet
        if item == None:
            itemDef = get_item_by_id(int(itemId))
            inventory[itemId] = {
                "searchable": itemDef['searchable'],
                "quantity": quantity,
                "name": itemDef['name'],
                "cost": itemDef['cost'],
                "weight": itemDef['weight']
            }
            newQuantity = quantity
            print(f"adding item to inventory. item: {itemDef}")
        # Item already present
        else:
            item['quantity'] += quantity
            newQuantity = item['quantity']
        update_character(characterId, {'inventory': inventory})

    print(f"new Quantity: {newQuantity}, numberRemoved: {numberRemoved}")
    return newQuantity, numberRemoved
        

def create_character(id, first, last):
    character = model_character.copy()
    character['first'] = first
    character['last'] = last
    character['id'] = int(id)
    character['rolls']['pid'] = str(id)
    characters.insert(character)


def delete_character(id):
    characters.remove(Row.id == id)


def get_character_data_by_json_path(id, jsonPath):
    data = get_character_by_id(id)
    keys = jsonPath.split('/')
    try:
        for key in keys:
            data = data[key]
    except:
        data = None
    return data


# ITEM DATA ------------------------------------------------------

def search_items(itemName):
    print(f"search_items '{itemName}'")
    results = []
    searchString = ''.join(itemName.split()).lower()
    for item in items.all():
        similarityIndex = similarity(searchString, item['searchable'])
        id = item.get('id')
        if similarityIndex == 1.0:
            print('match found')
            results = [SearchResult(similarityIndex, id)]
            break
        elif similarityIndex > 0.5:
            results.append(SearchResult(similarityIndex, id))
    results.sort(key=sort_by_similarity_index)
    return results


def get_item_by_id(id):
    return items.get(Row.id == id)
    

def get_item_best_match(itemName):
    results = search_items(itemName)
    if len(results) == 0:
        return None
    bestMatch = results[0]
    for result in results:
        if result.similarityIndex > bestMatch.similarityIndex:
            bestMatch = result
    return bestMatch
