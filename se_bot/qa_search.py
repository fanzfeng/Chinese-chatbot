# -*- coding: utf-8 -*-
# version=3.6.4
# @Date  : 2019/1/2
# @Author  : fanzfeng

import time
import jieba
from collections import Counter
import pandas as pd

import os, sys
botPath = "/".join(os.path.split(os.path.realpath(__file__))[0].split('/')[:-1])
print(botPath)
sys.path.append(botPath)

from bot_config import logging


class SearchEngine(object):
    def __init__(self, query2rid_file, rid2res_file, file_stop_dict, words_cut_func=None, stop_limit=60):
        self.query2rid = pd.read_csv(query2rid_file, encoding="utf-8", sep=",").set_index("question")["answer"].to_dict()
        if rid2res_file is not None:
            self.rid2res = pd.read_excel(rid2res_file, sheet_name="sale_E").set_index("Id")["Answer"].to_dict()
        with open(file_stop_dict, "r", encoding="utf-8") as fp:
            stops_list = [k.strip() for k in fp.readlines()]
        if stop_limit < 0 or stop_limit is None:
            self.stop_words = stops_list
        else:
            max_words_cnt = len(stops_list)
            self.stop_words = "你们 我们 你 我 的 吗 呢 啊".split() + stops_list[0:min(stop_limit, max_words_cnt)]
        self.key_dict = dict()
        self.ix2doc = dict()
        if words_cut_func is None:
            self.words_cut = jieba.cut
        else:
            self.words_cut = words_cut_func

    def text_process(self, sent, out_type="list", drop_stop=True):
        if drop_stop:
            cut_res = [k for k in self.words_cut(sent) if k not in self.stop_words]
        else:
            cut_res = [k for k in self.words_cut(sent)]
        if len(cut_res) > 0:
            if out_type == "list":
                return cut_res
            else:
                return " ".join(cut_res)
        else:
            logging.warning("text {} invalid".format(sent))
            return [] if out_type == "list" else ""
            # raise Exception("Not valid word in {}".format(sent))

    def build_index(self):
        t0 = time.time()
        logging.info("SearchEngine begin create index ...")
        ix = 0
        for doc in self.query2rid:
            self.ix2doc[ix] = doc
            words = self.text_process(doc)
            for k in words:
                if k not in self.key_dict:
                    self.key_dict[k] = [ix]
                elif ix not in self.key_dict[k]:
                    self.key_dict[k] += [ix]
            ix += 1
        logging.info("SearchEngine index finish with time {}s".format(time.time()-t0))

    def query_search(self, query_text, res_num=2):
        logging.debug("Query text: {}".format(query_text))
        t0 = time.time()
        res = []
        assert isinstance(query_text, (list, str))
        if isinstance(query_text, str):
            words = self.text_process(query_text)
        else:
            words = query_text
        query_len = len(words)
        query_set = set(words)
        if query_len > 0:
            doc_related = []
            # weights = [1/query_len]*query_len
            for w in words:
                doc_related += self.key_dict.get(w, [])
            res_len = len(doc_related)
            if res_len > 0:
                doc_freq = Counter(doc_related)
                doc_res = doc_freq.most_common()[0:min(res_num, res_len)]
                #print(doc_res)
                for d in doc_res:
                    doc_text = self.ix2doc[d[0]]
                    doc_set = set(self.text_process(doc_text))
                    res += [{"query_ix": d[0],
                             "query_text": doc_text,
                             #"score": len(doc_set & query_set)/len(doc_set | query_set),
                             "score": len(doc_set & query_set)/len(query_set),
                             "answer": self.query2rid[doc_text]}]
        logging.debug("Search finish with time {}s".format(time.time() - t0))
        logging.debug("Response result: {}".format(res))
        return res


if __name__ == "__main__":
    base_path = "/home/fanzfeng/nlp_config/"
    query2rid_file = base_path+"3w_bot.csv"
    se = SearchEngine(query2rid_file=query2rid_file, rid2res_file=None,
                      file_stop_dict=base_path+"stop_words.txt")
    se.build_index()
    se.query_search("我今天心情很糟")
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit"):
            print("再见")
            break
        print(se.query_search(user_input))
