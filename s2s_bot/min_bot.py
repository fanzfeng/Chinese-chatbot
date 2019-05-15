# -*- coding: utf-8 -*-

import os
import time
import jieba
import numpy as np
import tensorflow as tf

import sys, codecs
sys.path.insert(0, "../")
try:
    sys.stdout = codecs.getwriter("utf-8")(sys.stdout.detach())
except:
    pass
from bot_config import logging
from s2s_bot.model import Seq2Seq
from s2s_bot.config import *
from utils_fanzfeng.tf_utils import load_vocab, seq2seq_get_batch


def check_restore_parameters(sess, saver, model_path):
    if not os.path.exists(model_path):
        print("Path of input not exist!!!")
        return None
    try:
        model_file = tf.train.latest_checkpoint(model_path)
    except:
        ix_files = sorted([f for f in os.listdir(model_path) if ".index" in f])
        if len(ix_files) <= 0:
            print("Path of input is null!!!")
            return None
        model_file = os.path.join(model_path, ix_files[-1].split(".")[0]+".ckpt")
    # ckpt = tf.train.get_checkpoint_state(model_path)
    # if ckpt and ckpt.model_checkpoint_path:
    print("Loading parameters for the model")
    saver.restore(sess, model_file)


def run_step(sess, model, encoder_inputs, decoder_inputs, decoder_masks, bucket_id, forward_only):
    encoder_size, decoder_size = BUCKETS[bucket_id]
    assert len(encoder_inputs) == encoder_size and len(decoder_inputs) == decoder_size and \
           len(decoder_masks) == decoder_size
    input_feed = {}
    for step in range(encoder_size):
        input_feed[model.encoder_inputs[step].name] = encoder_inputs[step]
    for step in range(decoder_size):
        input_feed[model.decoder_inputs[step].name] = decoder_inputs[step]
        input_feed[model.decoder_masks[step].name] = decoder_masks[step]

    last_target = model.decoder_inputs[decoder_size].name
    input_feed[last_target] = np.zeros([model.batch_size], dtype=np.int32)

    if not forward_only:
        output_feed = [model.train_ops[bucket_id], model.gradient_norms[bucket_id], model.losses[bucket_id]]
    else:
        output_feed = [model.losses[bucket_id]]
        for step in range(decoder_size):  # output logits.
            output_feed.append(model.outputs[bucket_id][step])
    outputs = sess.run(output_feed, input_feed)
    if not forward_only:
        return outputs[1], outputs[2], None
    else:
        return None, outputs[0], outputs[1:]


class ChatBot(object):
    def __init__(self, data_path, model_path, words_cut_func=None):
        tf.reset_default_graph()
        self.model = Seq2Seq(forward_only=True, batch_size=1, BUCKETS=BUCKETS, DEC_VOCAB=68067, ENC_VOCAB=64647,
                             NUM_SAMPLES=NUM_SAMPLES, HIDDEN_SIZE=HIDDEN_SIZE, NUM_LAYERS=NUM_LAYERS, LR=LR,
                             MAX_GRAD_NORM=MAX_GRAD_NORM)
        self.model.build_graph()
        saver = tf.train.Saver()
        self.sess = tf.Session()
        self.sess.run(tf.global_variables_initializer())
        check_restore_parameters(self.sess, saver, model_path=model_path)
        _, self.enc_vocab = load_vocab(os.path.join(data_path, 'vocab.enc'))
        self.dec_vocab_list, _ = load_vocab(os.path.join(data_path, 'vocab.dec'))
        if words_cut_func is None:
            self.words_cut = jieba.cut
        else:
            self.words_cut = words_cut_func
        logging.info("Chat model load done")

    def construct_response(self, output_logits):
        outputs = [int(np.argmax(logit, axis=1)) for logit in output_logits]
        if EOS_ID in outputs:
            outputs = outputs[:outputs.index(EOS_ID)]
        return "".join([tf.compat.as_str(self.dec_vocab_list[output]) for output in outputs])

    def s2s_bot(self, user_input, method="cn"):
        if method == "en":
            words_list = user_input.strip().split()
        elif method == "cn":
            words_list = self.words_cut(user_input.strip())
        token_ids = [self.enc_vocab.get(token, self.enc_vocab['<unk>']) for token in words_list]
        token_cnt = len(token_ids)
        token_ids = token_ids[0:min(BUCKETS[-1][0], token_cnt)]
        bucket_id = min([b for b in range(len(BUCKETS)) if BUCKETS[b][0] >= len(token_ids)])
        token_cnt = len(token_ids)
        token_ids += [self.enc_vocab['<unk>']]*(BUCKETS[bucket_id][0]-token_cnt)
        # print("input len: ", len(token_ids))
        dec_ids = [self.enc_vocab['<unk>']]*BUCKETS[bucket_id][-1]
        encoder_inputs, decoder_inputs, decoder_masks = seq2seq_get_batch(data_bucket=[(token_ids, dec_ids)],
                                                                          batch_size=1,
                                                                          bucket_config=BUCKETS[bucket_id],
                                                                          sys_token=default_token)
        _, _, output_logits = run_step(self.sess, self.model, encoder_inputs, decoder_inputs, decoder_masks,
                                       bucket_id, True)
        response = self.construct_response(output_logits)
        return response


if __name__ == "__main__":
    t0 = time.time()
    t1 = time.time()
    print("Load model use time totally {}min".format((t1 - t0) / 60))
    bot = ChatBot(data_path="/home/fanzfeng/backup/processed",
                  model_path="/home/fanzfeng/backup/s2s_lr0.5_ft256")
    while True:
        user_input = input("> ").strip().replace(" ", "")
        if user_input in ("bye", "quit"):
            print("再见")
            break
        print(bot.s2s_bot(user_input))
