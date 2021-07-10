# commands relating to dice rolling, saved dice rolls

from discord.ext import commands
from botcommands.utils import deleteAfter
import botcommands.handler as handler


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
            return
        elif len(args) == 1:
            diceString = args[0]
        else:
            diceString = ' '.join(args)

        response = handler.handler(ctx, 'roll', diceString)
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


    @commands.command()
    async def save(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
            return
        elif len(args) == 1:
            diceString = args[0]
        else:
            diceString = ' '.join(args)

        newArgs = diceString.split('=')
        if len(newArgs) != 2:
            await ctx.send(f"```Invalid save string. Expected something like 'acrobatics = 1d20 + dex' ```", delete_after=15.0)
            await deleteAfter(ctx, 15)
            
        response = handler.handler(ctx, 'save', *newArgs)
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()


    @commands.command()
    async def erase(self, ctx, *args):
        if len(args) == 0:
            await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
            return
        elif len(args) == 1:
            key = args[0]
        else:
            key = ' '.join(args)
        response = handler.handler(ctx, 'erase', key)
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()


    @commands.command(aliases=['rolls'])
    async def list(self, ctx, *args):
        response = handler.handler(ctx, 'list')
        await ctx.send(f"```{response}```", delete_after=60.0)
        await ctx.message.delete()


def setup(bot):
    bot.add_cog(CommandCog(bot))