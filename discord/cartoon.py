from discord.midjourney_api import MidjourneyApi
import discord.face
import cv2
import time
from discord.discord_api import DiscordMessage
from discord.config import *


def cuts(image_path, idx=1):
    image = cv2.imread(image_path)

    h, w, _ = image.shape

    h_half = int(h / 2)
    w_half = int(w / 2)

    image1 = image[0:h_half, 0:w_half, :]
    image2 = image[0:h_half, w_half:w, :]
    image3 = image[h_half:h, 0:w_half, :]
    image4 = image[h_half:h, w_half:w, :]

    cv2.imwrite("images/cuts_1.png", image1)
    cv2.imwrite("images/cuts_2.png", image2)
    cv2.imwrite("images/cuts_3.png", image3)
    cv2.imwrite("images/cuts_4.png", image4)

    return f'images/cuts_{idx}.png'


# def get_processing_image():

midjourney = MidjourneyApi(application_id=application_id, guild_id=guild_id,
                           channel_id=channel_id, version=version, id=id, authorization=authorization)

discord_obj = DiscordMessage(channel_id, authorization)


def gen_prompt(image):
    prompt = "{} simple avatar, pixar, 3d rendering, 3D character from Disney Pixar Animation, --s 500 --iw 1.5 --quality 0.5 --aspect 1:1"
    ret, mess_id, image_url = discord_obj.upload_image(image)
    return ret, prompt.format(image_url)


def cartoon(photo):
    # return photo
    beg = time.time()
    ret, prompt_cmd = gen_prompt(photo)
    print(prompt_cmd)
    image = midjourney.midjourney_imagine(prompt_cmd)
    cuts_image_path = cuts(image)
    ret, imgname = discord.face.swap_face(cuts_image_path, photo)
    # end = time.time()
    # cost = end - beg
    # print(f'cost : {cost} second')
    return imgname


def get_generate_status():
    """
    # idle, wait, start, done
    # image_path
    """
    return midjourney.get_generate_status()


if __name__ == '__main__':
    prompt_cmd = ""
    photo = './sample/gyy.jpg'
    beg = time.time()
    cartoon(photo)
    end = time.time()
    print(end - beg)
