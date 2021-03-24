import os
import re
import json
import hmac
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
# from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks

load_dotenv()
app = web.Application()
routes = web.RouteTableDef()
API_SECRET_CODE = os.getenv("API_SECRET_CODE")

class Server(commands.Cog):
    def __init__(self, clientbot):
        self.clientbot = clientbot
        self.debug = False
        self.webserver.start()

        @routes.get('/')
        async def home(request):
            print(request)
            return web.Response(text="Hello World", status=200)

        @routes.post('/entrance')
        async def entrance(request):
            if request.headers.get("Authorization") == API_SECRET_CODE:
                data = await request.json()
                # need a way to get channel ID's automatically
                # channel = self.clientbot.get_channel(testID)
                # await channel.send(data)
                print(data)
                return web.Response(text="communication successful", status=200)
            else:
                data = await request.json()
                actualsignature = request.headers.get("Twitch-Eventsub-Message-Signature")
                print(actualsignature)
                message = request.headers.get("Twitch-Eventsub-Message-ID").encode() + request.headers.get('Twitch-Eventsub-Message-Timestamp').encode() + data
                signature = hmac.new(API_SECRET_CODE, message, )
                print(signature)
                expectedsignature = "sha256" + signature.hexdigest()
                print(expectedsignature)
                    # message = request.headers.get("Twitch-Eventsub-Message-ID") + request.headers.get('Twitch-Eventsub-Message-Timestamp') + request.body
                    # print(message)
                # except:
                #     data = await request.json()
                #     print(data)
                #     return web.Response(text="communication successful but not trusted", status=200)

        self.port = os.environ.get("PORT", 5000)
        print("Quenchbot server loaded on PORT:" + str(self.port))
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
