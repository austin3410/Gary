.. image:: https://img.shields.io/github/v/release/Pycord-Development/pycord?include_prereleases&label=Pycord%20Version&logo=github&sort=semver&style=for-the-badge&logoColor=white
   :target: https://github.com/Pycord-Development/pycord/releases/tag/v2.4.1
   :alt: Pycord Version

About
-----
Gary is a SpongeBob themed Discord Bot I **work on in my spare time**, specifically for a SpongeBob themed Discord server.

While it's only intended to be used in my Discord server, I will keep the code open for viewing.

Gary is written using the `Pycord <https://github.com/Pycord-Development/pycord>`__ fork of `discord.py <https://github.com/Rapptz/discord.py>`__.

Requirements
------------

There are a few requirements to take full advantage of Gary.
All of these requirements should be added to ``config.py`` as seen in ``config-example.py``.

- ``self.id`` - Your Discord Bot ID.
- ``self.token`` - Your Discord Bot Token.
- ``other_class.serpapi_key`` - A `SERPAPI <https://serpapi.com/>`__ API key used in the ``gif.py`` cog.
- ``other_class.openai_key`` - An `OpenAI <https://beta.openai.com/>`__ API key used in the ``askgary.py`` cog.
- ``other_class.openai_orginization`` - Your users `OpenAI <https://beta.openai.com/>`__ orginization used in the ``askgary.py`` cog.
- ``other_class.gallery_channel_name`` - The name of a channel Gary will send saved images to.
- All pip packages listed in ``requirements.txt``.
- Gary uses the Wavelink library to play music and thus requires a Lavalink server.*

The DEV class within ``config-example.py`` is only there incase you plan on developing Gary further. If not, you can remove it.

Features
--------

Gary comes with an assortment of features:

- **Bikini Bottom Trading Card Game** -  BBTCG is a game about buying, selling, and stealing trading cards in the form of different Bikini Bottom characters.
- **GIF** - A better ``/gif`` command that uses Google as its search backend.
- **Interactive Music Player** - A music player with buttons and menus, instead of all slash commands.
- **SpongeBob Mock Case** - A message command to convert any previous message to mock case (will also automatically pick someone to mock)
- **ChatGPT Powered AI Responses** - Any @Gary message is routed through ChatGPT for seemless AI answers, right in Discord!
- **ChatGPT Powered AI Image Generation** - Use DALL·E 3 to generate AI images!
- **Much More!**

Wavelink Music
--------------

Gary uses the Wavelink Python module for its music commands which requires a connection to a Lavalink Server.
Running a Lavalink server is fairly straight forward and can be done by following `this <https://dsharpplus.github.io/DSharpPlus/articles/audio/lavalink/setup.html>`__ link.

Ensure to stay up to day with the latest Lavalink server version available. This can change often due to backend changes done by YouTube which may break compatibility with Lavalink.

FFMPEG Music
------------
Note: I won't be providing any support for the FFMPEG cog. It's only being included because it's what Gary used to use.

If you are unable to host a Lavalink server or just don't want to, Gary also includes an FFMPEG based music cog which looks and works nearly the same.

In order to use the FFMPEG music cog, you'll need to do the following:

Within ``gary.py``:

- Change the ``wavelink_music`` entry in the ``cogs_to_load`` list to ``DEPRICATED-music``

**Windows:**

Download `FFMPEG <https://ffmpeg.org/download.html>`__  and place it in Gary's root directory.

**Linux:**

Install FFMPEG through your preferred package manager.

USING DEPRICATED FEATURES
-------------------------
Some features have been replaced with better versions or removed entirely and replaced by native Discord integrations.
If you wish to re-activate these features, simply add the file name to Gary's ``cogs_to_load`` list in ``gary.py``.

**NOTE:** These features may work after re-activation, but will not be supported moving forward and are provided as is.

- ``DEPRICATED-subscribe.py`` - Replaced by Discord's Forum Channels. This featured allowed users to see channels that they were interested in and be hidden from ones they weren't.
- ``DEPRICATED-yesno.py`` - Replaced by ``askgary.py``. This feature allowed users to @Gary with a Yes or No question which would be answered by Gary.
- ``DEPRICATED-music.py`` - Replaced by ``wavelink_music.py``. This is the old FFMPEG based music cog. It should look and work nearly the same. Refer to the "FFMPEG Music" section.
