## dnd-botv2

A simple discord bot to handle dice rolls and character info for table top games.

The bot supports a single character per member on a discord server. You cannot have more than 1 character in a server, and you cannot access the same character data on other servers that use the bot.

To set up on your machine, clone a fork. Add a "config.json" in the project root with the following values:

```
{
    "discord_token": "your discord bot token",
    "ruleset": "pathfinder2e"
}
```

"ruleset" is used to point to the default character data for creating a new character. Currently ruleset must be set to "pathfinder2e" or "dnd5e". You can add json documents to the database/models folder to add more options.
