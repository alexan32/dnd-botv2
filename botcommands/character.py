# commands related to spell slots and hit point tracking

from discord.ext import commands
import botcommands.handler as handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['createCharacter', 'characterCreate', 'create_character'])
    async def register(self, ctx, first, last):
        response = handler.handler(ctx, 'create_character', first.lower(), last.lower())
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()

    @commands.command(aliases=['selectCharacter', 'select_character'])
    async def character(self, ctx, first):
        response = handler.handler(ctx, 'select_character', first.lower())
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()

    @commands.command(aliases=['characterList', 'listCharacters'])
    async def characters(self, ctx):
        response = handler.handler(ctx, 'list_characters')
        await ctx.send(f"```{response}```", delete_after=20.0)
        await ctx.message.delete()

    @commands.command()
    async def deleteCharacter(self, ctx, first):
        response = handler.handler(ctx, 'delete_character', first.lower())
        await ctx.send(f"```{response}```", delete_after=25.0)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(CommandCog(bot))
