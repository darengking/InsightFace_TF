import tensorflow as tf
import math


def arcface_loss(embedding, labels, out_num, s=64., m=0.5):
    '''
    :param embedding: the input embedding vectors
    :param labels:  the input labels, the shape should be eg: (batch_size, 1)
    :param s: scalar value default is 64
    :param out_num: output class num
    :param m: the margin value, default is 0.5
    :return: the final cacualted output, this output is send into the tf.nn.softmax directly
    '''
    cos_m = math.cos(m)
    sin_m = math.sin(m)
    mm = sin_m * m * s
    threshold = math.cos(math.pi - m)
    with tf.variable_scope('arcface_loss'):
        # inputs and weights norm
        embedding_norm = tf.norm(embedding, axis=1, keep_dims=True)
        embedding = tf.div(embedding, embedding_norm, name='norm_embedding')
        weights = tf.get_variable(name='embedding_weights', shape=(embedding.get_shape().as_list()[-1], out_num),
                                  initializer=tf.truncated_normal_initializer(stddev=0.1), dtype=tf.float32)
        weights_norm = tf.norm(weights, axis=0, keep_dims=True)
        weights = tf.div(weights, weights_norm, name='norm_weights')
        # cos(theta+m)
        cos_t = tf.matmul(embedding, weights, name='cos_t')
        cos_t2 = tf.square(cos_t, name='cos_2')
        sin_t2 = tf.subtract(1., cos_t2, name='sin_2')
        sin_t = tf.sqrt(sin_t2, name='sin_t')
        cos_mt = s * tf.subtract(tf.multiply(cos_t, cos_m), tf.multiply(sin_t, sin_m), name='cos_mt')

        cond_v = cos_t - threshold
        cond = tf.cast(tf.nn.relu(cond_v, name='if_else'), dtype=tf.bool)

        keep_val = s*(cos_t - mm)
        cos_mt_temp = tf.where(cond, cos_mt, keep_val)

        mask = tf.one_hot(labels, depth=out_num, name='one_hot_mask')
        inv_mask = tf.subtract(1., mask, name='inverse_mask')

        s_cos_t = tf.multiply(s, cos_t, name='scalar_cos_t')

        output = tf.add(tf.multiply(s_cos_t, inv_mask), tf.multiply(cos_mt_temp, mask), name='arcface_loss_output')
    return output


def cosineface_losses(embedding, labels, out_num, s=30., m=0.4):
    '''
    :param embedding: the input embedding vectors
    :param labels:  the input labels, the shape should be eg: (batch_size, 1)
    :param s: scalar value, default is 30
    :param out_num: output class num
    :param m: the margin value, default is 0.4
    :return: the final cacualted output, this output is send into the tf.nn.softmax directly
    '''
    with tf.variable_scope('cosineface_loss'):
        # inputs and weights norm
        embedding_norm = tf.norm(embedding, axis=1, keep_dims=True)
        embedding = tf.div(embedding, embedding_norm, name='norm_embedding')
        weights = tf.get_variable(name='embedding_weights', shape=(embedding.get_shape().as_list()[-1], out_num),
                                  initializer=tf.truncated_normal_initializer(stddev=0.1), dtype=tf.float32)
        weights_norm = tf.norm(weights, axis=0, keep_dims=True)
        weights = tf.div(weights, weights_norm, name='norm_weights')
        # cos_theta - m
        cos_t = tf.matmul(embedding, weights, name='cos_t')
        cos_t_m = tf.subtract(cos_t, m, name='cos_t_m')

        mask = tf.one_hot(labels, depth=out_num, name='one_hot_mask')
        inv_mask = tf.subtract(1., mask, name='inverse_mask')

        output = tf.add(s * tf.multiply(cos_t, inv_mask), s * tf.multiply(cos_t_m, mask), name='cosineface_loss_output')
    return output