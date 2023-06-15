import datetime
import numpy as np
import os
import os.path as osp
import glob
import time
import cv2
import insightface
from insightface.app import FaceAnalysis
from insightface.data import get_image as ins_get_image
import matplotlib.pyplot as plt
import math

print('insightface', insightface.__version__)
print('numpy', np.__version__)

assert float('.'.join(insightface.__version__.split('.')[:2])) >= float('0.7')

app = FaceAnalysis(name='buffalo_l')
app.prepare(ctx_id=0, det_size=(640, 640))

swapper = insightface.model_zoo.get_model('./discord/model/inswapper_128.onnx',
                                          download=False,
                                          download_zip=False)


def swap_face(input_image, face_image):
    """
    :param input_image:
    :param face_image:
    :return: status, result image path
    """
    print("[face] swap face prepare to generate ... ")
    input_img = cv2.imread(input_image)
    in_faces = app.get(input_img)

    face_img = cv2.imread(face_image)
    faces = app.get(face_img)

    if len(in_faces) <= 0 or len(faces) <= 0:
        print("[face] generate failed! no faces!")
        return False, input_image

    # Sorts left to right
    # in_faces = sorted(in_faces, key=lambda x: x.bbox[0])
    #
    # face_img = cv2.imread(face_image)
    # faces = app.get(face_img)
    # if len(faces) > 2 or len(faces) != len(in_faces):
    #     print("Cartoon generate failed! face count not matched!")
    #     return False, input_image
    #
    # faces = sorted(faces, key=lambda x: x.bbox[0])

    in_faces = sorted(in_faces, key=lambda x: math.fabs(x.bbox[0] - x.bbox[2]) * math.fabs(x.bbox[1] - x.bbox[3]),
                      reverse=True)
    faces = sorted(faces, key=lambda x: math.fabs(x.bbox[0] - x.bbox[2]) * math.fabs(x.bbox[1] - x.bbox[3]),
                   reverse=True)

    max_cnt = 2
    size = min(len(in_faces), len(faces), max_cnt)
    in_faces = in_faces[:size]
    faces = faces[:size]

    mid_face = 0
    min_distance = 1000000000
    h, w, _ = face_img.shape
    for idx, face in enumerate(faces):
        mx = math.fabs(face.bbox[0] - face.bbox[2]) / 2
        if math.fabs(w/2 - mx) < min_distance:
            min_distance = math.fabs(w/2 - mx)
            mid_face = idx

    faces = [faces[mid_face]]

    mid_face = 0
    min_distance = 1000000000
    h, w, _ = input_img.shape
    for idx, face in enumerate(in_faces):
        mx = math.fabs(face.bbox[0] - face.bbox[2]) / 2
        if math.fabs(w / 2 - mx) < min_distance:
            min_distance = math.fabs(w / 2 - mx)
            mid_face = idx
    in_faces = [in_faces[mid_face]]

    if len(faces) > max_cnt or len(faces) != len(in_faces):
        print("[face] generate failed! face count not matched!")
        return False, input_image

    for idx, face in enumerate(in_faces):
        input_img = swapper.get(input_img, face, faces[idx], paste_back=True)

    file_name = os.path.join('./images', str(time.time()) + '_swapface.png')
    cv2.imwrite(file_name, input_img)
    print("[face] generate finished!")
    return True, file_name


if __name__ == '__main__':
    input = 'images/face/cartoon.png'
    ret, img = swap_face(input, 'images/face/person_0.jpg')
    if ret:
        plt.imshow(img[:, :, ::-1])
        plt.show()
