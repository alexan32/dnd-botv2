import database.database as database
import diceParser.diceParserV2 as parser

from pprint import pprint

dice = parser.Parser()


async def execute(ctx, command, *args):
    userId = database.get_assumed_id(ctx.author.id)
    print(f"command: {command}\nid: {userId}\nargs: {args}")

    if command == 'player_roll':
        response = player_roll(userId, args[0])
        await ctx.send(f"```{response}```", delete_after=15.0)


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


def player_list_inventory(playerId):
    player = database.get_player_by_id(playerId)
    itemList = []
    for key in player['inventory'].keys():
        itemList.append(player['inventory'][key])
    return build_inventory_string(itemList, includeTotal=True)


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
    # print(player_save_roll(239517576781234177, 'unarmed strike', '1d20 + prof + max(str, dex)'))
    # print(player_roll(239517576781234177, 'unarmed strike'))
    # print(player_delete_roll(239517576781234177, 'unarmed'))

    print(player_list_inventory(239517576781234177))
