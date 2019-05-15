#!/usr/bin/env python
# version='3.5.2'
# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import sys, codecs
sys.path.insert(0, "../")
# sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from aiml.constants import *
import aiml

from getweather import weather_bot

import elasticsearch
# ip = "101.200.61.56"
# es = elasticsearch.Elasticsearch([ip], http_auth=('elastic', 'changeme'))

k = aiml.Kernel()
k.loadSubs('subbers.ini')
k.learn("startup.xml")
k.respond("load aiml cn")


def mix_bot(text_, sid):
    return k.respond(text_.upper().replace(" ", ""), sessionID=sid)


if __name__ == "__main__":
    while True:
        input_ = input("> ").upper().replace(" ", "")
        if "天气" in input_ or "温度" in input_:
            weather_bot(input_)
        else:
            print(k.respond(input_))
