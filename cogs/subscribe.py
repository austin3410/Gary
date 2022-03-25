from discord.ext import commands
from discord.commands import slash_command, Option
import asyncio
import discord

class Subscription(commands.Cog):

    def __init__(self, bot):
        self.bot = bot
        self.target_category_name = "Subscribeable Channels"
        self.target_how_to_name = "how-to-subscribe"
        self.embed_description = 'Use "/subscribe {channel name}" to see and chat in that channel.\nOr "/unsubscribe {channel name}" to unsubscribe from the channel.'
    
    async def subscribe_autocomplete(self, ctx: discord.AutocompleteContext):
        possible_channels = []
        ctx_channel = await self.bot.fetch_channel(ctx.interaction.channel_id)
        category_id = ctx_channel.category_id
        category = self.bot.get_channel(int(category_id))
        for c in category.channels:
            if c.name == self.target_how_to_name:
                continue
            
            perms = c.permissions_for(ctx.interaction.user)

            if perms.read_messages == False:
                possible_channels.append(c)
                
        
        return [c.name for c in possible_channels if c.name.startswith(ctx.value.lower())]
    
    async def unsubscribe_autocomplete(self, ctx: discord.AutocompleteContext):
        possible_channels = []
        ctx_channel = await self.bot.fetch_channel(ctx.interaction.channel_id)
        category_id = ctx_channel.category_id
        category = self.bot.get_channel(int(category_id))
        for c in category.channels:
            if c.name == self.target_how_to_name:
                continue
            
            perms = c.permissions_for(ctx.interaction.user)

            if perms.read_messages == True:
                possible_channels.append(c)
                
        
        return [c.name for c in possible_channels if c.name.startswith(ctx.value.lower())]
        

    # AUTO MESSAGE REMOVE
    @commands.Cog.listener()
    async def on_message(self, ctx):
        if ctx.channel.type != discord.ChannelType.private:
            if ctx.channel.name == self.target_how_to_name and int(ctx.author.id) != int(self.bot.id):
                if ctx.content.startswith("!") or ctx.content.startswith("|"):
                    pass
                else:
                    await ctx.respond(f"Please only send commands to this channel to keep it clean.", delete_after=5)


    # SUBSCRIBE command
    @slash_command(name="subscribe", guild_ids=[389818215871676418], description="Allows you to subscribe to spoiler channels. Use /listsubs for more info.")
    async def subscribe(self, ctx, channel: Option(str, autocomplete=subscribe_autocomplete, description="Which channel would you like to subscribe to?")):
        if ctx.channel.name != self.target_how_to_name:
            return await ctx.respond(f"Please subscribe to a channel in the '{self.target_how_to_name}' channel.", delete_after=10)
        
        ctx_channel = ctx.channel
        category_id = ctx_channel.category_id
        category = self.bot.get_channel(int(category_id))
        for c in category.channels:
            if c.name == channel:
                await c.set_permissions(ctx.author, read_messages=True, send_messages=True)
                return await ctx.respond(f"You're now subscribed to **#{channel}**!", ephemeral=True)
        
        return await ctx.respond(f"I couldn't find **{channel}**, are you sure you spelled it correctly?", delete_after=10)
    
    # UNSUBSCRIBE command
    @slash_command(name="unsubscribe", guild_ids=[389818215871676418], description="Allows you to unsubscribe from a spoiler channel.")
    async def unsubscribe(self, ctx, channel: Option(str, autocomplete=unsubscribe_autocomplete, description="Which channel would you like to unsubscribe from?")):
        if ctx.channel.name != self.target_how_to_name:
            return await ctx.respond(f"Please unsubscribe from a channel in the '{self.target_how_to_name}' channel.", delete_after=20)
        
        ctx_channel = ctx.channel
        category_id = ctx_channel.category_id
        category = self.bot.get_channel(int(category_id))
        for c in category.channels:
            if c.name == channel:
                await c.set_permissions(ctx.author, read_messages=False, send_messages=False)
                return await ctx.respond(f"You're now unsubscribed from **#{channel}**!", ephemeral=True)
        
        return await ctx.respond(f"I couldn't find **{channel}**, are you sure you spelled it correctly?", delete_after=10)
    
    # LISTSUBS command
    @slash_command(name="listsubs", guild_ids=[389818215871676418], description="Shows you all of the channels you can subscribe to.")
    async def listsubs(self, ctx):
        if ctx.channel.name != self.target_how_to_name:
            await ctx.respond(f"Please requests all subs in the '{self.target_how_to_name}' channel.", delete_after=10)

        
        channel = ctx.channel
        category_id = channel.category_id
        category = self.bot.get_channel(int(category_id))
        embed=discord.Embed(title="Current List of Spoiler Channels", color=0xc40e0e, description=self.embed_description)
        for channel in category.channels:
            if channel.name != ctx.channel.name:
                embed.add_field(name=f"{channel.name}", value=f"{channel.topic}", inline=False)

        await ctx.respond(embed=embed)
    
    # AUTO LISTSUBS - CHANNEL CREATE
    @commands.Cog.listener()
    async def on_guild_channel_create(self, channel):
        category_channel = self.bot.get_channel(int(channel.category_id))
        for c in category_channel.channels:
            if c.name == self.target_how_to_name:
                embed=discord.Embed(title="Current List of Spoiler Channels", color=0xc40e0e, description=self.embed_description)
                for cc in category_channel.channels:
                    if cc.name != self.target_how_to_name:
                        embed.add_field(name=f"{cc.name}", value=f"{cc.topic}", inline=False)
                await c.purge(check=self.purge_gary)
                await c.send(embed=embed)
    
    # AUTO LISTSUBS - CHANNEL DELETE
    @commands.Cog.listener()
    async def on_guild_channel_delete(self, channel):
        category_channel = self.bot.get_channel(int(channel.category_id))
        for c in category_channel.channels:
            if c.name == self.target_how_to_name:
                embed=discord.Embed(title="Current List of Spoiler Channels", color=0xc40e0e, description=self.embed_description)
                for cc in category_channel.channels:
                    if cc.name != self.target_how_to_name:
                        embed.add_field(name=f"{cc.name}", value=f"{cc.topic}", inline=False)
                await c.purge(check=self.purge_gary)
                await c.send(embed=embed)
    
    # AUTO LISTSUBS - CHANNEL UPDATE
    @commands.Cog.listener()
    async def on_guild_channel_update(self, before, after):
        channel = after
        before_channel = before
        if channel.name != before_channel.name or channel.topic != before_channel.topic:
            category_channel = self.bot.get_channel(int(channel.category_id))
            for c in category_channel.channels:
                if c.name == self.target_how_to_name:
                    embed=discord.Embed(title="Current List of Spoiler Channels", color=0xc40e0e, description=self.embed_description)
                    for cc in category_channel.channels:
                        if cc.name != self.target_how_to_name:
                            embed.add_field(name=f"{cc.name}", value=f"{cc.topic}", inline=False)
                    await c.purge(check=self.purge_gary)
                    await c.send(embed=embed)
    
    # GARY CHECK
    def purge_gary(self, m):
        return m.author == self.bot.user


def setup(bot):
    bot.add_cog(Subscription(bot))