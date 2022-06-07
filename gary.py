import discord
import sys
import traceback
from discord.ext import commands
import config
import logging

# First we load the environment classes which hold the token and id of the different Gary bots.
try:
    if sys.argv[1] == "DEV":
       env = config.DEV()
except:
    env = config.PRODUCTION()

# Then we establish that we are using the discord.Bot lib.
logging.basicConfig(level=logging.WARNING, filename="gary.log", filemode="a", format='%(asctime)s:%(levelname)8s: %(message)s', datefmt='%Y-%m-%d %H:%M:%S')
bot = discord.Bot()
bot.id = env.id
bot.token = env.token
bot.gif_token = env.gif_token

# Then we start to load in all of the selected cogs in the cogs folder.
cogs_to_load = ["ping", "burn", "yesno", "quote", "mock", "music", "bbtcg", "meow", "subscribe", "bbtcg_games", "help"]

if __name__ == '__main__':
    for cog in cogs_to_load:
        try:
            bot.load_extension("cogs." + cog)
        except Exception as e:
            # If something goes wrong this should print that a cog failed to load.
            print(f'Failed to load cog {cog}.', file=sys.stderr)
            traceback.print_exc()
            input(" ")

# When Gary is ready, this is fired.
@bot.event
async def on_ready():
    channels = bot.get_all_channels()
    for c in channels:
        if c.name == "admin-log":
            bot.admin_log = c
    
    # This constructs all the background info for the help command.
    command_helps = {}
    for command in bot.commands:
        #print(command.default_member_permissions)
        if command.default_member_permissions != None:
            continue

        if "SlashCommandGroup" in str(type(command)):
            #command_helps = {**command_helps, command.name: {"description": command.description, "type": "SlashCommandGroup"}}
            for c in command.subcommands:
                command_helps = {**command_helps, c.name: {"description": c.description, "parent": command.name, "type": "SlashCommand"}}

        elif "SlashCommand" in str(type(command)):
            command_helps = {**command_helps, command.name: {"description": command.description, "type": "SlashCommand"}}

        elif "UserCommand" in str(type(command)):
            command_helps = {**command_helps, command.name: {"description": command.__dict__["__original_kwargs__"]["help"], "type": "UserCommand"}}

        elif "MessageCommand" in str(type(command)):
            command_helps = {**command_helps, command.name: {"description": command.__dict__["__original_kwargs__"]["help"], "type": "MessageCommand"}}
    
    bot.command_helps = command_helps
    print(bot.command_helps)

    print("~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n"
          "~ Thanks for using Gary! ~\n"
          "~~~~~~~~~~~~~~~~~~~~~~~~~~~~\n")
    print(f"Logged in as {bot.user}.")

# This catches any application command (slash command) errors.
# This includes cooldowns.
@bot.event
async def on_application_command_error(ctx, event):
    if "Command" in str(event) and "is not found" in str(event):
        await ctx.respond("Meow?")
    elif "is a required argument that is missing" in str(event):
        await ctx.respond(f"You are missing arguments to that command!")
    elif isinstance(event, commands.CommandOnCooldown):
        seconds =  int(str(event)[34:-4])
        seconds_in_day = 60 * 60 * 24
        seconds_in_hour = 60 * 60
        seconds_in_minute = 60

        days = seconds // seconds_in_day
        hours = (seconds - (days * seconds_in_day)) // seconds_in_hour
        minutes = (seconds - (days * seconds_in_day) - (hours * seconds_in_hour)) // seconds_in_minute
        seconds_left = seconds - (days * seconds_in_day) - (hours * seconds_in_hour) - (minutes * seconds_in_minute)

        if days == 0:
            days_output = ""
        elif days == 1:
            days_output = f" {days} day"
        else:
            days_output = f" {days} days"
        
        if hours == 0:
            hours_output = ""
        elif hours == 1:
            hours_output = f" {hours} hour"
        else:
            hours_output = f" {hours} hours"
        
        if minutes == 0:
            minutes_output = ""
        elif minutes == 1:
            minutes_output = f" {minutes} minute"
        else:
            minutes_output = f" {minutes} minutes"
        
        if seconds_left == 0:
            seconds_output = " <1 second"
        elif seconds_left == 1:
            seconds_output = f" {seconds_left} second"
        else:
            seconds_output = f" {seconds_left} seconds"

        await ctx.respond(f"You can't do that yet! Try again in{days_output}{hours_output}{minutes_output}{seconds_output}!", ephemeral=True)
    
    elif "CheckFailure" in str(type(event)):
        await ctx.respond(f"Please use this command in the correct channel!", ephemeral=True)
    else:
        print(type(event))
        print(f"\nSomething caused this error:\n{event}")
        traceback.print_exc()

bot.run(bot.token)