# commands related to spell slots and hit point tracking

from discord.ext import commands
import botcommands.handler as handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register(self, ctx, first, last):
        response = handler.handler(ctx, 'register', first, last)
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()


    @commands.command()
    async def unregister(self, ctx):
        response = handler.handler(ctx, 'unregister')
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(CommandCog(bot))
