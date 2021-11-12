import tensorflow as tf
import tensorflow.keras.backend as K

import model


class EditDistanceCalculator:
    def __init__(self, cer, wer, counter, total, **kwargs):
        self.cer_accumulator = cer
        self.wer_accumulator = wer
        self.counter = counter
        self.total = total

    def update_state(self, y_true, y_pred):
        input_shape = K.shape(y_pred)
        input_length = tf.ones(shape=input_shape[0]) * K.cast(input_shape[1], 'float32')

        decode, log = K.ctc_decode(y_pred, input_length, greedy=True)

        decode = K.ctc_label_dense_to_sparse(decode[0], K.cast(input_length, 'int32'))
        y_true_sparse = K.ctc_label_dense_to_sparse(y_true, K.cast(input_length, 'int32'))

        decode = tf.sparse.retain(decode, tf.not_equal(decode.values, -1))
        distance = tf.edit_distance(decode, K.cast(y_true_sparse, tf.int64), normalize=True)

        correct_words_amount = tf.reduce_sum(tf.cast(tf.not_equal(distance, 0), tf.float32))

        self.cer_accumulator.assign_add(tf.reduce_sum(distance))
        self.wer_accumulator.assign_add(correct_words_amount)
        self.counter.assign_add(tf.cast(len(y_true), tf.float32))

    def result(self):
        return self.counter

    def result_cer(self):
        return tf.math.divide_no_nan(self.cer_accumulator, self.counter)

    def result_wer(self):
        return tf.math.divide_no_nan(self.wer_accumulator, self.counter)

    def reset_states(self):
        self.cer_accumulator.assign(0.0)
        self.wer_accumulator.assign(0.0)
        self.counter.assign(0.0)


class CERMetric(tf.keras.metrics.Metric):
    """
    A custom Keras metric to compute the Character Error Rate
    """

    def __init__(self, calculator, name='CER', **kwargs):
        super(CERMetric, self).__init__(name=name, **kwargs)
        self.calculator = calculator

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.calculator.update_state(y_true, y_pred)

    def result(self):
        return self.calculator.result_cer()

    def reset_states(self):
        self.calculator.reset_states()


class WERMetric(tf.keras.metrics.Metric):
    """
    A custom Keras metric to compute the Word Error Rate
    """

    def __init__(self, calculator, name='WER', **kwargs):
        super(WERMetric, self).__init__(name=name, **kwargs)
        self.calculator = calculator

    def update_state(self, y_true, y_pred, sample_weight=None):
        self.calculator.update_state(y_true, y_pred)

    def result(self):
        return self.calculator.result_wer()

    def reset_states(self):
        self.calculator.reset_states()