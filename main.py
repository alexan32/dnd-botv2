import json
import os
import commands.handler
from commands.utils import deleteAfter
import discord
from discord.ext import commands


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.json")) as f:
    config = json.load(f)

intents = discord.Intents.default()
intents.typing = False
intents.presences = False
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)
bot.remove_command("help")
# bot.load_extension("commands.character")
# bot.load_extension("commands.roll")
# bot.load_extension("commands.counter")
# bot.load_extension("commands.spells")

standardHelp = """
COMMANDS:
- !roll
- !rolls
- !delete_roll
- !adv
- !dadv
- !counter
- !counters
- !create_character
- !upload_character
- !download_character
- !cast

type "!help <command>" to see more details on a specific command.
"""


@bot.event
async def on_ready():
    await bot.load_extension("commands.character")
    await bot.load_extension("commands.roll")
    await bot.load_extension("commands.counter")
    await bot.load_extension("commands.spells")
    print("bot is ready\n" + ''.ljust(20, '='))


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         print(error)
#         await ctx.send(f"""```{error}```""", delete_after=20.0)
#         await deleteAfter(ctx, 20.0)
#     elif isinstance(error, commands.MissingRequiredArgument):
#         print(error)
#         await ctx.send(f"""```{error}. type !help for more details```""", delete_after=20.0)
#         await deleteAfter(ctx, 20.0)
#     else:
#         print(error)
#         await ctx.send(f"```An unhandled exception occurred```", delete_after=20.0)
#         await deleteAfter(ctx, 20.0)
#         # raise error

@bot.command()
async def help(ctx, *args):
    if len(args) == 0:
        response = standardHelp

    elif args[0] == "roll":
        response = """
ROLL

    !roll <dice string>
    !roll <assignment statement>

ROLLING DICE

To roll a dice string, type the !roll command and follow the command with a dice string notation representing the dice you would like to roll. For those unfamiliar with dice notation, it follows this format:

    NdX

"N" is a number of dice that have "X" sides. For example, two six sided dice would be "2d6". You can include parenthesis and simple arithmetic as well. Division will always result in a whole number. There are no decimal places.

    !roll 1d20 + 2 * ( 3 / 2 )

SAVING DICE STRINGS

Use this command to save and roll dice. To save a dice roll, follow the command word with an assignment statement. Assignment statements are made using the following format:

    !roll <save name> = <save string>

Save names are unique names used as place holders for each dice string. You can use save names inside of a save string as variables. In the following example, "int" and "prof" are save names for pre-existing dice strings. We are incorporating them into a new dice string called "intelligencesave". Although we are including a space between "intelligence" and "save" in the command, the bot will remove the space when storing the new dice string. If we want to reference this dice string in another dice string, we will have to type it as "intelligencesave".

    !roll intelligence save = 1d20 + int + prof
"""

    elif args[0] == "rolls":
        response = """
ROLLS

    !rolls

LISTING DICE

To view your saved dice strings, use the rolls command.

    !rolls

If you have many saved rolls, the results will be split into multiple pages. You can navigate pages providing a page number:

    !rolls <page number>

If you don't want to see the full list, you can provide a save name to search for:

    !rolls <save name>
        """
    
    elif args[0] == "delete_roll":
        response = """
DELETE ROLL

    !delete_roll <save name>

To remove a roll from your saved dice strings, use the delete_roll command. 
"""
    elif args[0] == "adv":
        response = """
ADVANTAGE

    !adv <dice string | saved dice string>
    !advantage <dice string | saved dice string>

Use this command to roll dice with advantage. This effective takes any instance of "1d20" inside of the dice expression and transforms it into "2d20kh1" (roll two twenty sided dice and keep the highest roll.)
    
"""

    elif args[0] == "dadv":
        response = """
DISADVANTAGE

    !dadv <dice string | saved dice string>
    !disadvantage <dice string | saved dice string>

    Use this command to roll dice with advantage. This effective takes any instance of "1d20" inside of the dice expression and transforms it into "2d20kl1" (roll two twenty sided dice and keep the lowest roll.)
"""

    elif args[0] == "create_character":
        response = """
CREATE CHARACTER

    !create_character <character first name> <character last name>

Use this command to create your character on this discord server. You cannot have more than one character on a server. You cannot access the same character data on another server.

WARNING! If you already have an existing character on this server, using this command will replace the existing character data with a new profile!
"""

    elif args[0] == "upload_character":
        response = """
UPLOAD CHARACTER

    !upload_character

Use this command to upload character data from a .json file. You must attach the file before you send the command.

"""

    elif args[0] == "download_character":
        response = """

DOWNLOAD CHARACTER

    !download_character

Use this command to download your character info as a .json file.

"""

    elif args[0] == "counter":
        response = """
COUNTER

    !counter <counter name> = <max value>
    !counter <counter name> <increment>

CREATE OR UPDATE COUNTER

    !counter <counter name> = <max value>

You can create new counters using an assignment statement. A new counter will be created or an existing counter will be overwritten with a new counter that has a specified maximum value. The current value on the counter will be set to the max value. For example, to create a counter called "hitpoints" with a max value of 42, you would do the following:

    !counter hitpoints = 42

INCREMENT A COUNTER

    !counter <counter name> <increment>

To update the value of a counter, you increment it via the counter command. A counters value cannot be increased above its maximum, and it cannot be decreased below 0. An increment must begin with a "+" or a "-" followed by a number. For example, to reduce the hitpoint counter by 10, you would do the following:

    !counter hipoints -10

"""

    elif args[0] == "counters":
        response = """
COUNTERS

    !counters
    !counters <counter name>
    !counters <page>

Use the counters command to list or search for existing counters.

LIST ALL COUNTERS

    !counters

NAVIGATE RESULTS

    !counters <page>

SEARCH COUNTERS

    !counters <search string>
"""
    elif args[0] == "cast":
        response = """
CAST

    !cast <spellname>
    !cast <spellname> slot=<integer> attack=<roll name|dice roll> save=<roll name|dice roll|integer> castor=<integer|roll name>

Use the cast command to show a spell card. Some cards have automated dice rolls that use saved rolls or optional input variables.

If the following rolls are saved for your character, then they will be used automatically when casting unless you add the optional argument:
    "level" --------> castor
    "spellsave" ----> save
    "spellattack"---> attack

Here are a few examples of using the cast command with optional arguments:

    !cast fireball slot=5 save=wizardspellsave

    !cast scorchingray attack=1d20+cha+proficiency slot=5

    !cast acidsplash save=8+prof+cha castor=6

Here is an explanation of what each optional argument does:

    - slot: the spell slot at which the spell is cast.
    - castor: the level of the castor. Some spells scale based of of the players level.
    - attack: the dice roll for the spell attack.
    - save: the spell save DC for the spll attack.
    """

    else:
        response = f"Command \"{args[0]}\" not found\n" + standardHelp
    
    await ctx.send(f"```{response}```", delete_after=120.0)
    await ctx.message.delete()

# execution -----------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config['discord_token'])