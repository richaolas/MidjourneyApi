# cartoon
import json

authorization = "MTExNTgzNjAwNTc1NzQ5NzM0Ng.G8x46O.B2mQSsLrSnz8vjjXc7-XAi73GyJsO6ZwoaAdyY"
pay_load = """
{"type":2,"application_id":"936929561302675456","guild_id":"1116559345858121780","channel_id":"1116559346600521780","session_id":"271e3d1dcf91ea1299b97026e34a5605","data":{"version":"1118961510123847772","id":"938956540159881230","name":"imagine","type":1,"options":[{"type":3,"name":"prompt","value":"water and fire"}],"application_command":{"id":"938956540159881230","application_id":"936929561302675456","version":"1118961510123847772","default_member_permissions":null,"type":1,"nsfw":false,"name":"imagine","description":"Create images with Midjourney","dm_permission":true,"contexts":[0,1,2],"options":[{"type":3,"name":"prompt","description":"The prompt to imagine","required":true}]},"attachments":[]},"nonce":"1127823259333558272"}
"""

json_payload = json.loads(pay_load)

application_id = json_payload["application_id"]
guild_id = json_payload["guild_id"]
channel_id = json_payload["channel_id"]
version = json_payload["data"]["version"]
id = json_payload["data"]["id"]
timeout_resend = 40

# swap face
swap_face = 0

# person segmention
person_segmention = 0

cartoon = 1

print = 0
