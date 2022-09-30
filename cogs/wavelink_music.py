import discord
from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
import wavelink
import asyncio


class Music(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.bot.wavelink = wavelink.
        self.songs = asyncio.Queue()
        self.play_next_song = asyncio.Event()
        self.bot.loop.create_task(self.connect_nodes())
    
    async def connect_nodes(self):
        await self.bot.wait_until_ready()
        
        node = await wavelink.NodePool.create_node(
            bot=self.bot,
            host='127.0.0.1',
            port=2333,
            password='SuperSecretPassword124'
        )

        node.set_hook(self.on_event_hook)

        while True:
            self.play_next_song.clear()
            song, guild_id = await self.songs.get()
            player = self.bot.wavelink.get_player(guild_id)
            await player.play(song)
            await self.play_next_song.wait()

    @commands.Cog.listener()
    async def on_ready(self):
        await self.connect_nodes()

    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        print(f"{node.identifier} is ready.")
    
    async def on_event_hook(self, event):
        if isinstance(event, (wavelink.TrackEnd, wavelink.TrackException)):
            self.play_next_song.set()

    @slash_command(name="play", description="This makes sure Gary is listening.", guild_ids=[389818215871676418])
    async def play(self, ctx, search: str):
        tracks = await self.bot.wavelink.YouTubeTrack.search(query=search, return_first=True)

        if not tracks:
            return await ctx.respond("No song found.")
        
        player = self.bot.wavelink.get_player(ctx.guild.id)
        if not player.is_connected:
            await player.connect(ctx.author.voice.channel.id)
        
        await ctx.respond(f"Playing {search}.")
        queue_item = (tracks[0], ctx.guild.id)
        await self.songs.put(queue_item)
        """vc = ctx.voice_client # define our voice client

        if not vc: # check if the bot is not in a voice channel
          vc = await ctx.author.voice.channel.connect(cls=wavelink.Player) # connect to the voice channel

        if ctx.author.voice.channel.id != vc.channel.id: # check if the bot is not in the voice channel
          return await ctx.respond("You must be in the same voice channel as the bot.") # return an error message

        song = await wavelink.YouTubeTrack.search(query=search, return_first=True) # search for the song

        if not song: # check if the song is not found
          return await ctx.respond("No song found.") # return an error message

        self.queue.put(song)
        
        await vc.play(song) # play the song
        await ctx.respond(f"Now playing: `{vc.source.title}`") # return a message"""

# Standard bot setup.
def setup(bot):
    bot.add_cog(Music(bot))