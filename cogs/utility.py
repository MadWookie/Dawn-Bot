import datetime
import time

import discord
from discord.ext import commands


def pin_check(m):
    return not m.pinned


class Utility:
    def __init__(self, bot):
        self.bot = bot

    def __unload(self):
        self.purge_task.cancel()

###################
#                 #
# COGS            #
#                 #
###################

    @commands.command(hidden=True)
    @commands.is_owner()
    async def reload(self, ctx, *, ext):
        """Reload a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.unload_extension(ext)
        except:
            pass
        try:
            self.bot.load_extension(ext)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f'Cog {ext} reloaded.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def load(self, ctx, *, ext):
        """Load a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.load_extension(ext)
        except Exception as e:
            await ctx.send(e)
        else:
            await ctx.send(f'Cog {ext} loaded.')

    @commands.command(hidden=True)
    @commands.is_owner()
    async def unload(self, ctx, *, ext):
        """Unload a cog."""
        if not ext.startswith('cogs.'):
            ext = f'cogs.{ext}'
        try:
            self.bot.unload_extension(ext)
        except:
            await ctx.send(f'Cog {ext} is not loaded.')
        else:
            await ctx.send(f'Cog {ext} unloaded.')

###################
#                 #
# MISCELLANEOUS   #
#                 #
###################

    @commands.command()
    @commands.has_permissions(administrator=True)
    async def playing(self, ctx, *, status: str):
        """Sets the 'Playing' message for the bot."""
        await self.bot.change_presence(game=discord.Game(name=status))

    @commands.command()
    async def uptime(self, ctx):
        """Shows the uptime of the bot."""
        up = abs(self.bot.uptime - int(time.perf_counter()))
        up = datetime.timedelta(seconds=up)
        await ctx.send(f'`Uptime: {up}`', delete_after=60)


def setup(bot):
    bot.add_cog(Utility(bot))
