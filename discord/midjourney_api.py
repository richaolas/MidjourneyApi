import requests
from urllib.parse import urlparse
import os
import random
import time
import json
import time
import requests
import shutil
import os


class MidjourneyApi:

    def __init__(self, application_id, guild_id, channel_id, version, id, authorization):
        self.application_id = application_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.id = id
        self.authorization = authorization
        # self.prompt = prompt
        self.message_id = ""
        self.custom_id = ""
        self.image_path_str = ""

        self.select_image_url = ""

        self.generate_status = ""  # idle, wait, start, done
        self.generate_image_path = ""
        self.save_image_path = "images"

        self.last_done_timestamp = None

        # beg = time.time()
        # self.send_message()
        # end = time.time()
        # print('send mj command: ', end - beg)
        # self.get_message()
        # self.choose_images()
        # self.download_image()

    def send_imagine_message(self, prompt):
        url = "https://discord.com/api/v9/interactions"
        data = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "session_id": "cannot be empty",
            "data": {
                "version": self.version,
                "id": self.id,
                "name": "imagine",
                "type": 1,
                "options": [
                    {
                        "type": 3,
                        "name": "prompt",
                        "value": prompt
                    }
                ],
                "application_command": {
                    "id": self.id,
                    "application_id": self.application_id,
                    "version": self.version,
                    "default_member_permissions": None,
                    "type": 1,
                    "nsfw": False,
                    "name": "imagine",
                    "description": "Create images with Midjourney",
                    "dm_permission": True,
                    "contexts": None,
                    "options": [
                        {
                            "type": 3,
                            "name": "prompt",
                            "description": "The prompt to imagine",
                            "required": True
                        }
                    ]
                },
                "attachments": []
            },
        }
        headers = {
            'Authorization': self.authorization,
            'Content-Type': 'application/json',
        }
        response = requests.post(url, headers=headers, json=data)

    def get_promote_message_id(self, prompt):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(10):
            try:
                idx = prompt.index(' ')
                sub_prompt = prompt[idx:]
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=1',
                                        headers=headers)
                if response.status_code == 200:
                    messages = response.json()
                    if len(messages) > 0 and messages[0]["content"].index(sub_prompt) >= 0:
                        return messages[0]['id']
                        break
            except:
                time.sleep(1)
                ValueError("Timeout")
        return ""

    def get_message_timestamp(self, message):
        print(message["timestamp"], message["timestamp"][:-6])
        return time.strptime(message["timestamp"][:-6], "%Y-%m-%dT%H:%M:%S.%f")

    def get_last_message(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=10',
                                headers=headers)
        if response.status_code != 200:
            return False
        messages = response.json()
        if messages:
            return messages[0]
        return None

    def get_message_by_id(self, message_id):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages?limit=10',
                                headers=headers)
        if response.status_code != 200:
            print(f"[midjourney] response.status_code != 200 : {response.status_code}")
            return False
        messages = response.json()

        message = None
        for mes in messages:
            # print(mes["id"], type(mes["id"]))
            if mes["id"] == message_id:
                message = mes
                break
        return message

    def midjourney_imagine_status(self, message_id):
        message = self.get_message_by_id(message_id)
        # 如果原始消息没有了，说明生成完毕,
        if not message:  # 说明生成完毕
            print("[midjourney] promote message is update to result message.")
            return "done"

        # 或者，如果最新的消息 id，不等于原来的消息id，也生成完毕
        last_message = self.get_last_message()
        cur_timestamp = self.get_message_timestamp(last_message)

        if last_message and last_message["id"] != message_id:
            if 'attachments' in last_message.keys() and len(last_message['attachments']) > 0:
                # 必须要求这个时间比上一次生成的时间晚，不然就是同一个消息了
                if not self.last_done_timestamp or (self.last_done_timestamp and cur_timestamp > self.last_done_timestamp):
                    print(
                        f"[midjourney] last message is 4 result image, but the src promote message still exist.{message_id}-{last_message['id']}")
                    return "done"

        # print(message, type(message), dir(message))
        if 'attachments' in message.keys() and len(message['attachments']) > 0:
            return "start"
        return "wait"

    """
    get processing image, get image by message id
    """

    def get_message_image(self, message_id):
        message = self.get_message_by_id(message_id)
        # print(message, type(message), dir(message))
        if message and 'attachments' in message.keys() and len(message['attachments']) > 0:
            image_url = message['attachments'][0]['url']
            image_response = requests.get(image_url)
            a = urlparse(image_url)
            image_name = os.path.basename(a.path)
            time_stamp = time.time()

            self.image_path_str = f"{self.save_image_path}/{time_stamp}_{image_name}"
            if not os.path.exists(self.save_image_path):
                os.makedirs(self.save_image_path)
            with open(self.image_path_str, "wb") as file:
                file.write(image_response.content)
            return self.image_path_str
        return ""

    """
    get last 4 images
    """

    def get_generate_4result(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        try:
            response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages',
                                    headers=headers)
            messages = response.json()
            message = messages[0]

            self.last_done_timestamp = self.get_message_timestamp(message)  # time.strptime(message["timestamp"][-6], "%Y-%m-%dT%H:%M:%S.%f")

            if 'attachments' in message.keys() and len(message['attachments']) > 0:
                image_url = message['attachments'][0]['url']
                image_response = requests.get(image_url)
                a = urlparse(image_url)
                image_name = os.path.basename(a.path)
                self.image_path_str = f"images/{image_name}"
                with open(f"images/{image_name}", "wb") as file:
                    file.write(image_response.content)
                return self.image_path_str
        except:
            return ""

    def get_message(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(12):
            time.sleep(10)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages',
                                        headers=headers)
                messages = response.json()
                # print("get message", response.json())
                # print("-----------------------------------------------"*2)
                most_recent_message_id = messages[0]['id']
                self.message_id = most_recent_message_id
                components = messages[0]['components'][0]['components']
                buttons = [comp for comp in components if comp.get('label') in ['U1', 'U2', 'U3', 'U4']]
                custom_ids = [button['custom_id'] for button in buttons]
                random_custom_id = random.choice(custom_ids)
                self.custom_id = random_custom_id
                break
            except:
                ValueError("Timeout")

    def choose_images(self):
        url = "https://discord.com/api/v9/interactions"
        headers = {
            "Authorization": self.authorization,
            "Content-Type": "application/json",
        }
        data = {
            "type": 3,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "message_flags": 0,
            "message_id": self.message_id,
            "application_id": self.application_id,
            "session_id": "cannot be empty",
            "data": {
                "component_type": 2,
                "custom_id": self.custom_id,
            }
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))

    def download_image(self):
        headers = {
            'Authorization': self.authorization,
            "Content-Type": "application/json",
        }
        for i in range(6):
            time.sleep(10)
            try:
                response = requests.get(f'https://discord.com/api/v9/channels/{self.channel_id}/messages',
                                        headers=headers)
                messages = response.json()
                most_recent_message_id = messages[0]['id']
                # 不能和四宫格一样啊
                if most_recent_message_id == self.message_id:
                    continue
                self.message_id = most_recent_message_id
                image_url = messages[0]['attachments'][0]['url']
                image_response = requests.get(image_url)
                a = urlparse(image_url)
                print("select image url: ", a)
                self.select_image_url = a
                image_name = os.path.basename(a.path)
                self.image_path_str = f"images/{image_name}"
                with open(f"images/{image_name}", "wb") as file:
                    file.write(image_response.content)
                break
            except:
                raise ValueError("Timeout")

    def image_path(self):
        return self.image_path_str

    def midjourney_imagine(self, prompt, timeout_resend=40):
        # midjourney = MidjourneyApi(prompt=prompt_cmd, application_id=application_id, guild_id=guild_id,
        #                           channel_id=channel_id, version=version, id=id, authorization=authorization)
        # global global_processing_image
        beg = time.time()
        message_id = ""
        while message_id == "":
            self.send_imagine_message(prompt)
            message_id = self.get_promote_message_id(prompt)
        end = time.time()
        print("[midjourney] send message time cost: ", end - beg)

        start_time = time.time()
        start_flag = False
        self.generate_status = 'idle'
        self.generate_image_path = ''
        while True:
            if time.time() - start_time > timeout_resend and not start_flag:
                self.send_imagine_message(prompt)
                message_id = self.get_promote_message_id(prompt)
                start_time = time.time()
                start_flag = False

            generate_status = self.midjourney_imagine_status(message_id)
            if generate_status == 'done':
                break
            elif generate_status == "start":
                print("[midjourney] start process ", time.time() - start_time)
                start_flag = True
                # global_processing_image = src_path = midjourney.get_message_image(message_id)
                self.generate_status = generate_status
                self.generate_image_path = self.get_message_image(message_id)
                print(f"[midjourney] generate {self.generate_image_path}")
            elif self.generate_status == "wait":
                self.generate_status = generate_status
                print("[midjourney] waiting for ", time.time() - start_time)
                time.sleep(1)

        print("[midjourney] midjourney during: ", time.time() - start_time)
        result_image_path = self.get_generate_4result()
        self.generate_status = 'done'
        self.generate_image_path = result_image_path
        print(result_image_path)

        return result_image_path

    def get_generate_status(self):
        return self.generate_status, self.generate_image_path

    def reset_generate_status(self):
        self.generate_status = 'idle'
        self.generate_image_path = ''
        return self.generate_status, self.generate_image_path


class InsightFaceApi:

    def __init__(self, prompt, application_id, guild_id, channel_id, version, id, authorization):
        self.application_id = application_id
        self.guild_id = guild_id
        self.channel_id = channel_id
        self.version = version
        self.id = id
        self.authorization = authorization
        # self.prompt = prompt
        # self.message_id = ""
        # self.custom_id = ""
        # self.image_path_str = ""

    def insight_face_swap(self, target_id):
        url = "https://discord.com/api/v9/interactions"
        headers = {
            "Authorization": self.authorization,
            "Content-Type": "application/json",
        }
        data = {
            "type": 2,
            "application_id": self.application_id,
            "guild_id": self.guild_id,
            "channel_id": self.channel_id,
            "session_id": "cannot be empty",
            "data": {
                "version": self.version,
                "id": self.id,
                "name": "INSwapper",
                "type": 3,
                "options": [],
                "application_command": {
                    "id": self.id,
                    "application_id": self.application_id,
                    "version": self.version,
                    "default_member_permissions": None,
                    "type": 3,
                    "nsfw": False,
                    "name": "INSwapper",
                    "description": "",
                    "dm_permission": True,
                    "contexts": None
                },
                "target_id": target_id,
                "attachments": []
            },
        }
        response = requests.post(url, headers=headers, data=json.dumps(data))


if __name__ == '__main__':
    pass
    # p = "https://s.mj.run/Ueo8RdCYi3s simple avatar, pixar, 3d rendering, 3D character from Disney Pixar Animation, --s 500 --iw 2.0 --quality 0.5 --aspect 1:1"
    # idx = p.index(' ')
    # print(p[idx:])
