# -*- coding: utf-8 -*-
# @Author  : fanzfeng

import os
import re
import logging

weixin_token = "" # 公众号号后台token
tuling_token = ""

default_response = ["你说的我没懂哦，正在拼命学习中",
                    "这个我就不懂了，你可以问下邻居小明",
                    "你待着不要动，我去买个句子",
                    "你这话我没法接[允悲]",
                    "嗯，然后呢",
                    "请继续你的表演"]
noinput_response = ["你不说话，我不说话，看谁先憋不住吧",
                    "此处静无声, 风儿停云儿憩",
                    "说吧，是不是手抖了[滑稽]",
                    "最怕空气突然安静"]
switch_response = ["你可以试着问我天气, 让我取名字、讲笑话，或者跟我闲聊瞎扯", "小胖正在学习中，目前只能查询天气、取名字、讲笑话、陪人闲聊吹水"]

gname_keywords = ["赐我姓名", "取名", "取个名"]
gname_rule = re.compile(".*姓([一-龥]+)")
gname_maxlen = 6
gname_reply = "请大声说出你想到的姓氏, 比如'姓王'"

weather_keywords = ["天气", "气温", "下雪", "下雨", "雾霾", "有雨", "雨天", "阴天", "晴天",
                    "今天", "今日", "明天", "后日", "后天"]

switch_rules = [".*?换.*?话题", ".*?话题.*?换"]
emotions = ["[奸笑]", "[捂脸]", "[发抖]", "[嘿哈]", "[机智]"]

botPath = os.path.split(os.path.realpath(__file__))[0]
nlp_path = os.path.join(botPath, "data")
file_stop_words = os.path.join(nlp_path, "stop_words.txt")
with open(file_stop_words, "r", encoding="utf-8") as fp:
    stops_list = [k.strip() for k in fp.readlines()][0:37] + ["'"]
query2rid_file = os.path.join(nlp_path, "3w_bot.csv")

MODAL_CN = '阿啊呃欸哇呀也耶哟欤呕噢呦嘢吧呗啵啦唻了嘞哩咧咯啰喽吗嘛嚜么麽哪呢呐否呵哈兮噻哉呸'
fmp_pat_not_modal = re.compile("|".join(list(MODAL_CN)))
fmt_pat_not_cn = re.compile('[^一-龥]')

log_file = os.path.join(botPath, "log/chat.log")
formatter = '[%(levelname)s] [%(asctime)s] [%(filename)s:%(lineno)d] [%(message)s]'
logging.basicConfig(filename=log_file, level=logging.DEBUG, format=formatter)
# FORMAT = '%(asctime)-15s %(levelname)s - %(message)s'·
