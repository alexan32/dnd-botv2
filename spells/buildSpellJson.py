# DESCRIPTION: this script utilizes 5e-spells.csv and the 5eEffects.csv file as well as webscraping 
# from http://dnd5e.wikidot.com/ to generate json files containing 5e spell info, which is utilized 
# by the "cast" command.

import json
import csv
import requests
from bs4 import BeautifulSoup
import time


def buildSpellJson():

    output = {"spellList": []}
    failedSpells = []

    print("READING SPELLS CSV")
    with open("./5e-spells.csv") as f:
        fileData = csv.reader(f)

        print("PROCESSING".ljust(50, "="))
        # populate using CSV
        for row in fileData:
            if row[0] == "Spell Name":
                continue
            spell = {
                "name": row[0],
                "description": "NA",
                "level": row[1],
                "ritual": row[3].strip() == "Ritual",
                "school": row[2],
                "castingTime": row[4],
                "range": row[5],
                "target": row[6] if row[6].strip() != "" else None,
                "components": row[7].strip() + row[8].strip() + row[9].strip(),
                "materials": row[10] if row[10].strip() != "" else None,
                "materialCost": row[11] if row[11].strip() !="" else None,
                "concentration": row[12].strip() == "Concentration",
                "duration": row[13],
                "saveEffect": row[14] if row[14] != "" else None,
                "damageType": row[15] if row[15] != "" else None,
                "damageOrHealing": row[16] if row[16] != "" else None,
                "effects": [],
                "atHigherLevels": row[20]
            }
            classes = []
            for x in [21, 22, 23, 24, 25, 26, 27, 28]:
                if row[x].strip() != "":
                    classes.append(row[x])
            spell["classes"] = classes

            # fetch description from http://dnd5e.wikidot.com/
            status, message, description, atHigherLevels = newSearchSpellDescription(row[0].strip())
            if status != 200:
                failedSpells.append((row[0].strip(), message))
            else:
                spell["description"] = description
                spell["atHigherLevels"] = atHigherLevels

            # add to spell list
            output["spellList"].append(spell)

    print("\nDONE".ljust(50, "-"))
    print(f"Total spells: " + str(len(output["spellList"])))

    print("saving spells as a list in json file")
    with open("./5e-spells-list.json", 'w+') as f:
        json.dump(output, f)

    print("saving spells as a dictionary in json file")
    with open("./5e-spells-dict.json", 'w+') as f:
        dictionary = {}
        for spell in output["spellList"]:
            name = "".join(spell["name"].split(" ")).lower()
            name = "".join(name.split("'"))
            dictionary[name] = spell

        json.dump(dictionary, f)


    if len(failedSpells) > 0:
        print("\nFailed to capture descriptions of the following spells: ")
        for x in failedSpells:
            print(x[0].ljust(30) + x[1])


def processEffects():

    with open("5e-spells-dict.json") as f:
        spellData = json.load(f)


    with open("./5eEffects.csv") as f:
        effectData = csv.reader(f)

        # populate using CSV
        for row in effectData:
            spellName = "".join(row[0].split(" "))
            spellName = "".join(spellName.split("'"))
            spellName = spellName.lower()

            if spellName in spellData:

                effect = {}

                if row[1].strip() == "TRUE":
                    effect["attackRoll"] = True

                if row[2].strip() != "":
                    effect["diceRoll"] = row[2]

                if row[3].strip() != "":
                    effect["spellSave"] = row[3]

                if row[4].strip() != "":
                    effect["N"] = row[4]

                if row[6].strip() != "":
                    effect["repeat"] = row[6]

                if row[5].strip() != "":
                    scale = {}
                    thresholds =  row[5].strip().split(",")
                    for x in thresholds:
                        key, value = x.split("-")
                        scale[key] = value
                
                    effect["c"] = scale

                if len(effect.keys()) != 0:
                    spellData[spellName]["effects"].append(effect)
                    print(spellName + "\n" + json.dumps(spellData[spellName]["effects"]))

            else:
                print("No match! Spell dictionary is missing " + spellName)


        with open("./5e-spells-dict.json", 'w+') as f:
            json.dump(spellData, f)


def newSearchSpellDescription(spellName:str, retries:int=0):
    status = 400
    message = "ok"
    description = None 

    try:
        words = spellName.split(" ")
        for x in range(len(words)):
            words[x] = words[x].lower().replace("'", "").replace("/", "-")
        name = "-".join(words) 
        print(f"{name}")

        r = requests.get(f"http://dnd5e.wikidot.com/spell:{name}")
        if r.status_code != 200:
            status = r.status_code
            message = "failed to retrieve data from dnd5e.wikidot.com"
            raise Exception("request failed")
        soup = BeautifulSoup(r.content, 'html.parser')
        spellCard = soup.find(id="page-content")

        description = ""
        atHigherLevels = ""
        recording = False
        for x in spellCard.children:
            txt = x.get_text()

            # skip empty text
            if txt.strip() == "":
                continue

            # don't include 'Spell Lists' in spell description
            if "Spell Lists" in txt and len(x.find_all("a")) > 0:
                break

            # At higher levels
            if txt.startswith("At Higher Levels"):
                atHigherLevels = txt
                break

            # add txt to description
            elif recording:
                description += txt

            # Spell info over, start collecting description
            elif "Duration" in x.get_text():
                recording = True

        description = description.encode("ascii", "ignore").decode()
        atHigherLevels = atHigherLevels.encode("ascii", "ignore").decode()

        status = 200
        
    except Exception as e:
        print(e)
        if retries < 3:
            time.sleep(1)
            status, message, description, atHigherLevels = newSearchSpellDescription(spellName, retries+1)

    return status, message, description, atHigherLevels


if __name__ == "__main__":
    buildSpellJson()
    processEffects()