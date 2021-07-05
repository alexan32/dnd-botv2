from discord.ext import commands

# back end extension -----------------------------------------------

class Extension:

    def __init__(self, diceParser, database):
        self.diceParser = diceParser
        self.database = database
        diceParser.functions['get_proficiency'] = self.get_proficiency
        

    def get_proficiency(self, playerId, itemId):
        player = self.database.get_player_by_id(playerId)
        proficient = itemId in player['']


def init_plugin(diceParser, database):
    extension = Extension(diceParser, database)


# bot extension -------------------------------------------------

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def proficiency(self, ctx, arg1=None):
        if arg1 == None:
            await ctx.send(f"```Missing required argument. See help for more details.```", delete_after=15.0)
            return

def setup(bot):
    bot.add_cog(CommandCog(bot))