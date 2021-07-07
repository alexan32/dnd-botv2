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

def sort_by_similarity_index(e):
    return e.similarityIndex

model_player = {
        "first": '',
        "last": '',
        "id": 0,
        "balance": 0,
        "rolls": {},                # contains dice rolls
        "inventory": {},            # contains simplified item data
        "counters": {},             # contains counters. min, max, current
        "misc": {}                  # free space for extensions
    }


class Database:

    model_player = {
        "first": '',
        "last": '',
        "id": 0,
        "balance": 0,
        "rolls": {},                # contains dice rolls
        "inventory": {},            # contains simplified item data
        "counters": {},             # contains counters. min, max, current
        "misc": {}                  # free space for extensions
    }

    model_item = {            
        "name": "",
        "id": 0,
        "searchable": "",
        "cost": "0",
        "weight": "0",
        "type": ""
    }

    model_weapon_properties = {
        "damage": "",
        "versatileDamage": "",
        "damageType": "",
        "range": "-",
        "properties": []
    }

    model_armor_properties = {
        "type": "",
        "ac": "",
        "stealthDisadvantage": False,
        "strengthRequirement": 0
    }

    # ADMIN LIST DATA -----------------------------------------------

    def set_admin(self, id):
        admins.insert({"id": id, "assumedId": None})

    def remove_admin(self, id):
        admins.remove(Row.id == id)

    def set_admin_assumed_id(self, id, assumedId=None):
        admins.update({"assumedId": assumedId}, Row.id == id)

    def get_assumed_id(self, id):
        assumedId = id
        admin = admins.get(Row.id == id)
        if admin != None and admin.get('assumedId') != None:
            assumedId = admin.get('assumedId')
        return assumedId

    def is_admin(self, id):
        return admins.get(Row.id == id) != None


    # PLAYER DATA ---------------------------------------------------

    def get_player_by_id(self, id):
        return players.get(Row.id == int(id))


    def get_player_by_name(self, firstName):
        return players.get(Row.first == firstName)


    def update_player(self, id, changedValues={}):
        print(f"changed values: {changedValues}")
        print(f"id: {id}")
        players.update(changedValues, Row.id == int(id))


    def search_player_inventory(self, id, itemName):
        searchString = ''.join(itemName.split()).lower()
        player = self.get_player_by_id(id)
        results = []
        for key in player['inventory'].keys():
            entry = player['inventory'][key]
            similarityIndex = similarity(searchString, entry['searchable'])
            id = entry.get('id')
            if similarityIndex == 1.0:
                results = [SearchResult(similarityIndex, id)]
                break
            elif similarityIndex > 0.5:
                results.append(SearchResult(similarityIndex, id))
        results.sort(key=sort_by_similarity_index)
        return results


    def search_player_inventory_best_match(self, id, itemName):
        results = self.search_player_inventory(id, itemName)
        if len(results) == 0:
            return None
        bestMatch = results[0]
        for result in results:
            if result.similarityIndex > bestMatch.similarityIndex:
                bestMatch = result
        return bestMatch


    def update_player_inventory(self, playerId, itemId, quantity=1):
        numberRemoved = 0
        newQuantity = 0
        
        itemId = str(itemId)
        
        player = self.get_player_by_id(playerId)
        inventory = player['inventory']
        item = inventory.get(itemId)
        print(f'item exists in players inventory? {item != None}')

        # Remove item
        if quantity < 0 and item != None:
            item['quantity'] += quantity
            numberRemoved = quantity
            newQuantity = item['quantity']
            if item['quantity'] <= 0:
                numberRemoved = quantity - item['quantity']
                newQuantity = 0
                del inventory[itemId]
            self.update_player(playerId, {'inventory': inventory})

        # Add item
        elif quantity > 0:
            # Item doesn't exist yet
            if item == None:
                itemDef = self.get_item_by_id(int(itemId))
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
            self.update_player(playerId, {'inventory': inventory})
            
        print(f"new Quantity: {newQuantity}, numberRemoved: {numberRemoved}")
        return newQuantity, numberRemoved
            

    def create_player(self, id, first, last):
        player = model_player.copy()
        player['first'] = first
        player['last'] = last
        player['id'] = int(id)
        players.insert(player)


    def delete_player(self, id):
        players.remove(Row.id == id)


    def get_player_data_by_json_path(self, id, jsonPath):
        data = self.get_player_by_id(id)
        keys = jsonPath.split('/')
        try:
            for key in keys:
                data = data[key]
        except:
            data = None
        return data


    # ITEM DATA ------------------------------------------------------

    def search_items(self, itemName):
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


    def get_item_by_id(self, id):
        return items.get(Row.id == id)
        

    def get_item_best_match(self, itemName):
        results = self.search_items(itemName)
        if len(results) == 0:
            return None
        bestMatch = results[0]
        for result in results:
            if result.similarityIndex > bestMatch.similarityIndex:
                bestMatch = result
        return bestMatch


class SearchResult:

    def __init__(self, similarityIndex, id, name=None):
        self.similarityIndex = similarityIndex
        self.id = id
        self.name = name

    def item(self):
        return items.get(Row.id == id)


if __name__ == '__main__':
    database = Database()
    pprint(database.get_player_by_id(239517576781234177))