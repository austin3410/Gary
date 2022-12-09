from discord.ext import commands
from random import randint
from requests import request

class Yesno(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
    
    # This is the function that actually uses Giphy's API to search for a gif on a random page.
    def get_gif(self, arg):
        url = f"http://api.giphy.com/v1/gifs/search?api_key={self.bot.gif_token}&limit=10&lang=en&fmt=json&offset={randint(1,100)}&q={arg}"
        r = request("GET", url)
        if r.status_code == 200:
            r = r.json()
            gif = r["data"][0]["bitly_gif_url"]
            return gif
        else:
            # If something goes wrong and the request failed this will log what happened and returns nothing so the command still functions.
            print(f"[YESNO] Something went wrong with the GIF search:\n{r.text}")
            return ""

    # This decorator and function fires everytime a message is sent that @'s Gary.
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.content.startswith(f"<@!{self.bot.id}>"):
            """try:

                # This should be all or at least most of the words that start a question.
                valid_kwords = ["DID", "SHOULD", "WILL", "CAN", "ARE", "IS", "AM", "CAN'T", "CANT", "COULD", "DOES", "HAS", "HAVE", "WERE", "WOULD", "DO"]
                m = str(ctx.content).split(" ")
                kword = m[1]

                # Checks to see if the first word of the message contains any of the valid_keywords.
                # If not, it's probably not a question.
                if kword.upper() in valid_kwords:
                    x = randint(1,101)
                    if x < 50:
                        gif = self.get_gif("yes")
                        await ctx.channel.send(f"YES!\n{str(gif)}")
                    elif x >= 50 and x <= 90:
                        gif = self.get_gif("no")
                        await ctx.channel.send(f"NO!\n{str(gif)}")
                    elif x >= 91:
                        gif = self.get_gif("i don't care")
                        await ctx.channel.send(f"¯\_(ツ)_/¯\nI DON'T CARE!\n{str(gif)}")
            except:
                pass"""
            
            r = request("GET", "https://api.openai.com/v1/completions", headers=headers, params=)

# Standard bot setup.
def setup(bot):
    bot.add_cog(Yesno(bot))