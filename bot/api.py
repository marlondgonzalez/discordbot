import os
import json
import requests
import aiohttp
from dotenv import load_dotenv
from discord.ext import commands, tasks
# from discord import Webhook, RequestsWebhookAdapter

load_dotenv()
TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")


# Base class for communicating with the Twitch.TV API
class TwitchAPI():
    def __init__(self):
        pass

class RegisterTwitchStreamer(TwitchAPI):
    def __init__(self, streamerUsername):
        super().__init__()
        self.clientID = TWITCH_CLIENT_ID
        self.clientSecret = TWITCH_CLIENT_SECRET
        self.streamerUsername = streamerUsername
        self.serverURL = r"https://stfquenchbot.herokuapp.com/entrance"

    def createTwitchAppToken(self):
        # url = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials&scope=<space-separated list of scopes>"
        url = f"https://id.twitch.tv/oauth2/token?client_id={self.clientID}&client_secret={self.clientSecret}&grant_type=client_credentials"
        response = requests.post(url).json()
        self.token = response["access_token"]
        return self.token

    def getUserID(self):
        url = f"https://api.twitch.tv/helix/users?login={self.streamerUsername}"
        headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"][0]
        self.userID = data['id']
        return self.userID

    def createTwitchDiscordWebhook(self):
        posturl = r"https://api.twitch.tv/helix/eventsub/subscriptions"
        payload = {
        "type": "stream.online",
        "version": "1",
        "condition": {
            "broadcaster_user_id": f"{self.userID}"
        },
        "transport": {
            "method": "webhook",
            "callback": f"{self.serverURL}",
            "secret": "secretcodeDFSDFEOIA"
        }
    }
        # create algorithm to generate secret ID per automated request to TwitchAPI
        headers = {"Client-ID":self.TWITCH_CLIENT_ID, "Authorization":"Bearer " + self.token, "Content-Type":"application/json"}
        self.response = requests.post(posturl, data=json.dumps(payload), headers=headers)
        return self.response

def establishConnection(streamerUsername):
    twitchStreamer = RegisterTwitchStreamer("DNGHoundz")
    twitchStreamer.createTwitchAppToken()
    twitchStreamer.getUserID()
    twitchStreamer.createTwitchDiscordWebhook()
    return twitchStreamer

x  = establishConnection("DNGHoundz")
print(x.clientID)
print(x.streamerUsername)
print(x.token)
print(x.userID)
print(x.response.text)
