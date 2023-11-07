
import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import openai
from openai import OpenAI
from discord.commands import Option
import io
import aiohttp
from PIL import Image

# This function pulls a file from memory so we can send it to Discord without saving it.
async def get_image_file(img_url):
    async with aiohttp.ClientSession() as session:
        async with session.get(img_url) as resp:
            if resp.status != 200:
                return False
            
            data = io.BytesIO(await resp.read())

            return data

# This is the class that controls how the /image previw window looks and works.
class ImageViewer(discord.ui.View):
    def __init__(self, img_url=None, timeout=None):
        super().__init__(timeout=timeout)
        self.img_url = img_url

    # This button simply sends the image to the person who clicked the button.
    @discord.ui.button(label="Save", emoji="💾", style=discord.ButtonStyle.success)
    async def save_image(self, button, interaction):
        msg = await interaction.user.send(self.img_url)
        await interaction.message.add_reaction(emoji="⭐")
        return await interaction.response.send_message(f"I've DM'd you this image!\n{msg.jump_url}", ephemeral=True)

    """# This button creates a variation of the previously created image.
    # Then creates a View loop more or less by spawning another instance of the ImageViewer View within itself...
    @discord.ui.button(label="Create Variation", emoji="🤩", style=discord.ButtonStyle.blurple)
    async def variate_image(self, button, interaction: discord.Interaction):
        # First we need to tell the user we're working on it.
        # We can't simply defer the message, otherwise we would replace the original image.
        await interaction.response.send_message(f"<@{interaction.user.id}>, creating variation...")

        # Now we get the current image URL.        
        img = await get_image_file(self.img_url)
        
        # Then we need to make it a little smaller to fit withint OpenAI's size limit of 4MB
        pilImage = Image.open(img)
        pilImage.resize((256, 256))
        img_bytes = io.BytesIO()
        pilImage.save(img_bytes, format='PNG')
        img_bytes = img_bytes.getvalue()
        img_mb = len(img_bytes) / 1024 / 1024
        if img_mb > 4:
            print(f"Can't variate, minimized image is too large at {img_mb}MB. (4MB max)")
            return await interaction.edit_original_response("Something went wrong, I couldn't generate the image. Please try again.")

        # Now we make an API request to create a variation of an image, and pass our minimized image.
        response = openai.Image.create_variation(
            image=img_bytes,
            n=1,
            size="1024x1024"
        )
        new_img_url = response["data"][0]["url"]
        
        # This converts the image into a useable format we can feed straight into Discord without first saving the file.
        data = await get_image_file(new_img_url)

        if data == False:
            return await interaction.edit_original_response("Something went wrong, I couldn't generate the image. Please try again.")
        
        # This gives the image a "file name" incase a user does actually want to download and save the image.
        filename = "varitation.png"
        file = discord.File(data, f"{filename}.png")
        
        # Here we generate the embed.
        embed = discord.Embed(title=f"{interaction.user.name}'s Image")
        embed.set_image(url=f"attachment://{filename}.png")

        # Now we edit the original response with the new (nested) view.
        response = await interaction.edit_original_response(content="", embed=embed, file=file, view=ImageViewer())
        
        # Lastly, we update the img_url variable with the new Discord CDN URL of our image variation.
        # This lets up keep creating image variations forever!
        await interaction.edit_original_response(view=ImageViewer(img_url=response.embeds[0].image.url))"""

# This class handles talking to Gary.
class AskGary(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.client = OpenAI(api_key=self.bot.openai_key, organization=self.bot.openai_orginization)
        #self.client.organization = self.bot.openai_orginization
        #elf.client.api_key = self.bot.openai_key
        #openai.orginization = self.bot.openai_orginization
        #openai.api_key = self.bot.openai_key
        

        # Adjust Gary's personality to be more or less true to the show.
        self.bot_personality = "You are Gary the snail from the TV Show SpongeBob Squarepants in a Discord server called Bikini Bottom. You're very helpful and enjoy answering everyones questions."

    # We need this function incase the response_text is longer than Discords tiny 2000/message character limit.    
    def split_response_text(self, response_text):
        
        # First we check if the response is actually over the limit.
        # If it's not, we'll just pass it as is.
        if len(response_text) > 2000:
            
            # This basically lets us remember how much of the message we've split and how much needs splitting.
            cursor_location = 0
            
            # This stores our message "chunks".
            messages = []
            
            # This runs through the response and creates smaller messages, 2000 characters at a time.
            while cursor_location < len(response_text):
                
                message_block = response_text[cursor_location:(cursor_location + 2000)]
                messages.append(message_block)
                cursor_location += 2000
            
            return messages
        else:
            return response_text

    
    # This function handles generating message blocks that get sent to ChatGPT and formating the questions/responses.
    async def generate_response(self, ctx, history=None):

        # This removes Gary's bot ID before sending it to ChatGPT.
        new_message = str(ctx.content).replace(f"<@{self.bot.id}> ", "")

        # This is the start of the message block that will inform ChatGPT of how the conversation is going so far.
        messages = [{"role": "system", "content": self.bot_personality}]

        # If history is present that means we're in an ongoing conversation.
        if history != None:

            # This is useful to remind ChatGPT of who started the conversation.
            history[0]["content"] = f"<@{history[0]['author_id']}> asks, hey Gary," + history[0]["content"]
            
            # This loops through all of the messages in the history and recreates the conversation from the beginning.
            for msg in history:

                # IF the author is Gary.
                if str(msg["author_id"]) == str(self.bot.id):

                    # We filter out Gary's automatic, "Meow." messages.
                    if msg["content"] == "Meow.":
                        pass
                    
                    # We include anything he says in the past as himself.
                    else:
                        messages.append({"role": "assistant", "content": msg["content"]})
                
                # Anything else must've come from a human (or possibly another bot.)
                else:
                    messages.append({"role": "user", "content": msg["content"], "name": str(msg['author_id'])})
            
            # Once all of the past messages are re-built, we append our new message to the message string.
            messages.append({"role": "user", "content": new_message, "name": str(ctx.author.id)})
        else:

            # If there is no history that means this is a new conversation and we need to make sure the message is formatted like a question for good results.
            messages.append({"role": "user", "content": f"<@{ctx.author.id}> asks, hey Gary," + new_message, "name": str(ctx.author.id)})

        # This is the actual request for a chat completion.
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo-16k",
                messages=messages, # This is our contructed block of past messages + our new message.
                temperature=0.9,
                max_tokens=15000,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
        except openai.error.InvalidRequestError:
            return "Sorry, I've reached my token limit. You'll need to start another conversation."
        except Exception as e:
            if "safety system" in str(e):
                return "Your prompt was rejected by the safety team. Try altering your request!"
            else:
                return "I couldn't complete the request at this time, please try again!"
        
        # The actual response text.
        response_text = response["choices"][0]["message"]["content"]
        
        # This made user ids parsable by Discord but seems to be no longer needed.
        #response_text = str(response_text).replace(str(ctx.author.id), f"<@{ctx.author.id}>")

        return response_text
    
    # The on_message hook that captures new messages and determines if they're ai chat messages.
    @commands.Cog.listener()
    async def on_message(self, ctx):

        # First and foremost, if the message is from Gary, ignore it.
        if str(ctx.author.id) != str(self.bot.id):

            # Now if the message is from a regular text channel
            if ctx.channel.type in [discord.ChannelType.text]:
                # If the message starts by @ing Gary.
                if ctx.content.startswith(f"<@{self.bot.id}>"):

                    # This is the start of a new conversation thread.
                    # Generate response text, create a thread, send the response.
                    response_text = await self.generate_response(ctx)
                    response_text = self.split_response_text(response_text)
                    thread_name = f"{ctx.author.name}'s Thread"
                    convo_thread = await ctx.create_thread(name=thread_name)
                    if isinstance(response_text, list):
                        for message in response_text:
                            await convo_thread.send(message)
                    else:
                        return await convo_thread.send(response_text)

            # If the channel is a thread, voice_text, or private/dm channel.
            if ctx.channel.type in [discord.ChannelType.public_thread, discord.ChannelType.voice, discord.ChannelType.private]:
                # If there's a reference that means the message is a reply to an earlier message, which makes this an on-going conversation.
                if ctx.reference:

                    # Since this is an on-going convo, we need to capture and rebuild the entire conversation up to this point.
                    history = []
                    target_message_id = ctx.reference.message_id
                    targeted_message = await ctx.channel.fetch_message(target_message_id)

                    # This makes sure the replied to message was a message we sent. If it's not, we'd be replying to someone elses thread... rude.
                    if str(targeted_message.author.id) != str(self.bot.id):
                        return

                    # Start typing...
                    async with ctx.channel.typing():
                        # This loop recursively bounces up the message chain to the first message and captures required data along the way.
                        while True:
                            next_hop_msg = await ctx.channel.fetch_message(target_message_id)

                            # If the next message == None, that means we're at the start of the message chain.
                            if next_hop_msg == None:
                                break
                            
                            # This captures the required info.
                            history.insert(0, {"author_name": next_hop_msg.author.name, "author_id": next_hop_msg.author.id, "content": next_hop_msg.content})

                            # This tries to queue up the next message in the chain. If it breaks that means there are no more messages and we are done.
                            try:
                                target_message_id = next_hop_msg.reference.message_id
                            except:
                                break
                            
                        # Now that we have our convo history, we can generate a response from ChatGPT.
                        response_text = await self.generate_response(ctx, history=history)
                        response_text = self.split_response_text(response_text)

                        # This replies instead of creating a thread since we're already in a thread, or the channel doesn't support a thread.
                        if isinstance(response_text, list):
                            for message in response_text:
                                await ctx.reply(message)
                        else:
                            return await ctx.reply(response_text)

                # If there's no reference, that means this is the start of a new conversation.
                # Depending on where this conversation is taking place we either NEED to be @ mentioned... or not.
                else:
                    # If Gary is @ mentioned and the channel isn't a DM, we're in a voice-text channel.
                    if ctx.content.startswith(f"<@{self.bot.id}>") and ctx.channel.type != discord.ChannelType.private:
                        # Start typing...
                        async with ctx.channel.typing():
                            response_text = await self.generate_response(ctx)
                            response_text = self.split_response_text(response_text)
                            if isinstance(response_text, list):
                                for message in response_text:
                                    await ctx.reply(message)
                            else:
                                return await ctx.reply(response_text)
                    
                    # If Gary isn't @ mentioned and it is a DM, then that's fine, we can proceed as normal. Plus we know it's not a on-going convo because it's NOT a reply.
                    elif ctx.channel.type == discord.ChannelType.private:
                        # Start typing...
                        async with ctx.channel.typing():
                            response_text = await self.generate_response(ctx)
                            response_text = self.split_response_text(response_text)
                            if isinstance(response_text, list):
                                for message in response_text:
                                    await ctx.reply(message)
                            else:
                                return await ctx.reply(response_text)

    # This is the autocomplete context for the below create_image function.
    #async def get_image_size(ctx: discord.AutocompleteContext):

    
    # This is the slash command to generate images.
    @slash_command(name="image", description="Gary will use AI to generate an image with the given prompt!")
    async def create_image(self, ctx, prompt: Option(str, description="What would you like Gary to create an image of?"), size: discord.Option(str, choices=["Square", "Portrait", "Landscape"], default="Square")):
        # We want to defer this because this operation will almost certainly take longer than 3 seconds.
        await ctx.defer()

        if size == "Square":
            size = "1024x1024"
        elif size == "Portrait":
            size = "1024x1792"
        elif size == "Landscape":
            size = "1792x1024"

        # This is the actual request that generates the image.
        # We need to put it in a try incase the prompt violates ChatGPT's rules. (nudity, gore, etc.)
        try:
            """response = openai.Image.create(
              prompt=prompt,
              n=1,
              size="1024x1024"
            )"""
            #image_url = response['data'][0]['url']
            response = self.client.images.generate(
                model="dall-e-3",
                prompt=prompt,
                size=size,
                quality="hd",
                n=1
            )
            image_url = response.data[0].url
        except Exception as e:
            if "safety system" in str(e):
                return await ctx.followup.send("Your prompt was rejected by the safety team. Try altering your request!", delete_after=30)
            else:
                print(e)
                return await ctx.followup.send("I couldn't complete the request at this time, please try again!", delete_after=30)

        # This converts the image into a useable format we can feed straight into Discord without first saving the file.
        data = await get_image_file(image_url)

        if data == False:
            return await ctx.followup.send("Something went wrong, I couldn't generate the image. Please try again.")
        
        # This gives the image a "file name" incase a user does actually want to download and save the image.
        filename = str(prompt[0:12]).replace(" ", "_")
        file = discord.File(data, f"{filename}.png")
        
        # Here we generate the embed.
        embed = discord.Embed(title=f"{ctx.author.name}'s Image")
        embed.set_image(url=f"attachment://{filename}.png")
        msg = await ctx.followup.send(embed=embed, file=file, view=ImageViewer())
        await msg.edit(view=ImageViewer(img_url=msg.embeds[0].image.url))

# Standard bot setup.
def setup(bot):
    bot.add_cog(AskGary(bot))