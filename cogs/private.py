import asyncio

from discord.ext import commands
import discord

from utils import errors, checks


@commands.check
def in_voice(ctx):
    if ctx.author.voice is not None:
        return True
    raise errors.NotConnected(ctx.message)


class Private():
    def __init__(self, bot):
        self.bot = bot

    @in_voice
    @checks.db
    @commands.group(invoke_without_command=True)
    async def private():
        """"""

    @in_voice
    @checks.db
    @private.command()
    async def new(self, ctx, channel_number: int):
        """Starts a new private channel."""
        channel = discord.utils.get(ctx.guild.voice_channels, name='Private Channel {}'.format(channel_number))
        if channel.members:
            await self.bot.say('Sorry, that channel is already being used.\nIf you\'d like to join that channel please use `!private join`.\nOtherwise please select a different channel.')
        else:
            await ctx.author.send('Please enter the password you\'d like to use for {}'.format(channel))
            m = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.author.channel.id)
            password = m.content
            # Sets password in database
            await ctx.author.move_to(channel)

    @in_voice
    @checks.db
    @private.command()
    async def join(self, ctx, channel_number: int):
        """Joins an already existing private channel."""
        channel = discord.utils.get(ctx.guild.voice_channels, name='Private Channel {}'.format(channel_number))
        if not channel.members:
            await self.bot.say('Sorry, that channel isn\'t being used.\nIf you\'d like to start a new chat in that channel please use `!private new`.\nOtherwise please select a different channel.')
        else:
            await ctx.author.send('Please enter the password for {}'.format(channel))
            m = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.author.channel.id)
            password = m.content
            # Get passwords of requested channel from database
            if password == password:
                await ctx.author.move_to(channel)
            else:
                await ctx.send(':x: **Invalid Password**.\nPlease check your password and make sure it is spelled correctly.')

    async def on_member_update(self, before: discord.Member, after: discord.Member):
        if before.voice and not after.voice and not before.voice.channel.members:
            # Delete password from db

def setup(bot):
    bot.add_cog(Private(bot))
