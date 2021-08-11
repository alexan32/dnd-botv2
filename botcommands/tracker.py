# commands related to spell slots and hit point tracking

from discord.ext import commands


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def tracker(self, ctx):
        pass


def setup(bot):
    bot.add_cog(CommandCog(bot))
