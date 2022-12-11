
import os
import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import openai
from discord.commands import Option
import requests

class ImageViewer(discord.ui.View):
    def __init__(self, img_url, timeout=None):
        super().__init__(timeout=timeout)
        self.img_url = img_url
    
    @discord.ui.button(label="Save", emoji="💾", style=discord.ButtonStyle.success)
    async def save_image(self, button, interaction):
        #await interaction.user.send(self.img_url)
        r = requests.get(self.img_url)

        with open(f"files//ai_images//{interaction.user.id}.png",'wb') as f:
            f.write(r.content)
        with open(f"files//ai_images//{interaction.user.id}.png", "rb") as f:
            pic = discord.File(f)
            await interaction.user.send(file=pic)
        await interaction.response.send_message(f"I've sent you this image!", ephemeral=True)
        os.remove(f"files//ai_images//{interaction.user.id}.png")
    
    """@discord.ui.Button(label="Revise", emoji="🤩", style=discord.ButtonStyle.blurple)
    async def revise_image(self, button, interaction: discord.Interaction):
        await interaction.response.defer()
        response = openai.Image.create(
          prompt=prompt,
          n=1,
          size="1024x1024"
        )
        image_url = response['data'][0]['url']"""

class AskGary(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        openai.orginization = self.bot.openai_orginization
        openai.api_key = self.bot.openai_key
    
    # This decorator and function fires everytime a message is sent that @'s Gary.
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.content.startswith(f"<@{self.bot.id}>"):
            async with ctx.channel.typing():
                question = ctx.content.replace(f"<@!{self.bot.id}>", "")
                response = openai.Completion.create(
                    model="text-davinci-003",
                    prompt=question,
                    temperature=0.9,
                    max_tokens=4000,
                    top_p=1,
                    frequency_penalty=0.0,
                    presence_penalty=0.0
                )
                response_text = response["choices"][0]["text"]
                print(response)
            
            await ctx.channel.send(f'<@{ctx.author.id}> {response_text}')
    
    @slash_command(name="image", description="Gary will use AI to generate an image with the given prompt!")
    async def create_image(self, ctx, prompt: Option(str, description="What would you like Gary to create an image of?")):
        await ctx.defer()
        response = openai.Image.create(
          prompt=prompt,
          n=1,
          size="1024x1024"
        )
        image_url = response['data'][0]['url']
        
        embed = discord.Embed(title=f"{ctx.author.name}'s Image")
        embed.set_image(url=image_url)
        await ctx.followup.send(embed=embed, view=ImageViewer(img_url=str(image_url)))

# Standard bot setup.
def setup(bot):
    bot.add_cog(AskGary(bot))