import database.database as database
import commands.utils as utils
import time
import json
import os

from pprint import pprint


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


def handler(ctx, command, *args, **kwargs):

    print(f"\ncommand: {command} {args} {kwargs}\n discordId: {ctx.author.id}\n guildId: {ctx.guild.id}\n")
    
    if command == 'create_character':
        return create_character(ctx, args[0], args[1])
    elif command == 'save_dice':
        return save_dice(ctx, args[0], args[1])
    elif command == 'roll_dice':
        return roll_dice(ctx, args[0])
    elif command == 'list_dice':
        return list_dice(ctx, args[0])
    elif command == 'search_dice':
        return search_dice(ctx, args[0])

def create_character(ctx, first, last):
    success = database.create_character(ctx.guild.id, ctx.author.id, first, last)
    if success:
        return f"Character \"{first} {last}\" created successfully."
    return f"Failed to create character."


def save_dice(ctx, key, value):
    for x in ['+', '-', '*', '/']:
        value = x.join(value.split(x))
        value = value.replace(x, f" {x} ")
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    print(character)
    character["rolls"][key] = value
    database.upsert_character(ctx.guild.id, ctx.author.id, character)
    return f"roll \"{key}\" set to \"{value}\""


def roll_dice(ctx, input):
    return utils.roll(ctx, input)


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