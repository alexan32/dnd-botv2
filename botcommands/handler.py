import database.database as database
import dice.dice_processor as dp
from uuid import uuid4
from pprint import pprint
import botcommands.utils as utils
import json
import os

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)

acceptedRoles = config["playerRoles"] + config["adminRoles"]
dice = dp.DiceProcessor()

def name_sort(e):
    return e['name']

def adminAccess(ctx):
    roles = ctx.author.roles
    for role in roles:
        if role.name.lower() in config["adminRoles"]:
            return True
    return False

def allowAccess(ctx):
    roles = ctx.author.roles
    for role in roles:
        if role.name.lower() in acceptedRoles:
            return True
    return False

adminRequiredMessage = "You need admin permissions for that. Ask a moderator to give you one of the following roles: "
for role in config['adminRoles']:
    adminRequiredMessage += f"\n{role}"

# HANDLER ------------------------------------------------------------------------

def handler(ctx, command, *args, **kwargs):

    print(f"\ncommand: {command} {args} {kwargs}\n discordId: {ctx.author.id}\n guildId: {ctx.guild.id}\n")

    if not allowAccess(ctx) and command != "register_server":
        print(f"access denied. user roles: {ctx.author.roles}")
        return f"You do not have the appropriate permission. Ask a server admin to give you the {config['playerRoles'][0]} role"

    user = database.get_user_by_id(ctx.author.id)
    if user is None:
        user = database.create_user(ctx.author.id)

    # server config
    if command == 'register_server':
        return register_server(ctx, "5e")

    elif command == 'server_ruleset':
        pass

    elif command == 'change_directory':
        return change_directory(ctx, args[0])

    elif command == 'list_directory':
        return list_directory(ctx)

    elif command == 'make_directory':
        return make_directory(ctx, args[0])

    # rolls
    elif command == 'roll':
        pass

    elif command == 'save_roll':
        pass

    elif command == 'delete_roll':
        pass

    elif command == 'list_rolls':
        pass
    # character inventory
    elif command == 'list_inventory':
        pass

    elif command == 'give_item':
        pass

    elif command == 'drop_item':
        pass

    # character
    elif command == 'create_character':
        return create_character(ctx, args[0], args[1])

    elif command == 'delete_character':
        pass

    elif command == 'list_characters':
        return list_characters(ctx)


def register_server(ctx, ruleset):
    if ctx.author.id != ctx.guild.owner_id:
        return False, "Only the server owner can register the server!"

    existing = database.get_game_by_id(ctx.guild.id)
    if not existing is None:
        return False, "Sorry! Only one game is allowed per server."

    game = database.create_game(ctx.guild.id, ruleset)

    return True, "Server registered successfully."


def change_directory(ctx, path):
    user = database.get_user_by_id(ctx.author.id)
    cwd = user['currentWorkingDirectory']

    directory = buildDirectory(ctx)
    _cwd, directory, message = utils.navigateDict(directory, cwd, path)

    if _cwd != cwd:
        user['currentWorkingDirectory'] = _cwd
        database.update_user(ctx.author.id, {'currentWorkingDirectory': _cwd})
    
    return directory, _cwd


def list_directory(ctx):
    user = database.get_user_by_id(ctx.author.id)
    cwd = user['currentWorkingDirectory']
    directory = buildDirectory(ctx)

    _cwd, directory, message = utils.navigateDict(directory, cwd, "")
    
    return directory, _cwd


def make_directory(ctx, directory_name):
    user = database.get_user_by_id(ctx.author.id)
    cwd = user['currentWorkingDirectory']

    character = database.get_character_by_id(ctx.author.id)
    ruleset = database.get_game_by_id(ctx.guild.id)["ruleset"]

    directory = {"ruleset": {**ruleset}, **character}
    
    _cwd, _directory, message = utils.navigateDict(directory, cwd, "")

    path = _cwd.split('/')
    cwd = "/".join(path.remove)
    if path[0] == 'ruleset':
        if not adminAccess(ctx):
            return "only admins are allowed to make changes to the ruleset"
        else:
            ruleset_directory = utils.navigateDict(ruleset)
    elif path[0] == 'character':
        character_directory = utils.navigateDict(character)
    database.update_game(ctx.guild.id, {"ruleset": ruleset})
    

def create_character(ctx, first, last):
    existing = database.get_character_by_name_and_game(ctx.guild.id, first)
    if not existing is None: 
        return f"A character already exists on this server with the first name \"{first}\"."

    character, cid = database.create_character(ctx.author.id, ctx.guild.id, first, last)
    user = database.get_user_by_id(ctx.author.id)
    user["characters"].append(cid)
    user["activeCharacter"] = cid
    database.update_user(ctx.author.id, {**user})
    return f"character \"{first} {last}\" created successfully and set active."


def list_characters(ctx):
    response = ""
    characters = database.search_character_by_user_and_game(ctx.author.id, ctx.guild.id)
    if len(characters) == 0:
        return "No characters found."
    else:
        for character in characters:
            response += f"\n - {character['first']} {character['last']}"
    return response


def buildDirectory(ctx):
    user = database.get_user_by_id(ctx.author.id)
    cid = user['activeCharacter']
    cwd = user['currentWorkingDirectory']

    character = database.get_character_by_id(cid)
    ruleset = database.get_game_by_id(ctx.guild.id)["ruleset"]
    directory = {"ruleset": {**ruleset}, **character}
    return directory