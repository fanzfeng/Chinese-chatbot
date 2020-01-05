# -*- coding: utf-8 -*-
# version=3.6.4
# @Author  : fanzfeng

import numpy as np
import random


def batch_iter(x_input, y_input, batch_size, shuffle=False):
    data_len = len(x_input)
    if shuffle:
        indices = np.random.permutation(np.arange(data_len))
        x, y = x_input[indices], y_input[indices]
    else:
        x, y = x_input, y_input
    num_batch = int((x.shape[0] - 1) / batch_size) + 1
    for i in range(num_batch):
        start_id = i * batch_size
        end_id = min((i + 1) * batch_size, x.shape[0])
        yield x[start_id:end_id], y[start_id:end_id]


def seq2seq_get_batch(data_bucket, bucket_config, batch_size, sys_token):
    encoder_size, decoder_size = bucket_config
    encoder_inputs, decoder_inputs = [], []

    for _ in range(batch_size):
        encoder_input, decoder_input = random.choice(data_bucket) # 抽取样本
        encoder_inputs.append(list(reversed(encoder_input))) # 输入倒序
        decoder_inputs.append(decoder_input)

    # now we create batch-major vectors from the data selected above.
    batch_encoder_inputs = transpose_batch(encoder_inputs, encoder_size, batch_size)
    batch_decoder_inputs = transpose_batch(decoder_inputs, decoder_size, batch_size)

    # create decoder_masks to be 0 for decoders that are padding.
    batch_masks = []
    for length_id in range(decoder_size):
        batch_mask = np.ones(batch_size, dtype=np.float32)
        for batch_id in range(batch_size):
            # we set mask to 0 if the corresponding target is a PAD symbol.
            # the corresponding decoder is decoder_input shifted by 1 forward.
            if length_id < decoder_size - 1:
                target = decoder_inputs[batch_id][length_id + 1]
            if length_id == decoder_size - 1 or target == sys_token.index('<pad>'):
                batch_mask[batch_id] = 0.0
        batch_masks.append(batch_mask)
    return batch_encoder_inputs, batch_decoder_inputs, batch_masks


def build_vocab(text_input, min_count=None, sys_token=['<unk>']):
    if isinstance(text_input, str):
        texts = open(text_input, 'r', encoding='utf-8').readlines()
    else:
        texts = text_input
    vocab = {}
    for line in texts:
        for token in line.strip().split(" "):
            if not token in vocab:
                vocab[token] = 0
            vocab[token] += 1
    sorted_vocab = sorted(vocab, key=vocab.get, reverse=True)
    if min_count is None:
        vocab_out = []
        for w in sorted_vocab:
            if vocab[w] < min_count:
                break
            vocab_out += [w]
    else:
        vocab_out = [w for w in sorted_vocab]
    return sys_token+vocab_out


def load_vocab(vocab_path):
    with open(vocab_path, 'r', encoding="utf-8") as f:
        words = f.read().splitlines()
    return words, {words[i]: i for i in range(len(words))}


def token2id(text_input, vocab_dict, max_len=None, mode=None):
    """ Convert all the tokens in the data into their corresponding index in the vocabulary. """
    if isinstance(text_input, str):
        text_list = open(text_input, 'r', encoding='utf-8').readlines()
    elif isinstance(text_input, (list, tuple)):
        text_list = text_input
    ix_list = []
    # we only care about '<s>' and </s> in encoder
    for line in text_list:
        ids = ([vocab_dict['<s>']] if mode == 'dec' else [])
        line_ix = [vocab_dict.get(token, vocab_dict['<unk>']) for token in line.strip().split()]
        if mode is None and max_len is not None and max_len > len(line_ix):
            ids.extend(line_ix+[vocab_dict['<pad>']]*(max_len-len(line_ix)))
        else:
            ids.extend(line_ix)
        if mode == 'dec':
            ids.append(vocab_dict['<\s>'])
        ix_list += [ids]
    return ix_list


def bucket_data(enc_list, dec_list, bucket_config, pad_ix):
    if len(enc_list) != len(dec_list):
        return "len error"
    data_buckets = [[] for _ in bucket_config]
    for i in range(len(enc_list)):
        encode_ids = enc_list[i]
        decode_ids = dec_list[i]
        for bucket_id, (encode_max_size, decode_max_size) in enumerate(bucket_config):
            if len(encode_ids) <= encode_max_size and len(decode_ids) <= decode_max_size:
                encode_ids += [pad_ix]*(encode_max_size-len(encode_ids))
                decode_ids += [pad_ix] * (decode_max_size - len(decode_ids))
                data_buckets[bucket_id].append([encode_ids, decode_ids])
                break
    return data_buckets


def transpose_batch(inputs, size, batch_size):
    """ Create batch-major inputs. Batch inputs are just re-indexed inputs
    """
    batch_inputs = []
    for length_id in range(size):
        batch_inputs.append(np.array([inputs[batch_id][length_id] for batch_id in range(batch_size)], dtype=np.int32))
    return batch_inputs
        
        
def load_glove(word_index, max_features, EMBEDDING_FILE):
    def get_coefs(word, *arr):
        return word, np.asarray(arr, dtype='float32')
    # EMBEDDING_FILE is text file not binary
    embeddings_index = dict(get_coefs(*o.split(" ")) for o in open(EMBEDDING_FILE))

    all_embs = np.stack(embeddings_index.values())
    emb_mean, emb_std = all_embs.mean(), all_embs.std()
    embed_size = all_embs.shape[1]

    # word_index = tokenizer.word_index
    nb_words = min(max_features, len(word_index))
    embedding_matrix = np.random.normal(emb_mean, emb_std, (nb_words, embed_size))
    for word, i in word_index.items():
        if i >= max_features: continue
        embedding_vector = embeddings_index.get(word)
        if embedding_vector is not None: embedding_matrix[i] = embedding_vector

    return embedding_matrix
