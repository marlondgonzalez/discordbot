import os
import discord
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# DATABASE_URL = os.getenv("DATABASE_URL")

client = commands.Bot(command_prefix = "!")
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# cursor = conn.cursor()

@client.event
async def on_ready():
    print(f"We have logged in as {client.user}")

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

client.run(DISCORD_TOKEN)
