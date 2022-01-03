from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
from discord.ext.commands.core import command, cooldown
from discord.ext.commands.help import HelpCommand


class Ping(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="ping", guild_ids=[389818215871676418], description="This makes sure Gary is listening.")
    #@cooldown(1, 30)
    async def ping(self, ctx):
        return await ctx.respond(":ping_pong:")


def setup(bot):
    bot.add_cog(Ping(bot))