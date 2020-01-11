# -*- coding: utf-8 -*-
# @Date  : 08/08/2018
# @Author  : fanzfeng
'''
天气助手：多轮对话
> 对话管理：槽位填充+if-else
> 文本理解：ner+规则
> 天气查询：高德API
'''

import time
import os, sys

botPath = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
print(botPath)
sys.path.append(botPath)

from bot_config import logging
from utils.weather import WeatherQA
from utils.mongo_service import MongoSevice


weather = WeatherQA()


def action_query(query_info):
    if len(query_info["loc_text"]) > 0 and query_info["date_ix"] is not None:
        return weather.weather_query(query_info["loc_text"], query_info["date_ix"])
    elif query_info["date_ix"] is not None:
        return "您要查询哪个城市的天气呢？"
    elif len(query_info["loc_text"]) > 0:
        return "您要查询{}什时候的天气呢，今天？明天？后天？".format(query_info["loc_text"])
    else:
        return "您要查询哪个城市什么时候的天气呢？"


class FRAME(object):
    def __init__(self):
        self.mong = MongoSevice(my_db="chatbot", my_set="weather", id_col="uid")
        self.res_default = {"loc_text": "", "date_ix": None}
        self.default_city = "深圳"

    def add_session(self, sessionID):
        res_mong = self.mong.find_request(sessionID)
        if isinstance(res_mong, dict):
            time_diff = int(time.time() - res_mong["update_time"])
            if time_diff < 60*10:
                self.mong.update_request(sessionID, set={"update_time": time.time()})
                return {k: res_mong[k] for k in self.res_default}
            else:
                self.mong.update_request(sessionID, set={"update_time": time.time(),
                                                         "loc_text": "", "date_ix": None})
                return self.res_default
        else:
            self.mong.insert_request(doc={"update_time": time.time(), "loc_text": "", "date_ix": None,
                                     "uid": sessionID})
            return self.res_default

    def respond(self, input_, sessionID="_global"):
        try:
            request_info = self.add_session(sessionID)
        except Exception as e:
            logging.error("Mongo search error, maybe about network: {}".format(e))
            request_info = self.res_default
        logging.debug("Session start json: {}".format(request_info))
        if len(input_) > 0:
            ad_dict = weather.loc_index(input_)
            if ad_dict:
                request_info["loc_text"] = ad_dict
                self.mong.update_request(sessionID,
                                         set={"loc_text": request_info["loc_text"], "update_time": time.time()})
            date_info = weather.date_index(input_)
            if date_info is not None:
                request_info["date_ix"] = date_info
                self.mong.update_request(sessionID, set={"date_ix": date_info, "update_time": time.time()})
            if len(request_info["loc_text"]) < len(self.default_city) > 0:
                request_info["loc_text"] = self.default_city
                self.mong.update_request(sessionID, set={"date_ix": date_info, "update_time": time.time()})
        logging.debug("Session end json: {}".format(request_info))
        return action_query(request_info)


if __name__ == "__main__":
    query = FRAME()
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit", "exit"):
            print("再见")
            break
        print(query.respond(user_input))
