# -*- coding: utf-8 -*-
# @Date  : 08/08/2018
# @Author  : fanzfeng

import os, sys, codecs
botPath = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
print(botPath)

sys.path.append(botPath)
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from utils.weather import WeatherQA

wea = WeatherQA()


def weather_bot(text):
    ad_text = wea.loc_index(text)
    date_set = wea.date_index(text)
    if ad_text:
        pass
    else:
        ad_text = "深圳"
    if date_set is None:
        print(wea.weather_query(ad_text, 0))
    else:
        print(wea.weather_query(ad_text, date_set))


def main():
    assert len(sys.argv) >= 2
    text = "".join([str(t) for t in sys.argv[1:]])
    weather_bot(text)


if __name__ == "__main__":
    weather_bot("明天上海天气")
