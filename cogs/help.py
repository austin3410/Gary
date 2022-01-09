import discord
from discord.commands import slash_command
import discord.commands.commands
from discord.ext import commands
from discord.ui import View, Select


class Help(commands.Cog):
    def __init__(self, bot):
        # Inits the bot instance so we can do things like send messages and get other Discord information.
        self.bot = bot

    @slash_command(name="help", guild_ids=[389818215871676418], description="Use this to learn about Gary!", help="You're looking at it!")
    #@cooldown(1, 30)
    async def help(self, ctx):

        # Creates the Select Menu framework.
        options = Select(placeholder="Select one of the commands listed..")

        # Interates through all of the loaded cogs.
        for cog_name in self.bot.cogs:
            
            # Get's the cogs properties and commands.
            cog = self.bot.get_cog(cog_name)

            # Iterates through the commands within a cog.
            for c in cog.walk_commands():
                
                # This check the type of command it is.
                if str(c).startswith("<discord.commands.UserCommand"):
                    options.add_option(label=f"{c.name} - user command.")
                elif str(c).startswith("<discord.commands.SlashCommand"):
                    options.add_option(label=f"{c.name} - slash command.")
                else:
                    options.add_option(label=f"{c.name} - message command.")

        # This defines what should happen when an option is selected.
        async def help_callback(interaction):

            # Since the only value that is returned is the label of the option, we need to parse it
            interaction_values = str(interaction.data["values"][0]).split(" -")
            command_name = interaction_values[0]

            if "message" in interaction_values[1]:
                interaction_type = discord.commands.MessageCommand
            elif "user" in interaction_values[1]:
                interaction_type = discord.commands.UserCommand
            else:
                interaction_type = discord.commands.SlashCommand
            
            # This again gets the command so we can pull its help information.
            c = self.bot.get_command(command_name, type=interaction_type)
            try:
                help_str = c.__dict__["__original_kwargs__"]["help"]
                
            except:
                help_str = c.description
                if c.description == "No description provided" or c.description is None or c.description == "":
                    print(f"No help or description attribute for {c.name}! Stop being lazy and add one!")
            
            help_msg = f"```Help - {c.name}{interaction_values[1]}\n" \
                        f"########################\n" \
                        f"{help_str}```"
            await interaction.response.send_message(help_msg, ephemeral=True, delete_after=60)
        
        # Adds the help_callback to the options menu.
        options.callback = help_callback

        # Creats a View and then adds the options menu to the View.
        view = View()
        view.add_item(options)
        
        # Send the initial help command and the View with the selction menu.
        await ctx.respond("Which command do you need help with?", view=view, ephemeral=True)

# Standard cog setup.
def setup(bot):
    bot.add_cog(Help(bot))