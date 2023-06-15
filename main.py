import time
import sys
from discord.cartoon import cartoon

sys.path.append("discord")

if __name__ == '__main__':
    prompt_cmd = ""
    photo = './discord/sample/gyy.jpg'
    beg = time.time()
    cartoon(photo)
    end = time.time()
    print(end - beg)
