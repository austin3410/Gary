from discord.commands import user_command
import discord
from discord.commands import Option  # Importing the decorator that makes slash commands.
from discord.ext import commands
import random

class Burn(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
    
    # Loads the spongebob_burns file and randomly selects one of the lines.
    def select_burn(self):
        with open("files//spongebob_burns.txt", "r") as file:
            all_burns = file.readlines()
            burn = random.choice(all_burns)
            return burn

    # Formats a randomly selected burn and responds to the request.
    @user_command(name="Burn", help="Burns another user!")
    async def burn(self, ctx, member: Option(discord.Member, "The member you want to burn!", required=True)):
        burn = self.select_burn()

        # If someone attempts to burn Gary, they burn themselves.
        if str(member.id) == str(self.bot.id):
            burn = "You think I'm gonna burn myself?\n" + burn
            await ctx.respond(str(burn).format(ctx.author.id))
        else:
            await ctx.respond(str(burn).format(member.id))


def setup(bot):
    bot.add_cog(Burn(bot))