from discord.midjourney_api import MidjourneyApi
from discord.midjourney_api import InsightFaceApi
import discord.face
import matplotlib.pyplot as plt
import time
import cv2
from urllib.parse import urlparse
import time
import requests
import shutil
import os

class DiscordMessage:

    def __init__(self, channel_id, authorization):
        self.channel_id = channel_id
        self.authorization = authorization
        self.last_message_id = ""
        self.message_id = ""

    def get_last_message_id(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(60):
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages',
                                        headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                if most_recent_message_id == self.last_message_id:
                    time.sleep(1)
                    continue
                self.last_message_id = most_recent_message_id
                self.message_id = most_recent_message_id
                break

            except:
                raise ValueError("Timeout 60s ...")

    def get_image_url(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(60):
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages',
                                        headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                image_url = messages[0]['attachments'][0]['url']
                image_response = requests.get(image_url)
                a = urlparse(image_url)
                return a.path
            except:
                raise ValueError("Timeout")
                time.sleep(1)

    """
    return status, message_id, image_url
    """
    def upload_image(self, image):
        # User's Token
        header = {
            'authorization': self.authorization,
        }

        # File
        files = {
            "file": (image, open(image, 'rb'))  # The picture that we want to send in binary
        }
        print(files)

        # Optional message to send with the picture
        payload = {
            "content": "message"
        }

        channel_id = self.channel_id  # Channel where we send the picture

        # self.get_last_message_id()
        # print(self.last_message_id)
        res = requests.post(f"https://discord.com/api/v9/channels/{channel_id}/messages", data=payload, headers=header,
                            files=files)
        if res.status_code == 200:
            return True, res.json()["id"], res.json()["attachments"][0]["url"]

        return False, 0, ""


# if __name__ == '__main__':
#     message = DiscordMessage(channel_id, authorization)
#     message.upload_image('./face.jpg')
#     url = message.get_image_url()
#     url = "https://cdn.discordapp.com/" + url
#     print(url)
#