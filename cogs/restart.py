import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
from math import floor


class Restart(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot

    # READ BEFORE USE!!!!
    # This simply quits the python process all together and relies on an outside system to restart it. I prefer cron but anything will do.
    @slash_command(name="restart", description="This restarts Gary.")
    async def restart(self, ctx):
        await ctx.respond(f"Restarting.. this can take up to 2 minutes.", ephemeral=True)
        quit()

# Standard bot setup.
def setup(bot):
    bot.add_cog(Restart(bot))