from dis import disco
import discord
from discord.commands import slash_command, user_command  # Importing the decorator that makes slash commands.
from discord.ext import commands
from discord import ButtonStyle
from discord.ui import View, button, Item

class BBTCG_Games(commands.Cog):
    # Inits the bot instance so we can do things like send messages and get other Discord information.
    def __init__(self, bot):
        self.bot = bot
    
    async def invite_p2(self, p1, p2, ctx, game):
        
        class Invite(discord.ui.View):
            def __init__(self, *items: Item, timeout: float = 180):
                super().__init__()

                self.value = None
            
            @button(label="Accept", custom_id="ACCEPT", style=ButtonStyle.success)
            async def accept_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.clear_items()
                await interaction.response.edit_message(content="Game on!", view=self)
                self.value = "ACCEPT"
                self.stop()
            
            @button(label="Reject", custom_id="REJECT", style=ButtonStyle.danger)
            async def reject_invite(self, button: discord.ui.Button, interaction: discord.Interaction):
                self.clear_items()
                await interaction.response.edit_message(content="Respectable.", view=self)
                self.value = "REJECT"
                self.stop()
        
        view = Invite()
        await p2.send(f"**<@{p1.id}>** has invited you to a game of {game}!", view=view)
        await view.wait()

        return view.value

            

    @user_command(name="tictactoe", help="Play a game of TicTacToe against other players for BBTCG Cash!", guild_ids=[389818215871676418])
    async def tictactoe(self, ctx, challenge: discord.User):
        player1 = ctx.author
        player2 = challenge

        await ctx.respond(f"Inviting {player2.name}...", ephemeral=True)

        #mp = await self.invite_p2(player1, player2, ctx, "Tic Tac Toe")
        #if mp == "REJECT":
        #    return await ctx.interaction.edit_original_message(content=f"{player2.name} refused your invite.")

        class ttt_board(discord.ui.View):

            def __init__(self, *items: Item, timeout: float = 600, player1, player2):
                super().__init__(*items, timeout=timeout)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_0", row=0)
            async def b0(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_1", row=0)
            async def b1(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_2", row=0)
            async def b2(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_3", row=1)
            async def b3(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_4", row=1)
            async def b4(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_5", row=1)
            async def b5(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_6", row=2)
            async def b6(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_7", row=2)
            async def b7(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            @button(label=" ", style=ButtonStyle.gray, disabled=False, custom_id="ttt_8", row=2)
            async def b8(self, button: discord.ui.Button, interaction: discord.Interaction):
                await self.ttt_button_click(button, interaction, player1, player2)
            
            async def ttt_button_click(self, button: discord.ui.Button, interaction: discord.Interaction):

                # HANDLE TURN CHANGES WITH USER.ID's, PLAYER1, and PLAYER2
                
                if str(interaction.user.id) in str(interaction.message.content):
                    pass
                else:
                    await interaction.followup(f"<@{interaction.user.id}> you can't go yet!")
                    return False

                if interaction.user == player1:
                    button.emoji = "❌"
                else:
                    button.emoji = "⭕"
                await interaction.response.edit_message(view=self)

                current_state = {} 
                for b in self.children:
                    try:
                        current_state = {**current_state, b.custom_id: b.emoji.name}
                    except:
                        current_state = {**current_state, b.custom_id: b.emoji}
                
                print(current_state)
            
            async def ttt_turn_manager(self, interaction: discord.Interaction):
                print(interaction.message.content)
                print(interaction.user.id)

                if str(interaction.user.id) in str(interaction.message.content):
                    return True
                else:
                    await interaction.followup(f"<@{interaction.user.id}> you can't go yet!")
                    return False


            

        
        

        gameboard = ttt_board(player1=player1, player2=player2)

        game_thread = await ctx.channel.create_thread(name=f"{player1.name} VS {player2.name}: TIC TAC TOE", type=discord.ChannelType.public_thread)
        await game_thread.send(content=f"<@{player2.id}> goes first!", view=gameboard)


        

        

# Standard bot setup.
def setup(bot):
    bot.add_cog(BBTCG_Games(bot))