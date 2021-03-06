# Import libraries
import os
import asyncpg
import discord
from dotenv import load_dotenv
from discord.ext import commands
from api import TwitchAPI

# Load Env Variables
load_dotenv()
DISCORD_TOKEN = os.getenv("DISCORD_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL")

# Initalize Bot
command_prefix = "!"
intents = discord.Intents.default()
intents.members = True
intents.guilds = True
intents.reactions = True
intents.voice_states = True
clientbot = commands.Bot(command_prefix=command_prefix, intents=intents, help_command=None) # In order to avoid confusion (I kept going back and forth between discord.Client and commands.Bot), I named the commands.Bot instance clientbot. NTS: it is a Bot not Client instance

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

# @clientbot.event #WIP, react to get role
# async def on_reaction_add(reaction, user):
#     emoji_role_dict = {":amongUs:": "Among Us Peeps", ":skull": "Dead By Daylight Peeps"}
#     channel = clientbot.get_channel('862975521835188225')
#     if reaction.message.channel.id != channel.id:
#         print("NA")
#         return
#     else:
#         print(channel)
#         role = discord.utils.get(user.server.roles, name=emoji_role_dict[reaction.emoji])
#         await bot.add_roles(user, role)

# Commands
@clientbot.command(aliases=["Hello"])
async def hello(ctx):
    await ctx.send("Hello there!")

@clientbot.command(aliases=["Ping"])
async def ping(ctx):
    await ctx.send(f"My current ping is {round(clientbot.latency * 1000, 3)}ms!")

# @clientbot.command(aliases=["Help"])
# async def help(ctx):
#     await ctx.send(f"I wonder if this overrides the default !help command")

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
    if len(allcommands) > 0:
        embed = discord.Embed(title="Our Discord Commands!")
        for command in allcommands:
            commandname = "**" + command[2] + "**"
            commandvalue = "`" + command[3] + "`"
            embed.add_field(name=commandname, value=commandvalue, inline=False)
        await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send("Error: No commands found, add new commands via '!addcommand' function" )

@clientbot.command(aliases=["getchannel"])
async def getChannel(ctx, argument):
    allchannels = {}
    for channel in ctx.guild.text_channels:
        allchannels[channel.name] = channel.id
    for channel in ctx.guild.voice_channels:
        allchannels[channel.name] = channel.id
    try:
        await ctx.channel.send(allchannels[argument])
    except:
        await ctx.channel.send("Error: Not Found")


# Caution: if two or more users in the guild have the same username, this command will only return one of them
@clientbot.command(aliases=["getmember"])
async def getMember(ctx, argument):
    allmembers = {}
    for member in ctx.guild.members:
        allmembers[member.name] = member.id
    try:
        await ctx.channel.send(allmembers[argument])
    except:
        await ctx.channel.send("Error: Not Found")

@clientbot.command(aliases=["registerstreamer"])
@commands.has_any_role("Guild Master", "Vice Guild Master", "Guild Tactician")
async def RegisterSubscription(ctx, streamerusername):
    twitch = TwitchAPI()
    twitch.registerTwitchStreamer(streamerusername)
    await ctx.channel.send("Registering Streamer")

@clientbot.command(aliases=["deletestreamer"])
@commands.has_any_role("Guild Master", "Vice Guild Master", "Guild Tactician")
async def DeleteSubscription(ctx, streamerusername):
    twitch = TwitchAPI()
    twitch.deleteActiveSubscription(streamerusername)
    print("Deleting Streamer")
    await ctx.channel.send("Deleting Streamer")

@clientbot.command(aliases=["liststreamers"])
@commands.has_any_role("Guild Master", "Vice Guild Master", "Guild Tactician")
async def ListSubscriptions(ctx):
    twitch = TwitchAPI()
    activesubscriptions = twitch.getActiveSubscriptions()
    if len(activesubscriptions) > 0:
        for i in range(0, len(activesubscriptions), 25):
            embed = discord.Embed(title="Bonobo Alliance")
            chunk = activesubscriptions[i:i+25]
            for streamer in chunk:
                streamername = "**" + streamer + "**"
                embed.add_field(name="**Streamer:**", value=streamername, inline=True)
            await ctx.channel.send(embed=embed)
    else:
        await ctx.channel.send("Error: No streamers featured, please add streamers to our community:)" )

# Main Process
clientbot.load_extension("cogs.database")
clientbot.load_extension("cogs.server")
clientbot.run(DISCORD_TOKEN)


# Prototype functions
# @clientbot.event
# async def on_voice_state_update(member, before, after):
#     voicechannelID = getChannel(" Waiting Room")
#     destinationID =
#     if before.channel == None and after.channel.id == voicechannelID:
#         channel = clientbot.get_channel(destinationID)
#         await channel.send(f"User {member.name} has entered voice channel {after.channel.name}")

# @clientbot.event
# async def on_raw_reaction_add():
    # this function will be used to react to rules / add roles / subscribe to channels

# @clientbot.command(aliases=["Edit"])
# async def edit(ctx):
#     channel = ctx.guild.text_channels[14]
#     channelname = channel.name
#     if "" in channelname:
#         newname = channelname[0:-2]
#         await channel.edit(name=newname)
#     else:
#         newname = channelname + r"-"
#         print(newname)
#         await channel.edit(name=newname)
#     await ctx.send("Changed Name")

# Helper functions
# def getChannel(guild, argument):
#     allchannels = {}
#     for channel in guild.text_channels:
#         allchannels[channel.name] = channel.id
#     for channel in ctx.guild.voice_channels:
#         allchannels[channel.name] = channel.id
#     return guild.get_channel(allchannels[argument])

# @clientbot.command()
# def editRole(ctx):
#
