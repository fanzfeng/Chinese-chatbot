# -*- coding: utf-8 -*-
# @Date  : 20/7/2019

import tensorflow as tf
try:
    from model import Model
except:
    from char_bot.model import Model

import os
from six.moves import cPickle
import pickle
import numpy as np


def weighted_pick(weights):
    t = np.cumsum(weights)
    s = np.sum(weights)
    return int(np.searchsorted(t, np.random.rand(1) * s))


class GenName(object):
    def __init__(self, save_dir="save", tool_file="data.pkl"):
        if not os.path.exists(save_dir):
            save_dir = os.path.join("char_bot", save_dir)
        tool_file = os.path.join(save_dir, tool_file)
        with open(os.path.join(save_dir, 'config.pkl'), 'rb') as f:
            self.saved_args = cPickle.load(f)
        with open(os.path.join(save_dir, 'chars_vocab.pkl'), 'rb') as f:
            self.chars, self.vocab = cPickle.load(f)
        self.graph = tf.get_default_graph()
        self.sess = tf.Session(graph=self.graph)
        self.model = Model(self.saved_args, training=False)
            # tf.global_variables_initializer().run()
        saver = tf.train.Saver(tf.global_variables())
        ckpt = tf.train.get_checkpoint_state(save_dir)
        if ckpt and ckpt.model_checkpoint_path:
            saver.restore(self.sess, ckpt.model_checkpoint_path)

        self.girl_keys = ["女", "水", "草"]
        self.girl_base = "美 丽 华 敏 梅 灵 月 琴 佳 玲 慧 静 雅 艳 红 洁 霞 雯 兰 紫 露 翠 韵 香 环 珏 璇 柔 伶 琳 怡 曼 纯".split()
        with open(tool_file, 'rb') as fd:
            self.data = pickle.load(fd)
        self.girl_chars = self.girl_base+self.chars_filter()

    def predict(self, vocab, char2id, prime, num=2, sampling_type=1):
        state = self.sess.run(self.model.cell.zero_state(1, tf.float32))
        for char in prime[:-1]:
            x = np.zeros((1, 1))
            x[0, 0] = char2id[char]
            feed = {self.model.input_data: x, self.model.initial_state: state}
            [state] = self.sess.run([self.model.final_state], feed)

        ret = prime
        char = prime[-1]
        for _ in range(num):
            x = np.zeros((1, 1))
            x[0, 0] = char2id[char]
            feed = {self.model.input_data: x, self.model.initial_state: state}
            [probs, state] = self.sess.run([self.model.probs, self.model.final_state], feed)
            p = probs[0]

            if sampling_type == 0:
                sample = np.argmax(p)
            elif sampling_type == 2:
                if char == ' ':
                    sample = weighted_pick(p)
                else:
                    sample = np.argmax(p)
            else:  # sampling_type == 1 default:
                sample = weighted_pick(p)

            pred = vocab[sample]
            ret += pred
            char = pred
        return ret

    def query(self, input_char, default=None):
        # 汉字拆解
        result = self.data.get(input_char, default)
        if result is None:
            return []
        return result[0]

    def chars_filter(self):
        # 过滤女性取名用字
        words_girl = []
        for w in self.chars:
            w_unit = self.query(w)
            if len(w_unit) > 0 and sum(k in w_unit for k in self.girl_keys) > 0:
                words_girl += [w]
        return words_girl

    def if_girl_char(self, full_name, start_ix=1):
        # 判断是否女性用名
        assert isinstance(full_name, str) and len(full_name) > 1
        for j in range(start_ix, len(full_name)):
            if full_name[j] in self.girl_chars:
                return True
        return False

    def gen_name(self, last_name, res_num=5):
        assert isinstance(last_name, str) and len(last_name) > 0
        with self.graph.as_default():
            res_names = []
            for _ in range(res_num):
                if np.random.random() >= 0.8:
                    gen_len = 1
                else:
                    gen_len = 2
                out_name = self.predict(self.chars, self.vocab, last_name, num=gen_len)
                if out_name not in res_names:
                    res_names.append(out_name)
        girl_names = [n for n in res_names if self.if_girl_char(n, len(last_name))]
        if len(girl_names) > 0:
            return "取名结果如下: {}. \n   其中 {} 可作为女生名字...".format("、".join(res_names), "、".join(girl_names))
        else:
            return "取名结果如下: {}.".format("、".join(res_names))


if __name__ == "__main__":
    gen = GenName()
    print(gen.gen_name("欧阳"))
