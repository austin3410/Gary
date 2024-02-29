from discord.ext import commands
from configparser import ConfigParser

class BBTCG_Settings(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.BBTCGdir = "files//BBTCG//"
        self.bbtcg_config = ConfigParser()
        self.bbtcg_config.read(self.BBTCGdir + "settings.ini")
        self.settings = dict(self.bbtcg_config.items())
    
    # READ Settings
    def read_settings(self):
        self.bbtcg_config.read(self.BBTCGdir + "settings.ini")
        return dict(self.bbtcg_config.items())
    
    # WRITE Settings
    def write_settings(self):
        with open(self.BBTCGdir + "settings.ini", "w") as settingsfile:
            self.bbtcg_config.write(settingsfile)

# Standard bot setup.
def setup(bot):
    bot.add_cog(BBTCG_Settings(bot))