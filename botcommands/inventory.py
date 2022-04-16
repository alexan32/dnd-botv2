# commands related to inventory management

from discord.ext import commands
import botcommands.handler as handler

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command(aliases=['listInventory'])
    async def inventory(self, ctx):
        response = handler.handler(ctx, 'inventory')
        await ctx.send(f"```{response}```", delete_after=60.0)
        await ctx.message.delete()


    @commands.command()
    async def drop(self, ctx, quantity, itemName):
        response = handler.handler(ctx, 'drop', item=itemName, count=int(quantity))
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()


    @commands.command()
    async def give(self, ctx, recipientName, quantity, itemName):
        response = handler.handler(ctx, 'give', recipient=recipientName.lower(), item=itemName, count=int(quantity))
        await ctx.send(f"```{response}```", delete_after=15.0)
        await ctx.message.delete()

def setup(bot):
    bot.add_cog(CommandCog(bot))
