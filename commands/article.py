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
    async def article(self, ctx, *args):
        _type, output = parseInput(args)
        if _type == 'get':
            print('get')
            response = handler.handler(ctx, 'get_article', output)
        elif _type == 'set':
            print('set')
            response = handler.handler(ctx, 'set_article', output[0], output[1])
        else:
            print('err')
            response = output
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(CommandCog(bot))
