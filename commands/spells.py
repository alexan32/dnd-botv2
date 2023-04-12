# commands relating to bot configuration and admin tasks
from commands.utils import deleteAfter, parseInput
import os
import json
from discord.ext import commands
import commands.handler as handler


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def cast(self, ctx, *args):
        _input = "".join(args)
        print(_input)


        # response = handler.handler(ctx, "cast")

        await ctx.send(f"```yo```", delete_after=5.0)
        await ctx.message.delete()

        

async def setup(bot):
    bot.add_cog(CommandCog(bot))
