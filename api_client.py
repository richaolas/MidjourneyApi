import requests
import json
import time
import cv2
import base64
import numpy as np
import utility

img = cv2.imread("tf.jpg")
img_base64 = utility.image_to_base64(img)

res = {
    "text": 'Kobe Bryant',
    "image": img_base64,
    'action': 'print',   # generate, print
    'count': '1'
    }

res = json.dumps(res)
# set headers
headers = {
    'Content-Type': 'application/json'
}

url = "http://127.0.0.1:9999/digital"
# send message by post type
result = requests.post(url, headers=headers, data=res)
response = json.loads(result.text)
print(response["result"])
#print(response)
image_base64 = response["image"]
image = utility.base64_to_image(image_base64)
cv2.namedWindow(' ', 0)
cv2.imshow(' ', image)
cv2.waitKey(0)
