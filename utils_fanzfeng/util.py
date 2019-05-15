#!/usr/bin/env python
# version='3.5.2'
# -*- coding: utf-8 -*-
# @Author  : fanzfeng
# for: common func
"""
常用函数集合：
pdf: 画出序列数据的累计分布图
concat_list: 合并list
diff_list：求list差集
update_dict: dict为key-[]结构，根据key-value更新dict
sub_list: 取定长的子序列
norm_list：根据一个list规范化另一个list，有交集取数，无交集取default，保证了索引一致
"""
import os
import time
import json
import hashlib
import platform
import numpy as np
import pandas as pd
from scipy.stats import f_oneway
import jieba
try:
    import pyltp
except:
    pass
from datetime import timedelta

config_dir = 'E:/Data/' if 'windows' in platform.architecture()[1].lower() else \
    '/users/fanzfeng/Data/'


# 单值数据处理,编码

def md_5(x):
    m2 = hashlib.md5()
    m2.update(x.encode())
    return m2.hexdigest()

def safe_str(obj):
    try: return str(obj)
    except UnicodeEncodeError:
        return obj.encode('ascii', 'ignore').decode('ascii')


# 数据读写

def readFirstCol(file, unique=True, signStr=" "):
    with open(file, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    alist = [k.strip().split(signStr)[0] for k in lines]
    return set(alist) if unique else alist

def read_file(filename):
    # 用于文本分类
    contents, labels = [], []
    with open(filename, "r", encoding='utf-8', errors='ignore') as f:
        for line in f:
            try:
                label, content = line.strip().split('\t')
                if content:
                    contents.append(content.split(" "))
                    labels.append(label)
            except:
                pass
    return contents, labels

def save_corpus(corpus_text, save_file):
    with open(save_file, "w", encoding="utf-8") as fp:
        for c in corpus_text:
            fp.write(c+"\n")

def save_json(data_series, save_file, complex_series=False):
    with open(save_file, "w", encoding="utf-8") as fp:
        if not complex_series:
            json.dump(data_series, fp, indent=4, ensure_ascii=False)
        else:
            for d in data_series:
                json.dump(d, fp, ensure_ascii=False)
                fp.write("\n")


# 常用函数

def sigmoid(x):
    return 1/(1+np.exp(-x))


# 程序过程

def get_time_dif(start_time):
    end_time = time.time()
    time_dif = end_time - start_time
    return timedelta(seconds=int(round(time_dif)))


# 基础序列数据处理

def dict_scan(adict, obs):
    i = 0
    for k in adict:
        if i < 10:
            print(k, "   ", adict[k])
            i += 1

def series_unique(series):
    new_series = []
    for s in series:
        if s not in new_series:
            new_series += [s]
    return new_series

def check_contain(series, x):
    cont = False
    for s in series:
        if x in s:
            cont = True
            break
    return cont

def concat_list(list1, list2):
    new_list = []
    for c in list1+list2:
        if c not in new_list:
            new_list += [c]
    return new_list

def diff_list(list1, list2, out_list=True):
    if out_list:
        return [k for k in list1 if k not in list2]
    else:
        try:
            set_dif = set(list1) - set(list2)
            return list(set_dif) if out_list else set_dif
        except Exception as e:
            print("Warning: ", e, "And output is list")
            return [k for k in list1 if k not in list2]

def update_dict(key_dict, akey, avalue, task_type="sum"):
    if task_type in ("sum", "count", "conclude"):
        adict = key_dict.copy()
        if akey in adict:
            if task_type == "sum":
                adict[akey] += avalue
            elif task_type == "count":
                adict[akey] += 1
            else:
                adict[akey] += [avalue]
        else:
            adict[akey] = (avalue if task_type == "sum" else 1 if task_type == "count" else [])
        return adict
    else:
        print("<{}>".format(task_type), "  param error!")

def sub_list(x, n_unit):
    if isinstance(x, list) and len(x) >= n_unit:
        if len(x) > n_unit:
            return [x[i:i+n_unit] for i in range(len(x)+1-n_unit)]
        else:
            return [x]

def norm_list(list_base, list1, default=0):
    vlist = []
    for c in list_base:
        if c in list1:
            vlist += [list1.count(c)/len(list1)]
        else:
            vlist += [default]
    return vlist

def to_tuple(x):
    if isinstance(x, pd.Series) and pd.core.common.is_datetime_or_timedelta_dtype(x):
        return tuple(x.diff().dropna().apply(lambda ts: ts.seconds))
    else:
        return tuple(x)

def list_sum(mix_seq, unique=False):
    res_list = []
    if isinstance(mix_seq, list):
        for mlist in mix_seq:
            res_list += mlist
    elif isinstance(mix_seq, dict):
        keys = [k for k in mix_seq]
        if isinstance(mix_seq[keys[0]], list):
            for k in keys:
                res_list += mix_seq[k]
        else:
            raise Exception("value in your dict not list")
    return res_list if not unique else set(res_list)


# 高级序列结构, dataframe, series, array

def pdf(value_set, normalize=True, n_split=100):
    import matplotlib.pyplot as plt
    values, base = np.histogram(value_set, bins=n_split)
    uo = np.cumsum(values)
    print("X:  ", base)
    print("Min: ", min(value_set), "Max: ", max(value_set))
    plt.plot(base[:-1], uo/len(value_set) if normalize else uo)
    plt.ylim(0, 1 if normalize else len(value_set))
    plt.show()

def group_select(dfs, group_col, sort_col, sort_asc=False, simple_rate=0.5, min_obs=3):
    new_df = dfs.sort_values(by=[group_col, sort_col], ascending=[True, sort_asc])
    simple_df_list = []
    n_series = dfs[group_col].value_counts()
    for g in set(dfs[group_col]):
        if simple_rate is None:
            num_obs = min(min_obs, n_series.ix[g])
            simple_df_list += [new_df[new_df[group_col] == g].iloc[0:num_obs]]
        else:
            num_obs = (min(min_obs, int(simple_rate*n_series.ix[g])) if min_obs < n_series.ix[g] else n_series.ix[g])
            simple_df_list += [new_df[new_df[group_col] == g].iloc[0:]]
    return pd.concat(simple_df_list, ignore_index=True)

def row_first(se):
    return se.iloc[0]


# 统计检验

def anova(dfs, col, col_group):
    alist = []
    for c in set(dfs[col_group]):
        alist += [dfs[dfs[col_group] == c][col]]
    return f_oneway(*alist)


# nlp基础函数

def cos_sim(vec1, vec2):
    # 存在计算精度的问题
    npvec1, npvec2 = np.array(vec1), np.array(vec2)
    cos = npvec1.dot(npvec2)/(np.sqrt((npvec1**2).sum()) * np.sqrt((npvec2**2).sum()))
    return cos if cos <= 1.0 else 1.0


def split_sentence(text_str):
    sents = pyltp.SentenceSplitter.split(text_str)
    return list(sents)


def n_gram(x, k, out_list=True):
    x_len = len(x)
    if x_len >= k:
        x_list = []
        for i in range(x_len-k+1):
            x_list += [x[i:i+k]]
    else:
        x_list = [""]
    return x_list if out_list else " ".join(x_list)


def word_cut(text_seq, drop_stop=True, config_stops=None, config_dict=None, config_lib="jieba", all_cut=False):
    if config_lib == "ltp":
        segmentor = pyltp.Segmentor()
        model_file = config_dir + "ltp_data_v3.4.0/cws.model"
        if config_dict is not None and isinstance(config_dict, str) and os.path.exists(config_dict):
            segmentor.load_with_lexicon(model_file, config_dict)
        else:
            segmentor.load(model_file)
        seg = segmentor.segment(dsf, )
    elif config_lib == "jieba":
        if config_dict is not None and isinstance(config_dict, str) and os.path.exists(config_dict):
            jieba.load_userdict(config_dict)
        seg = jieba.cut
    if config_stops is not None and isinstance(config_stops, str) and os.path.exists(config_stops):
        stops_file = config_stops
    else:
        stops_file = config_dir+"stop_words.txt"
    if drop_stop:
        with open(stops_file, "r", encoding="utf-8") as fp:
            stop_words = [k.strip() for k in fp.readlines()]
    grams_series = []
    for x in text_seq:
        series_words = (seg(x, cut_all=all_cut) if config_lib == "jieba" else seg(x))
        if drop_stop:
            grams_series += [" ".join([word for word in series_words if word not in stop_words])]
        else:
            grams_series += [" ".join(series_words)]
    if config_lib == "ltp":
        segmentor.release()
    return grams_series

def segment(list_sents, config_lib="jieba", drop_stop=True, flags_config=None, output_postags=False):
    if config_lib == "ltp":
        postagger = pyltp.Postagger()
        postagger.load(config_dir+"ltp_data_v3.4.0/pos.model")
        text_list = word_cut(list_sents, config_lib="ltp")
    else:
        text_list = list_sents.copy()
    result, out_put = [], []
    # seg_list = jieba.cut(lstr, cut_all=True) cut_all为True则是全模式，反则精确模式，默认False
    # HMM默认为True为新词发现模式
    if drop_stop:
        with open(config_dir+"stop_words.txt", "r", encoding="utf-8") as fp:
            stopwords = [line.strip() for line in fp.readlines()]
    else:
        stopwords = []
    for s in text_list:
        if config_lib == "ltp":
            word_list = s.split(" ")
            postags = postagger.postag(word_list)
            ptag_list = list(postags)
            if len(word_list) == len(ptag_list):
                result += [(word_list, ptag_list)]
        else:
            import jieba.posseg as pseg
            seg_res = [(w, p) for w, p  in pseg.cut(s)]
            result += [([k[0] for k in seg_res], [k[1] for k in seg_res])]
    if config_lib == "ltp":
        postagger.release()
    for wlist,plist in result:
        w_list, p_list = [], []
        if flags_config is None:
            for i in range(len(wlist)):
                if wlist[i] not in stopwords:
                    w_list += [wlist[i]]
                    p_list += [plist[i]]
        elif "delete" in flags_config:
            for i in range(len(wlist)):
                if wlist[i] not in stopwords and plist[i] not in flags_config["delete"]:
                    w_list += [wlist[i]]
                    p_list += [plist[i]]
        elif "retain" in flags_config:
            for i in range(len(wlist)):
                if wlist[i] not in stopwords and plist[i] in flags_config["retain"]:
                    w_list += [wlist[i]]
                    p_list += [plist[i]]
        else:
            w_list, p_list = wlist.copu(), plist.copy()
        out_put += [(w_list, p_list)]
    return out_put if output_postags else [" ".join(w) for w, p in out_put]

def ner(text_list, config_lib="ltp"):
    if config_lib == "ltp":
        recognizer = pyltp.NamedEntityRecognizer()
        recognizer.load(config_dir+"ltp_data_v3.4.0/ner.model")
        word_tag = segment(text_list, config_lib="ltp", output_postags=True)
        out_put = []
        for w,p in word_tag:
            netags = recognizer.recognize(w, p)
            out_put += [(w, p, list(netags))]
        recognizer.release()
        return out_put

def nlp_vector(corpus, method=["count", "tfidf"][0], smooth=False):
    '''
    vectorizer.get_feature_names()
    X.toarray()
    vectorizer.transform(['A new document.']).toarray()
    '''
    from sklearn.feature_extraction.text import CountVectorizer
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(corpus)
    if method == "tfidf":
        from sklearn.feature_extraction.text import TfidfTransformer
        transformer = TfidfTransformer(smooth_idf=smooth)
        tfidf = transformer.fit_transform(X)
        return tfidf.toarray()
    else:
        return X.toarray()


if __name__ == "__main__":
    # 暖奶洗碗机
    # 避谷方法
    # 糖猫价格
    # print(word_cut(["糖猫价格"], drop_stop=False, all_cut=True))
    # print(word_cut(["我爱北京天安门"], drop_stop=False, all_cut=True))
    # print(word_cut(["暖奶洗碗机"], drop_stop=False, config_lib="ltp"))
    print(segment(["我很喜欢塞北雪，风格不错"], config_lib="ltp", output_postags=True))
    kk = segment(["我去人民公园吃炸鸡，碰巧看到王二小,他说深圳市人民政府大楼很棒",
                  "要求中共19大直选总书记的前云南省委党校教师、中共党员子肃举起双手，投降"],
                 config_lib="jieba", output_postags=True,
                 flags_config={"retain": ['nr', 'n', 'ns', 'nt', 'ng', 'nx', 'nz']})
    # ['n', 'nh', 'ni', 'ns', 'nz'
    for k in kk:
        print("-"*40, "\n", k[0], "\n", k[1])
