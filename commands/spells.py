# commands relating to bot configuration and admin tasks
from commands.utils import deleteAfter, cleanInput, sendMessage
import os
import json
from discord.ext import commands
import commands.handler as handler
import re

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


class SpellCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cast(self, ctx, *args):
        _input = cleanInput("".join(args))
        print(_input)
        _list = re.split("(slot=)|(attack=)|(castor=)|(save=)", _input)
        _list = list(filter(lambda x: x !=None, _list))
        print(_list)

        # castSpell(spell:dict, slotLevel:int, castingInfo:dict, rollsLibrary={}, attackRoll="1d20", spellSave="8", characterLevel="1")
        spellName = _list[0]
        slotLevel = None
        attackRoll= None
        spellSave = None
        characterLevel = None
        
        x=1
        while x < len(_list):
            word = _list[x]
            if word == "slot=":
                slotLevel = int(_list[x+1])
                x+=2
                continue
            elif word == "attack=":
                attackRoll = _list[x+1]
                x+=2
                continue
            elif word == "save=":
                spellSave = _list[x+1]
                x+=2
                continue
            elif word == "castor=":
                characterLevel = _list[x+1]
                x+=2
                continue
            else:
                print(f"Invalid expression for \"cast\" command: {_input} \"{_list[x]}\"")
                break

        try:
            results = handler.handler(ctx, "cast", spellName, slotLevel, attackRoll, spellSave, characterLevel)
        except Exception as e:
            print(e)
            await ctx.send(f"```Sorry! We messed up. Tell that asshole Seth to check the logs.```")
            return
        
        await sendMessage(ctx, f"{results[0]}", delete_after=120.0)
        for result in results[1:]:
            await ctx.send(f"```{result}```")
        await ctx.message.delete()

        

async def setup(bot):
    await bot.add_cog(SpellCog(bot))
