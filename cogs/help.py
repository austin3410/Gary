from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
from discord.ext.commands.core import command, cooldown
from discord.ext.commands.errors import PrivateMessageOnly
from discord.ext.commands.help import HelpCommand


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="help", guild_ids=[389818215871676418], description="Use this to learn about Gary!")
    #@cooldown(1, 30)
    async def help(self, ctx):
        help = HelpCommand()
        for cog_name in self.bot.cogs:
            cog = self.bot.get_cog(cog_name)
            for c in cog.get_commands():
                print(vars(c))
        await ctx.respond(help.send_bot_help())


def setup(bot):
    bot.add_cog(Help(bot))