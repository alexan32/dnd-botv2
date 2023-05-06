import database.database as database
import commands.utils as utils
import spells.spells as spells
import time
import json
import os
import re

from pprint import pprint


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


def handler(ctx, command, *args, **kwargs):

    print(f"\ncommand: {command} {args} {kwargs}\n discordId: {ctx.author.id}\n guildId: {ctx.guild.id}\n")
    
    existingCharacter = database.get_user_character(ctx.author.id, ctx.guild.id)
    if existingCharacter is None and command != "create_character":
        return "You don't have a character yet! Use the \"!create_character\" command to get started."

    if command == 'create_character':
        return create_character(ctx, args[0], args[1])
    elif command == 'get_character':
        return get_character(ctx)
    elif command == 'put_character':
        return put_character(ctx, args[0])
    elif command == 'save_dice':
        return save_dice(ctx, args[0], args[1])
    elif command == 'roll_dice':
        if len(args) > 1:
            return roll_dice(ctx, args[0], args[1])
        return roll_dice(ctx, args[0])
    elif command == 'list_dice':
        return list_dice(ctx, args[0])
    elif command == 'search_dice':
        return search_dice(ctx, args[0])
    elif command == 'delete_dice':
        return delete_dice(ctx, args[0])
    elif command == 'save_counter':
        return save_counter(ctx, args[0], args[1])
    elif command == 'increment_counter':
        return increment_counter(ctx, args[0], args[1])
    elif command == 'list_counters':
        return list_counters(ctx, args[0])
    elif command == 'search_counters':
        return search_counters(ctx, args[0])
    elif command == 'cast':
        return cast_spell(ctx, *args)


def create_character(ctx, first, last):
    success = database.create_character(ctx.guild.id, ctx.author.id, first, last)
    if success:
        return f"Character \"{first} {last}\" created successfully."
    return f"Failed to create character."


def get_character(ctx):
    return database.get_user_character(ctx.author.id, ctx.guild.id)

def put_character(ctx, content):
    content["discordId"] = ctx.author.id
    content["guildId"] = ctx.guild.id
    try:
        assert "rolls" in content
        assert "first" in content
        assert "last" in content
        assert "counters" in content
        assert "articles" in content
    except:
        return "Character failed to upload. Invalid or missing data."
    try:
        database.upsert_character(ctx.author.id, ctx.guild.id, content)
    except:
        return "Character failed to upload. Database error."
    return "Character uploaded successfully."

def delete_dice(ctx, saveName):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    if saveName in character["rolls"]:
        del character["rolls"][saveName]
        database.upsert_character(ctx.author.id, ctx.guild.id, character)
        response = f"\"{saveName}\" deleted from saved dice rolls."
    else:
        response = f"No dice string named \"{saveName}\"."
    return response


def save_dice(ctx, key, value):
    for x in ['+', '-', '*', '/']:
        value = x.join(value.split(x))
        value = value.replace(x, f" {x} ")
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    # print(character)
    character["rolls"][key] = value
    database.upsert_character(ctx.guild.id, ctx.author.id, character)
    return f"roll \"{key}\" set to \"{value}\""


def roll_dice(ctx, input, adv=""):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    try:
        response = utils.roll(ctx, input, adv)
    except Exception as e:
        print(e)
        return e.message
    if input in character["rolls"].keys():
        response = f"{character['first']} {character['last']} rolled {input}: {response}"
    print(response)
    return response


def list_dice(ctx, index):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    pages = utils.paginateDict(character["rolls"])
    if index > len(pages)-1:
        index = len(pages)-1
    return f"Page {index+1}/{len(pages)}" + " ".ljust(30, "=") + "\n" + pages[index]


def search_dice(ctx, searchString):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    temp = {}
    for key in character["rolls"].keys():
        if utils.similarity(key, searchString) > 0.6:
            temp[key] = character["rolls"][key]
    if len(temp.keys()) == 0:
        return f"No dice rolls matched with \"{searchString}\""
    pages = utils.paginateDict(temp)
    return pages[0]


def save_counter(ctx, counterName, max):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    isNew = counterName not in character["counters"].keys()
    character["counters"][counterName] = {
        "max": int(max),
        "value": int(max)
    }
    database.upsert_character(ctx.author.id, ctx.guild.id, character)

    if isNew:
        return f"Created counter \"{counterName}\" with a max value of {max}."
    else:
        return f"Counter \"{counterName}\" set to {max}."


def increment_counter(ctx, counterName, increment):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    if not counterName in character["counters"]:
        return f"Counter \"{counterName}\" not found."
    counter = character["counters"][counterName]
    counter["value"] = int(counter["value"]) + int(increment)
    if counter["value"] > counter["max"]:
        counter["value"] = counter["max"]
    elif counter["value"] < 0:
        counter["value"] = 0
    character["counters"][counterName] = counter
    database.upsert_character(ctx.author.id, ctx.guild.id, character)
    return f"{counterName}: {counter['value']} / {counter['max']}"


def list_counters(ctx, index):
    print(f"list_counters. index: {index}")
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    counters = character["counters"]
    temp = {}
    for key in counters.keys():
        temp[key] = f"{counters[key]['value']} / {counters[key]['max']}"
    pages = utils.paginateDict(temp)
    if index > len(pages)-1:
        index = len(pages)-1
    return f"Page {index+1}/{len(pages)}" + " ".ljust(30, "=") + "\n" + pages[index]


def search_counters(ctx, searchString):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    counters = character["counters"]
    temp = {}
    for key in counters.keys():
        if utils.similarity(key, searchString) > 0.6:
            temp[key] = f"{counters[key]['value']} / {counters[key]['max']}"
    if len(temp.keys()) == 0:
        return f"No dice rolls matched with \"{searchString}\""
    pages = utils.paginateDict(temp)
    return pages[0]

# def castSpell(spell:dict, slotLevel:int, attackRoll="1d20", spellSave="8", characterLevel="1", rollsLibrary={})
def cast_spell(ctx, spellName, slotLevel, attackRoll, spellSave, characterLevel):
    if not spells.spellExists(spellName):
        return [f"No spell matches for \"{spellName}\""]
    
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    rolls = character['rolls']
    spell = spells.getSpell(spellName)
    
    if not slotLevel:
        slotLevel = int(spell["level"])

    if not attackRoll:
        if "spellattack" in rolls:
            attackRoll = rolls["spellattack"]
        else:
            attackRoll="1d20"
    elif attackRoll in rolls:
        attackRoll = rolls[attackRoll]

    if not spellSave:
        if "spellsave"in rolls:
            spellSave = rolls["spellsave"]
        else:
            spellSave = "8"
    elif spellSave in rolls:
        spellSave = rolls["spellsave"]

    if not characterLevel:
        if "level" in rolls:
            characterLevel = rolls["level"]
        else:
            characterLevel = "1"
    elif characterLevel in rolls:
        characterLevel = rolls[characterLevel]

    return spells.castSpell(spell, slotLevel, attackRoll, spellSave, characterLevel, rolls)