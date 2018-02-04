import asyncio

from discord.ext import commands
import discord

from utils import errors, checks


@commands.check
def in_voice(ctx):
    if ctx.author.voice is not None:
        return True
    raise errors.NotConnected(ctx.message)


class Private:
    def __init__(self, bot):
        self.bot = bot
        self.creating = {}

    @in_voice
    @checks.db
    @commands.guild_only()
    @commands.group(invoke_without_command=True)
    async def private(self, ctx):
        """Create and manage private, password-protected voice channels."""

    @in_voice
    @checks.db
    @commands.guild_only()
    @private.command()
    async def new(self, ctx, channel_number: int):
        """Starts a new private channel."""
        channel = discord.utils.get(ctx.guild.voice_channels, name='Private Channel {}'.format(channel_number))
        if channel is None:
            await ctx.send('That private channel does not exist, please choose a different one.')
        elif channel.members:
            await ctx.send('Sorry, that channel is already being used.\nIf you\'d like to join that channel please use `!private join`.\nOtherwise please select a different channel.')
        else:
            creating = self.creating[ctx.guild.id] = self.creating.get(ctx.guild.id, [])
            if channel_number in creating:
                await ctx.send('Sorry, that channel is already being used. Please choose a different one.')
                return
            creating.append(channel_number)
            await ctx.author.send('Please enter the password you\'d like to use for {}'.format(channel))
            m = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.author.dm_channel.id and m.author == ctx.author, timeout=60)
            password = m.content
            async with ctx.con.transaction():
                await ctx.con.execute('''
                    INSERT INTO privatechannels (guild_id, channel_num, owner_id, password) VALUES ($1, $2, $3, $4)
                    ON CONFLICT (guild_id, channel_num) DO
                    UPDATE SET (owner_id, password) = ($3, $4)
                    ''', ctx.guild.id, channel_number, ctx.author.id, password)
            creating.remove(channel_number)
            await ctx.author.move_to(channel)

    @in_voice
    @checks.db
    @commands.guild_only()
    @private.command()
    async def join(self, ctx, channel_number: int):
        """Joins an already existing private channel."""
        channel = discord.utils.get(ctx.guild.voice_channels, name='Private Channel {}'.format(channel_number))
        if channel is None:
            await ctx.send('That private channel does not exist, please choose a different one.')
        elif not channel.members:
            await ctx.send('Sorry, that channel isn\'t being used.\nIf you\'d like to start a new chat in that channel please use `!private new`.\nOtherwise please select a different channel.')
        else:
            await ctx.author.send('Please enter the password for {}'.format(channel))
            m = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.author.dm_channel.id and m.author == ctx.author, timeout=60)
            password = m.content
            correct_password = await ctx.con.fetchval('''
                SELECT password FROM privatechannels WHERE guild_id = $1 AND channel_num = $2
                ''', ctx.guild.id, channel_number)
            if password == correct_password:
                await ctx.author.move_to(channel)
            else:
                await ctx.author.send(':x: **Invalid Password**.\nPlease check your password and make sure it is spelled correctly.')

    @checks.db
    @commands.guild_only()
    @private.command()
    async def password(self, ctx, channel_number: int):
        """Change the password for a private channel you started."""
        channel = discord.utils.get(ctx.guild.voice_channels, name='Private Channel {}'.format(channel_number))
        exists = await ctx.con.fetchval('''
            SELECT EXISTS(SELECT * FROM privatechannels WHERE guild_id = $1 AND channel_num = $2 AND owner_id = $3)
            ''', ctx.guild.id, channel_number, ctx.author.id)
        if not exists:
            await ctx.send('That channel does not exist or you did not start it.')
        else:
            await ctx.author.send('Please enter the password for {}'.format(channel))
            m = await self.bot.wait_for('message', check=lambda m: m.channel.id == ctx.author.dm_channel.id and m.author == ctx.author, timeout=60)
            password = m.content
            async with ctx.con.transaction():
                await ctx.con.execute('''
                    UPDATE privatechannels SET password = $3 WHERE guild_id = $1 AND channel_num = $2
                    ''', ctx.guild.id, channel_number, password)
            await ctx.send('The password for {} has been updated.'.format(channel))


def setup(bot):
    bot.add_cog(Private(bot))
