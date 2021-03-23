import os
import re
import json
import requests
import aiohttp
from dotenv import load_dotenv
from discord import Webhook, RequestsWebhookAdapter

TWITCH_CLIENT_ID = os.getenv("TWITCH_CLIENT_ID")
TWITCH_CLIENT_SECRET = os.getenv("TWITCH_CLIENT_SECRET")

# req = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials&scope=<space-separated list of scopes>"
def createTwitchAppToken():
    url = f"https://id.twitch.tv/oauth2/token?client_id={TWITCH_CLIENT_ID}&client_secret={TWITCH_CLIENT_SECRET}&grant_type=client_credentials"
    response = requests.post(url).json()
    token = response["access_token"]
    return token

def getUserID(username, token):
    url = f"https://api.twitch.tv/helix/users?login={username}"
    #headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization":"Bearer " + createTwitchAppToken()}
    headers = {"Client-ID": TWITCH_CLIENT_ID, "Authorization":"Bearer " + token}
    response = requests.get(url, headers=headers)
    return response
    #return userID

def createTwitchDiscordWebhook(userID, server, token):
    posturl = r"https://api.twitch.tv/helix/eventsub/subscriptions"
    webhookurl = server
    payload = {
    "type": "stream.online",
    "version": "1",
    "condition": {
        "broadcaster_user_id": f"{userID}"
    },
    "transport": {
        "method": "webhook",
        "callback": f"{webhookurl}",
        "secret": "secretcodeDFSDFEOIA"
    }
}
    # create algorithm to generate secret ID per automated request to TwitchAPI
    headers = {"Client-ID":TWITCH_CLIENT_ID, "Authorization":"Bearer " + token, "Content-Type":"application/json"}
    response = requests.post(posturl, data=json.dumps(payload), headers=headers)
    return response
