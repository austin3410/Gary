"""
Please understand Music bots are complex, and that even this basic example can be daunting to a beginner.
For this reason it's highly advised you familiarize yourself with discord.py, python and asyncio, BEFORE
you attempt to write a music bot.
This example makes use of: Python 3.6
For a more basic voice example please read:
    https://github.com/Rapptz/discord.py/blob/rewrite/examples/basic_voice.py
This is a very basic playlist example, which allows per guild playback of unique queues.
The commands implement very basic logic for basic usage. But allow for expansion. It would be advisable to implement
your own permissions and usage logic for commands.
e.g You might like to implement a vote before skipping the song or only allow admins to stop the player.
Music bots require lots of work, and tuning. Goodluck.
If you find any bugs feel free to ping me on discord. @Eviee#0666
"""

import discord
from discord.ext import commands

from discord.commands import slash_command  # Importing the decorator that makes slash commands.
from discord.commands import Option
from discord.ui import View, Button, Select

import asyncio
import itertools
import sys
import traceback
from async_timeout import timeout
from functools import partial
from youtube_dl import YoutubeDL


ytdlopts = {
    'format': 'bestaudio/best',
    'outtmpl': 'downloads/%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0'  # ipv6 addresses cause issues sometimes
}

ffmpegopts = {
    'before_options': '-nostdin -reconnect 1 -reconnect_streamed 1 -reconnect_delay_max 1',
    'options': '-vn'
}

ytdl = YoutubeDL(ytdlopts)

class VoiceConnectionError(commands.CommandError):
    """Custom Exception class for connection errors."""


class InvalidVoiceChannel(VoiceConnectionError):
    """Exception for cases of invalid Voice Channels."""

class YTDLSource(discord.PCMVolumeTransformer):

    def __init__(self, source, *, data, requester):
        super().__init__(source)
        self.requester = requester

        self.title = data.get('title')
        self.web_url = data.get('webpage_url')
        self.thumbnail = data.get('thumbnail')

        # YTDL info dicts (data) have other useful information you might want
        # https://github.com/rg3/youtube-dl/blob/master/README.md

    def __getitem__(self, item: str):
        """Allows us to access attributes similar to a dict.
        This is only useful when you are NOT downloading.
        """
        return self.__getattribute__(item)

    @classmethod
    async def create_source(cls, ctx, search: str, *, loop, download=False):
        loop = loop or asyncio.get_event_loop()

        to_run = partial(ytdl.extract_info, url=search, download=download)
        data = await loop.run_in_executor(None, to_run)

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        embed = discord.Embed(title=data["title"], url=data["webpage_url"])
        embed.set_author(name=f"Song Requested By: {ctx.author.name}")

        await ctx.send(embed=embed, delete_after=15)

        if download:
            source = ytdl.prepare_filename(data)
        else:
            return {'webpage_url': data['webpage_url'], 'requester': ctx.author, 'title': data['title']}

        return cls(discord.FFmpegPCMAudio(source), data=data, requester=ctx.author)

    @classmethod
    async def regather_stream(cls, data, *, loop):
        """Used for preparing a stream, instead of downloading.
        Since Youtube Streaming links expire."""
        loop = loop or asyncio.get_event_loop()
        requester = data['requester']
        to_run = partial(ytdl.extract_info, url=data['webpage_url'], download=False)
        data = await loop.run_in_executor(None, to_run)
        
        return cls(discord.FFmpegPCMAudio(data['url']), data=data, requester=requester)


class MusicPlayer:
    """A class which is assigned to each guild using the bot for Music.
    This class implements a queue and loop, which allows for different guilds to listen to different playlists
    simultaneously.
    When the bot disconnects from the Voice it's instance will be destroyed.
    """

    __slots__ = ('bot', '_guild', '_channel', '_cog', 'queue', 'next', 'current', 'np', 'volume', 'skip_count',
                 'skippers')

    def __init__(self, ctx):
        self.bot = ctx.bot
        self._guild = ctx.guild
        self._channel = ctx.channel
        self._cog = ctx.cog

        self.queue = asyncio.Queue()
        self.next = asyncio.Event()

        self.np = None  # Now playing message
        self.volume = .5
        self.current = None

        ctx.bot.loop.create_task(self.player_loop())

    async def player_loop(self):
        """Our main player loop."""
        await self.bot.wait_until_ready()

        while not self.bot.is_closed():
            self.next.clear()

            try:
                # Wait for the next song. If we timeout cancel the player and disconnect...
                async with timeout(300):  # 300 seconds (5 minutes)
                    source = await self.queue.get()
            except asyncio.TimeoutError as e:
                if str(e) == None or str(e) == "":
                    pass
                else:
                    print("Generated an asyncio.exceptions.TimeoutError within def player_loop():")
                    print(e)
                return self.destroy(self._guild)
            
            try:
                if source["custom"]:
                    og_title = source["title"]
            except:
                pass

            if not isinstance(source, YTDLSource):
                # Source was probably a stream (not downloaded)
                # So we should regather to prevent stream expiration
                try:
                    source = await YTDLSource.regather_stream(source, loop=self.bot.loop)
                except Exception as e:
                        await self._channel.send(f'There was an error processing your song.\n'
                                                 f'```css\n[{e}]\n```')
                        continue
            
            try:
                if og_title:
                    source.title = og_title
            except:
                pass

            source.volume = self.volume
            self.current = source

            self._guild.voice_client.play(source, after=lambda _: self.bot.loop.call_soon_threadsafe(self.next.set))

            embed = discord.Embed(title=f"Requested by: {source.requester}", color=0x00ff00)
            if source.thumbnail:
                embed.set_image(url=source.thumbnail)

            embed.set_author(name=source.title)

            class PlayerControl(discord.ui.View):
                def __init__(self, guild, destroy):
                    super().__init__(timeout=None)
                    self._guild = guild
                    self.destroy = destroy
                
                @discord.ui.button(label="Play/Pause", emoji="⏯", style=discord.ButtonStyle.blurple)
                async def toggle_playback_callback(self, button, interaction):
                    if self._guild.voice_client.is_playing():
                        self._guild.voice_client.pause()
                        await interaction.response.send_message(f"{interaction.user.name} paused the music.", delete_after=5)
                    else:
                        self._guild.voice_client.resume()
                        await interaction.response.send_message(f"{interaction.user.name} resumed the music.", delete_after=5)
                
                @discord.ui.button(label="Skip", emoji="⏩", style=discord.ButtonStyle.blurple)
                async def skip_callback(self, button, interaction):
                    self._guild.voice_client.stop()
                    await interaction.response.send_message(f"{interaction.user.name} skipped the current song.", delete_after=5)
                
                @discord.ui.button(label="Stop", emoji="⏹", style=discord.ButtonStyle.blurple)
                async def stop_callback(self, button, interaction):
                    await self._guild.voice_client.disconnect()
                    await interaction.response.send_message(f"{interaction.user.name} stopped the music.", delete_after=5)
                    self.destroy(self._guild)
                
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
                    self._guild.voice_client.source.volume = int(new_volume) / 100
                    await interaction.response.send_message(f"{interaction.user.name} adjusted the volume to {new_volume}.", delete_after=5)




            self.np = await self._channel.send(embed=embed, view=PlayerControl(guild=self._guild, destroy=self.destroy))
            await self.bot.change_presence(status=discord.Status.online, activity=discord.Game(name=f"{source.title}"))
            await self.next.wait()

            # Make sure the FFmpeg process is cleaned up.
            source.cleanup()
            self.current = None

            try:
                # We are no longer playing this song...
                await self.np.delete()
            except discord.HTTPException:
                pass

    def destroy(self, guild):
        """Disconnect and cleanup the player."""
        return self.bot.loop.create_task(self._cog.cleanup(guild))


class Music(commands.Cog):
    """Music related commands."""

    __slots__ = ('bot', 'players')

    def __init__(self, bot):
        self.bot = bot
        self.players = {}

    async def channel_check(self, ctx):
        if str(ctx.channel.name) != "music_requests":
            await ctx.send("Please submit music requests in the #music_requests channel!", delete_after=10)
            await ctx.message.delete()
            return False
        else:
            return True

    async def cleanup(self, guild):
        try:
            await guild.voice_client.disconnect()
            await self.bot.change_presence(status=discord.Status.online)

        except AttributeError:
            pass

        try:
            del self.players[guild.id]
        except KeyError:
            pass

    async def __local_check(self, ctx):
        """A local check which applies to all commands in this cog."""
        if not ctx.guild:
            raise commands.NoPrivateMessage
        return True

    async def __error(self, ctx, error):
        """A local error handler for all errors arising from commands in this cog."""
        if isinstance(error, commands.NoPrivateMessage):
            try:
                return await ctx.send('This command can not be used in Private Messages.')
            except discord.HTTPException:
                pass
        elif isinstance(error, InvalidVoiceChannel):
            await ctx.send('Error connecting to Voice Channel. '
                           'Please make sure you are in a valid channel or provide me with one')

        print('Ignoring exception in command {}:'.format(ctx.command), file=sys.stderr)
        traceback.print_exception(type(error), error, error.__traceback__, file=sys.stderr)

    def get_player(self, ctx):
        """Retrieve the guild player, or generate one."""
        try:
            player = self.players[ctx.guild.id]
        except KeyError:
            player = MusicPlayer(ctx)
            self.players[ctx.guild.id] = player
            player.skip_count = 0
            player.skippers = []

        return player

    #@slash_command(name="summon", description="Joins Gary to your current voice channel.")
    async def connect_(self, ctx, *, channel: discord.VoiceChannel=None):
        """Connect to voice.
        Parameters
        ------------
        channel: discord.VoiceChannel [Optional]
            The channel to connect to. If a channel is not specified, an attempt to join the voice channel you are in
            will be made.
        This command also handles moving the bot to different channels.
        """
        cc = await self.channel_check(ctx)
        if cc is False:
            return

        if not channel:
            try:
                channel = ctx.author.voice.channel
                if channel.name == "Kelp Forest":
                    return await ctx.channel.send("Sorry, that's KelpyG's turf.")
            except AttributeError:
                await ctx.send(f"<@{ctx.author.id}>, are you sure you're in a VoiceChannel?")
                raise InvalidVoiceChannel('No channel to join. Please either specify a valid channel or join one.')

        vc = ctx.voice_client

        if vc:
            if vc.channel.id == channel.id:
                return
            try:
                await vc.move_to(channel)
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Moving to channel: <{channel}> timed out.')
        else:
            try:
                await channel.connect()
            except asyncio.TimeoutError:
                raise VoiceConnectionError(f'Connecting to channel: <{channel}> timed out.')

    @slash_command(name="play", description="Plays a song or radio station.")
    async def stream_(self, ctx, search: Option(str, description="Song name or YouTube URL.")):
        try:
            channel = ctx.author.voice.channel
            if channel.name == "Kelp Forest":
                return await ctx.respond("Sorry, that's KelpyG's turf.")
        except:
            return await ctx.respond("You need to be in a voice channel.", delete_after=5)
        
        """Request a song and add it to the queue.
        This command attempts to join a valid voice channel if the bot is not already in one.
        Uses YTDL to automatically search and retrieve a song.
        Parameters
        ------------
        search: str [Required]
            The song to search and retrieve using YTDL. This could be a simple search, an ID or URL.
        """
        # Fixed sations, will probably change to a semi-automated system.
        stations = [
            {"stationID": "1", "stationName": "KSHE 95", "stationBio": "Real. Rock. Radio.", "streamURL": "https://17343.live.streamtheworld.com/KSHEFM.mp3"},
            {"stationID": "2", "stationName": "100.3 The Beat", "stationBio": "STL’s Hip Hop and R&B.", "streamURL": "https://n06a-e2.revma.ihrhls.com/zc1289?rj-ttl=5&rj-tok=AAABezug6J8ATiCiNMef-ze0rA"},
            {"stationID": "3", "stationName": "106.5 The Arch", "stationBio": "You never know what you'll hear next.", "streamURL": "https://18103.live.streamtheworld.com/WARHFM.mp3"},
            {"stationID": "4", "stationName": "K-HITS 106.9", "stationBio": "Top 40 Mainstream.", "streamURL": "https://prod-34-83-204-199.wostreaming.net/griffin-khttfmaac-imc2"},
            {"stationID": "5", "stationName": "That 70's Channel", "stationBio": "The Biggest Hits of the 70's!", "streamURL": "https://streaming.live365.com/a09646"},
            {"stationID": "6", "stationName": "Flood FM", "stationBio": "Your Indie Alternative.", "streamURL": "https://streaming.live365.com/a78844"},
            {"stationID": "7", "stationName": "Country Roads", "stationBio": "Today's biggest country music hits!", "streamURL": "https://rfcmedia.streamguys1.com/countryroads.mp3"},
            {"stationID": "8", "stationName": "Smooth Jazz", "stationBio": "Sit down and relax.", "streamURL": "https://rfcmedia.streamguys1.com/smoothjazz.mp3"},
            {"stationID": "9", "stationName": "Coffee House", "stationBio": "A carefully brewed blend of soft, acoustic sounds.", "streamURL": "https://rfcmedia.streamguys1.com/coffeehouse.mp3"},
            {"stationID": "10", "stationName": "Channel 44000", "stationBio": "Today's latest dance music.", "streamURL": "https://streaming.live365.com/a82630"},
            {"stationID": "11", "stationName": "Radio Los Santos", "stationBio": "You already know what it is.", "streamURL": "https://radio.epcgamers.com/radio/8010/radio.mp3"},
            {"stationID": "12", "stationName": "K-POP OnlyHits", "stationBio": "Top 20 K-POP Hits.", "streamURL": "https://strw1.openstream.co/2147"}
            ]

        # Keyword to return list of all stations
        if search == "stations":
            embed=discord.Embed(title="Speed Dial Stations", description="These are all of the saved internet radio stations.", color=0x73d251)
            for s in stations:
                embed.add_field(name=f"{s['stationName']} - {s['stationBio']}", value=f"Speed Dial: {s['stationID']}", inline=False)
            return await ctx.respond(embed=embed)

        # Assumes music should be played and readies itself.
        cc = await self.channel_check(ctx)
        if cc is False:
            return

        await ctx.delete()
        await ctx.trigger_typing()

        vc = ctx.voice_client

        if not vc:
                await self.connect_(ctx, channel=channel)

        player = self.get_player(ctx)
        
        # Assumes listener is requesting a station off of the stations list.
        try:
            if int(search):
                station = search
                for s in stations:
                    if station == s["stationID"]:
                        station = s
            
            source = {'webpage_url': station["streamURL"], 'requester': ctx.author, 'title': station["stationName"], "custom": "custom"}
        
        except:

            # If download is False, source will be a dict which will be used later to regather the stream.
            # If download is True, source will be a discord.FFmpegPCMAudio with a VolumeTransformer.
            source = await YTDLSource.create_source(ctx, search, loop=self.bot.loop, download=False)

        await player.queue.put(source)

    @slash_command(name="queue", description="Shows what's to play next.")
    async def queue_info(self, ctx):
        """Retrieve a basic queue of upcoming songs."""
        cc = await self.channel_check(ctx)
        if cc is False:
            return

        vc = ctx.voice_client

        if not vc or not vc.is_connected():
            return await ctx.send('I am not currently connected to voice!', delete_after=20)

        player = self.get_player(ctx)
        if player.queue.empty():
            return await ctx.send('There are currently no more queued songs.')

        # Grab up to 5 entries from the queue...
        upcoming = list(itertools.islice(player.queue._queue, 0, 5))

        fmt = '\n'.join(f'**`{_["title"]}`**' for _ in upcoming)
        embed = discord.Embed(title=f'Upcoming - Next {len(upcoming)}', description=fmt, color=0x8080ff)

        await ctx.respond(embed=embed, ephemeral=True)


def setup(bot):
    bot.add_cog(Music(bot))