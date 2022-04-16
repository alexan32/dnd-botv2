from tinydb import TinyDB, Query
from difflib import SequenceMatcher
from pprint import pprint
from uuid import uuid4
import json
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
games = TinyDB(os.path.join(script_dir, 'data/games.json'))
items = TinyDB(os.path.join(script_dir, 'data/items.json'))
characters = TinyDB(os.path.join(script_dir, 'data/characters.json'))
users = TinyDB(os.path.join(script_dir, 'data/users.json'))
Row = Query()

with open(os.path.join(script_dir, "models/game.json")) as f:
    model_game = json.load(f)
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

# GAME DATA -----------------------------------------------

def get_game_by_id(guildId):
    return games.get(Row.id == int(guildId))

def create_game(guildId, ruleset):
    with open(os.path.join(script_dir, f"ruleset/{ruleset}.json")) as f:
        gameConfig = json.load(f)
    game = model_game.copy()
    game['id'] = int(guildId)
    game = {**game, **gameConfig}
    games.insert(game)
    return game

def update_game(guildId, changedValues = {}):
    games.update(changedValues, Row.id == int(guildId))

# USER DATA -----------------------------------------------

def create_user(discordId):
    user = model_user.copy()
    user['id'] = int(discordId)
    users.insert(user)
    return user

def get_user_by_id( discordId):
    return users.get(Row.id == int(discordId))

def update_user( id, changedValues={}):
    print(f"changed values: {changedValues}")
    print(f"id: {id}")
    users.update(changedValues, Row.id == int(id))

# PLAYER DATA ---------------------------------------------------

def get_character_by_id( id):
    return characters.get(Row.id == id)

def get_character_by_name( firstName):
    return characters.get(Row.first == firstName)

def get_character_by_name_and_game(guildId, firstName):
    return characters.get((Row.first == firstName) & (Row.guildId == guildId))

def get_character_by_name_and_user(discordId, firstName):
    return characters.get((Row.first == firstName) & (Row.discordId == discordId))

def search_character_by_user_and_game(discordId, guildId):
    return characters.search((Row.discordId == discordId) & (Row.guildId == guildId))

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
        

def create_character(discordId, guildId, first, last):
    rulesetCharacter = get_game_by_id(guildId)["models"]["character"]
    cid = str(uuid4())
    character = model_character.copy()
    character['first'] = first
    character['last'] = last
    character['id'] = cid
    character['discordId'] = discordId
    character['guildId'] = guildId
    character = {**character, **rulesetCharacter}
    characters.insert(character)
    return character, cid


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


if __name__ == "__main__":
    print(get_user_by_id(123456789))