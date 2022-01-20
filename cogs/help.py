import discord
from discord.commands import slash_command, Option  # Importing the decorator that makes slash commands.
from discord.ext import commands

class Help(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot

    
    def command_autocomplete(self, ctx: discord.AutocompleteContext):

        return [c for c in self.bot.command_helps if str(c).startswith(ctx.value.lower())]

    @slash_command(name="help", description="You're looking at it!")
    async def help(self, ctx, command: Option(str, description="Which command do you need help with?", autocomplete=command_autocomplete, required=False)):
        help_str = "```"

        if command != None:
            command_name = command
            command = self.bot.command_helps[command]
            
            if command["type"] == "SlashCommand":
                help_str += "/"
            
            if "parent" in command.keys():
                help_str += f"{command['parent']} "

            help_str += f"{command_name} - {command['type']}\n==========\n" + command["description"] + "```"

        else:
            help_str += "Thanks for using Gary! Here are all of his commands!\n\n"
            for command in self.bot.command_helps:

                if self.bot.command_helps[command]["type"] == "SlashCommand":
                    help_str += "/"
                
                if "parent" in self.bot.command_helps[command].keys():
                    help_str += f"{self.bot.command_helps[command]['parent']} "

                help_str += f"{command} - {self.bot.command_helps[command]['type']}\n==========\n" + self.bot.command_helps[command]["description"] + "\n\n"

            help_str += "```"
        
        await ctx.respond(help_str, ephemeral=True)

# Standard bot setup.
def setup(bot):
    bot.add_cog(Help(bot))