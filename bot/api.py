import os
import time
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
        self.token = None

    def createTwitchAppToken(self):
        if self.token == None:
            # url = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials&scope=<space-separated list of scopes>"
            url = f"https://id.twitch.tv/oauth2/token?client_id={self.clientID}&client_secret={self.clientSecret}&grant_type=client_credentials"
            response = requests.post(url)
            jsonresponse = response.json()
            if response.status_code == 200:
                self.token = jsonresponse["access_token"]
                return self.token
            else:
                raise ValueError("Failed to generate token")
        else:
            return None

    def getUserID(self, streamerusername):
        self.createTwitchAppToken()
        url = f"https://api.twitch.tv/helix/users?login={streamerusername}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"][0]
        self.userID = data['id']
        return self.userID

    def getUserName(self, UserID):
        self.createTwitchAppToken()
        url = f"https://api.twitch.tv/helix/channels?broadcaster_id={UserID}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"]
        username = data[0]['broadcaster_name']
        return username

# WIP
    def getStreamData(self, UserID):
        self.createTwitchAppToken()
        url = f"https://api.twitch.tv/helix/streams?user_id={UserID}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"][0]
        game = data["game_name"]
        title = data["title"]
        views = data["viewer_count"]
        thumbnail = data["thumbnail_url"] + "?r=" + str(round(time.time()))
        if thumbnail.find("width") != -1 or thumbnail.find("height") == -1:
            thumbnail = thumbnail.replace("{width}", "300")
            thumbnail = thumbnail.replace("{height}", "180")
        return game, title, views, thumbnail

    def getUserData(self, UserID):
        self.createTwitchAppToken()
        url = f"https://api.twitch.tv/helix/users?id={UserID}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"][0]
        profile = data["profile_image_url"] #set width/height to 300x300
        return profile

    def createTwitchDiscordWebhook(self):
        self.createTwitchAppToken()
        url = r"https://api.twitch.tv/helix/eventsub/subscriptions"
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
        headers = {"Client-ID":self.clientID, "Authorization":"Bearer " + self.token, "Content-Type":"application/json"}
        self.response = requests.post(url, data=json.dumps(payload), headers=headers)
        print("Webhook sent")
        return self.response

    def registerTwitchStreamer(self, streamerusername):
        self.getUserID(streamerusername)
        self.createTwitchDiscordWebhook()
        return self

    def getActiveSubscriptions(self):
        self.createTwitchAppToken()
        allusernames = []
        url = f"https://api.twitch.tv/helix/eventsub/subscriptions?status=enabled"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"]
        users = [user["condition"]["broadcaster_user_id"] for user in data]
        for userID in users:
            username = self.getUserName(userID)
            allusernames.append(username)
        print("Listed Streamers")
        return allusernames

    def deleteActiveSubscription(self, streamerusername):
        self.createTwitchAppToken()
        self.getUserID(streamerusername)
        pairings = {}
        url = f"https://api.twitch.tv/helix/eventsub/subscriptions?status=enabled"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.get(url, headers=headers)
        data = json.loads(response.text)["data"]
        for user in data:
            userID = user["condition"]["broadcaster_user_id"]
            ID = user["id"]
            pairings[userID] = ID
        notificationID = pairings[self.userID]
        url = f"https://api.twitch.tv/helix/eventsub/subscriptions?id={notificationID}"
        headers = {"Client-ID": self.clientID, "Authorization":"Bearer " + self.token}
        response = requests.delete(url, headers=headers)
        print("Deleted Streamer")
