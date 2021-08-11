# commands relating to bot configuration and admin tasks

import discord
from discord.ext import commands
import botcommands.handler as handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def addPlayer(self, ctx):
    #     response = handler.setup()
    #     await ctx.send(f"```{response}```", delete_after=15.0)
    #     await ctx.message.delete()
    #     return


    @commands.command()
    async def myid(self, ctx):
        await ctx.send(f"```{ctx.author.id}```", delete_after=15.0)
        await ctx.message.delete()
        return


def setup(bot):
    bot.add_cog(CommandCog(bot))
