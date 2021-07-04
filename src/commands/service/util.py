import database.database as database
import diceParser.diceParserV2 as parser

dice = parser.Parser()

# def weaponAttack(playerId, weaponId):
#     player = database.get_player_by_id(playerId)
#     weapon = database.get_item_by_id(weaponId)
#     finesse = 'finesse' in weapon.properties.properties
#     if finesse and player

# def weaponDamage(playerId, weaponId):
#     player = database.get_player_by_id(playerId)
#     weapon = database.get_item_by_id(weaponId)

# {
#     "type": "medium",
#     "ac": "12 + min(dex, 2)",
#     "stealthDisadvantage": false,
#     "strengthRequiremeent": 0
# }

def itemInfo(itemId):
    item = database.get_item_by_id(itemId)

    info = item['name'].upper().ljust(25) + f"cost: {item['cost']}".ljust(15) + f"weight: {item['weight']}".ljust(15) + "\n"
    
    if item['type'] == 'armor':
        info += f"armor type: {item['properties']['type']}\n"
        info += f"AC: {item['properties']['ac']}\n"
        disadvantage = "yes\n" if item['properties']['stealthDisadvantage'] else "no\n"
        info += f"stealth disadvantage: {disadvantage}"
        requirement = "none" if item['properties']['strengthRequirement'] == 0 else str(item['properties']['strengthRequirement'])
        info += f"strength requirement: {requirement}"

    elif item['type'] == 'weapon':
        info += f""
    return info

if __name__ == '__main__':
    print(itemInfo(1))
    print()
    print(itemInfo(9))