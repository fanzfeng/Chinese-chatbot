# -*- coding: utf-8 -*-
# version=3.6.4
# @Author  : fanzfeng

import os
import re
import jieba
import jieba.posseg as pseg
import platform


class ZhNlp(object):
    def __init__(self, config_lib="ltp", config_dict=None, config_stop=None, config_dir=None, seg_out_list=False):
        self.input_type = str
        self.config_dir = config_dir
        if config_dir is None:
            self.config_dir = 'E:/Data/' if 'windows' in platform.architecture()[1].lower() else '/users/fanzfeng/Data/'

        self.stop_config = False
        if config_stop is not None and isinstance(config_stop, str) and os.path.exists(config_stop):
            self.stop_config = True
            with open(config_stop, "r", encoding="utf-8") as fp:
                self.stop_words = [k.strip() for k in fp.readlines() if len(k.strip()) > 0]
        elif isinstance(config_stop, (list, tuple, set)) and len(config_stop) > 0:
            self.stop_config = True
            self.stop_words = config_stop

        self.all_cut = False
        self.seg_out_list = seg_out_list

        self.config_lib = config_lib
        if config_lib == "jieba":
            self.jieba_ner = "nr ns nt m".split()
            if config_dict is not None and isinstance(config_dict, str) and os.path.exists(config_dict):
                jieba.load_userdict(config_dict)
            self.seg = jieba.cut
            self.pos_seg = pseg.cut
        elif config_lib == "ltp":
            import pyltp
            self.segmentor = pyltp.Segmentor()
            if config_dict is not None and isinstance(config_dict, str) and os.path.exists(config_dict):
                self.segmentor.load_with_lexicon(os.path.join(self.config_dir, "ltp_data_v3.4.0/cws.model"), config_dict)
            else:
                self.segmentor.load(os.path.join(self.config_dir, "ltp_data_v3.4.0/cws.model"))
            self.seg = self.segmentor.segment
            self.postagger = pyltp.Postagger()
            self.text_splitter = pyltp.SentenceSplitter.split
            self.postagger.load(os.path.join(self.config_dir, "ltp_data_v3.4.0/pos.model"))
            self.recognizer = pyltp.NamedEntityRecognizer()
            self.recognizer.load(self.config_dir + "ltp_data_v3.4.0/ner.model")

    def split_sentence(self, doc, delimiters=list("。？！")):
        if self.config_lib == "ltp":
            sents = self.text_splitter(doc)
            return list(sents)
        else:
            return re.split("|".join(delimiters), doc)

    def ltp_close(self):
        if self.config_lib == "ltp":
            self.segmentor.release()
            self.postagger.release()
            self.recognizer.release()

    def zh_seg(self, text_input, drop_stop=True, all_cut=False, output_postags=False, out_list=False):
        text_seq = None
        if isinstance(text_input, str):
            text_seq = [text_input]
        elif isinstance(text_input, (list, tuple)):
            text_seq = text_input
        elif isinstance(text_input, (int, float)):
            return [str(text_input)] if self.seg_out_list else str(text_input)
        if text_seq:
            grams_series = []
            for x in text_seq:
                series_words = (self.seg(x, cut_all=self.all_cut) if self.config_lib == "jieba" else self.seg(x))
                if self.stop_config:
                    grams_series += [[w for w in series_words if w not in self.stop_words]]
                else:
                    grams_series += [list(series_words)]
            if not self.seg_out_list:
                grams_series = [" ".join(s) for s in grams_series]
            return grams_series[0] if isinstance(text_input, str) else grams_series

    def zh_pos(self, text_input):
        if isinstance(text_input, str):
            text_seq = [text_input]
        elif isinstance(text_input, (list, tuple)):
            text_seq = text_input
        if text_seq:
            grams_series = []
            for s in text_seq:
                if self.config_lib == "ltp":
                    word_list = list(self.seg(s))
                    postags = self.postagger.postag(word_list)
                    ptag_list = list(postags)
                    if len(word_list) == len(ptag_list):
                        grams_series += [(word_list, ptag_list)]
                else:
                    seg_res = [(w, p) for w, p in self.pos_seg(s)]
                    grams_series += [([k[0] for k in seg_res], [k[1] for k in seg_res])]
            out_put = []
            if self.stop_config:
                for wlist, plist in grams_series:
                    w_list, p_list = [], []
                    for i in range(len(wlist)):
                        if wlist[i] not in self.stop_words:
                            w_list += [wlist[i]]
                            p_list += [plist[i]]
                    out_put += [(w_list, p_list)]
            else:
                for wlist, plist in grams_series:
                    w_list, p_list = [], []
                    for i in range(len(wlist)):
                        w_list += [wlist[i]]
                        p_list += [plist[i]]
                    out_put += [(w_list, p_list)]
            return out_put[0] if isinstance(text_input, str) else out_put

    def zh_ner(self, text):
        if isinstance(text, str) and len(text) > 0:
            if self.config_lib == "ltp":
                seg_res, pos_res = self.zh_pos(text)
                netags = self.recognizer.recognize(seg_res, pos_res)
                ner_res = (seg_res, netags)
                return ner_res
            else:
                return self.zh_pos(text)

