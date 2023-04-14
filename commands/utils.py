import asyncio
from difflib import SequenceMatcher
from database import database
import dice.dice_processor as dp

dice = dp.DiceProcessor()

# deletes the command message after a number of seconds has passed
async def deleteAfter(ctx, seconds):
    await asyncio.sleep(seconds)
    await ctx.message.delete()


# breaks messages apart if they are too large for the send message api to handle
async def sendMessage(ctx, formattedResponse, **kwargs):
    if len(formattedResponse) > 2000:
        words = iter(formattedResponse.split(" "))
        lines, current = [], next(words)
        for word in words:
            if len(current) + 1 + len(word) > 1990:
                lines.append(current + "...")
                current = word
            else:
                current += " " + word
        lines.append(current)
        for line in lines:
            await ctx.send(f"```{line}```", **kwargs)
    else:
        await ctx.send(f"```{formattedResponse}```", **kwargs)


def roll(ctx, input):
    character = database.get_user_character(ctx.author.id, ctx.guild.id)
    rolls = character["rolls"]

    print(f"input string: {input}")
    if input in rolls:
        diceString = rolls[input]
    else:
        diceString = input
    print(f"diceString: {diceString}")
    return dice.processString(diceString, rolls)
    

def parseInput(args:list):
    sentence = "".join(args)
    # input is key, fetch value
    if sentence.count("=") == 0:
        key = "".join(sentence.split(" ")).lower()
        return "get", key
    # input is assignement, set value
    elif sentence.count("=") == 1:
        asList = sentence.split("=")
        key = "".join(asList[0].split(" ")).lower()
        value = asList[1]
        return "set", (key, value)
    # invalid input
    else:
        return "err", f"Invalid statement \"{sentence}\". Assignment statments must include only one \"=\"."

def cleanInput(input:str):
    input = input.lower()
    for x in [" ", "'", "\""]:
        input = "".join(input.split(x))
    return input

def paginateDict(dictionary: dict):
    keys = sorted(list(dictionary.keys()))
    print(f"total keys: {len(keys)}")
    pages = []
    processed = 0
    message = ""
    for key in keys:
        line = f"{key}".ljust(25, ".") + f" {dictionary[key]}\n"
        if len(message) + len(line) >= 800:
            pages.append(message)
            message = ""
        message += line
        processed += 1
    if message != "":
        pages.append(message)
    return pages


def similarity(a, b):
    sim = SequenceMatcher(None, a, b).ratio()
    return sim