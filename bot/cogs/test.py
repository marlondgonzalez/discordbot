import discord
from discord.ext import commands

class Test(commands.Cog) # change class name to whatever you want the "category" to be
    def __init__(self, clientbot):
        self.clientbot = clientbot

    @commands.command()
    async def test(self, ctx):
        await ctx.send("testing")

def setup(clientbot):
    clientbot.add_cog(Test(clientbot))
