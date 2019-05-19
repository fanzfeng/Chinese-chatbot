# -*- coding: utf-8 -*-
# version=3.6.4
# @Date  : 2019/1/19
# @Author  : fanzfeng

import re
import time
import jieba
import random
import requests
import json

from bot_config import *

# from s2s_bot.min_bot import ChatBot
from frame_bot.frame_chatbot import FRAME
from se_bot.qa_search import SearchEngine

t0 = time.time()
logging.info("Load our bots...")
cn_text_cut = jieba.cut

personality = SearchEngine(query2rid_file=query2rid_file,
                           rid2res_file=None,
                           file_stop_dict=file_stop_words,
                           words_cut_func=cn_text_cut)
personality.build_index()
weather_query = FRAME()
# chat_query = ChatBot(data_path="/home/fanzfeng/backup/processed",
#                      model_path="/home/fanzfeng/backup/s2s_lr0.5_ft256",
#                      words_cut_func=cn_text_cut)

t1 = time.time()
logging.info("Bots is ready (use time {0:.2f}min), here we go.".format(t1/60-t0/60))


def clean_input_bound(text, s_ix=0):
    if len(text) > 0:
        if text[s_ix] in stops_list:
            if len(text) > 1:
                return clean_input_bound(text[s_ix+1:], s_ix) if s_ix >= 0 else clean_input_bound(text[:s_ix], s_ix)
            else:
                return ""
        else:
            return text


def api_chat(user_text="附近的酒店"):
    url = "http://openapi.tuling123.com/openapi/api/v2"
    js = {
        "reqType": 0,
        "perception": {"inputText": {"text": user_text},
                       "inputImage": {"url": "imageUrl"},
                       "selfInfo": {"location": {"city": "北京"}}
                       },
        "userInfo": {
            "apiKey": "a391ecb267d34c95b58c6487e3a549a0",
            "userId": "a391ecb267d34c95b58c6487e3a549a0"
        }
    }
    res = requests.post(url, data=json.dumps(js))
    return res.json()['results'][0]['values']['text'].replace("图灵", "")


def clean_input(text):
    text_left = clean_input_bound(text)
    return clean_input_bound(text=text_left, s_ix=-1)


def text_unique(output_text):
    words_list = list(cn_text_cut(output_text))
    new_list = []
    if len(words_list) > 1:
        new_list.append(words_list[0])
        for w in words_list[1:]:
            if w != new_list[-1]:
                new_list.append(w)
    elif len(words_list) == 1:
        new_list += words_list
    return new_list


def one_bot(input_str, uid="_global", min_score=0.6):
    input_text = clean_input(input_str.strip().replace(" ", ""))
    if len(input_text) <= 0:
        return random.choice(noinput_response)
    elif len(input_text) <= 1:
        return random.choice(default_response)
    elif sum(re.match(r, input_text) is not None for r in switch_rules) > 0:
        return random.choice(switch_response)
    elif sum(k in input_text for k in weather_keywords) > 0:
        return weather_query.respond(input_text, uid)
    else:
        per_res = personality.query_search(input_text, res_num=1)
        if len(per_res) >= 1 and per_res[0]["score"] > min_score:
            return per_res[0]["answer"]
        try:
            res_text = api_chat(input_text)
        except Exception as e:
            logging.info("turing api error: {}".format(e))
            # print("turing api error: ",e)
            res_text = ""      
        # print("api res: ", res_text)
        # res_text = chat_query.s2s_bot(input_text)
        if len(res_text) <= 1:
            return random.choice(default_response)
        return res_text
        # res_text_clean = clean_input(res_text)
        # if len(res_text_clean) <= 1:
        #    return random.choice(default_response)
        # text_unq = text_unique(res_text_clean)
        # if len(text_unq) <= 1:
        #    return random.choice(default_response)
        # else:
        #    return None


if __name__ == "__main__":
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit"):
            print("再见")
            break
        print(one_bot(user_input))
