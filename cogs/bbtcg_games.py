import discord
from discord.commands import slash_command, Option  # Importing the decorator that makes slash commands.
from discord.ext.commands.core import check
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, button, Item, Button
import asyncio
from .bbtcg import BBTCG

class BBTCG_Games(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
        self.BBTools = BBTCG
        self.BBTCGdir = "files//BBTCG//"
    
    # This is a channel check that occurs before the command is invoked
    # which prevents unintentional cooldowns.
    def before_invoke_channel_check(ctx):
        if str(ctx.channel.type) == "private":
            return False
        if ctx.command.name == "tictactoe" or ctx.command.name == "cointoss":
            return ctx.channel.name == "games"
    
    # This handles inviting someone to play a game.
    async def invite_p2(self, host, guest, ctx, game, bet):
        
        # Prevents people from placing negative bets.
        if int(bet) < 0:
            return await ctx.interaction.edit_original_message(content="Your bet must be a positive number.")

        guest_user = self.BBTools.load_user(self, guest.id)
        host_user = self.BBTools.load_user(self, host.id)

        # Prevents the host from betting money they don't have.
        if int(host_user["money"]) < bet:
            return await ctx.interaction.edit_original_message(content="You can't bet more than you have.")
                
        # Creates the view that will be sent.
        class Invite(discord.ui.View):
            def __init__(self, guest_user):
                super().__init__()

                # This value holds the accept/reject status.
                self.value = None

            # This prevents the guest from accepting bets if they don't have enough money by altering the disabled state of the Accept button.
            if int(guest_user["money"]) < bet:
                accept_button_disabled = True
                accept_button_label = "Insufficient Funds"
            else:
                accept_button_disabled = False
                accept_button_label = f"Accept - ${bet}"

            # This is the accept button.
            @button(label=accept_button_label, custom_id="ACCEPT", style=ButtonStyle.success, disabled=accept_button_disabled)
            async def accept_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.clear_items()
                msg = interaction.message
                await msg.delete()
                self.value = "ACCEPT"
                self.stop()
            
            # This is the reject button.
            @button(label="Reject", custom_id="REJECT", style=ButtonStyle.danger)
            async def reject_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.clear_items()
                msg = interaction.message
                await msg.delete()
                self.value = "REJECT"
                self.stop()
        
        # Creates an instance of the invite view and passes it the guest user.
        view = Invite(guest_user=guest_user)

        # This sends the guest player thier invite and the view with the accept/reject buttons.
        await guest.send(f"**<@{host.id}>** has invited you to a game of {game}! The bet is **${bet}**!\nYou have **${guest_user['money']}**", view=view)

        # Waits until the view is "finished" before continuing.
        await view.wait()

        # Evals the result of the view.value to see if the user accepted the game or rejected the game.
        if view.value == None:
            await ctx.interaction.edit_original_message(content=f"{guest.name} didn't respond.")
        elif view.value == "REJECT":
            await ctx.interaction.edit_original_message(content=f"{guest.name} refused your invite.")
        else:
            # This triggers if the user accepts the game.
            return view.value

    # This handles pre-game checks to make sure the game would be valid.
    async def pregame_check(self, ctx, against: discord.User, bet: int):
        host = ctx.author
        guest = against

        # Checks to see if the host is trying to invite themselves to a game.
        if host == guest:
            msg = {"result": False, "reason": "You can't play yourself."}
            return msg
        
        # Loads the hosts user file to check if they have sufficient funds to place their bet.
        host_user = self.BBTools.load_user(self, host.id)
        if host_user["money"] < bet:
            msg = {"result": False, "reason": "You can't bet more money than you currently have."}
            return msg
        
        # If everything is good, the game can continue.
        return {"result": True}

    # COIN TOSS - Slash command
    """@slash_command(name="cointoss", description="Play a Coin Toss game for greater and greater rewards!", guild_ids=[389818215871676418])
    @check(before_invoke_channel_check)
    async def cointoss(self, ctx):
        
        player = ctx.author
        player_user = self.load_user(ctx.author.id)

        if player_user["money"] < 10:
            return await ctx.respond("You don't have enough money to play Coin Toss. The buy-in is $10.")
        else:
            await ctx.delete()

        # This creates the thread channel the game takes place in.
        game_thread = await ctx.channel.create_thread(name=f"{player.name}: COIN TOSS",  type=discord.ChannelType.public_thread, auto_archive_duration=60)
        
        class ct(discord.ui.View):
            def __init__(self, *items: Item, timeout: float = 120, player: discord.User, game_thread):
                super().__init__(*items, timeout=timeout)
                self.player = player
                self.game_thread = game_thread
                self.round = 1
                self.multiplier = 3
                self.buyin = 10
                self.value = None
                self.inter = None

            @button(label="Flip", style=ButtonStyle.danger, disabled=False, custom_id="flip", row=0)
            async def flip(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.flip_callback(button, interaction)
            
            @button(label="Stay", style=ButtonStyle.success, disabled=False, custom_id="stay", row=0)
            async def stay(self, button: discord.ui.Button, interaction: discord.Interaction):
                pass
            
            async def flip_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
                flip = random.choice([":arrow_up:", ":arrow_down:"])
                if flip == ":arrow_up:":
                    self.buyin  *= self.multiplier
                    self.multiplier += 1
                    self.round += 1
                    await interaction.response.edit_message(content=f"Round {self.round}\nCurrent pot: **${self.buyin}**", view=self)
                else:
                    self.clear_items()
                    await interaction.response.edit_message(content=f"{flip} Sorry, you lose! You lasted {self.round} rounds!", view=self)
                    self.buyin = 0
                    self.value = "LOST"
                    self.inter = interaction
                    self.stop()
            async def stay_callback(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.value = "STAY"
                self.stop()
        
        class ctplayagain(discord.ui.View):
            def __init__(self, *items: Item, timeout: float = 20, game_thread, inter: discord.Interaction):
                super().__init__(*items, timeout=timeout)
                self.game_thread = game_thread
                self.inter = inter
                self.value = None
            
            async def on_timeout(self):
                self.value = "PASS"
            
            @button(label="Play Again?", style=ButtonStyle.blurple, custom_id="play_again")
            async def play_again(self, button:discord.ui.Button, interaction: discord.Interaction):
                self.value = "PLAY AGAIN"
                self.clear_items()
                await self.inter.delete_original_message()
                await interaction.response.edit_message(content="New game starting...", view=self)
                self.stop()
        while True:
            await game_thread.purge(limit=1)
            cointoss = ct(player=player, game_thread=game_thread)
            await game_thread.send(content="Round 1", view=cointoss)
            timeout = await cointoss.wait()
            
            if cointoss.value == "LOST":
                ctpa = ctplayagain(game_thread=game_thread, inter=cointoss.inter)
                await game_thread.send(view=ctpa)
                timeout = await ctpa.wait()
                print(timeout)
                if timeout == True:
                    break
                elif ctpa.value == "PLAY AGAIN":
                    pass"""

    # TIC TAC TOE - Slash command
    @slash_command(name="tictactoe", description="Play a game of TicTacToe against other players for BBTCG Cash!")
    @check(before_invoke_channel_check)
    async def tictactoe(self, ctx, against: Option(discord.User, "Who do you want to play against?"), bet: Option(int, "How much BBTCG cash are you betting?")):

        pregame_check = await self.pregame_check(ctx, against, bet)
        if pregame_check["result"] == False:
            return await ctx.respond(f"{pregame_check['reason']}", ephemeral=True)
        
        # Sets player1 as the Guest (who goes first) and player2 as the host (who started the game).
        player2 = ctx.author
        player1 = against

        # Placeholder response while the guest accepts or rejects the invite (initial interactions require a response within 3 seconds or they'll timeout)
        await ctx.respond(f"Inviting {player1.name}...", ephemeral=True)

        # This starts the invite process and makes sure the guest accepts the game before continuing.
        mp = await self.invite_p2(player2, player1, ctx, "Tic Tac Toe", bet)
        if mp != "ACCEPT":
            return

        # This is the main login for Tic Tac Toe with all of the required buttons, win conditions, etc.
        class ttt_board(discord.ui.View):

            def __init__(self, *items: Item, timeout: float = 120, player1: discord.User, player2: discord.User, game_thread):
                super().__init__(*items, timeout=timeout)
                self.player1 = player1
                self.player2 = player2
                self.game_thread = game_thread
                self.winner = None
                self.loser = None
                self.current_turn_player = None
                self.last_player = None
            
            async def on_timeout(self):
                self.winner = {"TIMEOUT_LOSER": self.current_turn_player, "TIMEOUT_WINNER": self.last_player}
            
            # These are all the required buttons for Tic Tac Toe
            # I may be able to make this look better if I can figure out how to generate buttons in a loop.

            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_0", row=0)
            async def b0(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_1", row=0)
            async def b1(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_2", row=0)
            async def b2(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_3", row=1)
            async def b3(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_4", row=1)
            async def b4(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_5", row=1)
            async def b5(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_6", row=2)
            async def b6(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_7", row=2)
            async def b7(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_8", row=2)
            async def b8(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction)
            
            # The main callback when any of the buttons are pressed.
            async def ttt_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):
                
                # This section checks to make sure whoever clicked a button is allowed to take a turn.
                # IF clicker's turn
                if str(interaction.user.id) in str(interaction.message.content):
                    pass
                # IF clicker isn't player1 or 2
                elif interaction.user.id != self.player1.id and interaction.user.id != self.player2.id:
                    await interaction.response.send_message(content=f"<@{interaction.user.id}>, this isn't your game! If you'd like to start one, use /tictactoe in #bbtcg_games.", ephemeral=True)
                    return False
                # IF it's not clickers turn
                else:
                    await interaction.response.send_message(content=f"<@{interaction.user.id}>, it's not your turn!", ephemeral=True)
                    return False

                # This changes the buttons state with the correct emoji
                # PLAYER1 (GUEST) is ALWAYS X
                # PLAYER2 (HOST) is ALWAYS O
                if interaction.user == self.player1:
                    button.emoji = "❌"
                elif interaction.user == self.player2:
                    button.emoji = "⭕"
                
                # This determins who's turn it is next
                players = [self.player1.id, self.player2.id]
                players.remove(interaction.user.id)

                # Updates the message with the new button states and turn
                self.current_turn_player = players[0]
                self.last_player = interaction.user.id
                await interaction.response.edit_message(content=f"<@{players[0]}>'s turn..", view=self)
                
                # This starts the process of checking to see if anyone has won the game and runs at every valid button click
                # First gathers all of the button states
                current_states = {} 
                for b in self.children:
                    try:
                        current_states = {**current_states, b.custom_id: b.emoji.name}
                    except:
                        # If the button is empty, the None emoji will not have a .name
                        current_states = {**current_states, b.custom_id: b.emoji}
                
                # Starts the find_winner function
                winner = self.find_winner(current_states)

                # IF there is a winner or a draw it ends the game and stops listening to button clicks.
                if winner == "DRAW":
                    await self.game_thread.send(f"It's a cat's game! Everyone keeps their bet.")
                    self.winner = winner
                    self.stop()
                elif winner != None:
                    await self.game_thread.send(content=f"<@{winner.id}> has won the game, taking the **${bet}** pot!")
                    self.winner = winner
                    self.stop()
            
            # This checks the current state of the game to win conditions
            def find_winner(self, current_states):
                # All possible winning matches for Tic Tac Toe
                winning_matches = [
                    ["ttt_0", "ttt_1", "ttt_2"],
                    ["ttt_3", "ttt_4", "ttt_5"],
                    ["ttt_6", "ttt_7", "ttt_8"],
                    ["ttt_0", "ttt_3", "ttt_6"],
                    ["ttt_1", "ttt_4", "ttt_7"],
                    ["ttt_2", "ttt_5", "ttt_8"],
                    ["ttt_0", "ttt_4", "ttt_8"],
                    ["ttt_2", "ttt_4", "ttt_6"]    
                ]

                # This builds sets of buttons that are all X's and all O's
                current_x = []
                current_o = []

                for state in current_states:
                    if current_states[state] == "❌":
                        current_x.append(state)
                    elif current_states[state] == "⭕":
                        current_o.append(state)

                # Simply checks to see if any of the winning sets are contained in the current sets
                # If so it declares the winner and loser
                for winning_match in winning_matches:
                    if all(elem in current_x for elem in winning_match):
                        self.loser = self.player2
                        return self.player1
                    elif all(elem in current_o for elem in winning_match):
                        self.loser = player1
                        return self.player2
                
                # IF all buttons contain X's or O's and no winning match is present, it's a draw.
                if not None in current_states.values():
                    return "DRAW"
                else:
                    return None
        
        # This creates the thread channel the game takes place in.
        game_thread = await ctx.channel.create_thread(name=f"{player1.name} VS {player2.name}: TIC TAC TOE",  type=discord.ChannelType.public_thread, auto_archive_duration=60)
        await game_thread.send("Each player has a 2 minute turn time per turn.")

        # This creates the game view itself.
        gameboard = ttt_board(player1=player1, player2=player2, game_thread=game_thread, timeout=120)

        # Sends the new game view into the thread thus actually starting the game.
        msg = await game_thread.send(content=f"<@{player1.id}> goes first!", view=gameboard)

        # This gets the game url for the players to instantly jump to the game.
        game_url = Button(label="Join Game", style=ButtonStyle.blurple, url=msg.jump_url)
        jump_url = View(game_url)
        await player1.send(content=f"Tic Tac Toe VS <@{player2.id}>:", view=jump_url)
        await ctx.interaction.edit_original_message(content="The game has started!", view=jump_url)
        
        # This waits until the game is over.
        timeout = await gameboard.wait()

        # Once the game is over this checks to see if a winner has been declared and transfers the money.
        # Also handles the winner and loser incase of timeout.
        if timeout == True:
            # For some reason, the timeout occurs past this point so it needs some time to return the correct variables.
            # Thus the sleep.
            await asyncio.sleep(2)
            winner_user = self.BBTools.load_user(self, uid=gameboard.winner["TIMEOUT_WINNER"])
            loser_user = self.BBTools.load_user(self, uid=gameboard.winner["TIMEOUT_LOSER"])
            await game_thread.send(f"<@{gameboard.winner['TIMEOUT_LOSER']}> failed to take their turn in the allowed time and forfeits the match!\n" \
                                    f"<@{gameboard.winner['TIMEOUT_WINNER']}> takes the pot of **${bet}**!")
        elif timeout == False and gameboard.winner != "DRAW":
            winner_user = self.BBTools.load_user(self, uid=gameboard.winner.id)
            loser_user = self.BBTools.load_user(self, uid=gameboard.loser.id)
            
            winner_user["money"] += bet
            loser_user["money"] -= bet

            # This prevents users cash from going negative if the user spent enough money to go negative from a loss during a game.
            if loser_user["money"] < 0:
                loser_user["money"] = 0

            # Saves the winner and loser with their new cash amounts.
            loser_save = self.BBTools.save_user(self, loser_user)
            if loser_save != True:
                return print("[BBTCG GAMES] [TTT] Something went wrong saving the loser.")

            winner_save = self.BBTools.save_user(self, winner_user)
            if winner_save != True:
                print("[BBTCG GAMES] [TTT] Something went wrong saving the winner.")
        
        # Waits 30 seconds before archiving the game thread. This prevents clutter.
        await asyncio.sleep(30)
        await game_thread.archive(locked=True)
    
    # Activity Reward System!!
    # This system automatically rewards players for spending time in activities while in Bikini Bottom.
    @commands.Cog.listener()
    async def on_ready(self):
        
        # First ID is Watch Together.
        activity_ids = [
            880218394199220334,
            755827207812677713,
            773336526917861400,
            814288819477020702,
            832012774040141894,
            879864070101172255,
            879863881349087252,
            832012854282158180,
            878067389634314250,
            902271654783242291,
            879863686565621790,
            879863976006127627,
            852509694341283871,
            832013003968348200,
            832025144389533716,
            945737671223947305,
            903769130790969345,
            947957217959759964,
            976052223358406656,
            950505761862189096,
            1006584476094177371
        ]
        
        while True:
            for guild in self.bot.guilds:
                for member in guild.members:
                    try:

                        # Checks if user is in ANY activites.
                        if hasattr(member, "activity"):

                            if member.activity == None:
                                continue

                            # Checks if the activity is a Discord Activites Game.
                            if hasattr(member.activity, "application_id"):

                                current_act = member.activity

                                # Checks to see if we've set a custom profile for the activity.
                                ref_act = None
                                ref_act = [x for x in activity_ids if x == int(current_act.application_id)]

                                # Checks if the party size is equal to or larger than 2.
                                if "size" in current_act.party:
                                    party_size = current_act.party["size"][0]
                                    if party_size >= 2:
                                        if hasattr(member.voice, "channel"):
                                            if member.voice.channel.guild.id == guild.id:

                                                # If all of the above passes this means the user is playing a Discord Activity with 1 or more other players in same Guild as Gary.
                                                # Then awards the player the appropriate amount of BBTCG Cash.
                                                user = self.BBTools.load_user(self, uid=member.id)
                                                if ref_act[0] == 880218394199220334:
                                                    user["money"] += 3
                                                    #print(f"{member.name} was awarded $3 for participating in {current_act.name}!")
                                                elif ref_act != None:
                                                    user["money"] += 5
                                                    #print(f"{member.name} was awarded $5 for participating in {current_act.name}!")

                                                #print(current_act.to_dict())
                                                #print(ref_act[0])
                                                self.BBTools.save_user(self, user=user)
                    except Exception as e:
                        print("[BBTCG Games] Something went wrong in the Activity Reward System!")
                        print(e)

            # This check runs every 30 seconds.
            await asyncio.sleep(30)

# Standard bot setup.
def setup(bot):
    bot.add_cog(BBTCG_Games(bot))