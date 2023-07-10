import cv2
import numpy as np
import base64
from aip import AipFace

# baidu app
APP_ID = '35776266'
API_KEY = 'qB2avj9CGzVEacVnXkQEor0n'
SECRET_KEY = 'xHuV1qaoyEnmSUFt7PEHe160DiGPiZoa'
client = AipFace(APP_ID, API_KEY, SECRET_KEY)


def image_to_base64(image_np):
    """
    将np图片(imread后的图片）转码为base64格式
    image_np: cv2图像，numpy.ndarray
    Returns: base64编码后数据
    """
    image = cv2.imencode('.png', image_np)[1]
    image_code = str(base64.b64encode(image))[2:-1]
    return image_code


def cal_iou(box1, box2):
    x1_min, y1_min, x1_max, y1_max = box1
    x2_min, y2_min, x2_max, y2_max = box2

    # 上取小下取大，右取小左取大
    xx1 = np.max([x1_min, x2_min])
    yy1 = np.max([y1_min, y2_min])
    xx2 = np.min([x1_max, x2_max])
    yy2 = np.min([y1_max, y2_max])

    # 计算各个框的面积
    area1 = (x1_max - x1_min) * (y1_max - y1_min)
    area2 = (x2_max - x2_min) * (y2_max - y2_min)

    # 计算相交的面积
    inter_area = (np.max([0, xx2 - xx1])) * (np.max([0, yy2 - yy1]))
    # 计算IoU
    iou = inter_area / (area1 + area2 - inter_area)
    return iou


def draw(image, face_info, percent_50_box):
    location = face_info['location']
    left = int(location['left'])
    top = int(location['top'])
    width = int(location['width'])
    height = int(location['height'])
    box = [left, top, left + width, top + height]
    x1, y1, x2, y2 = box
    cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 255), 2)  # 画边框
    cv2.rectangle(image, (percent_50_box[0], percent_50_box[1]), (percent_50_box[2], percent_50_box[3]), (0, 255, 0),
                  2)  # 画边框
    cv2.imshow("111", image)
    cv2.waitKey(0)


def baidu_face_detect(image_path):
    # 按顺序构造出图片路径
    print("image name is {}".format(image_path))
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    percent_50_box = [int(width * 0.25), 0, int(width * 0.75), height]
    image_code = image_to_base64(image)
    face_res = client.detect(image_code, "BASE64",
                             options={'face_field': "age,expression,face_shape,gender,glasses", 'max_face_num': "10"})

    if not face_res['result']:
        return None

    face_list = face_res['result']['face_list']
    max_face_iou = 0.0
    max_face_index = 0
    for i, face in enumerate(face_list):
        location = face['location']
        left = int(location['left'])
        top = int(location['top'])
        width = int(location['width'])
        height = int(location['height'])
        box = [left, top, left + width, top + height]
        iou = cal_iou(box, percent_50_box)
        if iou > max_face_iou:
            max_face_iou=iou
            max_face_index = i
    face_info = face_list[max_face_index]
    # draw(image, face_info, percent_50_box)
    return face_info


if __name__ == '__main__':
    baidu_face_detect(r"C:\Users\UF100195\Desktop\show\images\mx\c04c52580140d16ebc0763a47cb7f7fb.jpeg")
