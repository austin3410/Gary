import discord
from discord.commands import slash_command, Option  # Importing the decorator that makes slash commands.
from discord.ext.commands.core import check
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, button, Item, Button
import asyncio
from .bbtcg import BBTCG
from random import randint, choice
import math


class BBTCG_Events(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.BBTools = BBTCG
        self.BBTCGdir = "files//BBTCG//"

    def list_events(self):
        return [
            {"name": "Opposite Day", "description": "Slots Jackpots are now Bankrupts, but 🧽's are worth $10 a piece!"},
            {"name": "Firesale", "description": "All cards in the market will be on a Firesale!"},
            {"name": "Scrapyard Wars", "description": "Scrap prices are now triple the cards value!"},
            {"name": "Me Money!", "description": "All players pay a %30 tax back to the bank!"},
            {"name": "Free Balloon Day", "description": "Slots is free to play!"},
            {""}
        ]
        

    


# Standard bot setup.
def setup(bot):
    bot.add_cog(BBTCG_Events(bot))