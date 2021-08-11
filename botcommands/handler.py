import database.database as database
import dice.dice_processor as dp
from uuid import uuid4
import json
import os

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)

dice = dp.DiceProcessor()

def name_sort(e):
    return e['name']

def is_admin(ctx):
    roles = ctx.author.roles
    for role in roles:
        print(role.name)
    return True

# HANDLER ------------------------------------------------------------------------

def handler(ctx, command, *args, **kwargs):

    userId = ctx.author.id
    print(f"\ncommand: {command} {args} {kwargs}\nid: {userId}\n")

    if command == 'roll':
        return character_roll(userId, args[0])

    elif command == 'save':
        return character_save_roll(userId, args[0], args[1])

    elif command == 'erase':
        return character_delete_roll(userId, args[0])

    elif command == 'list':
        return character_list_rolls(userId)

    elif command == 'inventory':
        return character_list_inventory(userId)

    elif command == 'give':
        print(kwargs)
        if is_admin(userId):
            print('sender is admin')
            return admin_give_item(kwargs['recipient'], kwargs['item'], kwargs['count'])
        else:
            print('sender is character')
            return character_give_item(userId, kwargs['recipient'], kwargs['item'], kwargs['count'])

    elif command == 'register':
        return register(userId, args[0], args[1])

    elif command == 'unregister':
        return unregister(userId)

# CHARACTER -----------------------------------------------------------------------

def register(characterId, first, last):
    user = database.get_user_by_id(id)
    for characterId in user["characters"]:
        existing = database.get_character_by_id(characterId)
        if first == existing['first']:
            return f"You already have a character named \"{first}\"."
    database.create_character(str(uuid4()), first, last)
    return f"character '{first}' created successfully"


def unregister(characterId):
    character = database.get_character_by_id(characterId)
    database.delete_character(characterId)
    return f"character '{character['first']}' deleted successfully"

# DICE ----------------------------------------------------------------------------

def character_roll(characterId, diceString):
    diceString = diceString.strip().lower()
    character = database.get_character_by_id(characterId)
    nameSpace = character['rolls']
    result = dice.processString(diceString, nameSpace)
    response = f"{character['first']} rolled {result}" if diceString not in nameSpace.keys() else f"{character['first']} rolled {diceString}: {result}"
    return response


def character_save_roll(characterId, key, diceString):
    diceString = diceString.strip().lower()
    key = key.strip().lower()
    character = database.get_character_by_id(characterId)
    character['rolls'][key] = diceString
    database.update_character(characterId, changedValues={'rolls': character['rolls']})
    return f"saved '{key}' successfully"


def character_delete_roll(characterId, key):
    key = key.strip().lower()
    character = database.get_character_by_id(characterId)
    try:
        del character['rolls'][key]
        database.update_character(characterId, changedValues={'rolls': character['rolls']})
    except KeyError as e:
        return f"Delete failed. No saved roll called {e}"
    return f"deleted '{key}' successfully"


def character_list_rolls(characterId):
    character = database.get_character_by_id(characterId)
    nameSpace = character['rolls']
    keys = [*nameSpace]
    keys.sort()

    response = f"{character['first']}'s dice\n" + ''.ljust(40, '=') + '\n'
    for key in keys:
        response += f"{key}:".ljust(25, ' ') + nameSpace[key] + "\n"
    return response


# INVENTORY ----------------------------------------------------------------------------

def character_list_inventory(characterId):
    character = database.get_character_by_id(characterId)
    itemList = []
    for key in character['inventory'].keys():
        itemList.append(character['inventory'][key])
    return build_inventory_string(itemList, includeTotal=True)


def admin_give_item(recipientName, itemName, quantity):
    # get recipientId
    recipient = database.get_character_by_name(recipientName)
    if recipient == None:
        return f"No character named '{recipientName}'"
    # get itemId
    results = database.search_items(itemName)
    if len(results) > 1:
        response = f"no matches for '{itemName}'. Did you mean one of these?"
        for result in results:
            response += f"- {result.name}"
        return response
    elif len(results) == 0:
        return f"No items matched '{itemName}'"
    else:
        newQuantity, numberRemoved = database.update_character_inventory(recipient['id'], results[0].id, quantity)
        return f"{recipientName} recieved {quantity} {itemName}('s)"


def character_drop_item(characterId, itemName, quantity):
    # get giver
    giver = database.get_character_by_id(characterId)

    # get Item Id
    results = database.search_items(itemName)
    if len(results) != 1:
        return f"No item named '{itemName}'"
    itemId = results[0].id

    newQuantity, numberRemoved = database.update_character_inventory(characterId, itemId, -1 * quantity)
    return f"{giver['first']} dropped {numberRemoved} {itemName}('s). {newQuantity} remaining."


def character_give_item(characterId, recipientName, itemName, quantity):
    # get giver
    giver = database.get_character_by_id(characterId)

    # get recipientId
    recipient = database.get_character_by_name(recipientName)
    if recipient == None:
        return f"No character named '{recipientName}'"

    # get Item Id
    results = database.search_items(itemName)
    if len(results) != 1:
        return f"No item named '{itemName}'"
    itemId = results[0].id
    
    # perform transaction
    newQuantity, numberRemoved = database.update_character_inventory(characterId, itemId, -1 * quantity)
    if numberRemoved == 0:
        return f"You do not have any {itemName}'s in your inventory"
    database.update_character_inventory(recipient['id'], itemId, numberRemoved)

    response = f"{giver['first']} gave {recipientName} {numberRemoved} {itemName}('s)"
    if numberRemoved != quantity:
        response = f"You do not have {quantity} {itemName}('s) in your inventory.\n" + response
    return response


def build_inventory_string(itemList, fill=' ', includeTotal=False):
    totalWeight = 0
    itemList.sort(key=name_sort)
    response = 'NAME'.ljust(35) +'QUANTITY'.ljust(10) + 'COST'.ljust(10) + 'WEIGHT\n'
    response += ''.ljust(60, '=') + '\n'
    for item in itemList:
        weight = float(item['weight']) * item['quantity']
        totalWeight += weight
        response += f"{item['name']}".ljust(35, fill) + f"x{item['quantity']}".ljust(10, fill) + item['cost'].ljust(10, fill) + str(weight) + '\n'

    if includeTotal:
        response += ''.ljust(60, '=') + '\n'
        response += 'Total:'.ljust(55, fill) + f"{totalWeight}"
    return response