# commands relating to bot configuration and admin tasks
from commands.utils import deleteAfter, parseInput
import os
import json
from discord.ext import commands
import commands.handler as handler


script_dir = os.path.dirname(__file__)
with open(os.path.join(script_dir, "../config.json")) as f:
    config = json.load(f)


class CounterCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.command()
    async def counter(self, ctx, *args):
        _input = "".join(args)

        # !counter <counter name> <increment>
        if _input.count("=") == 0:
            if len(args) == 2:
                counterName = args[0]
                increment = args[1]
                if increment.startswith('+') or increment.startswith('-'):
                    increment = increment[1:] if increment.startswith('+') else increment
                    try:
                        increment = int(increment)
                    except:
                        response = f"Invalid increment \"{increment}\". Increments must be whole numbers."
                    else:
                        response = handler.handler(ctx, "increment_counter",  counterName, increment)
                else:
                    response = f"Invalid increment \"{increment}\". Increments must start with a \"+\" or \"-\"."
            else:
                response = f"Missing required args. Expected \"!counter <counter name> <increment>\""

        # !counter <counter name> = <max>
        elif _input.count("=") == 1:
            values = _input.split("=")
            counterName = values[0]
            _max = values[1]
            if not _max.isdigit():
                response = f"Invalid parameter \"{_max}\". Max value must be a whole number."
            else:
                print(f"save counter {counterName} {_max}")
                response = handler.handler(ctx, "save_counter", counterName, _max)
        else:
            print("invalid args")

        await ctx.send(f"```{response}```")
        await ctx.message.delete()


    @commands.command()
    async def counters(self, ctx, *args):
        if len(args) > 1:
            searchString = "".join(args)
            response = handler.handler(ctx, 'search_counters', searchString)
        if len(args) == 1:
            if args[0].isdigit():
                response = handler.handler(ctx, 'list_counters', int(args[0])-1)
            else:
                response = handler.handler(ctx, 'search_counters', args[0])
        else:
            response = handler.handler(ctx, 'list_counters', 0)
        await ctx.send(f"```{response}```", delete_after=60.0)
        await ctx.message.delete()
        

async def setup(bot):
    await bot.add_cog(CounterCog(bot))
