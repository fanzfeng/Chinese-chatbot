# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import os
import sys
botPath = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
print(botPath)
sys.path.append(botPath)

from aiml.constants import *
import aiml

from getweather import weather_bot

weather_keywords = ["天气", "下雨", "晴天", "阳光", "温度", "下雪"]

k = aiml.Kernel()
k.loadSubs('subbers.ini')
k.learn("startup.xml")
k.respond("load aiml cn")


def mix_bot(text_, sid):
    return k.respond(text_.upper().replace(" ", ""), sessionID=sid)


if __name__ == "__main__":
    while True:
        input_ = input("> ").upper().replace(" ", "")
        if sum(k in input_ for k in weather_keywords) > 0:
            weather_bot(input_)
        else:
            print(k.respond(input_))
