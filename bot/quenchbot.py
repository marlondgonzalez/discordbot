# Import libraries
import os
import asyncpg
import discord
from dotenv import load_dotenv
from discord.ext import commands
from api import establishConnection, RegisterTwitchStreamer

# Load Env Variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initalize Bot
command_prefix = "!"
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
clientbot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None) # In order to avoid confusion (I kept going back and forth between discord.Client and commands.Bot), I named the commands.Bot instance clientbot. NTS: it is a Bot not Client instance

# Establish pool connection
# async def createDataBasePool():
#     clientbot.pg_con = await asyncpg.create_pool(DATABASE_URL)
#     await clientbot.pg_con.execute("CREATE TABLE IF NOT EXISTS TestRun (UserID bigint, GuildID bigint, UserName varchar(255));")
#     await clientbot.pg_con.execute("CREATE TABLE IF NOT EXISTS Sample (UserID bigint, GuildID bigint, ArgumentName varchar(255), Content text);")

# Events
@clientbot.event
async def on_ready():
    print(f"Discord bot {clientbot.user} logged in and ready for input")

@clientbot.event
async def on_message(message):
    if message.author == clientbot.user:
        return
    firstword = message.content.split(" ")[0]
    content = await clientbot.pg_con.fetchval("SELECT Content FROM Sample WHERE ArgumentName = $1", firstword)
    if content is None:
        await clientbot.process_commands(message)
    else:
        await message.channel.send(str(content))

@clientbot.event
async def on_member_join(member):
    guild = member.guild
    welcomechannel = guild.text_channels[0]
    rolechannel = guild.text_channels[2]
    ruleschannel = guild.rules_channel
    await welcomechannel.send(
    f'''Hey {member.mention}, welcome to **{guild.name}**! :peace112:

Thanks for joining our community, please be nice and considerate.

To see the whole server, you will have to go to {ruleschannel.mention} to read and react to the rules of the server.

If you want to receive a role in the server, please go to {rolechannel.mention} where you will automatically be given a role depending on what you choose.

Hope you enjoy your time here! :music112:''')

# @clientbot.event
# async def
#

# @clientbot.event
# async def on_raw_reaction_add():
    # this function will be used to react to rules / add roles / subscribe to channels

# Commands
@clientbot.command(aliases=["Hello"])
async def hello(ctx):
    await ctx.send("Hello there!")

@clientbot.command(aliases=["Ping"])
async def ping(ctx):
    await ctx.send(f"My current ping is {round(clientbot.latency * 1000, 3)}ms!")

@clientbot.command(aliases=["Edit"])
async def edit(ctx):
    channel = ctx.guild.text_channels[14]
    channelname = channel.name
    if "🔴" in channelname:
        newname = channelname[0:-2]
        await channel.edit(name=newname)
    else:
        newname = channelname + r"-🔴"
        print(newname)
        await channel.edit(name=newname)
    await ctx.send("Changed Name")

@clientbot.command(aliases=["Help"])
async def help(ctx):
    await ctx.send(f"I wonder if this overrides the default !help command")

# Custom Commands
@clientbot.command(aliases=["addcommand"])
async def addCommand(ctx, argument, *, content):
    userID = ctx.author.id
    guildID = ctx.guild.id
    if argument[0] != command_prefix:
        argument = command_prefix + argument
    await clientbot.pg_con.execute("INSERT INTO Sample (UserID, GuildID, ArgumentName, Content) VALUES ($1, $2, $3, $4)", userID, guildID, argument, content)
    await ctx.channel.send(f"Added \"{content}\" under {argument}")

@clientbot.command(aliases=["deletecommand"])
async def deleteCommand(ctx, argument):
    userID = ctx.author.id
    guildID = ctx.guild.id
    if argument[0] != command_prefix:
        argument = command_prefix + argument
    rawcount = await clientbot.pg_con.execute("DELETE FROM Sample WHERE ArgumentName = $1", argument)
    count = int(rawcount.split(" ")[1])
    if count > 0:
        await ctx.channel.send(f"Deleted {argument} command")
    else:
        await ctx.channel.send(f"Command not found, did not delete any command")

@clientbot.command(aliases=["allcommands"])
async def allCommands(ctx):
    allcommands = await clientbot.pg_con.fetch("SELECT * FROM Sample")
    embed = discord.Embed(title="Our Discord Commands!")
    for command in allcommands:
        commandname = "**" + command[2] + "**"
        commandvalue = "`" + command[3] + "`"
        embed.add_field(name=commandname, value=commandvalue, inline=False)
    await ctx.channel.send(embed=embed)

@clientbot.command(aliases=["getchannel"])
async def getChannel(ctx):
    id = ctx.channel.id
    await ctx.channel.send(id)


# Quote Group Commands
# @clientbot.group()
# async def quote(ctx)

# @quote.command()
# async def addquote(ctx)

# @quote.command()
# async def deletequote(ctx)

# @quote.command()
# async def allquotes(ctx)

# Main Process

clientbot.load_extension("cogs.database")
clientbot.load_extension("cogs.server")
x  = establishConnection("chewymarlon")
print(x.clientID)
print(x.streamerUsername)
print(x.token)
print(x.userID)
print(x.response.text)

clientbot.run(DISCORD_TOKEN)
