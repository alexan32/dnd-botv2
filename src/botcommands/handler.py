import database.database as database
import diceParser.diceParserV2 as parser
import importlib.util
import json
import os


dice = parser.Parser()
databaseObject = database.Database()

print("\ninitializing back end extensions...\n")
script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, '../../config.json')) as f:
    config = json.load(f)
    for plugin in config['plugins']:
        spec = importlib.util.spec_from_file_location(plugin, os.path.join(script_dir, f"../../plugins/{plugin}.py"))
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        try:
            mod.init_plugin(dice, databaseObject)
        except AttributeError:
            print(f"* plugin '{plugin}' had no init_plugin function and will be skipped")
        else:
            print(f"* loaded '{plugin}'")
    print('done')


# HANDLER ------------------------------------------------------------------------

async def handler(ctx, command, *args):
    userId = database.get_assumed_id(ctx.author.id)
    print(f"command: {command}\nid: {userId}\nargs: {args}")

    if command == 'player_roll':
        response = player_roll(userId, args[0])
        await ctx.send(f"```{response}```", delete_after=15.0)


# CHARACTER -----------------------------------------------------------------------

def register(playerId, first, last):
    database.create_player(playerId, first, last)
    return f"player '{first}' created successfully"


def unregister(playerId):
    player = database.get_player_by_id(playerId)
    database.delete_player(playerId)
    return f"player '{player['first']}' deleted successfully"

# DICE ----------------------------------------------------------------------------

def player_roll(playerId, diceString):
    diceString = diceString.strip().lower()
    player = database.get_player_by_id(playerId)
    nameSpace = player['rolls']
    if diceString in nameSpace.keys():
        result = dice.parse(nameSpace[diceString], nameSpace)
        response = f"{player['first']} rolled '{diceString}': {result[1]}"
    else:
        result = dice.parse(diceString, nameSpace)
        response = f"{player['first']} rolled {result[1]}"
    return response


def player_save_roll(playerId, key, diceString):
    diceString = diceString.strip().lower()
    key = key.strip().lower()
    player = database.get_player_by_id(playerId)
    player['rolls'][key] = diceString
    database.update_player(playerId, changedValues={'rolls': player['rolls']})
    return f"saved '{key}' successfully"


def player_delete_roll(playerId, key):
    key = key.strip().lower()
    player = database.get_player_by_id(playerId)
    del player['rolls'][key]
    database.update_player(playerId, changedValues={'rolls': player['rolls']})
    return f"deleted '{key}' successfully"


def player_list_rolls(playerId):
    player = database.get_player_by_id(playerId)
    nameSpace = player['rolls']
    keys = [*nameSpace]
    keys.sort()

    response = f"{player['first']}'s dice\n" + ''.ljust(60, '=') + '\n'
    for key in keys:
        response += f"{key}:".ljust(30, '.') + nameSpace[key] + "\n"
    return response


# INVENTORY ----------------------------------------------------------------------------

def player_list_inventory(playerId):
    player = database.get_player_by_id(playerId)
    itemList = []
    for key in player['inventory'].keys():
        itemList.append(player['inventory'][key])
    return build_inventory_string(itemList, includeTotal=True)


def admin_give_item(recipientName, itemName, quantity):
    # get recipientId
    recipient = database.get_player_by_name(recipientName)
    if recipient == None:
        return f"No character named '{recipientName}'"
    # get itemId
    results = database.search_items()
    if len(results) > 1:
        response = f"no matches for '{itemName}'. Did you mean one of these?"
        for result in results:
            response += f"- {result.name}"
        return response
    elif len(results) == 0:
        return f"No items matched '{itemName}'"
    else:
        database.update_player_inventory(recipient['id'], results[0].id, quantity)


def player_drop_item(playerId, itemName, quantity):
    # get giver
    giver = database.get_player_by_id(playerId)

    # get Item Id
    results = database.search_items(itemName)
    if len(results) != 1:
        return f"No item named '{itemName}'"
    itemId = results[0].id

    newQuantity, numberRemoved = database.update_player_inventory(playerId, itemId, -1 * quantity)
    return f"{giver['first']} dropped {numberRemoved} {itemName}('s). {newQuantity} remaining."


def player_give_item(playerId, recipientName, itemName, quantity):
    # get giver
    giver = database.get_player_by_id(playerId)

    # get recipientId
    recipient = database.get_player_by_name(recipientName)
    if recipient == None:
        return f"No character named '{recipientName}'"

    # get Item Id
    results = database.search_items(itemName)
    if len(results) != 1:
        return f"No item named '{itemName}'"
    itemId = results[0].id
    
    # perform transaction
    newQuantity, numberRemoved = database.update_player_inventory(playerId, itemId, -1 * quantity)
    if numberRemoved == 0:
        return f"You do not have any {itemName}'s in your inventory"
    database.update_player_inventory(recipient['id'], itemId, numberRemoved)

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


def name_sort(e):
    return e['name']


if __name__ == '__main__':
    pass
    # print(player_save_roll(239517576781234177, 'unarmed strike', '1d20 + prof + max(str, dex)'))
    # print(player_roll(239517576781234177, 'dagger'))
    # print(player_delete_roll(239517576781234177, 'unarmed'))
    # print(player_list_inventory(239517576781234177))
