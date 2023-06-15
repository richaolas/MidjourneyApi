import discord.face
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

if __name__ == '__main__':
    input = './discord/faces/art.jpg'
    face = './discord/faces/gyy_face.jpg'
    ret, img = discord.face.swap_face(input, face)
    if ret:
        plt.imshow(img[:, :, ::-1])
        plt.show()