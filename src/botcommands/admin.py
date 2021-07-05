# commands relating to dice rolling, saved dice rolls
import discord
from discord.ext import commands
import botcommands.handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def identity(self, ctx, *args):
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return

    @commands.command()
    async def admin(self, ctx, *args):
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return

def setup(bot):
    bot.add_cog(CommandCog(bot))
