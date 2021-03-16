import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# DATABASE_URL = os.getenv("DATABASE_URL")

clientbot = commands.Bot(command_prefix = "!") # In order to avoid confusion (I kept going back and forth between discord.Client and commands.Bot), I named the commands.Bot instance clientbot. NTS: it is a Bot not Client instance
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# cursor = conn.cursor()

@clientbot.event
async def on_ready():
    print(f"We have logged in as {clientbot.user}")

@clientbot.command()
async def Hello(ctx):
    await ctx.send("Hello there!")

clientbot.run(DISCORD_TOKEN)
