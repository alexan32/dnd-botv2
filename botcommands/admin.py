# commands relating to bot configuration and admin tasks
from botcommands.utils import deleteAfter
import os
import json
import discord
from discord.ext import commands
import botcommands.handler as handler

script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)

class CommandCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def register_server(self, ctx):
        success, response = handler.handler(ctx, 'register_server')
        if success:
            response += await setup_server(ctx)
        await ctx.send(f"```{response}```")
        await ctx.message.delete()


    @commands.command()
    async def context(self, ctx):
        response = f"channel: {ctx.channel.name}\nchannel id: {ctx.channel.id}\nchannel type: {ctx.channel.type}\nid: {ctx.author.id}\n"
        response += f"guild: {ctx.author.guild}\nguild id: {ctx.guild.id}\nuser:{ctx.author.name}\nnickname:{ctx.author.nick}\n"
        response += f"display name: {ctx.author.display_name}\nguild permissions:{ctx.author.guild_permissions}\nroles: {ctx.author.roles}\n"
        response += f"top_role: {ctx.author.top_role}\ncolor: {ctx.author.color}"
        response += f"\nguild owner: {ctx.guild.owner_id}"
        await ctx.send(f"```{response}```", delete_after=20.0)
        await deleteAfter(ctx, 20.0)


    @commands.command(aliases=['cd'])
    async def change_directory(self, ctx, path):
        directory, cwd = handler.handler(ctx, 'change_directory', path)
        response = directory_response(directory, cwd)
        await ctx.send(f"```{response}```", delete_after=60.0)
        await deleteAfter(ctx, 60.0)


    @commands.command(aliases=['ls'])
    async def list_directory(self, ctx):
        directory, cwd = handler.handler(ctx, 'list_directory')
        response = directory_response(directory, cwd)
        await ctx.send(f"```{response}```", delete_after=60.0)
        await deleteAfter(ctx, 60.0)
    

    @commands.command(aliases=['mkdir'])
    async def make_directory(self, ctx, directory_name):
        directory, cwd = handler.handler(ctx, 'make_directory', directory_name)


async def setup_server(ctx):
    guild = ctx.guild
    member = ctx.message.author
    gm = await guild.create_role(name=config['adminRoles'][0])
    await member.add_roles(gm)
    return f"\nGave {ctx.author.display_name} the {config['adminRoles'][0]} role"


def directory_response(directory:dict, cwd:str):
    response = f"{cwd}\n" + "\n".rjust(30, "=")
    dicts = []
    other = []
    for key in directory:
        if type(directory) is list:
            for item in directory:
                other.append(f"- {item}")
        elif type(directory[key]) is dict:
            dicts.append(f"/{key}")
        elif type(directory[key]) is list:
            if len(directory[key]) == 0:
                other.append(f"{key}: []")
            else:
                other.append(f"{key}: [ {directory[key][0]}, ...]")
        elif type(directory[key]) is str:
            other.append(f"{key}: {directory[key]}")
    for line in dicts:
        response += f"{line}\n"
    for line in other:
        response += f"{line}\n"

    return response


def setup(bot):
    bot.add_cog(CommandCog(bot))
