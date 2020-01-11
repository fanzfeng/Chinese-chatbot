# -*- coding: utf-8 -*-
# @Date  : 07/08/2018
# @Author  : fanzfeng

import requests
from utils.nlp_utils import ZhNlp

nlp = ZhNlp(config_lib="jieba")


class WeatherQA(object):
    def __init__(self):
        self.user_key = "5467ebc56c2c008233d0d81d0c92a17a"

        self.area_find_url = "https://restapi.amap.com/v3/config/district?keywords={area_words}&subdistrict=0&key={key}"

        self.weather_url = "https://restapi.amap.com/v3/weather/weatherInfo?key={key}&output=json" \
              "&extensions=all&city={area_code}"

        self.date_config = [["今天", "今日"], ["明天", "后日"], ["后天"]]
        self.w_p = ["ns"]

    def weather_api(self, ad_word):
        url_ = self.area_find_url.format(area_words=ad_word, key=self.user_key)
        res = requests.get(url_).json()
        ad_json = res["districts"]
        if len(ad_json) > 0:
            ad_code = ad_json[0]["adcode"]
            return requests.get(self.weather_url.format(key=self.user_key, area_code=ad_code)).json()

    def date_index(self, d):
        for i in range(len(self.date_config)):
            for s in self.date_config[i]:
                if s in d:
                    return i
        return None

    def loc_index(self, s):
        loc = None
        if isinstance(s, str) and len(s) > 1:
            res = nlp.zh_ner(s)
            if res:
                n = len(res[-1])
                for i in range(n):
                    if res[-1][i] in self.w_p:
                        loc = res[0][i]
        return loc

    def weather_query(self, loc_text, date_ix):
        if date_ix is not None:
            js_res = self.weather_api(loc_text)
            if not isinstance(js_res, dict):
                return "查无此地，请改正后重试"
            js_data = js_res["forecasts"][0]
            area, js_dict = js_data["city"], js_data["casts"][date_ix]
            res = area + " " + js_dict['date'] + " 天气播报：\n"
            res += "白天{}，晚上{}\n".format(js_dict['dayweather'], js_dict['nightweather'])
            res += "温度预测，白天{}℃ 晚上{}℃".format(js_dict['daytemp'], js_dict['nighttemp'])
            return res
