import importlib.util
import json
import os
from botcommands.utils import deleteAfter
from discord.ext import commands
from dice.dice_processor import DiceProcessorError

script_dir = os.path.dirname(__file__)

with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
bot.load_extension("botcommands.admin")
bot.load_extension("botcommands.dice")
bot.load_extension("botcommands.inventory")
bot.load_extension("botcommands.tracker")
bot.load_extension("botcommands.character")


print("\ninitializing discord bot extensions...\n")
for plugin in config['plugins']:
    spec = importlib.util.spec_from_file_location(plugin, os.path.join(script_dir, f"../plugins/{plugin}.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    try:
        mod.setup(bot)
    except AttributeError as e:
        print(f"* plugin '{plugin}' had no setup function and will be skipped.")
    else:
        print(f"* loaded '{plugin}'")
print('done\n')


@bot.event
async def on_ready():
    print("bot is ready\n" + ''.ljust(20, '='))


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, commands.CommandNotFound) or isinstance(error, DiceProcessorError):
        print(error)
        await ctx.send(f"""```{error}```""", delete_after=20.0)
        await deleteAfter(ctx, 20.0)
    elif isinstance(error, commands.MissingRequiredArgument):
        print(error)
        await ctx.send(f"""```{error}. type !help for more details```""", delete_after=20.0)
        await deleteAfter(ctx, 20.0)
    else:
        print(error)
        await ctx.send(f"```An unhandled exception occurred```", delete_after=20.0)
        await deleteAfter(ctx, 20.0)


# execution -----------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config['discord_token'])