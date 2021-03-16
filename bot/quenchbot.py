# Import libraries
import os
import discord
import asyncpg
from discord.ext import commands
from dotenv import load_dotenv

# Load Env Variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initalize Bot
clientbot = commands.Bot(command_prefix = "!") # In order to avoid confusion (I kept going back and forth between discord.Client and commands.Bot), I named the commands.Bot instance clientbot. NTS: it is a Bot not Client instance

# Establish pool connection
async def create_db_pool():
    clientbot.pg_con = await asyncpg.create_pool(DATABASE_URL)
    await clientbot.pg_con.execute("CREATE TABLE IF NOT EXISTS TestRun (UserID bigint, GuildID bigint, UserName varchar(255));")

# Events
@clientbot.event
async def on_ready():
    print(f"We have logged in as {clientbot.user}")

# Commands
@clientbot.command(aliases=["Hello"])
async def hello(ctx):
    await ctx.send("Hello there!")

@clientbot.command(aliases=["Ping"])
async def ping(ctx):
    await ctx.send(f"My current ping is {round(clientbot.latency * 1000, 3)}ms!")

@clientbot.command()
async def addme(ctx):
    UserID = ctx.author.id
    GuildID = ctx.guild.id
    UserName = ctx.author.name
    await clientbot.pg_con.execute("INSERT INTO TestRun (UserID, GuildID, UserName) VALUES ($1, $2, $3);", UserID, GuildID, UserName)
    await ctx.send(f"Added your credentials to our database: \n UserID: {UserID}, UserName: {UserName}")


# Main Process
clientbot.loop.run_until_complete(create_db_pool())
clientbot.run(DISCORD_TOKEN)
