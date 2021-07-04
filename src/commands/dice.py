# commands relating to dice rolling, saved dice rolls

from discord.ext import commands
import service.database as database

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def roll(self, ctx, arg1=None):
        if arg1 == None:
            await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
            return

    @commands.command()
    async def save(self, ctx):    
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return


    @commands.command()
    async def erase(self, ctx):
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return


def setup(bot):
    bot.add_cog(CommandCog(bot))