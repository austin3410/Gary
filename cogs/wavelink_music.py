import discord
from discord.commands import slash_command, Option  # Importing the decorator that makes slash commands.
from discord.ext import commands
import wavelink

# This represents the Discord View which acts as the media controller. (Where the buttons live)
class PlayerControl(discord.ui.View):
                def __init__(self, vc: wavelink.Player):
                    super().__init__(timeout=None)
                    self.vc = vc
                    print("[WaveLink] PlayerControl initialized.")
                
                @discord.ui.button(label="Play/Pause", emoji="⏯", style=discord.ButtonStyle.blurple)
                async def toggle_playback_callback(self, button, interaction):
                    if self.vc.is_paused():
                        await self.vc.resume()
                        await interaction.response.send_message(f"{interaction.user.name} resumed the music.", delete_after=5)
                    else:
                        await self.vc.pause()
                        await interaction.response.send_message(f"{interaction.user.name} paused the music.", delete_after=5)
                
                @discord.ui.button(label="Skip", emoji="⏩", style=discord.ButtonStyle.blurple)
                async def skip_callback(self, button, interaction):
                    await self.message.delete()
                    await self.vc.stop()
                    await interaction.response.send_message(f"{interaction.user.name} skipped the current song.", delete_after=5)
                    self.stop()
                
                @discord.ui.button(label="Stop", emoji="⏹", style=discord.ButtonStyle.blurple)
                async def stop_callback(self, button, interaction):
                    await self.message.delete()
                    self.vc.queue.clear()
                    await self.vc.stop()
                    await interaction.response.send_message(f"{interaction.user.name} stopped the music.", delete_after=5)
                    self.stop()
                
                @discord.ui.button(label="Queue", emoji="📃", style=discord.ButtonStyle.blurple)
                async def queue_callback(self, button, interaction):
                    
                    queue_msg = ""
                    if not self.vc.queue.is_empty:
                        for song in self.vc.queue:
                            if song == self.vc.queue[0]:

                                queue_msg += f"Coming up next:\n``{song}``\n\n"

                                if len(self.vc.queue) > 1:

                                    queue_msg += f"After that:\n"
                            
                            else:
                                queue_msg += f"``{song}``\n"
                    else:
                        queue_msg += "There's nothing in queue! Use /play to add something!"

                    return await interaction.response.send_message(queue_msg, delete_after=15)
                
                vol_options = [
                    discord.SelectOption(label="Volume 100"),
                    discord.SelectOption(label="Volume 75"),
                    discord.SelectOption(label="Volume 50"),
                    discord.SelectOption(label="Volume 25"),
                    discord.SelectOption(label="Volume 10")
                ]

                @discord.ui.select(placeholder="Volume 100", options=vol_options)
                async def vol_callback(self, select, interaction):
                    new_volume = str(select.values[0]).split(" ")[1]
                    await self.vc.set_volume(volume=(int(new_volume) / 100))
                    await interaction.response.send_message(f"{interaction.user.name} adjusted the volume to {new_volume}%.", delete_after=5)

class Music(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        # self.vc stands for voice_client. This is the input which Gary plays through Discord.
        self.vc = None
        # self.np stands for now_playing. This is will always be an instance of the PlayerControl class.
        self.np = None
        # self.mr_channel stands for music_requests_channel. This is the channel messages should be sent to.
        self.mr_channel = None
        
    
    @commands.Cog.listener()
    async def on_ready(self):
        for channel in self.bot.get_all_channels():
            #print(channel.name)
            if channel.name == "music_requests":
                self.mr_channel = channel
                await self.create_node()
                print("[WaveLink] Node created, mr_channel found.")
                break
        
        if self.mr_channel == None:
            print("No 'music_requests' channel exists. Music plugin won't work.")
        
    # Created the Wavelink Node and connects to the Lavelink Server.
    async def create_node(self):

        await self.bot.wait_until_ready()

        await wavelink.NodePool.create_node(
            bot=self.bot,
            host="127.0.0.1",
            port=2333,
            password="SuperSecretPassword124"
        )
    
    @commands.Cog.listener()
    async def on_wavelink_node_ready(self, node: wavelink.Node):
        self.node = node
        print(f"Wavelink Node connected and ready!")
    
    # This function creates self.vc and actually connects Gary to a voice channel.
    async def connect(self, ctx):
        if self.vc == None:
            try:
                channel = ctx.author.voice.channel
            except Exception as e:
                await ctx.respond("Are you sure you're in a channel?", ephemeral=True)
                return None

            vc: wavelink.Player = await channel.connect(cls=wavelink.Player)
            self.vc = vc
        else:
            vc = self.vc

        print("[WaveLink] VC created/found and returned.")
        return vc
    
    # This determines whether a song should be played immediately or put into the queue.
    async def play_song(self, song: wavelink.YouTubeTrack):
        print("[WaveLink] STARTING play_song")
        if self.vc == None:
            return print("Can't play song. Self doesn't contain a voice_client.")

        if self.vc.is_playing() == True or self.vc.is_paused() == True:
            print("[WaveLink] Song placed in queue.")
            self.vc.queue.put(song)
            print(self.vc.queue)
            return
        
        if self.vc.queue.is_empty:
            print("[WaveLink] Song played immediately.")
            return await self.vc.play(song)
        
        print("[WaveLink] play_song END PLAYING SONG")
        return await self.vc.play(song)
    
    # This triggers when a track finishes playing (whether it finishes naturally, or is stopped early).
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track: wavelink.Track, reason):
        print("[WaveLink] TRACK END!")
        print(self.vc.queue)
        print("[WaveLink] STARTING TRACK END WORK!")
        # If the queue isn't empty, get the next song and play it.
        if not self.vc.queue.is_empty:
            next_song = self.vc.queue.get()
            print(f"[WaveLink] NEXT TRACK: {next_song.info}!")
            await self.play_song(next_song)
            print("[WaveLink] PLAYING NEXT!")
            return
        
        # If the queue is empty, clear the playing status, disconnect from the channel and clear self.vc.
        else:
            # This is a safety cleanup action to make sure the PlayerControl gets deleted.
            try:
                await self.np.delete()
            except:
                pass
            await self.bot.change_presence(status=discord.Status.online)
            await self.vc.disconnect()
            self.vc = None
            print("[WaveLink] DISCONNECTING!")
            return
        
        print("[WaveLink] NOTHING!")

    # This triggers when a track starts playing.
    # This sets Gary's status, then generates and sends the PlayerControl class.
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, player: wavelink.Player, track: wavelink.YouTubeTrack):
        print("[WaveLink] TRACK START")
        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{track.title}"))
        embed = discord.Embed(title=track.title, color=0x00ff00)
        embed.set_image(url=f"http://img.youtube.com/vi/{track.identifier}/0.jpg")
        self.np = await self.mr_channel.send(embed=embed, view=PlayerControl(vc=self.vc))
    
    # The actual /play command.
    @slash_command(name="play", description="Play a song.")
    async def play(self, ctx, search: Option(str, description="Song name or YouTube URL.")):

        await ctx.defer()

        if ctx.channel.name != self.mr_channel.name:
            return await ctx.respond("Send music requests to #music_requests.", ephemeral=True)

        song = await wavelink.YouTubeTrack.search(query=search, return_first=True)

        vc = await self.connect(ctx)
        if vc == None:
            return
        if vc.channel != ctx.author.voice.channel:
            return await ctx.respond("You must be in the same channel as Gary!", ephemeral=True)
        else:
            await self.play_song(song)
            print("[WaveLink] Song played/added to queue.")
            return await ctx.respond(f"Adding `{song.title}` to the queue.", delete_after=5)
    
# Standard bot setup.
def setup(bot):
    bot.add_cog(Music(bot))