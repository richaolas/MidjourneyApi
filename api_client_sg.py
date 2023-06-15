import requests
import json
import time
import cv2
import base64
import numpy as np
import utility

def image_to_base64(image_np):
    """
    将np图片(imread后的图片）转码为base64格式
    image_np: cv2图像，numpy.ndarray
    Returns: base64编码后数据
    """
    image = cv2.imencode('.bmp', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def base64_to_image(base64_code):
    """
    将base64编码解析成opencv可用图片
    base64_code: base64编码后数据
    Returns: cv2图像，numpy.ndarray
    """
    # base64解码
    img_data = base64.b64decode(base64_code)
    # 转换为np数组
    img_array = np.fromstring(img_data, np.uint8)
    # 转换成opencv可用格式
    img = cv2.imdecode(img_array, -1)

    return img


# set headers
headers = {
    'Content-Type': 'application/json'
}

# url = "http://127.0.0.1:8090//v1/yolov8_api"
url = "http://127.0.0.1:9999/v1/digital"
# url = "http://127.0.0.1:8090///v1/Logic_unit_api"


img = cv2.imread("tf.jpg")
img_base64 = utility.image_to_base64(img)

res = {
    "text": '',
    "image": img_base64,
    'action': 'generate',   # generate, print
    'count': '0'
    }
# res = {"Message": "123"}

res = json.dumps(res)

# send message by post type
result = requests.post(url, headers=headers, data=res)
response = json.loads(result.text)
# print(response["message"])
image_base64 = response["image"]
image = base64_to_image(image_base64)
cv2.imwrite("response.png",image)

# cv2.imshow("frame", image)
# cv2.waitKey(0)
# cv2.waitKey(0)
# cv2.destroyAllWindows()
# cv2.imwrite("client.jpg", image)
