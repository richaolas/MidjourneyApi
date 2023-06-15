import os.path
import time

from flask import request
from flask import Flask
from flask_cors import CORS
import traceback
import cv2
import base64
import numpy as np
import utility
import printer
import signature
from segmention import segmention_main, save_img, save_img_byte
from cartoon import cartoon, get_generate_status


app = Flask(__name__)
DIGITAL_URL = "/v1/digital"

IMAGE_SRC = '_src.png'
IMAGE_REMOVE_BG = '_nobg.png'
IMAGE_CARTOON = '_cartoon.png'
IMAGE_CUT = '_cut.png'

global_timestamp = time.time()
# global_processing_image ="./images/face/global_processing_image.webp"

def get_image_path(type):
    return os.path.join("images", str(global_timestamp) + type)


def print_image(imagefile, text, count):
    cnt = 1  # default is just one photo print
    try:
        cnt = int(count)
    except ValueError as e:
        print('value error')
        pass
    print(f'print count {cnt} with text: {text}')
    img_name = imagefile
    print('# save image: ', img_name)
    if text.strip():
        signature_image = signature.generate_signature(text)
        update_image = signature.merge(cv2.imread(img_name), signature_image)
        cv2.imwrite(img_name, update_image)
        print('print service save image ', img_name)

    ret = True
    for c in range(cnt):
        print('print ...')
        t = printer.print_image(img_name, printer.DMPAPER_METRIC_PHOTO_L, margin=(0, 0))
        ret = ret and t
    return ret, utility.image_to_base64(cv2.imread(img_name))


def generate_cartoon(image):
    cartoon_image_path = cartoon(image)
    image = cartoon_image_path
    seg_image_path = segmention_main(image, 1)

    return seg_image_path


def generate_image(image):
    pass


def invalid_parameter():
    return {'code': 201, 'result': 'invalid parameter'}

def fetch_process_image():

    status, image_path = get_generate_status()
    image_base64=''
    if os.path.exists(image_path):
        print("processing image is {}".format(image_path))
        image = cv2.imread(image_path)
        image_base64=utility.image_to_base64(image)

    return image_base64

def cut_image(image_path):
    image = cv2.imread(image_path, -1)

    h, w, _, = image.shape

    list = [i for i in range(0, h)]
    cut_index = 0
    for i in list[::-1]:
        image_row = image[i, :, 3]
        num = np.sum(image_row != 0)
        transparent_rate = num / w
        if transparent_rate > 0.1:
            cut_index = i-10
            break

    image_cut = image[0:cut_index, :, :]
    global_timestamp = time.time()
    image_path = get_image_path(IMAGE_CUT)
    cv2.imwrite(image_path, image_cut)
    return image_path

@app.route(DIGITAL_URL, methods=['POST'])
def digital():
    global global_timestamp
    global_timestamp = time.time()

    try:
        image = request.json['image']
        text = request.json['text']
        action = request.json['action']
        count = request.json['count']

        if image!="":
            cv2.imwrite(get_image_path(IMAGE_SRC), utility.base64_to_image(image))

        if action == 'print':
            print(text)
            ret, base64 = print_image(get_image_path(IMAGE_SRC), text, count)
            return {'code': 200, 'result': 'print success', 'image': base64}
        elif action == 'generate':
            image_path = generate_cartoon(get_image_path(IMAGE_SRC))
            image_path = cut_image(image_path)
            print ("cut image done!")
            image = cv2.imread(image_path, -1)
            base64 = utility.image_to_base64(image)
            os.remove(global_processing_image)
            return {'code': 200, 'result': 'generate success', 'image': base64}
        elif action == 'processing':
            base64=fetch_process_image()
            return {'code': 200, 'result': 'processing success', 'image': base64}
        # print(request.json)
        # image = base64_to_image(info)
        # image = cv2.cvtColor(image,cv2.COLOR_RGB2GRAY)
        # image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        # info = image_to_base64(image)
        # print(info)
        # cv2.imwrite("server.jpg", image)
        return {'code': 201, 'result': 'invalid parameter', 'image': ''}
    except Exception as e:
        traceback.print_exc()
        return {'code': 201, 'result': 'invalid parameter', 'image': ''}


if __name__ == "__main__":
    CORS(app, resources={r"/*": {"origins": "*"}})
    app.run(host='0.0.0.0', port=9999)
