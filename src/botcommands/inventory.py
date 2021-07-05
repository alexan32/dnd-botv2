# commands related to inventory management

from discord.ext import commands
import database.database as database

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def inventory(self, ctx):
        player = database.get_player_by_id(int(ctx.author.id))
        print(player)


    @commands.command()
    async def give(self, ctx):    
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return


    @commands.command()
    async def drop(self, ctx):
        await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
        return

def setup(bot):
    bot.add_cog(CommandCog(bot))
