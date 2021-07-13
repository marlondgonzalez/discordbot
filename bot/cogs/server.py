import os
import re
import json
import hmac
import discord
import hashlib
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
# from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks

load_dotenv()
app = web.Application()
routes = web.RouteTableDef()
API_SECRET_CODE = os.getenv("API_SECRET_CODE")
COMMAND_CHANNEL_ID = os.getenv("COMMAND_CHANNEL_ID")
NOTIFICATION_CHANNEL_ID = os.getenv("NOTIFICATION_CHANNEL_ID")

class Server(commands.Cog):
    def __init__(self, clientbot):
        self.clientbot = clientbot
        self.debug = False
        self.webserver.start()

        @routes.get('/')
        async def home(request):
            print(request)
            return web.Response(text="Hello World", status=200)

        @routes.post('/callback')
        async def callback(request):
            headertype = request.headers.get("Twitch-Eventsub-Message-Type")
            body = await request.read()
            actualsignature = request.headers.get("Twitch-Eventsub-Message-Signature")
            message = request.headers.get("Twitch-Eventsub-Message-ID").encode() + request.headers.get('Twitch-Eventsub-Message-Timestamp').encode() + body
            expectedsignature = "sha256=" + hmac.new(API_SECRET_CODE.encode(), message, hashlib.sha256).hexdigest()
            if actualsignature == expectedsignature:
                if headertype == "webhook_callback_verification":
                    content = await request.json()
                    challenge = content["challenge"]
                    print("Webhook callback verification completed, sending challenge to Twitch API server")
                    commandchannel = self.clientbot.get_channel(int(COMMAND_CHANNEL_ID))
                    await commandchannel.send("Connected to Twitch server, streamer notifications successful")
                    return web.Response(text=challenge, status=200)
                if headertype == "notification":
                    content = await request.json()
                    event = content["event"]
                    liveStreamer = event["broadcaster_user_name"]
                    streamURL = f"https://www.twitch.tv/{liveStreamer}"
                    notificationchannel = self.clientbot.get_channel(int(NOTIFICATION_CHANNEL_ID))
                    embed = discord.Embed(title=f"{liveStreamer} is now live!", url=streamURL)
                    await notificationchannel.send(embed=embed)
                    print(f"{liveStreamer} is now live!")
                    return web.Response(status=200)
            else:
                print("Communication successful but not trusted")
                return web.Response(status=200)

        self.port = os.environ.get("PORT", 5000)
        print(f"Server loaded on PORT:" + str(self.port))
        app.add_routes(routes)

    @tasks.loop()
    async def webserver(self):
        runner = web.AppRunner(app)
        await runner.setup()
        if self.debug == True:
            site = web.TCPSite(runner, host="127.0.0.1", port=self.port)
        else:
            site = web.TCPSite(runner, host="0.0.0.0", port=self.port)
        await site.start()

    @webserver.before_loop
    async def webserver_before_loop(self):
        await self.clientbot.wait_until_ready()

def setup(clientbot):
    clientbot.add_cog(Server(clientbot))
