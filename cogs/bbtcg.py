import asyncio
import inspect
from discord.commands import Option
from discord.ext import commands
from discord.commands import slash_command, user_command, SlashCommandGroup
from discord.ext.commands import Cooldown  # Importing the decorator that makes slash commands.
from discord.ext.commands.core import cooldown, check, dynamic_cooldown
#from discord.ui import Button, View
from datetime import datetime, timedelta
from discord import default_permissions
import discord
import pickle
import random
import os
import json
import math
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from configparser import ConfigParser

from files.BBTCG.check_achievements import CheckAchievements
from .bbtcg_settings import BBTCG_Settings as BBTCG_Settings

class BBTCG(commands.Cog):

    def __init__(self, client):
        self.client = client
        self.bot = client
        self.BBTCGdir = "files//BBTCG//"
        self._buckets = [commands.BucketType.user]
        
        # Loads the settings Python file which parses and handles the actual settings file.
        self.BBTCG_Settings = BBTCG_Settings(self.bot)
        
        # Asks the settings Python file to read and return the actual settings file.
        self.settings = self.BBTCG_Settings.read_settings()
    
    # AUTO MARKET Reset
    # This refreshes the auto-generated market every hour.
    @commands.Cog.listener()
    async def on_ready(self):
        while True:
            await self.auto_market()
            try:
                await self.record_history()
            except:
                pass
            # This sets the timer between refreshes. 3600 - 1 hour.
            await asyncio.sleep(int(self.settings["auto_market"]["timer"]))
    
    async def record_history(self):
        history = self.load_history()
        
        # First mark the time.
        current_time = datetime.now().strftime("%d-%m-%y %I:%M:%S %p")
        #print(current_time)

        # Next we need to load in all the users and check the card value average for all players.
        users = []
        all_users_card_total = 0
        for user_file in os.listdir(self.BBTCGdir + "users//"):
            if user_file != "0.pickle":
                user = self.load_user(str(user_file).replace(".pickle", ""))
                users.append(user)
        
        for user in users:
            total_cards_value = 0
            for c in user["inventory"]:
                total_cards_value += c["value"]
            all_users_card_total += total_cards_value
        
        # Calculates average and compares it against the historical average.
        all_user_card_average = int(all_users_card_total / len(users))
        if history["current_average"] == all_user_card_average:
            pass
            #print("Nothing has changed, history will not be written.")
        
        # Now that we know things are different, start to add to the history file.
        else:
            #print("Stats have changed, history will be written!")
            for user in users:
                discord_user = await self.bot.fetch_user(user["id"])
                
                # Calculates total card value to add to plot points.
                total_cards_value = 0
                for c in user["inventory"]:
                    total_cards_value += c["value"]

                # Checks if the current user is not in any of the user dictionaries.
                if not any(d["username"] == discord_user.name for d in history["users"]):
                    user_plots = []
                    for i in range(len(history["times"])):
                        user_plots.append(0)
                    user_plots.append(total_cards_value)
                    history["users"].append({"username": discord_user.name, "plots": user_plots})
                
                # If they are already in a dictionary.
                else:
                    for u in history["users"]:
                        if u["username"] == discord_user.name:
                            u["plots"].append(total_cards_value)
            
            # Appends the current time to the times list.
            history["times"].append(current_time)

            #Last, updates the historical average with the new average.
            history["current_average"] = all_user_card_average

        self.save_history(history)
        
    async def auto_market(self):
        try:
            # Loads the market and the available cards
            market = self.load_market()
            cards = self.load_cards()
            # Checks to see if there are already Bikini Bottom Dweller cards in the market.
            to_be_renewed = []
            if market != []:
                for c in market:
                    if int(c["seller_id"]) == 0:
                        to_be_renewed.append(c)
                for c in to_be_renewed:
                    market.remove(c)
                    c.pop("seller")
                    c.pop("seller_id")
                    c.pop("selling_price")
                    c.pop("selling_start_time")
                    cards.append(c)
            # Randomly picks between 4 and 8 new cards to add to the market.
            drop = []
            amount_of_cards = random.randrange(int(self.settings["auto_market"]["cards_min"]), int(self.settings["auto_market"]["cards_max"]))
            for i in range(0, amount_of_cards):
                try:
                    card = random.choice(cards)
                    drop.append(card)
                    cards.remove(card)
                except:
                    self.save_cards(cards)
                    await self.end_game()
                    break
            # Assigns the cards price, seller, and seller_id.
            for c in drop:
                c["seller"] = "someone"
                c["seller_id"] = 0
                c["selling_start_time"] = datetime.now()
                firesale = random.randint(0, int(self.settings["auto_market"]["firesale_chance"]))
                if firesale == 25:
                    print(f"Fire sale on {c['name']} !!!")
                    c["selling_price"] = round(int(c["value"]) * float(self.settings["auto_market"]["firesale_mult"]))
                else:
                    c["selling_price"] = round(int(c["value"]) * random.uniform(float(self.settings["auto_market"]["cardprice_min_mult"]), float(self.settings["auto_market"]["cardprice_max_mult"])))
                market.append(c)
            saved_market = self.save_market(market)
            saved_cards = self.save_cards(cards)
            if saved_cards != True or saved_market != True:
                return print("Something went wrong.. unable to save market or cards in auto market!")
        
        except Exception as e:
            print(f"Something went wrong in auto market:\n{e}")

    # This function loads all of the available cards that are in play. If the available_cards file doesn't exist it creates it and returns it.
    # If this function creates a new available_cards file, it basically starts a fresh game.
    def load_cards(self):
            try:
                with open(self.BBTCGdir + "cards//available_cards.pickle", "rb") as file:
                    available_cards = pickle.load(file)
                
                return available_cards
            
            except:
                print("[BBTCG] available_cards.pickle not found, loading default list.")
                if not os.path.exists(self.BBTCGdir + "cards//"):
                    os.makedirs(self.BBTCGdir + "cards//")
                with open(self.BBTCGdir + "card_data.pickle", "rb") as file:
                    all_cards = pickle.load(file)

                with open(self.BBTCGdir + "cards//available_cards.pickle", "wb") as file:
                    pickle.dump(all_cards, file)
                
                return all_cards
    
    # This function saves a variable called cards to the available_cards pool.
    # If it can't, it returns false since this should only be called in the middle of a game, thus the available_cards file should exist.
    def save_cards(self, cards):
        try:
            with open(self.BBTCGdir + "cards//available_cards.pickle", "wb") as file:
                pickle.dump(cards, file)
                return True
        except:
            return False
    
    # This function loads and returns a user file.
    # If it can't, it creates a user file and returns it. This is basically the user joining the game.
    def load_user(self, uid):
        try:
            with open(self.BBTCGdir + f"users//{uid}.pickle", "rb") as file:
                user = pickle.load(file)
                return user
        except Exception as e:
            if not os.path.exists(self.BBTCGdir + "users//"):
                os.makedirs(self.BBTCGdir + "users//")
            with open(self.BBTCGdir + f"users//{uid}.pickle", "wb") as file:
                user = {
                    "id": uid, 
                    "inventory": [], 
                    "money": 50, 
                    "earned_achievements": [], 
                    "shop_stats": {
                        "cards_purchased": 0, 
                        "steals_purchased": 0, 
                        "cards_stolen": []
                        },
                    "market_stats": {
                        "cards_purchased": 0, 
                        "cards_sold": 0, "cards_scrapped": 0
                        }, 
                    "slots_stats": {
                        "slots_played": 0, 
                        "time_since_last_played": 0
                        }
                    }
                pickle.dump(user, file)
                return user
    
    # This function saves a users file.
    def save_user(self, user):
        try:
            with open(self.BBTCGdir + f"users//{user['id']}.pickle", "wb") as file:
                pickle.dump(user, file)
                return True
        except Exception as e:
            print(e)
            return False
    
    # This function generates the Discord embed object of a given card.
    def generate_card(self, card):
        embed = discord.Embed(title=card["name"], description=f"{card['category']} - {card['rarity']}", color=int(card["color"], 16))
        embed.set_image(url=card["img"])
        embed.add_field(name="Value", value=f"${card['value']}", inline=False)
        embed.set_footer(text=f"Card no. {card['num']}")
        return embed
    
    # This function opens and loads the market file.
    def load_market(self):
        try:
            with open(self.BBTCGdir + f"cards//market.pickle", "rb") as file:
                market = pickle.load(file)
                return market
        except:
            if not os.path.exists(self.BBTCGdir + "cards//"):
                os.makedirs(self.BBTCGdir + "cards//")
            market = []
            with open(self.BBTCGdir + f"cards//market.pickle", "wb") as file:
                pickle.dump(market, file)
            return market
    
    # This function saves the market file with a new one.
    def save_market(self, market):
        with open(self.BBTCGdir + f"cards//market.pickle", "wb") as file:
            pickle.dump(market, file)
            return True
    
    # This loads the history file, if it exists.
    def load_history(self):
        try:
            with open(self.BBTCGdir + f"cards//history.pickle", "rb") as file:
                history = pickle.load(file)
                return history
        except:
            if not os.path.exists(self.BBTCGdir + "cards//"):
                os.makedirs(self.BBTCGdir + "cards//")
            history = {"current_average": 0, "times": [], "users": []}
            with open(self.BBTCGdir + f"cards//history.pickle", "wb") as file:
                pickle.dump(history, file)
            return history
    
    # This function saves the history file with a new one.
    def save_history(self, history):
        with open(self.BBTCGdir + f"cards//history.pickle", "wb") as file:
            pickle.dump(history, file)
            return True
    
    # This function loads the created_roles file or creates a new one.
    def load_roles(self):
        try:
            with open("files//BBTCG//cards//created_roles.pickle", "rb") as file:
                created_roles = pickle.load(file)
                return created_roles
        except:
            with open("files//BBTCG//cards//created_roles.pickle", "wb") as file:
                created_roles = []
                pickle.dump(created_roles, file)
            
            return created_roles
    
    # This function saves the created_roles file.
    def save_roles(self, created_roles):
        with open("files//BBTCG//cards//created_roles.pickle", "wb") as file:
            pickle.dump(created_roles, file)
            return True
    
    # This function checks to make sure a message is sent in the correct channel.
    async def channel_check(self, message, desired_channel):
        if str(message.channel.type) == "private":
            await message.respond(f"Please use this command in #{desired_channel}!", delete_after=10)
            return False
        if str(message.channel.name) != desired_channel:
            await message.respond(f"Please use this command in #{desired_channel}!", delete_after=10)
            return False
        else:
            return True
    
    # This function triggers when the game is over or almost over and there are no more cards left to draw.
    async def end_game(self):
        # Loads the cards to check its current status.
        cards = self.load_cards()

        # Checks if both the market and available card pools are empty.
        if len(cards) <= 0:

            # Finds the BBTCG channel to post messages to.
            for channel in self.client.get_all_channels():
                if channel.name == "bbtcg":
                    bbtcg_channel = channel
                    bbtcg_guild = bbtcg_channel.guild

            # Loads the market to check its current status.
            market = self.load_market()
            if len(market) <= 0:
                
                # If both are empty the game is over and cleanup/after game stats occur.
                # Creates a winner placeholder.
                winner = None
                second_place = None
                third_place = None
                users = []

                # Loads the all of the user files and compares their card values.
                user_files = os.listdir("files//BBTCG//users")
                for file in user_files:
                    # This skips the market user.
                    if file == "0.pickle":
                        pass
                    else:
                        user = self.load_user(file.replace(".pickle", ""))
                        user_card_value = 0

                        # Calculates card values.
                        for card in user["inventory"]:
                            user_card_value = user_card_value + card["value"]
                        user["card_value"] = user_card_value
                        users.append(user)
                
                # This sorts the users
                sorted_users = sorted(users,  key=lambda d: d["card_value"])
                winner = sorted_users[-1]
                try:
                    second_place = sorted_users[-2]
                except:
                    pass
                try:
                    third_place = sorted_users[-3]
                except:
                    pass

                
                # This starts the cleanup and game reset.
                # First deletes all of the created roles.
                roles = self.load_roles()
                if len(roles) >= 1:
                    for created_role in roles:
                        role = bbtcg_guild.get_role(created_role["id"])
                        await role.delete(reason="Game over.")
                        print("deleted role " + role.name)
                
                # Send a message declaring the winner of the game.
                msg = f"All cards have been drawn or bought! The game is over!\nThe top three players are:\n"
                if winner != None:
                    msg = msg + f"<@{winner['id']}>, they had **${winner['card_value']}** worth of cards!\n"
                if second_place != None:
                    msg = msg + f"<@{second_place['id']}>, they had **${second_place['card_value']}** worth of cards!\n"
                if third_place != None:
                    msg = msg + f"<@{third_place['id']}>, they had **${third_place['card_value']}** worth of cards!"
                await bbtcg_channel.send(msg)

                await self.record_history()
                graph = await self.generate_history_graph()
                await bbtcg_channel.send(file=graph)

                # Deletes all of the generated files for a fresh start.
                cards_files = os.listdir("files//BBTCG//cards//")
                for card_file in cards_files:
                    os.remove("files//BBTCG//cards//" + card_file)
                    print(f"deleted {card_file}")
                user_files = os.listdir("files//BBTCG//users//")
                for user_file in user_files:
                    os.remove("files//BBTCG//users//" + user_file)
                    print(f"deleted {user_file}")
                
                # Declares a new game has begun.
                await bbtcg_channel.send(f"A new game will begin soon. Gary must restart to cleanup from the previous game.")
                quit()
            
            # This triggers when the available card pool is empty but the market still has cards.
            return await bbtcg_channel.send("The pool of available cards has run dry! The only remaining cards are in the market! Quick, buy'em up!!")
    
    async def draw_card(self, ctx, internal=False):
        
        user = self.load_user(str(ctx.author.id))

        # Loads available card pool.
        cards = self.load_cards()

        # Randomly draws a card from the pool and removes it from said pool.
        try:
            drawn_card = random.choice(cards)
            cards.remove(drawn_card)
        except:
            return await self.end_game()
        # Saves the new pool to the available cards file. If it fails it cancels the transaction.
        saved_cards = self.save_cards(cards)
        if saved_cards == False:
            return await ctx.channel.send("I was unable to draw a card for you!")
        
        # Adds the drawn card to the users reserved list. Then saves the user.
        user["inventory"].append(drawn_card)
        saved_user = self.save_user(user)
        if saved_user != True:
            return await ctx.channel.send("I wasn't able to save your user file after drawing a card...")
        
        # Creates the card embed and sends it to the user.
        embed = self.generate_card(drawn_card)

        await ctx.respond(f"<@{ctx.user.id}> congrats on the draw!", embed=embed)

        await self.check_for_achievements(user, ctx)
        await self.record_history()

        return await self.end_game()
    
    async def check_for_achievements(self, user, ctx=None):
        cc = CheckAchievements()
        attrs = (getattr(cc, name) for name in dir(cc))
        achievement_list = filter(inspect.ismethod, attrs)
        for achievement in achievement_list:
            payload = False
            if achievement.__name__.startswith("__"):
                continue
            else:
                if user["earned_achievements"] != []:
                    ach_uids = [ach["uid"] for ach in user["earned_achievements"]]
                    if achievement.__name__ in ach_uids:
                        continue
                
                payload = achievement(user)

            try:
                if payload != False:
                    user["money"] = user["money"] + payload["reward"]
                    user["earned_achievements"].append(payload)
                    saved_user = self.save_user(user)
                    if saved_user != False:
                        embed=discord.Embed(title="BBTCG Achievements", description="You earned an achievement!", color=payload["color"])
                        embed.add_field(name=payload["name"], value=payload["description"], inline=False)
                        embed.add_field(name="Reward", value=f"${payload['reward']}", inline=False)
                        disc_user = await self.bot.fetch_user(int(user["id"]))
                        if ctx == None:
                            await disc_user.send(embed=embed)
                        else:
                            await ctx.respond(embed=embed, ephemeral=True)
                elif payload == False:
                    pass
            except Exception as e:
                print(e)
    
    async def unequip(self, ctx, cardno, internal=False):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            return print("Channel Check failed.")
        
        user = self.load_user(ctx.author.id)
        # First checks to see if the specified card is in the users inventory.
        card_to_unequip = next((item for item in user["inventory"] if int(item["num"]) == int(cardno)), None)
        if card_to_unequip == None:
            if internal == True:
                return
            else:
                return await ctx.respond("You can't unequip a card that you don't own!", ephemeral=True)

        # Then checks to see if the specified card has a created role already.
        created_roles = self.load_roles()
        created_role = next((item for item in created_roles if int(item["card"]["num"]) == int(cardno)), None)

        if created_role == None:
            if internal == True:
                return
            else:
                return await ctx.respond("That role doesn't exist!", ephemeral=True)

        # Then checks to see if the user is a member of that created role.
        role_to_unequip = next((item for item in ctx.author.roles if item.id == int(created_role["id"])), None)

        if role_to_unequip == None:
            if internal == True:
                return
            else:
                return await ctx.respond("You don't have that card equipped!", ephemeral=True)
        
        return await ctx.author.remove_roles(role_to_unequip)
    
    # This is a channel check that occurs before the command is invoked
    # which prevents unintentional cooldowns.
    def before_invoke_channel_check(ctx):
            if str(ctx.channel.type) == "private":
                return False
            if ctx.command.name == "slots":
                return ctx.channel.name == "games"
            elif ctx.command.name == "store" or ctx.command.name == "draw" or ctx.command.name == "history":
                return ctx.channel.name == "bbtcg"
    
    # This lets us dynamically create an appropriate cooldown for slots.
    def slots_cooldown(message):
        # If an amount of spins was specified.
        try:
            spins = message.selected_options[0]["value"]
        
        # If the default value was used.
        except:
            spins = message.unselected_options[0].default
        
        # Calcuates cooldown time in seconds.
        cd_time = spins * 45

        return Cooldown(1, cd_time)

    async def generate_history_graph(self):
        history = self.load_history()
        #print(history)

        # This checks to make sure we can actually generate a useful history graph.
        if len(history["times"]) <= 1:
            return "Not enough time has passed to generate a history graph."
        elif len(history["users"]) <= 1:
            return "There aren't enough players to generate a history graph."
        elif history["current_average"] < 1:
            return "The current average for all players is too low to record on a graph."

        x = history["times"]
        x[0] = "Start - " + x[0]
        y = []
        labels = []

        for user in history["users"]:
            labels.append(user["username"])
            y.append(user["plots"])
        
        z = 0
        for l in y:
            plt.plot(x, l, label=labels[z])
            plt.annotate(f"${int(l[-1])}", xy=(1, l[-1]), xytext=(8, 0), xycoords=("axes fraction", "data"), textcoords="offset points")
            #plt.axhline(y=l[-1], color="y", linestyle="-.")
            z += 1
        
        plt.legend(loc="upper left")
        plt.title("BBTCG Current Match Timeline")
        plt.xticks(ticks=[x[0], (x[int(len(x)/2)]), "Now"])
        plt.xlabel("Time")
        plt.ylabel("Card Value in $")
        plt.tight_layout()
        plt.grid(visible=True)
        plt.style.use("seaborn-darkgrid")
        plt.savefig(self.BBTCGdir + "graph.png")

        with open(self.BBTCGdir + "graph.png", "rb") as file:
            pic = discord.File(file)
        
        # If we don't close the figure, each player will be added again.
        plt.close()
        
        return pic


################################################################################################
# BELOW ARE ALL OF THE ACTUAL DISCORD COMMANDS                                                 #
################################################################################################

    # DRAW command - Picks a random card from the available card pool and awards it to the user.
    @slash_command(name="draw", description="Draws a card for BBTCG! Use in #bbtcg", help="This draws a BBTCG card for you. Can be used once per hour. Use in #bbtcg")
    @check(before_invoke_channel_check)
    @cooldown(1, 3600, commands.BucketType.user)
    async def bbtcg_draw(self, message):
        await self.draw_card(message)
    
    # HISTORY Command
    @slash_command(name="history", description="Shows a brief history of the current match.", help="Shows a brief history of the current match.")
    @check(before_invoke_channel_check)
    async def bbtcg_history(self, ctx):
        graph = await self.generate_history_graph()
        if isinstance(graph, str):
            await ctx.respond(graph)
        else:
            await ctx.respond(file=graph)

    # PRINT USER Command
    @user_command(name="BBTCG Print", help="Prints out a users BBTCG profile.")
    @default_permissions(administrator=True)
    async def bbtcg_print(self, ctx, member: Option(discord.Member, description="Target user ID.")):
        user = self.load_user(member.id)
        temp_file_path = f"files//BBTCG//{member.name}.json"
        with open(temp_file_path, "w") as file:
            user_json = json.dumps(user, indent=4, sort_keys=True, default=str)
            file.write(user_json)
        await ctx.respond(file=discord.File(temp_file_path), ephemeral=True)
        return os.remove(temp_file_path)
    
    # AUTO MARKET Command
    @slash_command(name="automarket", description="Renews the current BBTCG market offerings.")
    @default_permissions(administrator=True)
    async def bbtcg_auto_market(self, message):
        await self.auto_market()
        return await message.respond("Market renewed.", ephemeral=True, delete_after=3)
    
    # ADJUST USER CASH Command
    @user_command(name="Adjust Cash", help="Adjusts a user BBTCG cash.")
    @default_permissions(administrator=True)
    async def bbtcg_adjust(self, ctx, member: Option(discord.Member, description="Target user ID.")):

        class AddCash(discord.ui.Modal):
            def __init__(self, member, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                self.member = member
                self.add_item(discord.ui.InputText(custom_id="amount", label="Amount:", placeholder="0", required=True, ))
            
            async def callback(self, interaction: discord.Interaction):
                self.stop()
                await interaction.response.edit_message(content="Working...", view=None)
        
        class SubCash(discord.ui.Modal):
            def __init__(self, member, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                self.member = member
                self.add_item(discord.ui.InputText(custom_id="amount", label="Amount:", placeholder="0", required=True))
            
            async def callback(self, interaction: discord.Interaction):
                self.stop()
                await interaction.response.edit_message(content="Working...", view=None)
        
        class SetCash(discord.ui.Modal):
            def __init__(self, member, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                self.member = member
                self.add_item(discord.ui.InputText(custom_id="amount", label="Amount:", placeholder="0", required=True))
            
            async def callback(self, interaction: discord.Interaction):
                self.stop()
                await interaction.response.edit_message(content="Working...", view=None)

        class AdjustUser(discord.ui.View):
            def __init__(self, member, *args, **kwargs) -> None:
                super().__init__(*args, **kwargs)
                
                self.member = member
                self.value = None

            @discord.ui.button(label="Add", style=discord.ButtonStyle.green)
            async def add_button(self, button, interaction):
                modal = AddCash(member=member, title="Give BBTCG Cash")

                await interaction.response.send_modal(modal)
                await modal.wait()

                amount = modal.children[0].value

                self.value = {"action": "add", "amount": amount}
                self.stop()
                return
            
            @discord.ui.button(label="Subtract", style=discord.ButtonStyle.danger)
            async def sub_button(self, button, interaction):
                modal = SubCash(member=member, title="Subtract BBTCG Cash")

                await interaction.response.send_modal(modal)
                await modal.wait()

                amount = modal.children[0].value

                self.value = {"action": "sub", "amount": amount}
                self.stop()
                return
            
            @discord.ui.button(label="Set", style=discord.ButtonStyle.blurple)
            async def set_button(self, button, interaction):
                modal = SetCash(member=member, title="Set BBTCG Cash")

                await interaction.response.send_modal(modal)
                await modal.wait()

                amount = modal.children[0].value

                self.value = {"action": "set", "amount": amount}
                self.stop()
                return
        
        user = self.load_user(member.id)
        member_menu = f"Member: {member.name}\nMember ID: {user['id']}\nMoney: **${user['money']}**"
        
        adjustuser_menu = AdjustUser(member=member)
        msg = await ctx.respond(member_menu, view=adjustuser_menu, ephemeral=True)
        await adjustuser_menu.wait()
        await asyncio.sleep(1)

        try:
            amount = int(adjustuser_menu.value["amount"])
        except:
            return await msg.edit_original_message(content=f"Amount must be in integer!", view=None)

        if adjustuser_menu.value["action"] == "add":
            user["money"] += amount
        
        elif adjustuser_menu.value["action"] == "sub":
            user["money"] -= amount
        
        elif adjustuser_menu.value["action"] == "set":
            user["money"] = amount
        
        saved_user = self.save_user(user)

        if saved_user == True:
            return await msg.edit_original_message(content=f"Done! :white_check_mark:", view=None)
        else:
            return await msg.edit_original_message(content=f"An error occurred!", view=None)
    
    # ACHIEVEMENTS command - Send the user a list of all of their earned achievements.
    @slash_command(name="achievements", description="Shows you your current BBTCG Achievements.", 
    help="achievements - ~This shows you all of the BBTCG Achievements you've earned so far this game.\nAchievements reset when a new game starts.")
    async def bbtcg_achievements(self, message):
        user = self.load_user(message.author.id)

        user_achievements = user["earned_achievements"]

        msg_header = f"============\n**{message.author.name}'s Achievements**\n\n"
        ach_count = 0
        ach_msg = ""

        for ach in user_achievements:
            ach_msg = ach_msg + f"`{ach['name']} - {ach['description']} - {ach['rarity']} - ${ach['reward']}`\n"
            ach_count += 1
        
        if ach_count == 1:
            achievement = "achievement"
        else:
            achievement = "achievements"
        
        msg_footer = f"\nYou have **{ach_count}** {achievement}!\n\n"

        if len(ach_msg) > 1700:
            await message.author.send(msg_header)

            msg = f"\nYou have so many cards that I can't send them all in a single Discord message. Instead, I had to send multiple messages." + msg_footer

            ach_msgs = ach_msg.splitlines()
            new_ach_msg = ""

            for ach_msg in ach_msgs:
                if len(new_ach_msg) + len(ach_msg) <= 1999:
                    ach_msg = ach_msg + "\n"
                    new_ach_msg = new_ach_msg + ach_msg
                    msg_sent = False
                else:
                    await message.author.send(new_ach_msg)
                    new_ach_msg = ""
                    msg_sent = True
            
            if msg_sent == False:
                await message.author.send(new_ach_msg)

        else:
            msg = msg_header + ach_msg + msg_footer
        
        # Sends either the larger inventory notice and msg_footer or just the msg_footer depending on the situation.
        await message.respond(msg, ephemeral=True)

        
    # INVENTORY command - Used by a user to check what cards they have and how much $ they have.
    @slash_command(name="inventory", description="Send you your current BBTCG inventory.",
    help="inventory - This shows you your current BBTCG inventory. This includes:\nCards (and all the information about your cards)\nHow much cash you have.\nYour total card value.\nYour total account value.")
    async def bbtcg_inventory(self, message):
        # Loads or creates a user.
        user = self.load_user(message.author.id)

        # Creates parts of the message and creates stastical counters.
        msg_header = f"============\n**{message.author.name}'s Inventory**\n\n"
        card_count = 0
        cards_value = 0
        card_msg = ""
        
        # Counts cards and formats them into another part of the message.
        for c in user["inventory"]:
            card_count = card_count + 1
            card_msg = card_msg + f"`{c['name']} - {c['rarity']} - ${c['value']} - Card no. {c['num']}`\n"
            cards_value = cards_value + c["value"]
        
        # Just for grammatical accuracy.
        if card_count == 1:
            card = "card"
        else:
            card = "cards"
        
        msg_footer = f"\nYou have **{card_count}** {card}!\nValue of cards: **${cards_value}**\nYour current cash: **${user['money']}**\nTotal account value: **${cards_value + user['money']}**\n\n" \
                        "To inspect a card use: /inspect <Card no.>"

        # Checks to see if the message can be sent within Discords 2000 character message limit.
        # If not then it intelligently splits the list of cards into sizable chunks.
        if len(card_msg) >= 1700:
            await message.respond(msg_header, ephemeral=True)

            msg = f"\nYou have so many cards that I can't send them all in a single Discord message. Instead, I had to send multiple messages." + msg_footer

            card_msgs = card_msg.splitlines()
            new_card_msg = ""

            for card_msg in card_msgs:
                if len(new_card_msg) + len(card_msg) <= 1999:
                    card_msg = card_msg + "\n"
                    new_card_msg = new_card_msg + card_msg
                    msg_sent = False
                else:
                    await message.author.send(new_card_msg)
                    new_card_msg = ""
                    msg_sent = True
            
            if msg_sent == False:
                await message.author.send(new_card_msg)

        else:
            msg = msg_header + card_msg + msg_footer
        
        # Sends either the larger inventory notice and msg_footer or just the msg_footer depending on the situation.
        await message.respond(msg, ephemeral=True)
    
    # INSPECT command - Sends the card that is specified.
    @slash_command(name="inspect", description="This sends you the card you request, if you have it.",
    help="inspect <card no> - This will generate the specified card itself and send it in the current channel.")
    async def bbtcg_inspect(self, message, cardno: Option(int, description="Card no.")):
        # Loads user to check if they own the card.
        user = self.load_user(message.author.id)
        for c in user["inventory"]:

            # If they own the card, the card will be generated and sent to the user in the channel they requested.
            if int(cardno) == int(c["num"]):
                embed = self.generate_card(c)
                return await message.respond(f"<@{message.author.id}>, here's your card:", embed=embed)
        
        # If they don't own the card they will be told they don't own the card.
        return await message.respond(f"<@{message.author.id}>, you don't own that card!")


    market = SlashCommandGroup("market", "All commands related to the BBTCG market.")
    
    @market.command(description="Shows the BBTCG market.")
    async def show(self, ctx):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            return
        
        # Loads the current market lists.
        market = self.load_market()
        if market == []:
            return await ctx.respond("There's currently nothing in the market right now.")
        else:
            msg = "============\n**Current Market Offerings**\nMarket Values: Common - $25 | Rare - $65 | Epic - $105 | Legendary - $215\n\n"
            for c in market:
                if c["selling_start_time"] < datetime.now():
                    msg = msg + f"`${c['selling_price']} from {c['seller']}: {c['name']} - {c['rarity']} - Card no. {c['num']}`\n"
            
            msg = msg + f"\nIf you would like to purchase any of these, use the command:\n/market buy <Card no.>"
            return await ctx.respond(msg)
    
    @market.command(description="Sells a card on the BBTCG market.")
    async def sell(self, ctx, cardno: Option(int, description="Card no you want to sell."), price: Option(int, description="Asking price.")):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            return
        
        # Sets a maximum asking price so that users can't prolong a game indefinitely with an insane asking price.
        if price > int(self.settings["market"]["sell_max_price"]):
            return await ctx.respond(f"The maximum asking price for any card is ${self.settings['market']['sell_max_price']}.", ephemeral=True)
        user = self.load_user(ctx.author.id)
        card_to_sell = next((item for item in user["inventory"] if int(item["num"]) == int(cardno)), None)
        
        # Checks to make sure the user actually owns the card.
        if card_to_sell == None:
            return await ctx.respond("That card isn't in your inventory.", ephemeral=True)
        
        await self.unequip(ctx=ctx, cardno=cardno, internal=True)
        
        # First removes the card from the users inventory and gives it the required selling info.
        user["inventory"].remove(card_to_sell)
        card_to_sell["seller"] = ctx.author.name
        card_to_sell["seller_id"] = ctx.author.id
        card_to_sell["selling_price"] = str(price).replace("$", "")
        card_to_sell["selling_start_time"] = datetime.now() + timedelta(minutes=int(self.settings["market"]["sell_timedelta_minutes"]))
        # Loads the market and adds the new listing to the market.
        market = self.load_market()
        market.append(card_to_sell)
        # Saves the user with their new smaller inventory.
        saved_user = self.save_user(user)
        saved_market = self.save_market(market)
        # Checks to make sure everything saved correctly.
        if saved_user != True:
            return print("Something went wrong in MARKET POST user not saved!")
        if saved_market != True:
            return print("Something went wrong in MARKET POST market not saved!")
        
        return await ctx.respond(f"I've created your market post for Card no. **{card_to_sell['num']}**!")
    
    @market.command(description="Buys a card on the BBTCG market.")
    @cooldown(1, 0, commands.BucketType.user)
    async def buy(self, ctx, cardno: Option(int, description="Card no you want to buy.")):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            self.buy.reset_cooldown(ctx)
            return
        
        market = self.load_market()
        card_to_buy = next((item for item in market if int(item["num"]) == int(cardno)), None)
        
        # Checks to make sure the specified card is actually on the market.
        if card_to_buy == None:
            self.buy.reset_cooldown(ctx)
            return await ctx.respond("That card isn't on the market. Maybe someone already bought it?", ephemeral=True)
        
        # Loads the buyer
        buyer = self.load_user(ctx.author.id)
        
        # Checks whether the seller is an actual user or a bot.
        if int(card_to_buy["seller_id"]) == 0:
            seller = {"id": 0, "money": 0, "market_stats": {"cards_sold": 0}}
        else:
            seller = self.load_user(card_to_buy["seller_id"])
        
        # Checks to ensure the buyer has sufficient funds.
        if int(buyer["money"]) < int(card_to_buy["selling_price"]):
            self.buy.reset_cooldown(ctx)
            return await ctx.respond("You don't have enough for that!", ephemeral=True)
        
        # Checks to make sure the buyer isn't attempting to purchase their own card.
        elif buyer["id"] == seller["id"]:
            self.buy.reset_cooldown(ctx)
            return await ctx.respond("You can't buy your own listing. Cancel it instead with:\n/market cancel <Card no.>", ephemeral=True)
        
        # Performs the actual transaction in terms of $.
        buyer["money"] = int(buyer["money"]) - int(card_to_buy["selling_price"])
        seller["money"] = int(seller["money"]) + int(card_to_buy["selling_price"])
        
        # Removes the card from the market and removes the selling information.
        market.remove(card_to_buy)
        card_to_buy.pop("seller")
        card_to_buy.pop("seller_id")
        card_to_buy.pop("selling_price")
        card_to_buy.pop("selling_start_time")
        
        # Adds the card to the buyers inventory and saves the buyer.
        buyer["inventory"].append(card_to_buy)
        buyer["market_stats"]["cards_purchased"] = buyer["market_stats"]["cards_purchased"] + 1
        saved_buyer = self.save_user(buyer)
        seller["market_stats"]["cards_sold"] = seller["market_stats"]["cards_sold"] + 1
        await self.check_for_achievements(buyer, ctx)
        if seller["id"] != 0:
            await self.check_for_achievements(seller)
        await self.record_history()
        
        # Saves the new smaller market and new richer seller.
        saved_market = self.save_market(market)
        saved_seller = self.save_user(seller)
        
        # Checks to make sure the saves completed.
        if saved_buyer != True or saved_market != True or saved_seller != True:
            self.buy.reset_cooldown(ctx)
            return print("Something went wrong with BUY!")
        
        await ctx.respond(f"Successfully purchased Card no. **{card_to_buy['num']}** from the market!")

        return await self.end_game()
    
    @market.command(description="Cancels your cards listing on the BBTCG market.")
    async def cancel(self, ctx, cardno: Option(int, description="Card no you want to cancel.")):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            return
        
        market = self.load_market()
        listing_to_cancel = next((item for item in market if int(item["num"]) == int(cardno)), None)
        
        # Checks to make sure that the user is the owner of the listing.
        if int(listing_to_cancel["seller_id"]) == int(ctx.author.id):
            
            # Removes the listing from the market, cleans off the market data, and returns the card to the users inventory.
            market.remove(listing_to_cancel)
            user = self.load_user(ctx.author.id)
            listing_to_cancel.pop("seller")
            listing_to_cancel.pop("seller_id")
            listing_to_cancel.pop("selling_price")
            user["inventory"].append(listing_to_cancel)
            
            # Saves the new market and new user.
            user_saved = self.save_user(user)
            market_saved = self.save_market(market)
            
            # Checks to make sure the save was successful.
            if user_saved != True or market_saved != True:
                return print("Something went wrong. Was unable to save user or market while canceling a listing.")
            else:
                return await ctx.respond(f"I've canceled the listing for Card no. {listing_to_cancel['num']}")
        
        else:
            return await ctx.respond("You can't cancel a listing that isn't yours!", ephemeral=True)

    @market.command(description="Immediately sells a card back to the BBTCG pool.")
    async def scrap(self, ctx, cardno: Option(int, description="Card no you want to scrap.")):
        cc = await self.channel_check(ctx, "bbtcg")
        if cc == False:
            return
        
        user = self.load_user(ctx.author.id)
        cards = self.load_cards()
        
        # Checks to make sure the user owns the specified card.
        card_to_scrap = next((item for item in user["inventory"] if int(item["num"]) == int(cardno)), None)
        if card_to_scrap == None:
            return await ctx.respond(f"You don't own that card!", ephemeral=True)
        
        # Runs an the unequip function to remove the user from the role if they are a part of it.
        await self.unequip(ctx=ctx, cardno=cardno, internal=True)
        
        # Awards the cash value of the card to the user and adjusts stats.
        scrap_price = round(int(card_to_scrap["value"]) * float(self.settings["market"]["scrap_price_mult"]))
        user["inventory"].remove(card_to_scrap)
        user["money"] = user["money"] + scrap_price
        user["market_stats"]["cards_scrapped"] = user["market_stats"]["cards_scrapped"] + 1
        
        # Adds the card back to the card pool.
        cards.append(card_to_scrap)
        
        # Saves the new user and the new card pool.
        saved_user = self.save_user(user)
        saved_cards = self.save_cards(cards)
        
        # Checks to make sure the saves were successful.
        if saved_user != True or saved_cards != True:
            return print("Something went wrong with scrapping a card.")
        else:
            await self.check_for_achievements(user, ctx)
            await self.record_history()
            return await ctx.respond(f"<@{ctx.author.id}>, I've scrapped your card and awarded you ${scrap_price}!")
    
    # UNEQUIP command - Removes a user from a card role.
    @slash_command(name="unequip", description="Unequips a BBTCG card.")
    async def bbtcg_unequip(self, ctx, cardno: Option(int, description="Card No.", Required=True)):
        await self.unequip(ctx, cardno, internal=False)
        return await ctx.respond("Card unequipped.", delete_after=3, ephemeral=True)

    # EQUIP command - Adds a user to a card role.
    @slash_command(name="equip", description="Equips a BBTCG card to your profile.")
    async def bbtcg_equip(self, message, cardno: Option(int, description="Card no.")):
        cc = await self.channel_check(message, "bbtcg")
        if cc == False:
            return print("Channel Check failed.")
        
        user = self.load_user(message.author.id)
        
        # Checks to see if the user owns the card.
        card_to_equip = next((item for item in user["inventory"] if int(item["num"]) == int(cardno)), None)
        if card_to_equip == None:
            return await message.respond("You can't equip a card that you don't own!", ephemeral=True)
        
        # Loads the current Guild the user is in so it can create and assing the correct role.
        guild = self.client.get_guild(message.guild.id)

        # Loads the roles it has created in the past.
        created_roles = self.load_roles()

        # This removes any other roles that are related to BBTCG before adding them to the desired role.
        # This ensures a user can only have a single card equipped at a time.
        for urole in message.author.roles:
            for role in created_roles:
                if urole.id == role["id"]:
                    await message.author.remove_roles(urole)

        # This determines if a new role is to be created and then creates it.
        # If not then it returns an existing role.
        role = next((item for item in guild.roles if item.name == card_to_equip["name"]), None)
        if role == None:
            color = int(card_to_equip["color"], 16)
            color = discord.Color(value=color)
            role = await guild.create_role(name=card_to_equip["name"], color=color, hoist=True, mentionable=True)

            new_role = {"role_name": role.name, "id": role.id, "card": card_to_equip}

            # Saves the newly created role for future reference.
            created_roles.append(new_role)
            saved_roles = self.save_roles(created_roles)

            if saved_roles != True:
                return print("Something went wrong. Couldn't save roles!")

        # Adds the user to the newly or previously created role.
        await message.author.add_roles(role)
        await message.respond(f"<@{message.author.id}> is now {role.name}!")

        # This is a gross process to make sure all of the roles appear in their proper order of rarity.
        # First it gets all of the roles in the server.
        guild_roles = await guild.fetch_roles()
        bbtcg_guild_roles = []

        # Then identifies which roles are part of BBTCG
        for grole in guild_roles:
            match = next((item for item in created_roles if item["id"] == grole.id), None)
            if match != None:
                # Adds the Discord role and the created role dicts together into a list.
                match = {"discord_role": grole, "created_role": match}
                bbtcg_guild_roles.append(match)
        
        # Then adds a key:value pair based on the rarity of the card.
        for object in bbtcg_guild_roles:
            if object["created_role"]["card"]["rarity"] == "Legendary":
                object["sorting_weight"] = 1
            elif object["created_role"]["card"]["rarity"] == "Epic":
                object["sorting_weight"] = 2
            elif object["created_role"]["card"]["rarity"] == "Rare":
                object["sorting_weight"] = 3
            elif object["created_role"]["card"]["rarity"] == "Common":
                object["sorting_weight"] = 4

        # This piece of magic sorts all of the roles by the sorting_weight value.
        sorted_bbtcg_guild_roles = sorted(bbtcg_guild_roles, key=lambda k: k["sorting_weight"])

        # Once prepped and sorted, we can create a bulk_position_update to update the position of all of the roles at once.
        # Role count helps maintain the sorting order.
        role_count = 1
        bulk_position_update = {}
        for object in sorted_bbtcg_guild_roles:
            guild_roles = await guild.fetch_roles()
            
            # We have to subtract 1 from the guild roles length because @everyone is a roll and take a number even though you can't interact with it.
            number_guild_roles = len(guild_roles) - 1
            
            role = object["discord_role"]
            new_position = number_guild_roles - role_count
            bulk_position_update[role] = new_position
            role_count = role_count + 1
        
        # This applies our generated bulk_position_update. If it fails, everything breaks so... please for the love of everything work.
        await guild.edit_role_positions(positions=bulk_position_update)
    
    # SLOTS command - Adds a user to a card role.
    @slash_command(name="slots", description="Plays slots for BBTCG cash! Use in #slots.")
    @check(before_invoke_channel_check)
    @dynamic_cooldown(cooldown=slots_cooldown, type=commands.BucketType.user)
    async def bbtcg_slots(self, message, spins: Option(int, description="How many spins would you like? Defaults to 20. Buy in is $5.", min_value=1, max_value=20, default=20, required=False)):

        user = self.load_user(message.author.id)

        try:
            last_played = user["slots_stats"]["time_since_last_played"]
        except:
            user["slots_stats"]["time_since_last_played"] = 0
            last_played = user["slots_stats"]["time_since_last_played"]
            
        if last_played == 0 or last_played < datetime.now() - timedelta(days=int(self.settings["slots"]["restbonus_timedelta_days"])):
            rest_bonus = True
            user["money"] = user["money"] + int(self.settings["slots"]["restbonus_amount"])
        else:
            rest_bonus = False

        user["slots_stats"]["time_since_last_played"] = datetime.now()
        user_saved = self.save_user(user)
        if user_saved != True:
            return print("Something went wrong. Unable to save user in slots.")
        user = self.load_user(message.author.id)
        
        try:
            await message.delete()
        except:
            pass

        buy_in = int(self.settings["slots"]["buyin_perspin_amount"]) * spins
        thread = await message.channel.create_thread(name=f"{message.author.name}'s Slots Match", type=discord.ChannelType.public_thread)
        if rest_bonus == True:
            await thread.send(f":tada: You just got ${self.settings['slots']['restbonus_amount']} in rest money! :tada:")
        # Loads the user and makes sure they have enough money to play.
        if user["money"] < buy_in:
            self.bot.get_application_command("slots").reset_cooldown(message)
            return await thread.send(f"You don't have enough money to play slots {spins} times! Don't worry, your cooldown wasn't triggered.")
        else:
            user["money"] -= buy_in
        
        user_saved = self.save_user(user)
        if user_saved != True:
            return print("Something went wrong. Unable to save user in slots.")

        earnings = 0
        spun = 0
        for x in range(spins):

            # This is the main logic for the game.
            possible_slots = [":shell:", ":ice_cream:", ":pineapple:", ":crab:", ":sponge:", ":snail:", ":octopus:", ":hamburger:"]

            roll1 = random.choice(possible_slots)
            roll2 = random.choice(possible_slots)
            roll3 = random.choice(possible_slots)

            # For debugging role matches.
            #roll1 = ":sponge:"
            #roll2 = ":crab:"
            #roll3 = ":octopus:"

            # SPINNING ANIMATION DISABLED DUE TO PERFORMANCE
            """rolling_msg = f"<@{message.author.id}>, rolling...\n{random.choice(possible_slots)} {random.choice(possible_slots)} {random.choice(possible_slots)}"
            msg = await message.channel.send(rolling_msg)

            # This creates the rolling messages that make it seem like slots are actually being "spun".
            for i in range(0, 3):
                await asyncio.sleep(.5)
                rolling_msg = f"<@{message.author.id}>, rolling...\n{random.choice(possible_slots)} {random.choice(possible_slots)} {random.choice(possible_slots)}"
                await msg.edit(content=rolling_msg)

            # Updates the message with what the user actually rolled.
            await asyncio.sleep(.5)"""
            # SPINNING ANIMATION DISABLED DUE TO PERFORMANCE

            final_msg = f"{roll1} {roll2} {roll3} - "
            user = self.load_user(message.author.id)
            # Tries to find a match.
            trio_roll = [":crab:", ":sponge:", ":snail:", ":octopus:"]
            roll_list = []
            for roll in [roll1, roll2, roll3]:
                if roll in trio_roll:
                    if roll not in roll_list:
                        roll_list.append(roll)
            if roll1 == roll2 == roll3:
                if roll1 in [":sponge:", ":snail:", ":octopus:", ":crab:"]:
                    # Jackpot payout!
                    earned = (int(self.settings["slots"]["buyin_perspin_amount"]) * int(self.settings["slots"]["jackpot_mult"]))
                    earnings += earned
                    await thread.send(f"{final_msg}\nYou just nailed a {int(self.settings['slots']['jackpot_mult'])}x **jackpot** of **${earned}** by getting a three of a kind with SpongeBob characters! :moneybag:")
                else:
                    # 25 times payout!
                    earned = (int(self.settings["slots"]["buyin_perspin_amount"]) * int(self.settings["slots"]["second_highest_mult"]))
                    earnings += earned
                    await thread.send(f"{final_msg}\nYou just nabbed a {int(self.settings['slots']['second_highest_mult'])}x payout of **${earned}** by getting a three of a kind! :dollar:")
            elif len(roll_list) == 3:
                # 10 times payout!
                earned = (int(self.settings["slots"]["buyin_perspin_amount"]) * int(self.settings["slots"]["third_highest_mult"]))
                earnings += earned
                await thread.send(f"{final_msg}\nYou just scored a {int(self.settings['slots']['third_highest_mult'])}x payout of **${earned}** by getting a trio of SpongeBob characters! :coin:")
            elif roll1 == roll2 or roll2 == roll3:
                # 4 times payout!
                earned = (int(self.settings["slots"]["buyin_perspin_amount"]) * int(self.settings["slots"]["fourth_highest_mult"]))
                earnings += earned
                await thread.send(f"{final_msg}\nYou just grabbed a {int(self.settings['slots']['fourth_highest_mult'])}x payout of **${earned}** by getting two in a row!")
            elif ":sponge:" in [roll1, roll2, roll3]:
                # 0.4 times payout.
                earned = math.floor((int(self.settings["slots"]["buyin_perspin_amount"]) * float(self.settings["slots"]["sponge_mult"])))
                earnings += earned
                await thread.send(f"{final_msg}\nYou got a sponge and **${earned}** of your buy-in back.")
            else:
                await thread.send(f"{final_msg}\nYou unfortunately didn't get anything, you should try again.")
            
            spun += 1
            await asyncio.sleep(1)
        
        user = self.load_user(message.author.id)
        user["money"] += earnings

        net = earnings - buy_in
        # Saves the user with their new winnings.
        if net > 0:
            await thread.send(f"You played slots {spun} times and made ${net}!")
        elif net == 0:
            await thread.send(f"You played slots {spun} times and came out even ¯\_(ツ)_/¯")
        else:
            await thread.send(f"You played slots {spun} times and lost ${str(net)[1:]}")
        
        user["slots_stats"]["slots_played"] += spun

        user_saved = self.save_user(user)
        if user_saved != True:
            return print("Something went wrong. Unable to save user in slots.")
    
    # CASH command - Prints the amount of cash a player has.
    @slash_command(name="cash", description="Shows you your current BBTCG cash.")
    async def bbtcg_cash(self, message):
        user = self.load_user(message.author.id)

        await message.respond(f"You have **${user['money']}**.", ephemeral=True)
    
    # STATS command - Command to see the status of the current game.
    @slash_command(name="stats", description="Shows you the current BBTCG game's standings.")
    async def bbtcg_stats(self, message):
        # Checks for the correct channel.
        cc = await self.channel_check(message, "bbtcg")
        if cc == False:
            return

        # Loads all of the necessary information.
        cards = self.load_cards()
        market = self.load_market()
        users = []
        for user_file in os.listdir(self.BBTCGdir + "users//"):
            if user_file != "0.pickle":
                user = self.load_user(str(user_file).replace(".pickle", ""))
                users.append(user)

        # Parcess all of the info into actual values.
        cards_left = len(cards)
        cards_in_market = len(market)
        total_users = len(users)

        all_user_cards = []
        if len(users) != 0:
            for user in users:
                try:
                    for c in user["inventory"]:
                        all_user_cards.append(c)
                except:
                    print(user)
        total_user_cards = len(all_user_cards)
        richest_player = None
        most_cards_player = None
        most_achievements = None
        most_stolen = None
        most_slots_played = None
        most_cards_purchased = None
        
        if len(users) != 0:
            for player in users:
                # Richest Player Check
                if richest_player == None:
                    richest_player = player
                else:
                    if int(player["money"]) > int(richest_player["money"]):
                        richest_player = player
                
                # Most Cards Check
                if most_cards_player == None and len(player["inventory"]) > 0:
                    most_cards_player = player
                elif most_cards_player != None:
                    if len(player["inventory"]) > len(most_cards_player["inventory"]):
                        most_cards_player = player
                
                # Most Achievements Check
                if most_achievements == None and len(player["earned_achievements"]) > 0:
                    most_achievements = player
                elif most_achievements != None:
                    if len(player["earned_achievements"]) > len(most_achievements["earned_achievements"]):
                        most_achievements = player
                
                # Most Stolen Check
                if most_stolen == None and player["shop_stats"]["steals_purchased"] > 0:
                    most_stolen = player
                elif most_stolen != None:
                    if player["shop_stats"]["steals_purchased"] > most_stolen["shop_stats"]["steals_purchased"]:
                        most_stolen = player
                
                # Most Slots Played Check
                if most_slots_played == None and player["slots_stats"]["slots_played"] > 0:
                    most_slots_played = player
                elif most_slots_played != None:
                    if player["slots_stats"]["slots_played"] > most_slots_played["slots_stats"]["slots_played"]:
                        most_slots_played = player
                
                # Most Cards Purchased Check
                if most_cards_purchased == None and player["shop_stats"]["cards_purchased"] > 0:
                    most_cards_purchased = player
                elif most_cards_purchased != None:
                    if player["shop_stats"]["cards_purchased"] > most_cards_purchased["shop_stats"]["cards_purchased"]:
                        most_cards_purchased = player


        # Gets the Discord users so we can retrieve their current names.
        guild = message.channel.guild
        if richest_player != None:
            richest_player_disc_user = await guild.fetch_member(int(richest_player["id"]))

        if most_cards_player != None:
            most_cards_player_disc_user = await guild.fetch_member(int(most_cards_player["id"]))
        
        if most_stolen != None:
            most_stolen_disc_user = await guild.fetch_member(int(most_stolen["id"]))
        
        if most_achievements != None:
            most_achievements_disc_user = await guild.fetch_member(int(most_achievements["id"]))
        
        if most_slots_played != None:
            most_slots_played_disc_user = await guild.fetch_member(int(most_slots_played["id"]))
        
        if most_cards_purchased != None:
            most_cards_purchased_disc_user = await guild.fetch_member(int(most_cards_purchased["id"]))

        #print(richest_player_disc_user)
        #print(most_cards_player_disc_user)
        # Generates an embed with all of the information.            
        embed=discord.Embed(title="BBTCG Current Stats", color=0x0bf4e4)
        embed.add_field(name="Cards Remaining in Pool", value=cards_left, inline=True)
        embed.add_field(name="Cards in Market", value=cards_in_market, inline=True)
        embed.add_field(name="Player Owned Cards", value=total_user_cards, inline=True)
        embed.add_field(name="Total Players", value=total_users, inline=True)

        if richest_player != None:
            try:
                embed.add_field(name="Moneybags", value=f"{richest_player_disc_user.name} - ${richest_player['money']}", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse richest_player: {e}"
                self.bot.logger.log.error(msg)
        
        if most_cards_player != None:
            try:
                embed.add_field(name="Collector", value=f"{most_cards_player_disc_user.name} - {len(most_cards_player['inventory'])} cards", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse most_cards_player: {e}"
                self.bot.logger.log.error(msg)
        
        if most_stolen != None:
            try:
                embed.add_field(name="Bandit", value=f"{most_stolen_disc_user.name} - {most_stolen['shop_stats']['steals_purchased']} cards stolen", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse most_stolen: {e}"
                self.bot.logger.log.error(msg)
        
        if most_achievements != None:
            try:
                embed.add_field(name="Over Achiever", value=f"{most_achievements_disc_user.name} - {len(most_achievements['earned_achievements'])} achievements", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse most_achievements: {e}"
                self.bot.logger.log.error(msg)
        
        if most_cards_purchased != None:
            try:
                embed.add_field(name="Repeat Customer", value=f"{most_cards_purchased_disc_user.name} - {most_cards_purchased['shop_stats']['cards_purchased']} cards purchased", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse most_cards_purchased: {e}"
                self.bot.logger.log.error(msg)
        
        if most_slots_played != None:
            try:
                embed.add_field(name="Gambler", value=f"{most_slots_played_disc_user.name} - {most_slots_played['slots_stats']['slots_played']} rounds of slots played", inline=False)
            except Exception as e:
                msg = f"[BBTCG] Couldn't parse most_slots_played: {e}"
                self.bot.logger.log.error(msg)
        
        # Sends the embed.
        return await message.respond(embed=embed)

     # STORE command - Opens a store menu to purchase things.
    @slash_command(name="store", description="Opens the BBTCG store. Use in #bbtcg")
    @check(before_invoke_channel_check)
    @cooldown(10, 3600, commands.BucketType.user)
    async def bbtcg_store(self, ctx):
        
        def load_user():
            # Loads users and cards
            user = self.load_user(ctx.author.id)
            return user
        
        user = load_user()
        cards = self.load_cards()

        # Calculates the draw_card_price by multipling the average value of all remaining cards by 1.1.
        if len(cards) > 0:
            draw_card_price = 0
            for c in cards:
                draw_card_price = draw_card_price + c["value"]

            draw_card_price = round((draw_card_price // len(cards)) * float(self.settings["store"]["draw_price_mult"]))
        else:
            draw_card_price = "DISABLE"

        # Calculates the steal_card_price by multiplying the average value of all player owned cards by 1.25.
        user_card_value = 0
        user_card_count = 0
        user_files = os.listdir(self.BBTCGdir + "users//")
        # This list is used when displaying targeted stealable accounts.
        stealable_users = []
        for user_file in user_files:
            if user_file == "0.pickle":
                pass
            elif str(user["id"]) in user_file:
                pass
            else:
                temp_user = self.load_user(user_file.replace(".pickle", ""))
                if len(temp_user["inventory"]) <= 1 or temp_user["id"] == user["id"]:
                    continue
                stealable_users.append(temp_user)
                for c in temp_user["inventory"]:
                    user_card_value = user_card_value + c["value"]
                    user_card_count += 1
        
        if user_card_value == 0:
            random_steal_price = "DISABLE"
        else:
            random_steal_price = round((user_card_value // user_card_count) * float(self.settings["store"]["randsteal_price_mult"]))

        # This preps all of the variables for the store buttons.
        if draw_card_price == "DISABLE":
            store_draw_card_label = "No Cards to Draw"
            store_draw_card_style = discord.ButtonStyle.grey
            store_draw_card_disabled = True
        
        elif int(draw_card_price) > int(user["money"]):
            store_draw_card_label = f"Draw a Card - ${draw_card_price}"
            store_draw_card_style = discord.ButtonStyle.grey
            store_draw_card_disabled = True
        
        else:
            store_draw_card_label = f"Draw a Card - ${draw_card_price}"
            store_draw_card_style = discord.ButtonStyle.blurple
            store_draw_card_disabled = False
        
        if random_steal_price == "DISABLE":
            random_steal_price_label = "No Stealable Cards"
            random_steal_price_style = discord.ButtonStyle.grey
            random_steal_price_disabled = True
        
        elif int(random_steal_price) > int(user["money"]):
            random_steal_price_label = f"Steal a Card - ${random_steal_price}"
            random_steal_price_style = discord.ButtonStyle.grey
            random_steal_price_disabled = True
        
        else:
            random_steal_price_label = f"Steal a Card - ${random_steal_price}"
            random_steal_price_style = discord.ButtonStyle.danger
            random_steal_price_disabled = False
        
        if stealable_users == []:
            targeted_steal_list_disabled = True
        else:
            targeted_steal_list_disabled = False

        # This is the Store class which houses the button functions.
        class Store(discord.ui.View):
            def __init__(self, user):
                super().__init__()
                #self.settings = BBTCG_Settings.read_settings(self=self)

                # We need this variable to refer to the users action later.
                self.value = None
                self.user = user

            async def interaction_check(self, interaction: discord.Interaction) -> bool:
                user = load_user()
                if int(self.user["money"]) != int(user["money"]):
                    return False
                else:
                    return True
            
            async def on_check_failure(self, interaction: discord.Interaction) -> None:
                self.clear_items()
                await interaction.response.edit_message(content="Your balance has changed! Please use /store again!", view=self)
                self.stop()
                return
            
            # These buttons are nearly identical, just return different values and look different. 
            # The important things is the self.stop(). This will close the interaction after a successful button press.
            @discord.ui.button(label=store_draw_card_label, style=store_draw_card_style, disabled=store_draw_card_disabled)
            async def store_draw_card(self, button: discord.ui.Button, interaction: discord.Interaction):
                
                # Checks if the user has enough cash.
                if self.user["money"] < draw_card_price:
                    await ctx.respond("You don't have enough cash for that!", ephemeral=True)
                else:
                    self.value = {"action": "DRAW"}
                    self.clear_items()
                    await interaction.response.edit_message(content="Thanks for the purchase!", view=self)
                    self.stop()
            
            @discord.ui.button(label=random_steal_price_label, style=random_steal_price_style, disabled=random_steal_price_disabled)
            async def store_steal_card(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.user = load_user()
                
                # Checks if the user has enough cash.
                if self.user["money"] < random_steal_price:
                    await ctx.respond("You don't have enough cash for that!", ephemeral=True)
                else:
                    self.value = {"action": "STEAL"}
                    self.clear_items()
                    await interaction.response.edit_message(content="Thanks for the purchase!", view=self)
                    self.stop()
            
            @discord.ui.select(disabled=targeted_steal_list_disabled, options=[discord.SelectOption(label="Select to load targets..", value="load")], placeholder="Select a user to steal from...")
            async def store_targeted_steal_card(self, view: discord.ui.Select, interaction: discord.Interaction):
                
                if view._selected_values[0] == "load":
                    view.options = []
                    for stealable_user in stealable_users:
                        user_card_count = 0
                        user_card_value = 0
                        for c in stealable_user["inventory"]:
                            user_card_value += c["value"]
                            user_card_count += 1
                        targeted_steal_price = round((user_card_value // user_card_count) * 1.5)
                        if self.user["money"] < targeted_steal_price:
                            continue
                        description = f"${targeted_steal_price}"
                        temp_discord_user = await interaction.channel.guild.fetch_member(stealable_user["id"])
                        view.add_option(label=str(temp_discord_user.name), value=str(temp_discord_user.id) + " " + str(targeted_steal_price), description=str(description))
                    
                    await interaction.response.edit_message(view=self)
                else:
                    self.user = load_user()
                    # Checks if the user has enough cash.
                    if self.user["money"] < random_steal_price:
                        await ctx.respond("You don't have enough cash for that!", ephemeral=True)
                    
                    self.value = {"action": "TARGETED_STEAL", "user": str(view._selected_values[0]).split(" ")[0], "price": str(view._selected_values[0]).split(" ")[1]}
                    self.clear_items()
                    await interaction.response.edit_message(content="Thanks for the purchase!", view=self)
                    self.stop()
                

        # Establishes the Store class as a view.
        view = Store(user=user)


        # Preps the store menu message and sends it along with the view.
        store_msg = f"============\nBBTCG Store\nYou have **${user['money']}**! You can either:\n" \
                    "`1. Draw a card immediately without using your cooldown.`\n" \
                    "`2. Steal a random card from a random player. (equipped cards are safe)`\n" \
                    "`3. Select a user from the list to steal a random card from them. (equipped cards are safe)`\n"
        await ctx.respond(store_msg, view=view, ephemeral=True)

        # This waits until the view is registered as finished (when self.stop() is called.) or the view reached its Timeout.
        await view.wait()

        # This is where the actual store actions happen.
        if view.value == None:
            # None generally means the view reached its timeout and did nothing.
            pass

        elif view.value["action"] == "DRAW":
            
            # Subtracts the purchase price from the user and adjusts their stats.
            user["money"] = user["money"] - draw_card_price
            user["shop_stats"]["cards_purchased"] = user["shop_stats"]["cards_purchased"] + 1
            saved_user = self.save_user(user)

            # Checks for earned achievements.
            await self.check_for_achievements(user, ctx)
            await self.record_history()

            if saved_user != True:
                print("Something went wrong. Was unable to save user in store - draw a card.")
            return await self.draw_card(ctx)
        
        elif view.value["action"] == "STEAL":

            # Picks a random user and random card from the user.
            valid_target_cards = []

            # Loads previously created roles.
            created_roles = self.load_roles()

            for user_file in user_files:
                
                # Ensure the user doesn't steal a card from themselves.
                if user_file.replace(".pickle", "") in ["0", str(user["id"])]:
                    continue
                
                # Loads the target to extract card information.
                target_user = self.load_user(user_file.replace(".pickle", ""))
                
                # Users with only 1 card as also safe.
                if len(target_user["inventory"]) <= 1:
                    continue
                
                for c in target_user["inventory"]:
                    
                    # Checks if the card even has a role associated to it.
                    c_role = next((item for item in created_roles if item["card"] == c), None)
                    
                    # If it does, check to make sure it's not equipped by the target user.
                    # This makes equiped cards safe.
                    if c_role != None:
                        target_discord_user = await ctx.channel.guild.fetch_member(int(target_user["id"]))
                        target_discord_user_role_ids = []
                        for role in target_discord_user.roles:
                            target_discord_user_role_ids.append(role.id)
                        if int(c_role["id"]) in target_discord_user_role_ids:
                            continue
                        else:
                            valid_target_card = {"target_user": target_user, "target_card": c}
                            valid_target_cards.append(valid_target_card)
                    
                    # If there is no role, then it can't be equipped, therefore, it's a valid card.
                    else:
                        valid_target_card = {"target_user": target_user, "target_card": c}
                        valid_target_cards.append(valid_target_card)
            
            # This shouldn't happen but just incase, there's a catch for it.
            if valid_target_cards == []:
                return await ctx.respond("I wasn't able to find any valid cards to steal! Maybe try again later. You weren't charged.", ephemeral=True)

            # Actually picks the card to steal.
            stolen_card_info = random.choice(valid_target_cards)
            target_card = stolen_card_info["target_card"]
            target_user = stolen_card_info["target_user"]

            # Subtracts the purchase price from the user and adjusts their stats.
            user["money"] = user["money"] - random_steal_price
            user["shop_stats"]["steals_purchased"] = user["shop_stats"]["steals_purchased"] + 1
            user["shop_stats"]["cards_stolen"].append(target_card["num"])

            # Removes the card from the random_target.
            target_user["inventory"].remove(target_card)
            saved_target = self.save_user(target_user)
            if saved_target != True:
                print("Something went wrong. Was unable to steal a card from:")
                print(target_user)
                print(target_card)
            else:
                await self.check_for_achievements(target_user)
                await self.record_history()

            # Adds the card to the users inventory.
            user["inventory"].append(target_card)
            saved_user = self.save_user(user)
            if saved_user != True:
                print("Something went wrong. Was unable to save stolen card to:")
                print(user)
                print(target_card)
            else:
                await self.check_for_achievements(user, ctx)
                await self.record_history()
            
            # Generates an embed to let the server know that someone stole a card!
            embed = self.generate_card(target_card)
            return await ctx.respond(f"<@{ctx.author.id}>, just stole a card from <@{target_user['id']}>:", embed=embed)
        
        elif view.value["action"] == "TARGETED_STEAL":

            # Picks a random user and random card from the user.
            valid_target_cards = []

            # Loads previously created roles.
            created_roles = self.load_roles()
            
            # Loads the target to extract card information.
            target_user = self.load_user(view.value["user"])
            
            for c in target_user["inventory"]:
                
                # Checks if the card even has a role associated to it.
                c_role = next((item for item in created_roles if item["card"] == c), None)
                
                # If it does, check to make sure it's not equipped by the target user.
                # This makes equiped cards safe.
                if c_role != None:
                    target_discord_user = await ctx.channel.guild.fetch_member(int(target_user["id"]))
                    target_discord_user_role_ids = []
                    for role in target_discord_user.roles:
                        target_discord_user_role_ids.append(role.id)
                    if int(c_role["id"]) in target_discord_user_role_ids:
                        continue
                    else:
                        valid_target_card = {"target_user": target_user, "target_card": c}
                        valid_target_cards.append(valid_target_card)
                
                # If there is no role, then it can't be equipped, therefore, it's a valid card.
                else:
                    valid_target_card = {"target_user": target_user, "target_card": c}
                    valid_target_cards.append(valid_target_card)
            
            # This shouldn't happen but just incase, there's a catch for it.
            if valid_target_cards == []:
                return await ctx.respond("I wasn't able to find any valid cards to steal! Maybe try again later. You weren't charged.", ephemeral=True)

            # Actually picks the card to steal.
            stolen_card_info = random.choice(valid_target_cards)
            target_card = stolen_card_info["target_card"]
            target_user = stolen_card_info["target_user"]

            # Subtracts the purchase price from the user and adjusts their stats.
            user["money"] = user["money"] - int(view.value["price"])
            user["shop_stats"]["steals_purchased"] = user["shop_stats"]["steals_purchased"] + 1
            user["shop_stats"]["cards_stolen"].append(target_card["num"])

            # Removes the card from the random_target.
            target_user["inventory"].remove(target_card)
            saved_target = self.save_user(target_user)
            if saved_target != True:
                print("Something went wrong. Was unable to steal a card from:")
                print(target_user)
                print(target_card)
            else:
                await self.check_for_achievements(target_user)
                await self.record_history()

            # Adds the card to the users inventory.
            user["inventory"].append(target_card)
            saved_user = self.save_user(user)
            if saved_user != True:
                print("Something went wrong. Was unable to save stolen card to:")
                print(user)
                print(target_card)
            else:
                await self.check_for_achievements(user, ctx)
                await self.record_history()
        
            # Generates an embed to let the server know that someone stole a card!
            embed = self.generate_card(target_card)
            return await ctx.respond(f"<@{ctx.author.id}>, just sniped a card from <@{target_user['id']}>:", embed=embed)

def setup(client):
    client.add_cog(BBTCG(client))