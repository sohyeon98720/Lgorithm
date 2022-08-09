import pandas as pd
import argparse
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Dropout, Activation, Embedding
# import keras.optimizers
import tensorflow.keras.losses


class MLP:

    def __init__(self, args):
        self.num_users = args.num_users
        self.num_items = args.num_items
        self.num_contexts = args.num_contexts
        self.layers = list(map(int, args.layers))
        self.num_layers = len(self.layers)
        self.regs = list(map(float, args.regs))
        tf.random.set_seed(args.seed)

        # inputs / context 1 : rec_no, context 2 : ma_fem_dv, context 3 : ages, context 4 : zon_hlv, context 5 : hcls
        user_input = keras.layers.Input(shape=(1,), dtype='float64')
        item_input = keras.layers.Input(shape=(1,), dtype='float64')
        context_input1 = keras.layers.Input(shape=(1,), dtype='float64')
        context_input2 = keras.layers.Input(shape=(1,), dtype='float64')
        context_input3 = keras.layers.Input(shape=(1,), dtype='float64')
        context_input4 = keras.layers.Input(shape=(1,), dtype='float64')
        context_input5 = keras.layers.Input(shape=(1,), dtype='float64')

        # embeddings
        user_embedding = keras.layers.Embedding(self.num_users, int(self.layers[0] / 7),
                                                embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                                name="user_embedding")(user_input)
        item_embedding = keras.layers.Embedding(self.num_items, int(self.layers[0] / 7),
                                                embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                                name='item_embedding')(item_input)
        context_embedding1 = Embedding(self.num_contexts[0], int(self.layers[0] / 7),
                                       embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                       name='context_embedding1')(context_input1)
        context_embedding2 = Embedding(self.num_contexts[1], int(self.layers[0] / 7),
                                       embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                       name='context_embedding2')(context_input2)
        context_embedding3 = Embedding(self.num_contexts[2], int(self.layers[0] / 7),
                                       embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                       name='context_embedding3')(context_input3)
        context_embedding4 = Embedding(self.num_contexts[3], int(self.layers[0] / 7),
                                       embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                       name='context_embedding4')(context_input4)
        context_embedding5 = Embedding(self.num_contexts[4], int(self.layers[0] / 7),
                                       embeddings_regularizer=keras.regularizers.l2(self.regs[0]),
                                       name='context_embedding5')(context_input5)
        # latents
        user_latent = keras.layers.Flatten()(user_embedding)
        item_latent = keras.layers.Flatten()(item_embedding)
        context_latent1 = keras.layers.Flatten()(context_embedding1)
        context_latent2 = keras.layers.Flatten()(context_embedding2)
        context_latent3 = keras.layers.Flatten()(context_embedding3)
        context_latent4 = keras.layers.Flatten()(context_embedding4)
        context_latent5 = keras.layers.Flatten()(context_embedding5)

        # concat  : layer 0 , size : layer[0]
        vector = keras.layers.concatenate([user_latent, item_latent,
                                           context_latent1, context_latent2,
                                           context_latent3, context_latent4,
                                           context_latent5])

        # hidden layers : 1 ~ num_layer
        for index in range(self.num_layers):
            vector = keras.layers.Dense(self.layers[index], kernel_regularizer=keras.regularizers.l2(self.regs[index]),
                                       name=f'layer{index}')(vector)
            vector = Dropout(0.3)(vector)
            vector = BatchNormalization()(vector)

        output = Dense(1, activation='sigmoid', kernel_initializer='he_normal', name='op')(vector)

        self.model = keras.Model(inputs=[user_input, item_input, context_input1,
                                         context_input2, context_input3, context_input4, context_input5],
                                 outputs=[output])

    def get_model(self):
        model = self.model
        return model
