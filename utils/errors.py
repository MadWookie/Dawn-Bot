from discord.ext import commands


class NotConnected(commands.CheckFailure):
    def __init__(self, VoiceState=None):
        self.VoiceState = None
