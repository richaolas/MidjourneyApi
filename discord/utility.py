import requests
import json
import time
import cv2
import base64
import numpy as np


def image_to_base64(image_np):
    """
    将np图片(imread后的图片）转码为base64格式
    image_np: cv2图像，numpy.ndarray
    Returns: base64编码后数据
    """
    image = cv2.imencode('.png', image_np)[1]
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
    img = cv2.imdecode(img_array, cv2.COLOR_RGB2BGR)

    return img
