# Import libraries
import os
import asyncpg
import asyncio
import discord
from dotenv import load_dotenv
from discord.ext import commands, tasks

# Load Env Variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

class Database(commands.Cog):
    def __init__(self, clientbot):
        self.clientbot = clientbot

    async def createDataBasePool(self):
        self.clientbot.pg_con = await asyncpg.create_pool(DATABASE_URL)
        print("Establishing connection to database")
        await self.clientbot.pg_con.execute("CREATE TABLE IF NOT EXISTS TestRun (UserID bigint, GuildID bigint, UserName varchar(255));")
        await self.clientbot.pg_con.execute("CREATE TABLE IF NOT EXISTS Sample (UserID bigint, GuildID bigint, ArgumentName varchar(255), Content text);")

def setup(clientbot):
    database = Database(clientbot)
    clientbot.add_cog(database)
    clientbot.loop.run_until_complete(database.createDataBasePool())
