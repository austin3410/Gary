import discord
from discord.commands import slash_command, message_command
from discord.commands import Option  # Importing the decorator that makes slash commands.
from discord.ext import commands
from random import random, randint
import os
import datetime

# This is needed to check the current time.
epoch = datetime.datetime.utcfromtimestamp(0)

class Mock(commands.Cog):

    def __init__(self, bot):
        self.bot = bot

    # 3rd party function that seeds a string to randomly capitalize it.
    def to_spongecase(self, orig, cap_chance=0.5):
        '''
        Returns a version of the given string that has randomly mixed case,
        in the style of the Mocking Spongebob meme. The capitalization
        pattern is consistent for a given string and capitalization chance.

        The capitalization chance is a number in the range [0.0, 1.0]. If a
        value outside these bounds is provided then this function will behave
        as though it had been clamped to the bounds. If no capitalization
        chance is given, it defaults to 50%.

        See also: http://knowyourmeme.com/memes/mocking-spongebob

        PARAM orig :: the original string, to be converted into sponge-caps
        PARAM cap_chance :: the percentage chance that any give letter will
        be capitalized

        RETURNS :: the spongecased version of the original string
        '''

        orig = str(orig)
        if len(orig) <= 1:
            return (orig.upper() if (random() < cap_chance) else orig.lower())
        else:

            spongecase = []
            for ch in orig:
                case_choice = random() < cap_chance
                spongecase.append(ch.upper() if (case_choice) else ch.lower())

            return ''.join(spongecase)

    # This function checks to see how long it's been since the last auto mock.
    def check_time(self, epoch):
        if os.path.isfile("files//mock_time.txt"):
            with open("files//mock_time.txt", "r") as file:
                last_time = float(file.read())

            time_diff = (datetime.datetime.utcnow() - epoch).total_seconds() - last_time
            #print(f"last_time: {last_time}\ntime_diff: {time_diff}\nepoch: {epoch}")
            
            # This ensures an auto mock will only occur every 5 minutes.
            if time_diff >= 300:
                new_time = (datetime.datetime.utcnow() - epoch).total_seconds()
                with open("files//mock_time.txt", "w") as file:
                    file.write(str(new_time))

                return True
            else:
                return False
        else:
            new_time = (datetime.datetime.utcnow() - epoch).total_seconds()
            with open("files//mock_time.txt", "w") as file:
                file.write(str(new_time))

    # MOCK slash command
    @slash_command(name="mock", description="This converts a sentence to SpongeBob Mock case.")
    async def mock(self, ctx, sentence: Option(str, "Enter any sentence", required=True)):
        if sentence == " " or sentence == "":
            raise Exception("is a required argument that is missing")
        final = self.to_spongecase(sentence)
        await ctx.respond(final)
    
    # MOCK message command
    @message_command(name="Mock Sentence", help="This converts a previously sent message to SpongeBob Mock case.")
    async def Mock(self, ctx, message: discord.Message):
        if message.content == " " or message.content == "":
            raise Exception("is a required argument that is missing")
        final = self.to_spongecase(message.content)
        await ctx.respond(final)

    # AUTO MOCK
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if "https://" in str(ctx.content) or "www" in str(ctx.content):
            return
        if str(ctx.author.id) != str(self.bot.id) and not ctx.author.bot:
            x = randint(1, 100)
            if x == 69:
                time_check = self.check_time(epoch)
                if time_check == True:
                    final = self.to_spongecase(ctx.content)
                    await ctx.channel.send(final)

def setup(bot):
    bot.add_cog(Mock(bot))

