import json
import os
import commands.handler
from commands.utils import deleteAfter
from discord.ext import commands


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "config.json")) as f:
    config = json.load(f)


bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
bot.load_extension("commands.character")
bot.load_extension("commands.roll")


@bot.event
async def on_ready():
    print("bot is ready\n" + ''.ljust(20, '='))


# @bot.event
# async def on_command_error(ctx, error):
#     if isinstance(error, commands.CommandNotFound):
#         print(error)
#         await ctx.send(f"""```{error}```""", delete_after=20.0)
#         await deleteAfter(ctx, 20.0)
#     elif isinstance(error, commands.MissingRequiredArgument):
#         print(error)
#         await ctx.send(f"""```{error}. type !help for more details```""", delete_after=20.0)
#         await deleteAfter(ctx, 20.0)
#     else:
#         raise error
    #     print(error)
    #     await ctx.send(f"```An unhandled exception occurred```", delete_after=20.0)
    #     await deleteAfter(ctx, 20.0)


# execution -----------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config['discord_token'])