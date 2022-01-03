from discord.commands import slash_command, user_command, message_command
import discord
from discord.commands.commands import Option  # Importing the decorator that makes slash commands.
from discord.ext import commands
from discord.ext.commands.core import command, cooldown


class Burn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @user_command(name="Burn", guild_ids=[389818215871676418], description="Burns another user!")
    #@cooldown(1, 30)
    async def burn(self, ctx, member: Option(discord.Member, "The member you want to burn!", required=True)):
        await ctx.delete()
        await ctx.channel.send(f"<@{member.id}>, you're a barnacle head!")


def setup(bot):
    bot.add_cog(Burn(bot))