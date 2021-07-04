
import json
from discord.ext import commands

# setup ---------------------------------------------------------------------------------
with open("./config.json") as f:
    config = json.load(f)

safeGet = lambda data, i: data[i] if (i < len(data) and i >= 0) else None

bot = commands.Bot(command_prefix="!")
bot.remove_command("help")
bot.load_extension("modules.commands.inventory")

@bot.event
async def on_ready():
    print("bot is ready")


# execution -----------------------------------------------------------------------------
if __name__ == "__main__":
    bot.run(config['discord_token'])