#!/usr/bin/env python
# version=3.6.4
# -*- coding: utf-8 -*-
# @Date  : 08/08/2018
# @Author  : fanzfeng

import sys, codecs
sys.path.insert(0, "../")
sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())

from utils_fanzfeng.weather import weather_api, weather_display, ner

date_config = [["今天", "今日"], ["明天", "后日"], ["后天"]]


def date_index(d):
    for i in range(len(date_config)):
        for s in date_config[i]:
            if s in d:
                return i


def weather_query(loc_text, date_ix):
    if date_ix is not None:
        js_res = weather_api(loc_text)
        if not isinstance(js_res, dict):
            return "地点新奇，本胖表示没听过"
        js_data = js_res["forecasts"][0]
        return weather_display(js_data["city"], js_data["casts"][date_ix])


def weather_bot(text):
    try:
        ad_text = ner(text)
        date_set = date_index(text)
        if 'Ns' not in ad_text:
            print("查无此地，本胖得了504[捂脸]")
        elif date_set is None:
            print(weather_query(ad_text['Ns'], 0))
        else:
            print(weather_query(ad_text['Ns'], date_set))
    except:
        print("尴尬啦，没查到# #")


def main():
    assert len(sys.argv) >= 2
    text = "".join([str(t) for t in sys.argv[1:]])
    weather_bot(text)


if __name__ == "__main__":
    main()