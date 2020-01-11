# -*- coding: utf-8 -*-

import logging
import tensorflow as tf

setattr(tf.contrib.rnn.GRUCell, '__deepcopy__', lambda self, _: self)
setattr(tf.contrib.rnn.BasicLSTMCell, '__deepcopy__', lambda self, _: self)
setattr(tf.contrib.rnn.MultiRNNCell, '__deepcopy__', lambda self, _: self)


class Seq2Seq(object):
    def __init__(self, forward_only, batch_size, BUCKETS, NUM_LAYERS, HIDDEN_SIZE, DEC_VOCAB, ENC_VOCAB,
                 NUM_SAMPLES, LR, MAX_GRAD_NORM):
        """forward_only: if set, we do not construct the backward pass in the model.
        """
        print('Initialize new model...')
        self.fw_only = forward_only
        self.batch_size = batch_size
        self.BUCKETS = BUCKETS
        self.DEC_VOCAB = DEC_VOCAB
        self.NUM_SAMPLES = NUM_SAMPLES
        self.HIDDEN_SIZE = HIDDEN_SIZE
        self.NUM_LAYERS = NUM_LAYERS
        self.ENC_VOCAB = ENC_VOCAB
        self.LR = LR
        self.MAX_GRAD_NORM = MAX_GRAD_NORM

    def _create_placeholders(self):
        logging.info('Create placeholders...') # Feeds for inputs. It's a list of placeholders
        self.encoder_inputs = [tf.placeholder(tf.int32, shape=[None], name='encoder{}'.format(i))
                               for i in range(self.BUCKETS[-1][0])]
        self.decoder_inputs = [tf.placeholder(tf.int32, shape=[None], name='decoder{}'.format(i))
                               for i in range(self.BUCKETS[-1][1] + 1)]
        self.decoder_masks = [tf.placeholder(tf.float32, shape=[None], name='mask{}'.format(i))
                              for i in range(self.BUCKETS[-1][1] + 1)]
        # Our targets are decoder inputs shifted by one (to ignore <GO> symbol)
        self.targets = self.decoder_inputs[1:]

    def _inference(self):
        logging.info('Create inference...')
        # If we use sampled softmax, we need an output projection.
        # Sampled softmax only makes sense if we sample less than vocabulary size.
        if 0 < self.NUM_SAMPLES < self.DEC_VOCAB:
            w = tf.get_variable('proj_w', [self.HIDDEN_SIZE, self.DEC_VOCAB])
            b = tf.get_variable('proj_b', [self.DEC_VOCAB])
            self.output_projection = (w, b)

        def sampled_loss(logits, labels):
            labels = tf.reshape(labels, [-1, 1])
            return tf.nn.sampled_softmax_loss(weights=tf.transpose(w), biases=b,
                                              inputs=logits, labels=labels,
                                              num_sampled=self.NUM_SAMPLES,
                                              num_classes=self.DEC_VOCAB)
        self.softmax_loss_function = sampled_loss
        single_cell = tf.contrib.rnn.GRUCell(self.HIDDEN_SIZE)
        self.cell = tf.contrib.rnn.MultiRNNCell([single_cell for _ in range(self.NUM_LAYERS)])

    def _create_loss(self):
        logging.info('Creating loss...\n    (It might take a couple of minutes depending on how many buckets you have.)')

        def _seq2seq_f(encoder_inputs, decoder_inputs, do_decode):
            return tf.contrib.legacy_seq2seq.embedding_attention_seq2seq(
                encoder_inputs, decoder_inputs, self.cell,
                num_encoder_symbols=self.ENC_VOCAB, num_decoder_symbols=self.DEC_VOCAB,
                embedding_size=self.HIDDEN_SIZE, output_projection=self.output_projection,
                feed_previous=do_decode)

        if self.fw_only:
            self.outputs, self.losses = tf.contrib.legacy_seq2seq.model_with_buckets(
                self.encoder_inputs, self.decoder_inputs, self.targets, self.decoder_masks,
                self.BUCKETS, lambda x, y: _seq2seq_f(x, y, True),
                softmax_loss_function=self.softmax_loss_function)
            # If we use output projection, we need to project outputs for decoding.
            if self.output_projection:
                for bucket in range(len(self.BUCKETS)):
                    self.outputs[bucket] = [tf.matmul(output, self.output_projection[0]) + self.output_projection[1]
                                            for output in self.outputs[bucket]]
        else:
            self.outputs, self.losses = tf.contrib.legacy_seq2seq.model_with_buckets(
                self.encoder_inputs, self.decoder_inputs, self.targets, self.decoder_masks,
                self.BUCKETS, lambda x, y: _seq2seq_f(x, y, False),
                softmax_loss_function=self.softmax_loss_function)
        tf.summary.scalar('loss', self.losses)

    def _creat_optimizer(self):
        logging.info('Create optimizer...\n    (It might take a couple of minutes depending on how many buckets you have.)')
        self.global_step = tf.Variable(0, dtype=tf.int32, trainable=False, name='global_step')

        if not self.fw_only:
            self.optimizer = tf.train.GradientDescentOptimizer(self.LR)
            trainables = tf.trainable_variables()
            self.gradient_norms, self.train_ops = [], []
            for bucket in range(len(self.BUCKETS)):
                clipped_grads, norm = tf.clip_by_global_norm(tf.gradients(self.losses[bucket], trainables),
                                                             self.MAX_GRAD_NORM)
                self.gradient_norms.append(norm)
                self.train_ops.append(self.optimizer.apply_gradients(zip(clipped_grads, trainables),
                                                                     global_step=self.global_step))

    def _create_summary(self):
        pass

    def build_graph(self):
        self._create_placeholders()
        self._inference()
        self._create_loss()
        self._creat_optimizer()
        self._create_summary()
