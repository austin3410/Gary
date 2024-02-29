from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
from math import floor


class Ping(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ping", description="This makes sure Gary is listening.")
    async def ping(self, ctx):
        # Multiplies the float value of the bots latency bu 1000 to get a whole number.
        latency = floor(self.bot.latency * 1000)
        return await ctx.respond(f":ping_pong: at {latency}ms ping.")

# Standard bot setup.
def setup(bot):
    bot.add_cog(Ping(bot))