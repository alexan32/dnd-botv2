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
    async def roll(self, ctx, *args):
        _type, output = parseInput(args)
        if _type == 'get':
            print('get')
            response = handler.handler(ctx, 'roll_dice', output)
        elif _type == 'set':
            print('get')
            response = handler.handler(ctx, 'save_dice', output[0], output[1])
        else:
            print('err')
            response = output
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


    @commands.command()
    async def rolls(self, ctx, *args):
        if len(args) > 1:
            searchString = "".join(args)
            response = handler.handler(ctx, 'search_dice', searchString)
        if len(args) == 1:
            if args[0].isdigit():
                response = handler.handler(ctx, 'list_dice', int(args[0])-1)
            else:
                response = handler.handler(ctx, 'search_dice', args[0])
        else:
            response = handler.handler(ctx, 'list_dice', 0)
        await ctx.send(f"```{response}```", delete_after=60.0)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(CommandCog(bot))
