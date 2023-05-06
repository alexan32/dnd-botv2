import re
import os
import json
import dice.diceDiceRevoloution as dp

processor = dp.DiceProcessor()
cantripScaling = {
    "5": "2",
    "11": "3",
    "17": "4"
}

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
with open(os.path.join(script_dir, "./spellCard.txt")) as f:
    spellCard = f.read()
with open(os.path.join(script_dir, "./5e-spells-dict.json")) as f:
    spells = json.load(f)

#  spell: spell dictionary from the 5e-spells-dict.json
#  slotLevel: int representing the level of the spell slot
#  castingInfo: dict which contains "castorLevel", "spellSave", and "attackRoll" for the spell
def castSpell(spell:dict, slotLevel:int, attackRoll="1d20", spellSave="8", characterLevel="1", rollsLibrary={}):
    results = []
    castingInfo = {
        "attackRoll": attackRoll,
        "spellSave": spellSave,
        "castorLevel": characterLevel,
        "spellLevel": spell['level'],
        "slot": slotLevel
    }

    print(json.dumps(castingInfo))

    # check spell slot level
    if slotLevel < int(spell["level"]):
        results.append(f"Insufficient spell slot: {slotLevel}")
        return results

    # build spell card
    results.append(buildSpellCard(spell))

    # process spell effects
    effects = spell.get("effects", [])
    for effect in effects:

        # repeat effect is primarily for spells with multiple attack rolls
        if "repeat" in effect:
            calculation = effect["repeat"].replace("s", str(slotLevel))
            totalRepeats = eval(calculation)

            while totalRepeats > 0:
                results.extend(processEffect(effect, slotLevel, castingInfo, rollsLibrary))
                totalRepeats -= 1

        else: 
            results.extend(processEffect(effect, slotLevel, castingInfo, rollsLibrary))

    return results


def buildSpellCard(spell):
    materials = f"({spell['materials']})" if spell['materials'] != "" else ""
    ritual = f"(ritual)" if spell['ritual'] else ""
    concentration = f"(concentration)" if spell['concentration'] else ""
    atHigherLevels = f"\nAt Higher Levels: {spell['atHigherLevels']}" if spell['atHigherLevels'] != "" else ""
    return spellCard.format(
        spellName=spell["name"], 
        school=spell["school"],
        level=spell["level"],
        castingTime=spell["castingTime"],
        ritual=ritual,
        range=spell["range"],
        target=spell["target"],
        components=spell["components"],
        materials=materials,
        duration=spell["duration"],
        concentration=concentration,
        description=spell["description"],
        atHigherLevels=atHigherLevels
    )


def processEffect(effect: dict, slotLevel: int, castingInfo: dict, rollsLibrary: dict = {}):
    results = []
    lib = {**rollsLibrary, **effect}
    
    # Attack Roll
    if effect.get("attackRoll") and "attackRoll" in castingInfo:
        results.append(f"Attack roll: {processor.processDiceString(castingInfo['attackRoll'], lib)[1]}")
        
    # Dice Roll
    if "diceRoll" in effect:
        diceRoll = effect["diceRoll"]
        _type = ""
        if "[" in diceRoll and "]" in diceRoll:
            _type = "[" + diceRoll[diceRoll.find("[")+1 : diceRoll.find("]")] + "]"
        diceRoll = re.sub("([\[]).*?([\]])", "", diceRoll)
        
        # basicN is shorthand N(s) func for spells whose "N" scales 1:1 with slot level
        # "diceRoll" : "basicNd8 [bludgeoning]"
        # "basicN" : "4"
        if re.match("basicN(?=d\d)", diceRoll) and "N" in effect:
            f = eval(f"{effect['N']} - {castingInfo['spellLevel']} + {slotLevel}")
            diceRoll = re.sub("basicN(?=d\d)", str(f), diceRoll)

        # Adjustment based on spellslot. N(s)
        # "diceRoll": "5 * N [bludgeoning]"
        # "N": "4 - 4 + s"
        elif "N" in effect:
            nEquation = effect["N"]
            nEquation = re.sub("s", str(slotLevel), nEquation)
            diceRoll = re.sub("N", f"{eval(nEquation)}", diceRoll)
            
        # Adjustment based on castor level. Commonly used for cantrips.
        # "diceRoll": "cd6 [acid]"
        # "c": {"5": "2", "11": "3", "17": "4"} (optional)
        if re.match("c(?=d\d)", diceRoll) and "castorLevel" in castingInfo:
            castorLevel = castingInfo["castorLevel"]
            scaling = effect.get("c") if "c" in effect else cantripScaling
            thresholds = list(scaling.keys())
            thresholds.sort(key= lambda x: int(x), reverse=True)
            key = next((x for x in thresholds if int(castorLevel) >= int(x)), None)
            c = "1" if key is None else scaling[key]
            diceRoll = re.sub("c(?=d\d)", str(c), diceRoll)

        # Save roll result with type added back in
        results.append("{roll} {type}".format(roll=processor.processDiceString(diceRoll, lib)[1], type= _type))

    # Spell Save
    if "spellSave" in effect and "spellSave" in castingInfo:
        results.append(f"Spell Save DC: {processor.processDiceString(castingInfo['spellSave'], lib)[0]} {effect['spellSave']}")

    return results

def spellExists(spellname:str):
    return spellname in spells.keys()

def getSpell(spellname:str):
    return spells[spellname]

if __name__ == "__main__":

    castingInfo = {
        "castorLevel": "20",
        "spellSave": "13",
        "attackRoll": "1d20 + wis + prof",
    }

    playerLibrary = {
        "wis": "3",
        "prof": "4"
    }

    results = castSpell(spells["armorofagathys"], 5, castingInfo)
    for x in results:
        print(x)
        print()


    print(spellExists("scorchingray"))