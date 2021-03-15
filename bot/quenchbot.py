import discord
import os
# import psycopg2
from dotenv import load_dotenv

load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
# DATABASE_URL = os.getenv("DATABASE_URL")

client = discord.Client()
# conn = psycopg2.connect(DATABASE_URL, sslmode='require')
# cursor = conn.cursor()

@client.event
async def on_ready():
    print('We have logged in as {0.user}'.format(client))

@client.event
async def on_message(message):
    if message.author == client.user:
        return
    if message.content.startswith("!hello"):
        await message.channel.send("Hello!")

client.run(DISCORD_TOKEN)
