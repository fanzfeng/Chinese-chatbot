# -*- coding: utf-8 -*-

min_word_freq = 6
model2file = {"enc": "query", "dec": "doc"}
default_token = ['<pad>', '<unk>', '<s>', '<\s>']
PAD_ID, UNK_ID, START_ID, EOS_ID = range(4)

BUCKETS = [(19, 19), (28, 28), (33, 33), (40, 43), (50, 50)]

TESTSET_SIZE = 45000
NUM_LAYERS, HIDDEN_SIZE = 3, 256
BATCH_SIZE = 64
LR = 0.5
MAX_GRAD_NORM = 5.0
NUM_SAMPLES = 512
print_every_n, save_every_n = 50, 100
