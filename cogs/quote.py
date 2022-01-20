from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import random

class Quote(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # Pretty simple command that just opens a file, randomly picks and line and sends it. Nothing too complicated.
    @slash_command(name="quote", description="This sends a random quote from SpongeBob!")
    async def quote(self, ctx):
        with open("files//spongebob_quotes.txt", "r") as file:
            quotes = file.read().splitlines()
            
        while True:
            quote = random.choice(quotes)
            if quote == "" or quote == " ":
                pass
            else:
                return await ctx.respond(quote)
    
    # I decided to remove the quote_add and quote_dump commands just cause no one used them... oh well.

def setup(bot):
    bot.add_cog(Quote(bot))