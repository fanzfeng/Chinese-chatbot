# -*- coding: utf-8 -*-
# version=3.6.4
# @Date  : 2019/1/19
# @Author  : fanzfeng

import time
import jieba
import random
import datetime
import requests
import json

from utils_fanzfeng.mysql_service import MysqlSevice
from bot_config import *

# from s2s_bot.min_bot import ChatBot
from frame_bot.frame_chatbot import FRAME
from se_bot.qa_search import SearchEngine
from char_bot.char_gen import GenName

t0 = time.time()
logging.info("Load our bots...")
cn_text_cut = jieba.cut
mysql = MysqlSevice()

personality = SearchEngine(query2rid_file=query2rid_file,
                           rid2res_file=None,
                           file_stop_dict=file_stop_words,
                           words_cut_func=cn_text_cut)
personality.build_index()
weather_query = FRAME()
bot_name = GenName()
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


def one_bot(input_str, uid="_global", min_score=0.7):
    input_text = clean_input(input_str.strip().replace(" ", ""))
    dt = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    date_int = datetime.datetime.now().strftime("%Y%m%d")
    reply_cate = "default"
    if len(input_text) <= 0:
        reply_cate = "noinput"
        reply_text = random.choice(noinput_response)
    elif len(input_text) <= 1:
        reply_text = random.choice(default_response)
    elif sum(re.match(r, input_text) is not None for r in switch_rules) > 0:
        reply_cate = "switch"
        reply_text = random.choice(switch_response)
    elif sum(k in input_text for k in weather_keywords) > 0:
        reply_cate = "weather"
        reply_text = weather_query.respond(input_text, uid)
    else:
        format_input = fmt_pat_not_cn.sub('', input_text)
        format_text = fmp_pat_not_modal.sub('', format_input)
        per_res = personality.query_search(input_text, res_num=1)
        gname_cond = gname_rule.match(format_text)
        if sum(k in format_text for k in gname_keywords) > 0:
            reply_cate = "get_name"
            return gname_reply
        elif len(format_text) < gname_maxlen and gname_cond:
            reply_cate = "get_name"
            return bot_name.gen_name(gname_cond.group(1))
        elif len(per_res) >= 1 and per_res[0]["score"] > min_score:
            reply_text = per_res[0]["answer"]
            reply_cate = "personality"
        else:
            try:
                reply_text = api_chat(input_text)
            except Exception as e:
                logging.warning("turing api error: {}".format(e))
            if 'reply_text' not in locals().keys() or not isinstance(reply_text, str):
                logging.warning("chat api of turing get error! ! !")
                reply_text = random.choice(default_response)
            elif "请求次数超限制" in reply_text:
                logging.warning("chat api of turing beyond use! ! !")
                reply_text = "."+random.choice(default_response)
            else:
                reply_cate = "chat"

        # res_text = chat_query.s2s_bot(input_text)
        # res_text_clean = clean_input(res_text)
        # if len(res_text_clean) <= 1:
        #    return random.choice(default_response)
        # text_unq = text_unique(res_text_clean)
        # if len(text_unq) <= 1:
        #    return random.choice(default_response)
        # else:
        #    return None

    mysql.insert([[uid, date_int, reply_cate, input_str, reply_text, dt]])
    return reply_text


if __name__ == "__main__":
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit"):
            print("再见")
            break
        print(one_bot(user_input))
