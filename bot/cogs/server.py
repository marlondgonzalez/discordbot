import os
import re
import json
import requests
import aiohttp
from aiohttp import web
from dotenv import load_dotenv
from discord import Webhook, AsyncWebhookAdapter
from discord.ext import commands, tasks

app = web.Application()
print("made app")
routes = web.RouteTableDef()
print("made routetable")

class Server(commands.Cog):
    def __init__(self, clientbot):
        self.clientbot = clientbot
        self.web_server.start()

        @routes.get('/')
        async def handle(request):
            return web.Response(text="Hello World", status=200)

        @routes.post('/entrance')
        async def entrance(request):
            print(request)
            if request.headers.get("Authorization") == "secretcode":
                data = await request.json()
                # need a way to get channel ID's automatically
                channel = self.clientbot.get_channel(testID)
                await channel.send(data)
                return web.Response(text="communication successful", status=200)
            else:
                return web.Response(text="communication successful but not trusted", status=200)

        self.webserver_port = os.environ.get("PORT", 5000)
        print(self.webserver_port)
        app.add_routes(routes)
        print("added routes")

    @tasks.loop()
    async def web_server(self):
        runner = web.AppRunner(app)
        await runner.setup()
        site = web.TCPSite(runner, host="0.0.0.0", port=self.webserver_port)
        await site.start()

    @web_server.before_loop
    async def web_server_before_loop(self):
        await self.clientbot.wait_until_ready()

def setup(clientbot):
    clientbot.add_cog(Server(clientbot))
