import discord
from discord.commands import slash_command, Option  # Importing the decorator that makes slash commands.
from discord.ext import commands

class Help(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot

    # This handles filling in the list of available commands that the user can request help text for.
    def command_autocomplete(self, ctx: discord.AutocompleteContext):

        return [c for c in self.bot.command_helps if str(c).startswith(ctx.value.lower())]

    # The main help slash command.
    @slash_command(name="help", description="You're looking at it!")
    async def help(self, ctx, command: Option(str, description="Which command do you need help with?", autocomplete=command_autocomplete, required=False)):
        help_str = "```"

        # If a command is passed, only the help text for that command will be sent.
        if command != None:
            command_name = command
            command = self.bot.command_helps[command]
            
            if command["type"] == "SlashCommand":
                help_str += "/"
            
            if "parent" in command.keys():
                help_str += f"{command['parent']} "

            help_str += f"{command_name} - {command['type']}\n==========\n" + command["description"] + "```"

        # If no command is passed, all of the help texts will be sent.
        else:
            help_str += "Thanks for using Gary! Here are all of his commands!\n==========\nA SlashCommand is a command that requires you type a / first in a text channel.\n" \
                "To use a UserCommand, just right click on any user and go to Apps.\nTo use a MessageCommand, just right click on any public message and go to Apps.\n\n"
            
            for command in self.bot.command_helps:
                
                # This checks to see if the message has reached Discords message char limit.
                # If so, it sends what it has and form a new message for the remaining help texts.
                if len(help_str) >= 1950:
                    help_str += "```"
                    await ctx.respond(help_str, ephemeral=True)
                    help_str = "```"

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