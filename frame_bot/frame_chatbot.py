# -*- coding: utf-8 -*-
# @Date  : 08/08/2018
# @Author  : fanzfeng

import time
import logging
import pyltp
import platform
import sys, codecs

sys.path.insert(0, "../")
try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
except:
    pass

from utils_fanzfeng.weather import WeatherQA
from utils_fanzfeng.mongo_service import MongoSevice


if platform.system() == 'Darwin':
    config_dir = '/users/fanzfeng/Data/'
elif platform.system() == 'Linux':
    config_dir = '/home/fanzfeng/nlp_config/'
segmentor = pyltp.Segmentor()
segmentor.load(config_dir + "ltp_data_v3.4.0/cws.model")
postagger = pyltp.Postagger()
postagger.load(config_dir + "ltp_data_v3.4.0/pos.model")
recognizer = pyltp.NamedEntityRecognizer()
recognizer.load(config_dir + "ltp_data_v3.4.0/ner.model")

weather = WeatherQA()


def ner(text):
    words = list(segmentor.segment(text))
    postags = list(postagger.postag(words))
    netags = list(recognizer.recognize(words, postags))
    jr = {}
    for h in ["B", "I", "E", "S"]:
        for s in ["Nh", "Ns", "Ni"]:
            if h + "-" + s in netags:
                jr[s] = words[netags.index(h + "-" + s)]
    return jr


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
            ad_dict = ner(input_)
            if 'Ns' in ad_dict or 'Ni' in ad_dict:
                request_info["loc_text"] = (ad_dict['Ns'] if 'Ns' in ad_dict else ad_dict['Ni'])
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

