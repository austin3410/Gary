import discord
from discord import ButtonStyle
from discord.ui import View, button, Item
from discord.commands import slash_command, Option
from discord.ext import commands
from serpapi import GoogleSearch
from random import randint

class Gif(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot

    @slash_command(name="gif", description="A better version of GIF search using Google.")
    async def gif(self, ctx, query: Option(str, description="GIF search query.", required=True)):

        class GifSelection(View):
            def __init__(self, *items: Item, timeout: float = 180, images_results):
                super().__init__(*items, timeout=timeout)
                self.selected_image = None
                self.max_image_index = len(images_results) - 1
                self.images = images_results
                self.current_image_index = 0
                self.current_image = self.images[self.current_image_index]["original"]
                    
            
            @button(custom_id="first", style=ButtonStyle.blurple, emoji="⏮")
            async def first_result(self, button: discord.Button, interaction: discord.Interaction):
                next_image = discord.Embed()
                next_image.set_image(url=self.images[0]["original"])
                self.current_image_index = 0
                await interaction.response.edit_message(embed=next_image, view=self)
            
            @button(custom_id="previous", style=ButtonStyle.blurple, emoji="◀")
            async def prev_result(self, button: discord.Button, interaction: discord.Interaction):
                next_image = discord.Embed()
                next_image.set_image(url=self.images[self.current_image_index - 1]["original"])
                self.current_image_index -= 1
                await interaction.response.edit_message(embed=next_image, view=self)
            
            @button(custom_id="select", style=ButtonStyle.blurple, emoji="✅")
            async def select_result(self, button: discord.Button, interaction: discord.Interaction):
                selected_image = discord.Embed()
                selected_image.set_image(url=self.images[self.current_image_index]["original"])
                await interaction.channel.send(content=f"{interaction.user.name} sent:", embed=selected_image)
                self.clear_items()
                await interaction.response.edit_message(content="I've sent your GIF.", embed=None, view=self)
                self.stop()
            
            @button(custom_id="next", style=ButtonStyle.blurple, emoji="▶")
            async def next_result(self, button: discord.Button, interaction: discord.Interaction):
                next_image = discord.Embed()
                if self.current_image_index == self.max_image_index:
                    self.current_image_index = 0
                else:
                    self.current_image_index += 1
                
                next_image.set_image(url=self.images[self.current_image_index]["original"])
                await interaction.response.edit_message(embed=next_image, view=self)
            
            @button(custom_id="last", style=ButtonStyle.blurple, emoji="⏭")
            async def last_result(self, button: discord.Button, interaction: discord.Interaction):
                next_image = discord.Embed()
                next_image.set_image(url=self.images[self.max_image_index]["original"])
                self.current_image_index = self.max_image_index
                await interaction.response.edit_message(embed=next_image, view=self)

            @button(label="First", disabled=True)
            async def blank1(self, button, interaction):
                pass
            @button(label="Prev", disabled=True)
            async def blank2(self, button, interaction):
                pass
            
            @button(custom_id="random", style=ButtonStyle.blurple, emoji="🎱")
            async def random_result(self, button: discord.Button, interaction: discord.Interaction):
                selected_image = discord.Embed()
                random_index = randint(0, self.max_image_index)
                selected_image.set_image(url=self.images[random_index]["original"])
                await interaction.channel.send(content=f"{interaction.user.name} randomly sent:", embed=selected_image)
                self.clear_items()
                await interaction.response.edit_message(content="I've sent your GIF.", embed=None, view=self)
                self.stop()
            
            @button(label="Next", disabled=True)
            async def blank3(self, button, interaction):
                pass
            
            @button(label="Last", disabled=True)
            async def blank4(self, button, interaction):
                pass

        params = {
            "api_key": self.bot.serpapi_key,
            "engine": "google",
            "ijn": "0",
            "q": query,
            "google_domain": "google.com",
            "tbm": "isch",
            "tbs": "itp:animated"
        }

        await ctx.defer(ephemeral=True)
        search = GoogleSearch(params)
        results = search.get_dict()
        
        gf = GifSelection(images_results=results["images_results"])
        first_result = discord.Embed()
        first_result.set_image(url=results["images_results"][0]["original"])
        await ctx.followup.send(embed=first_result, view=gf)

        await gf.wait()

# Standard bot setup.
def setup(bot):
    bot.add_cog(Gif(bot))