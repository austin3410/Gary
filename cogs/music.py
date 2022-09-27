from sqlite3 import connect
import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import wavelink


class Music(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
    
    async def connect_nodes(self):
        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host='127.0.0.1',
            port=2333,
            password='SuperSecretPassword124'
        )

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_nodes()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node.identifier} is ready.")

    @slash_command(name="play", description="This makes sure Gary is listening.", guild_ids=[389818215871676418])
    async def play(self, ctx, search: str):
        vc = ctx.voice_client # define our voice client

        if not vc: # check if the bot is not in a voice channel
          vc = await ctx.author.voice.channel.connect(cls=wavelink.Player) # connect to the voice channel

        if ctx.author.voice.channel.id != vc.channel.id: # check if the bot is not in the voice channel
          return await ctx.respond("You must be in the same voice channel as the bot.") # return an error message

        song = await wavelink.YouTubeTrack.search(query=search, return_first=True) # search for the song

        if not song: # check if the song is not found
          return await ctx.respond("No song found.") # return an error message

        await vc.play(song) # play the song
        await ctx.respond(f"Now playing: `{vc.source.title}`") # return a message

# Standard bot setup.
def setup(bot):
    bot.add_cog(Music(bot))