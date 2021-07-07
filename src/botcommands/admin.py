# commands relating to bot configuration and admin tasks

import discord
from discord.ext import commands
import botcommands.handler as handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    # @commands.command()
    # async def identity(self, ctx, *args):
    #     await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
    #     return

    # @commands.command()
    # async def admin(self, ctx, *args):
    #     await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
    #     return


    @commands.command()
    async def setup(self, ctx):
        response = handler.setup()
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()
        return


    @commands.command()
    async def myid(self, ctx):
        await ctx.send(f"```{ctx.author.id}```", delete_after=15.0)
        await ctx.message.delete()
        return


def setup(bot):
    bot.add_cog(CommandCog(bot))
