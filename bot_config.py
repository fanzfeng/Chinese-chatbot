# -*- coding: utf-8 -*-
# version=3.6.4
# @Date  : 2019/5/15
# @Author  : fanzfeng

import os
import platform
import logging

default_response = ["你说的我没懂哦，正在拼命学习中",
                    "这个我就不懂了，你可以问下邻居小明",
                    "你站在此地不要动，我去买个句子",
                    "你这话我没法接[允悲]",
                    "嗯，然后呢",
                    "请继续你的表演"]
noinput_response = ["你不说话，我不说话，看谁先憋不住吧",
                    "此处静无声, 风儿停云儿憩",
                    "说吧，是不是手抖了[滑稽]",
                    "最怕空气突然安静"]
switch_response = ["你可以试着问我天气, 跟我闲聊瞎扯", "小胖正在学习中，目前只能查询天气、陪人闲聊吹水"]
weather_keywords = ["天气", "气温", "下雪", "下雨", "雾霾", "有雨", "雨天", "阴天", "晴天",
                    "今天", "今日", "明天", "后日", "后天"]

switch_rules = [".*?换.*?话题", ".*?话题.*?换"]
emotions = ["[奸笑]", "[捂脸]", "[发抖]", "[嘿哈]", "[机智]"]


if platform.system() != 'Darwin':
    nlp_path = "/home/fanzfeng/nlp_config"
else:
    nlp_path = "/Users/fanzfeng/Data/for_application"
file_stop_words = os.path.join(nlp_path, "stop_words.txt")
with open(file_stop_words, "r", encoding="utf-8") as fp:
    stops_list = [k.strip() for k in fp.readlines()][0:37] + ["'"]
query2rid_file = os.path.join(nlp_path, "3w_bot.csv")

log_file = "./chat.log"
formatter = '[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] [%(message)s]'
logging.basicConfig(filename=log_file, level=logging.INFO, format=formatter)
# FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'
