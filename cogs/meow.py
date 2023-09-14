from discord.ext import commands

class Meow(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message):
        if str(message.author.id) != str(self.bot.id) and not str(message.content).startswith(f"<@{self.bot.id}>"):
            nicknames = ["GARY", "GARE", "GARE BEAR", self.bot.id]
            if [name for name in nicknames if name in message.content.upper()]:
                return await message.channel.send("Meow.")
                

def setup(bot):
    bot.add_cog(Meow(bot))