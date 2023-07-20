
import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import openai
from discord.commands import Option
import io
import aiohttp

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
    def __init__(self, img_url, timeout=None):
        super().__init__(timeout=timeout)
        self.img_url = img_url
    
    # Disabled for now because OpenAI's docs suck.
    """async def modal_callback(self, interaction):
        #revision_prompt = interaction.data["components"][0]["components"][0]["value"]
        og_image_url = interaction.message.embeds[0].image.url
        print(og_image_url)

        response = openai.Image.create_variation(
          image=og_image_url,
          n=1,
          size="1024x1024"
        )
        image_url = response['data'][0]['url']

        data = await get_image_file(image_url)

        if data == False:
            return await interaction.response.send_message("Something went wrong, I couldn't generate the image. Please try again.")
        
        interaction_thread = await interaction.message.create_thread(name="Revised Images:")

        #filename = str(revision_prompt[0:12]).replace(" ", "_")
        filename = "revised_photo"
        file = discord.File(data, f"{filename}.png")
        
        embed = discord.Embed(title=f"{interaction.user.name}'s Image")
        embed.set_image(url=f"attachment://{filename}.png")
        await interaction_thread.send(embed=embed, file=file)

        self.stop()"""

        

    # This button simply sends the image to the person who clicked the button.
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

        

        print(modal_return)
        print(modal.to_dict())"""

# This class handles talking to Gary.
class AskGary(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        openai.orginization = self.bot.openai_orginization
        openai.api_key = self.bot.openai_key

        # Adjust Gary's personality to be more or less true to the show.
        self.bot_personality = "You are Gary the snail from the TV Show SpongeBob Squarepants in a Discord server called Bikini Bottom. You're very helpful and enjoy answering everyones questions."
        
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
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages, # This is our contructed block of past messages + our new message.
                temperature=0.9,
                max_tokens=3000,
                top_p=1,
                frequency_penalty=0.0,
                presence_penalty=0.0
            )
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
                    thread_name = f"{ctx.author.name}'s Thread"
                    convo_thread = await ctx.create_thread(name=thread_name)
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

                        # This replies instead of creating a thread since we're already in a thread, or the channel doesn't support a thread.
                        return await ctx.reply(response_text)

                # If there's no reference, that means this is the start of a new conversation.
                # Depending on where this conversation is taking place we either NEED to be @ mentioned... or not.
                else:
                    # If Gary is @ mentioned and the channel isn't a DM, we're in a voice-text channel.
                    if ctx.content.startswith(f"<@{self.bot.id}>") and ctx.channel.type != discord.ChannelType.private:
                        # Start typing...
                        async with ctx.channel.typing():
                            response_text = await self.generate_response(ctx)
                            return await ctx.reply(response_text)
                    
                    # If Gary isn't @ mentioned and it is a DM, then that's fine, we can proceed as normal. Plus we know it's not a on-going convo because it's NOT a reply.
                    elif ctx.channel.type == discord.ChannelType.private:
                        # Start typing...
                        async with ctx.channel.typing():
                            response_text = await self.generate_response(ctx)
                            return await ctx.reply(response_text)

    # This is the slash command to generate images.
    @slash_command(name="image", description="Gary will use AI to generate an image with the given prompt!")
    async def create_image(self, ctx, prompt: Option(str, description="What would you like Gary to create an image of?")):
        # We want to defer this because this operation will almost certainly take longer than 3 seconds.
        await ctx.defer()

        # This is the actual request that generates the image.
        # We need to put it in a try incase the prompt violates ChatGPT's rules. (nudity, gore, etc.)
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
        msg = await ctx.followup.send(embed=embed, file=file)
        await msg.edit(view=ImageViewer(img_url=msg.embeds[0].image.url))

# Standard bot setup.
def setup(bot):
    bot.add_cog(AskGary(bot))