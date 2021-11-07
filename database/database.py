from tinydb import TinyDB, Query
from difflib import SequenceMatcher
from pprint import pprint
from uuid import uuid4
import json
import os

script_dir = os.path.dirname(__file__) #<-- absolute dir the script is in
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)
Row = Query()

# id: uuid
# guildId: discord guildid
# userId: discord userid
# rolls: dict
# articles: dict
# counters: dict
# first: first name
# last: last name
characterTable = TinyDB(os.path.join(script_dir, 'data/characters.json'))


with open(os.path.join(script_dir, f"models/{config['ruleset']}.json")) as f:
    model_character = json.load(f)

# CHARACTER

def get_user_character(discordId, guildId):
    return characterTable.get(((Row.discordId == discordId) & (Row.guildId == guildId)))

def create_character(guildId:int, discordId:int, first:str, last:str):
    print(discordId)
    try:
        character = model_character.copy()
        character["discordId"] = discordId
        character["guildId"] = guildId
        character["first"] = first
        character["last"] = last
        characterTable.upsert(character, ((Row.discordId == discordId) & (Row.guildId == guildId)))
        return True
    except Exception as e:
        print(f"Error occurred in character creation. Error: {e}")
        return False


def upsert_character(discordId, guildId, character):
    characterTable.upsert(character, ((Row.discordId == discordId) & (Row.guildId == guildId)))
