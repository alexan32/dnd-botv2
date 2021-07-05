import importlib.util
import json
import os
from discord.ext import commands

script_dir = os.path.dirname(__file__)

with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
bot.load_extension("botcommands.admin")
bot.load_extension("botcommands.dice")
bot.load_extension("botcommands.inventory")
bot.load_extension("botcommands.tracker")


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
    print("bot is ready")


# execution -----------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config['discord_token'])