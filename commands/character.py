# commands relating to bot configuration and admin tasks
from commands.utils import deleteAfter, parseInput
import os
import json
from discord.ext import commands
import commands.handler as handler
from discord import File
import requests


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def create_character(self, ctx, firstName, lastName):
        response = handler.handler(ctx, 'create_character', firstName, lastName)
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


    @commands.command()
    async def download_character(self, ctx):
        character = handler.handler(ctx, 'get_character')
        print(character)
        fileName = f"{character['first']}-{character['last']}.json"
        f = open(fileName, 'w')
        f.write(json.dumps(character))
        f.close()
        f = open(fileName, 'r')
        await ctx.send(file=File(f), delete_after=60.0)
        await ctx.message.delete()
        f.close()
        os.remove(fileName)


    @commands.command()
    async def upload_character(self, ctx):
        try:
            attachment_url = ctx.message.attachments[0].url
            file_request = requests.get(attachment_url)
            contents = json.loads(file_request.content.decode("utf-8"))
        except Exception as e:
            print(e)
            await ctx.send(f"```Failed to process file. Make sure that you attach a valid character file before sending.```", delete_after=60.0)
            await ctx.message.delete()
        else:
            print(contents)
            response = handler.handler(ctx, "put_character", contents)
            await ctx.send(f"```{response}```", delete_after=60.0)
            await ctx.message.delete()


def setup(bot):
    bot.add_cog(CommandCog(bot))
