
import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import openai
from discord.commands import Option
import io
import aiohttp

async def get_image_file(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            if resp.status != 200:
                return False
            
            data = io.BytesIO(await resp.read())

            return data

class ImageViewer(discord.ui.View):
    def __init__(self, img_url, timeout=None):
        super().__init__(timeout=timeout)
        self.img_url = img_url
    
    # Disabled for now because OpenAI's docs suck.
    """async def modal_callback(self, interaction):
        revision_prompt = interaction.data["components"][0]["components"][0]["value"]
        og_image_url = interaction.message.embeds[0].image.url

        response = openai.Image.create_edit(
          prompt=revision_prompt,
          image="https://i.imgur.com/qq80w2f.jpeg",
          n=1,
          size="1024x1024",
          mask=""
        )
        image_url = response['data'][0]['url']

        data = await get_image_file(image_url)

        if data == False:
            return await interaction.response.send_message("Something went wrong, I couldn't generate the image. Please try again.")
        
        interaction_thread = await interaction.message.create_thread(name="Revised Images:")

        filename = str(revision_prompt[0:12]).replace(" ", "_")
        file = discord.File(data, f"{filename}.png")
        
        embed = discord.Embed(title=f"{interaction.user.name}'s Image")
        embed.set_image(url=f"attachment://{filename}.png")
        await interaction_thread.send(embed=embed, file=file)

        self.stop()"""

        

    
    @discord.ui.button(label="Save", emoji="💾", style=discord.ButtonStyle.success)
    async def save_image(self, button, interaction):
        
        msg = await interaction.user.send(self.img_url)
        await interaction.message.add_reaction(emoji="⭐")
        return await interaction.response.send_message(f"I've DM'd you this image!\n{msg.jump_url}", ephemeral=True)
        
    # Disabled for now because OpenAI's docs suck.
    """@discord.ui.button(label="Revise", emoji="🤩", style=discord.ButtonStyle.blurple)
    async def revise_image(self, button, interaction: discord.Interaction):

        modal = discord.ui.Modal(title="Revise an Image...")
        modal.add_item(discord.ui.InputText(label="Revision Prompt", placeholder="What would you like to add or change?", min_length=1, required=True))
        modal.callback = self.modal_callback

        await interaction.response.send_modal(modal=modal)
        modal_return = await modal.wait()

        

        #print(modal_return)
        #print(modal.to_dict())"""

class AskGary(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        openai.orginization = self.bot.openai_orginization
        openai.api_key = self.bot.openai_key
    
    #@commands.Cog.listener()
    #async def on_ready(self):
    #    self.bot.add_view(ImageViewer())
    
    # This decorator and function fires everytime a message is sent that @'s Gary.
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.content.startswith(f"<@{self.bot.id}>"):
            async with ctx.channel.typing():
                question = str(ctx.content).replace("<@704812476184788992>", "")
                question = f"{ctx.author.name} asks, hey Gary," + question
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
                response_text = str(response_text).replace(f"{ctx.author.name}", f"<@{ctx.author.id}>")
                
                return await ctx.reply(f'{response_text}')


    
    @slash_command(name="image", description="Gary will use AI to generate an image with the given prompt!")
    async def create_image(self, ctx, prompt: Option(str, description="What would you like Gary to create an image of?")):
        await ctx.defer()
        try:
            response = openai.Image.create(
              prompt=prompt,
              n=1,
              size="1024x1024"
            )
            image_url = response['data'][0]['url']
        except Exception as e:
            if "safety system" in str(e):
                return await ctx.followup.send("Your prompt was rejected by the safety team. Try altering your request!", delete_after=30)
            else:
                return await ctx.followup.send("I couldn't complete the request at this time, please try again!", delete_after=30)

        data = await get_image_file(image_url)

        if data == False:
            return await ctx.followup.send("Something went wrong, I couldn't generate the image. Please try again.")
        
        filename = str(prompt[0:12]).replace(" ", "_")
        file = discord.File(data, f"{filename}.png")
        
        embed = discord.Embed(title=f"{ctx.author.name}'s Image")
        embed.set_image(url=f"attachment://{filename}.png")
        msg = await ctx.followup.send(embed=embed, file=file)
        await msg.edit(view=ImageViewer(img_url=msg.embeds[0].image.url))

# Standard bot setup.
def setup(bot):
    bot.add_cog(AskGary(bot))