from discord.ext import commands
from  botcommands.utils import deleteAfter
from database.database import Database
from dice.dice_processor import DiceProcessor
import re

database: Database = None
dice: DiceProcessor = None

def setup(bot, _dice, _database):
    global database
    global dice
    dice = _dice
    database = _database
    Extension(dice, database)
    bot.add_cog(CommandCog(bot))
    
# Dice Processor plugin --------------------------------------------

class Extension:

    def __init__(self, dice:DiceProcessor, database:Database):
        self.dice = dice
        self.database = database

        # update database models with plugin specific structure
        self.database.model_player['misc']['5e_proficiency'] = {
            'proficiency': [],
            'expertise': []
        }
        self.database.model_player['rolls']['prof'] = '1'

        # add plugin specific functions to dice processor
        self.dice.functions['prof'] = get_proficiency
        

def get_proficiency(playerId, itemId):
    print(f"get_proficiency")
    player = database.get_player_by_id(int(playerId))
    bonus = player['rolls']['prof']
    if int(itemId.strip()) in player['misc']['5e_proficiency']['expertise']:
        return [str(int(bonus) * 2) ]
    elif int(itemId.strip()) in player['misc']['5e_proficiency']['proficiency']:
        return [bonus]
    return ['0']


# bot extension -------------------------------------------------

class CommandCog(commands.Cog):
    
    def __init__(self, bot):
        self.bot = bot


    @commands.command()
    async def proficiency(self, ctx, modifier):
        userId = database.get_assumed_id(ctx.author.id)
        result = re.match("\d+$", modifier)
        if result == None:
            await ctx.send(f"```Proficiency must be a positive number```", delete_after=15.0)
            await deleteAfter(ctx, 15)
            return
        player = database.get_player_by_id(userId)
        data = player['rolls']
        data['prof'] = str(modifier)
        database.update_player(userId, {'rolls': data})
        await ctx.send(f'```Proficiency bonus set to "{modifier}"```', delete_after=15.0)
        await ctx.message.delete()


    @commands.command()
    async def proficient(self, ctx, itemName):
        userId = database.get_assumed_id(ctx.author.id)
        item = database.get_item_best_match(itemName)
        player = database.get_player_by_id(userId)
        if item == None:
            await ctx.send(f'```No match for item "{itemName}"```', delete_after=15.0)
            await deleteAfter(ctx, 15)
            return
        item = item.item()
        message = self.updateProficiencyList(userId, player, 'proficiency', item)
        await ctx.send(f'```{message}```', delete_after=15.0)
        await ctx.message.delete()


    @commands.command(aliases=['expertise'])
    async def expert(self, ctx, itemName):
        userId = database.get_assumed_id(ctx.author.id)
        item = database.get_item_best_match(itemName)
        player = database.get_player_by_id(userId)
        if item == None:
            await ctx.send(f'```No match for item "{itemName}"```', delete_after=15.0)
            await deleteAfter(ctx, 15)
            return
        item = item.item()
        message = self.updateProficiencyList(userId, player, 'expertise', item)
        await ctx.send(f'```{message}```', delete_after=15.0)
        await ctx.message.delete()


    def updateProficiencyList(self, userId, player, proficiencyKey, item):
        data = player['misc']
        if item['id'] in data['5e_proficiency'][proficiencyKey]:
            print('deleting proficiency')
            data['5e_proficiency'][proficiencyKey].remove(item['id'])
            message = f"deleted {proficiencyKey} in {item['name']}"
        else:
            print('adding proficiency')
            data['5e_proficiency'][proficiencyKey].append(item['id'])
            message = f"added {proficiencyKey} in {item['name']}"
        try:
            database.update_player(userId, {'misc': data})
        except Exception as e:
            print(e)
            message = f"Failed to update {proficiencyKey}"
        return message
