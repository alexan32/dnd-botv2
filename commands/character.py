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
    async def create_character(self, ctx, firstName, lastName):
        response = handler.handler(ctx, 'create_character', firstName, lastName)
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(CommandCog(bot))
