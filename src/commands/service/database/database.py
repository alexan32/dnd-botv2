from tinydb import TinyDB, Query
from difflib import SequenceMatcher
from pprint import pprint
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
items = TinyDB(os.path.join(script_dir, 'data/output/items.json'))
players = TinyDB(os.path.join(script_dir, 'data/output/players.json'))
admins = TinyDB(os.path.join(script_dir, 'data/output/admins.json'))
Row = Query()

def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()

class SearchResult:

    def __init__(self, similarityIndex, id, name=None):
        self.similarityIndex = similarityIndex
        self.id = id
        self.name = name

    def item(self):
        return get_item_by_id(self.id)

# ADMIN LIST DATA -----------------------------------------------

def set_admin(id):
    admins.insert({"id": id, "assumedId": None})

def remove_admin(id):
    admins.remove(Row.id == id)

def set_admin_assumed_id(id, assumedId=None):
    admins.update({"assumedId": assumedId}, Row.id == id)

def get_assumed_id(id):
    assumedId = id
    admin = admins.get(Row.id == id)
    if admin != None and admin.get('assumedId') != None:
        assumedId = admin.get('assumedId')
    return assumedId

# PLAYER DATA ---------------------------------------------------

def get_player_by_id(id):
    return players.get(Row.id == id)


def get_player_by_name(firstName):
    return players.get(Row.first == firstName)


def update_player(id, changedValues={}):
    players.update(changedValues, Row.id == id)


# Returns a list that can contain multiple SearchResult objects
def search_player_inventory(id, itemName):
    searchString = ''.join(itemName.split()).lower()
    player = get_player_by_id(id)
    results = []
    for key in player['inventory'].keys():
        entry = player['inventory'][key]
        similarityIndex = similarity(searchString, entry['searchable'])
        id = entry.get('id')
        if similarityIndex == 1.0:
            results = [SearchResult(similarityIndex, id)]
            break
        elif similarityIndex > 0.7:
            results.append(SearchResult(similarityIndex, id))
    return results


# Returns back a single SearchResult or None 
def search_player_inventory_best_match(id, itemName):
    results = search_player_inventory(id, itemName)
    if len(results) == 0:
        return None
    bestMatch = results[0]
    for result in results:
        if result.similarityIndex > bestMatch.similarityIndex:
            bestMatch = result
    return bestMatch


# Add or remove items from player inventory, return newQuantity and numberRemoved
def update_player_inventory(playerId, itemId, quantity=1):
    numberRemoved = 0
    newQuantity = 0
    
    itemId = str(itemId)
    
    player = get_player_by_id(playerId)
    inventory = player['inventory']
    item = inventory.get(itemId)

    # Remove item
    if quantity < 0 and item != None:
        item['quantity'] += quantity
        numberRemoved = quantity
        newQuantity = item['quantity']
        if item['quantity'] <= 0:
            numberRemoved = quantity - item['quantity']
            newQuantity = 0
            del inventory[itemId]
        update_player(playerId, {'inventory': inventory})

    # Add item
    elif quantity > 0:
        # Item doesn't exist yet
        if item == None:
            itemDef = get_item_by_id(int(itemId))
            print()
            inventory[itemId] = {
                "searchable": itemDef['searchable'],
                "quantity": quantity,
                "name": itemDef['name'],
                "cost": itemDef['cost'],
                "weight": itemDef['weight']
            }
            newQuantity = quantity
        # Item already present
        else:
            item['quantity'] += quantity
            newQuantity = item['quantity']
        update_player(playerId, {'inventory': inventory})

    return newQuantity, numberRemoved
        

# ITEM DATA ------------------------------------------------------

# Returns list of SearchResult objects
def search_items(itemName):
    results = []
    searchString = ''.join(itemName.split()).lower()
    for item in items.all():
        similarityIndex = similarity(searchString, item['searchable'])
        id = item.get('id')
        if similarityIndex == 1.0:
            results = [SearchResult(similarityIndex, id)]
            break
        elif similarityIndex > 0.7:
            results.append(SearchResult(similarityIndex, id))
    return results


def get_item_by_id(id):
    return items.get(Row.id == id)
    

# Returns a single SearchResult or 'None'
def get_item_best_match(itemName):
    results = search_items(itemName)
    if len(results) == 0:
        return None
    bestMatch = results[0]
    for result in results:
        if result.similarityIndex > bestMatch.similarityIndex:
            bestMatch = result
    return bestMatch


if __name__ == '__main__':
    pprint(get_player_by_id(239517576781234177))
    # print(search_player_inventory(239517576781234177, 'crossbow'))
    # results = search_items('crossbow')
    # for result in results:
    #     pprint(result.item())

    # pprint(get_item_best_match('crossbow').item())
    pprint(get_player_by_id(239517576781234177))