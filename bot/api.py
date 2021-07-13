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
API_SECRET_CODE = os.getenv("API_SECRET_CODE")
WEBSITE_CALLBACK_URL = os.getenv("WEBSITE_CALLBACK_URL")

# Base class for communicating with the Twitch.TV API
class TwitchAPI():
    def __init__(self):
        self.clientID = TWITCH_CLIENT_ID
        self.clientSecret = TWITCH_CLIENT_SECRET
        self.serverURL = WEBSITE_CALLBACK_URL
        
    def createTwitchAppToken(self):
        # url = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials&scope=<space-separated list of scopes>"
        url = f"https://id.twitch.tv/oauth2/token?client_id={self.clientID}&client_secret={self.clientSecret}&grant_type=client_credentials"
        response = requests.post(url)
        jsonresponse = response.json()
        if response.status_code == 200:
            self.token = jsonresponse["access_token"]
            return self.token
        else:
            raise ValueError("Failed to generate token")

    def getUserID(self, streamerUsername):
        url = f"https://api.twitch.tv/helix/users?login={streamerUsername}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
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
            "secret": f"{API_SECRET_CODE}"
        }
    }
        # create algorithm to generate secret ID per automated request to TwitchAPI
        headers = {"Client-ID":self.clientID, "Authorization":"Bearer " + self.token, "Content-Type":"application/json"}
        self.response = requests.post(posturl, data=json.dumps(payload), headers=headers)
        return self.response

    def registerTwitchStreamer(self, streamerUsername):
        self.createTwitchAppToken()
        self.getUserID(streamerUsername)
        self.createTwitchDiscordWebhook()
        return self

    def getActiveSubscriptions(self):
        self.createTwitchAppToken()
        url = f"https://api.twitch.tv/helix/eventsub/subscriptions" #?status=enabled
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"]
        print(data)
        return data

    def deleteActiveSubscription(self, streamerUsername):
        activesubscriptions = self.getActiveSubscriptions()
        ID = activesubscriptions[streamerUsername] # WIP
        url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={ID}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.delete(url, headers=headers)
