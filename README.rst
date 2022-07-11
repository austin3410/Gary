.. image:: https://img.shields.io/discord/881207955029110855?label=discord&style=for-the-badge&logo=discord&color=5865F2&logoColor=white
   :target: https://pycord.dev/discord
   :alt: Discord server invite
.. image:: https://img.shields.io/github/v/release/Pycord-Development/pycord?include_prereleases&label=Pycord%20Version&logo=github&sort=semver&style=for-the-badge&logoColor=white
   :target: https://github.com/Pycord-Development/pycord/releases/tag/v2.0.0
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
- ``other_class.gif_token`` - A Giphy API Token that is used in the ``yesno.py`` cog.
- ``other_class.serpapi_key`` - A SERPAPI key that is used in the ``gif.py`` cog.
- All pip packages listed in ``requirements.txt``.

Features
--------

Gary comes with an assortment of features:

- **Bikini Bottom Trading Card Game** -  BBTCG is a game about buying, selling, and stealing trading cards in the form of different Bikini Bottom characters.
- **GIF** - A better ``/gif`` command that uses Google as its search backend.
- **Interactive Music Player** - A music player with buttons and menus, instead of all slash commands.
- **Subscription Channels** - Integrated system to let users subscribe to different channels to keep unwanted notifications and spoilers out of their feed.
- **SpongeBob Mock Case** - A message command to convert any previous message to mock case (will also automatically pick someone to mock)
- **Answer Yes/No Questions** - Any @Gary that's in the form of a Yes or No question will be answered! 
- **Much More!**

