# %matplotlib_inline
import argparse

import pandas as pd

from data import DataLoader
from model import MLP
import tensorflow as tf
import tensorflow.keras as keras
from tensorflow.keras import optimizers
import matplotlib.pyplot as plt
from tensorflow.keras.layers import Input, Dense, BatchNormalization, Dropout, Activation, Embedding
# import tensorflow.keras.optimizers
import tensorflow.keras.losses


def convert(x):
    try:
        y = [x[:, 0], x[:, 1], x[:, 2], x[:, 3], x[:, 4], x[:, 5], x[:, 6]]
    except:
        y = [x[:, 0], x[:, 1], x[:, 2], x[:, 3], x[:, 4], x[:, 5]]
    return y


def convert_(x):
    return tf.convert_to_tensor([x])


################### Arguments ####################
def arguments():
    parser = argparse.ArgumentParser(description="MLP.")

    # recommendation args
    parser.add_argument('--epochs', default=1000)
    parser.add_argument('--batch', default=20000)
    parser.add_argument('--learningrate', default=1e-4)

    # model args
    parser.add_argument('--num_users', default=100000)  # 고객 10만명까지 임베딩
    parser.add_argument('--num_items', default=10000)  # 중분류 1000개까지 임베딩
    parser.add_argument('--num_contexts', default=[4, 2, 6, 16, 60])
    parser.add_argument('--layers', default=[224, 128, 64, 32, 16])
    parser.add_argument('--regs', default=[0.001 for _ in range(5)])
    parser.add_argument('--seed', default=7)
    parser.add_argument('--train', default=True)
    parser.add_argument('--out', default='./weights/mlp_220807.h5')

    return parser.parse_args()


class TrainTest:
    def __init__(self, args):
        tf.random.set_seed(args.seed)
        self.lr = args.learningrate
        self.batch_size = args.batch
        self.epochs = args.epochs
        self.train = args.train
        self.filename = args.out

        if self.train:
            self.dload = DataLoader()
            self.x_train, self.y_train = self.dload.generate_train()
            self.x_test, self.y_test = self.dload.generate_test()
            model = MLP(args)
            self.model = model.get_model()
        else:
            self.x_test, self.y_test = self.dload.generate_test()
            self.model = keras.models.load_model(self.filename)


    def prediction(self, pred_x): # predict one instance, pred_x : [user_index, item_index, demo(rct_no, ma_fem, ages, zon), hcls]
        x = list(map(convert_, pred_x))
        return self.model.predict(x)[0][0]

    def train_model(self):
        model_out = self.filename
        model_check_cb = keras.callbacks.ModelCheckpoint(model_out, save_best_only=True, monitor='loss')

        self.model.compile(optimizer=optimizers.Adam(learning_rate=self.lr),
                           loss=keras.losses.mse)

        self.history = self.model.fit(convert(self.x_train), self.y_train,
                                      epochs=self.epochs, batch_size=self.batch_size,
                                      callbacks=[model_check_cb])

        pd.DataFrame(self.history.history).plot(figsize=(8, 5))
        plt.savefig('train_result'+str(min(self.history.history['loss']))+'.png')

    def test_model(self, best_model=None):
        if best_model:
            eval_model = keras.models.load_model(best_model)
        else:
            eval_model = self.model
        loss = eval_model.evaluate(convert(self.x_test), self.y_test)
        print("loss : ", loss)

    def train_test(self):
        self.train_model()
        self.test_model()


if __name__ == "__main__":
    args = arguments()
    rec = TrainTest(args)
    rec.train_test()
