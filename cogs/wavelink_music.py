from discord.commands import slash_command, Option # Importing the decorator that makes slash commands.
from discord.ext import commands
import discord
import asyncio
from typing import cast
import wavelink
from random import uniform


class PlayerControl(discord.ui.View):
                def __init__(self, vc: wavelink.Player):
                    super().__init__(timeout=None)
                    self.vc = vc
                    if self.vc._autoplay == wavelink.AutoPlayMode.enabled:
                        self.radio_mode = discord.ButtonStyle.success
                    else:
                        self.radio_mode = discord.ButtonStyle.gray
                
                @discord.ui.button(label="Play/Pause", emoji="⏯", style=discord.ButtonStyle.blurple)
                async def toggle_playback_callback(self, button, interaction):
                    if self.vc._paused:
                        await self.vc.pause(False)
                        await interaction.response.send_message(f"{interaction.user.name} resumed the music.", delete_after=5)
                    else:
                        await self.vc.pause(True)
                        await interaction.response.send_message(f"{interaction.user.name} paused the music.", delete_after=5)
                
                @discord.ui.button(label="Skip", emoji="⏩", style=discord.ButtonStyle.blurple)
                async def skip_callback(self, button, interaction):
                    await self.vc.skip()
                    await interaction.response.send_message(f"{interaction.user.name} skipped the current song.", delete_after=5)
                
                @discord.ui.button(label="Stop", emoji="⏹", style=discord.ButtonStyle.blurple)
                async def stop_callback(self, button, interaction):
                    self.vc.queue.clear()
                    await self.vc.stop()
                    self.vc.autoplay = wavelink.AutoPlayMode.partial
                    await self.vc.disconnect()
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
                
                @discord.ui.button(label="Radio Mode", emoji="📻", style=discord.ButtonStyle.gray)
                async def radio_callback(self, button, interaction):

                    if self.vc._autoplay == wavelink.AutoPlayMode.partial:
                        self.vc.autoplay = wavelink.AutoPlayMode.enabled
                        button.style = discord.ButtonStyle.success
                        await interaction.response.edit_message(view=self)
                    elif self.vc._autoplay == wavelink.AutoPlayMode.enabled:
                        self.vc.autoplay = wavelink.AutoPlayMode.partial
                        button.style = discord.ButtonStyle.gray
                        await interaction.response.edit_message(view=self)
                        
                
                """filter_options = [
                    discord.SelectOption(label="Default Mix", value="Default 1 1 1"),
                    discord.SelectOption(label="Nightcore", value="Nightcore 1.2 1.2 1"),
                    discord.SelectOption(label="Lo-fi", value="Lo-fi .6 .9 1"),
                    discord.SelectOption(label="Random", value="Random"),
                ]
                
                @discord.ui.select(placeholder="Default Mix", options=filter_options)
                async def set_filter(self, select, interaction):
                    new_filter = select.values[0].split(" ")
                    if new_filter[0] == "Random":
                        p = uniform(.4, 1.5)
                        s = uniform(.4, 1.5)
                        new_filter.append(p)
                        new_filter.append(s)
                        new_filter.append(1)
                        print(new_filter)
                    filters: wavelink.Filters = self.vc.filters
                    filters.timescale.set(pitch=new_filter[1], speed=new_filter[2], rate=new_filter[3])
                    await self.vc.set_filters(filters)
                    await interaction.response.send_message(f"{interaction.user.name} set the filter to {new_filter[0]}.", delete_after=10)"""

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
                    await self.vc.set_volume(int(new_volume))
                    await interaction.response.send_message(f"{interaction.user.name} adjusted the volume to {new_volume}%.", delete_after=5)

class Music(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.player = None
        self.player_control = None
        self.player_control_msg = None
    
    @commands.Cog.listener()
    async def on_ready(self):
        nodes = wavelink.Node(uri="http://127.0.0.1:2333", password="youshallnotpass124",)
        await wavelink.Pool.connect(nodes=[nodes], client=self.bot)
        print("Connected to Wavelink!")
        for channel in self.bot.get_all_channels():
            #print(channel.name)
            if channel.name == "music_requests":
                self.mr_channel = channel
                break
    
    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: discord.Embed = discord.Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += f"\n\n`This track was recommended via {track.source}`"

        if track.album.name:
            embed.add_field(name="Album", value=track.album.name)

        if self.player_control_msg == None and self.player_control == None:
            self.player_control = PlayerControl(vc=player)
            self.player_control_msg = await self.mr_channel.send(embed=embed, view=self.player_control)
        else:
            print("Editing player_control_msg")
            await self.player_control_msg.edit(embed=embed, view=self.player_control)

        await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{track.title}"))

    # This triggers when a track finishes playing (whether it finishes naturally, or is stopped early).
    @commands.Cog.listener()
    async def on_wavelink_track_end(self, payload: wavelink.TrackEndEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return
        
        if player._autoplay == wavelink.AutoPlayMode.enabled:
            return
        
        if player.queue.is_empty and not player.playing:
            await self.player_control_msg.delete()
            self.player = None
            self.player_control = None
            self.player_control_msg = None
            await self.bot.change_presence(status=discord.Status.online)
            await asyncio.sleep(1)
            await player.disconnect()
        return

    @commands.Cog.listener()
    async def on_wavelink_track_exception(self, payload: wavelink.TrackEndEventPayload) -> None:
        print("TRACK EXCEPTION")
    
    @commands.Cog.listener()
    async def on_wavelink_track_stuck(self, payload: wavelink.TrackEndEventPayload) -> None:
        print("TRACK STUCK")
    
    @commands.Cog.listener()
    async def on_wavelink_websocket_closed(self, payload: wavelink.TrackEndEventPayload) -> None:
        print("WEBSOCKET CLOSED")
    
    @commands.Cog.listener()
    async def on_wavelink_node_closed(self, payload: wavelink.TrackEndEventPayload) -> None:
        print("NODE CLOSED")
    
    @commands.Cog.listener()
    async def on_wavelink_extra_event(self, payload: wavelink.TrackEndEventPayload) -> None:
        print("EXTRA EVENT")
    
    
    async def create_player(self, ctx):
        if not ctx.guild:
            return
    
        player: wavelink.Player
        player = cast(wavelink.Player, ctx.voice_client)  # type: ignore
    
        if not player:
            try:
                player = await ctx.author.voice.channel.connect(cls=wavelink.Player)  # type: ignore
            except AttributeError:
                await ctx.respond("Please join a voice channel first before using this command.")
                return
            except discord.ClientException:
                await ctx.respond("I was unable to join this voice channel. Please try again.")
                return
    
        # Turn on AutoPlay to enabled mode.
        # enabled = AutoPlay will play songs for us and fetch recommendations...
        # partial = AutoPlay will play songs for us, but WILL NOT fetch recommendations...
        # disabled = AutoPlay will do nothing...
        player.autoplay = wavelink.AutoPlayMode.partial
    
        # Lock the player to this channel...
        #if not hasattr(player, "Kelp Forest"):
        #    player.home = ctx.channel
        #elif player.home != ctx.channel:
        #    await ctx.send(f"You can only play songs in {player.home.mention}, as the player has already started there.")
        #    return
    
        # This will handle fetching Tracks and Playlists...
        # Seed the doc strings for more information on this method...
        # If spotify is enabled via LavaSrc, this will automatically fetch Spotify tracks if you pass a URL...
        # Defaults to YouTube for non URL based queries...

        return player
    
    @slash_command(name="play", description="Play a song.")
    async def play(self, ctx, query: Option(str, description="Song name or YouTube URL.")):
        """Play a song with the given query."""
        await ctx.defer()
        
        if self.player == None:
            self.player = await self.create_player(ctx)
        
        tracks: wavelink.Search = await wavelink.Playable.search(query)
        if not tracks:
            await ctx.respond(f"{ctx.author.mention} - Could not find any tracks with that query. Please try again.", delete_after=10)
            return
        if isinstance(tracks, wavelink.Playlist):
            # tracks is a playlist...
            added: int = await self.player.queue.put_wait(tracks)
            await ctx.respond(f"Added the playlist **`{tracks.name}`** ({added} songs) to the queue.", delete_after=10)
        else:
            track: wavelink.Playable = tracks[0]
            await self.player.queue.put_wait(track)
            await ctx.respond(f"Added **`{track}`** to the queue.", delete_after=10)
        if not self.player.playing:
            # Play now since we aren't playing anything...
            await self.player.play(self.player.queue.get(), volume=50)

# Standard bot setup.
def setup(bot):
    bot.add_cog(Music(bot))