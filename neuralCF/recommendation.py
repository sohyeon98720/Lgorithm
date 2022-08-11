import os
import sys
sys.path.insert(0, os.getcwd())
import pickle

import tensorflow.keras.models
import numpy as np
import pandas as pd
import tensorflow as tf

from .data import DataLoader


DATAPATH = os.path.join(os.path.abspath('.'),'neuralCF', 'data')
WEIGHTPATH = os.path.join(os.path.abspath('.'),'neuralCF', 'weights')

def mcls_index():
    with open(os.path.join(DATAPATH,'mcls_index.p'), 'rb') as f:
        return pickle.load(f)


def user_index():
    with open(os.path.join(DATAPATH,'allusers_index.p'), 'rb') as f:
        return pickle.load(f)


def convert(x):
    try:
        y = [x[:, 0], x[:, 1], x[:, 2], x[:, 3], x[:, 4], x[:, 5], x[:, 6]]
    except:
        y = [x[:, 0], x[:, 1], x[:, 2], x[:, 3], x[:, 4], x[:, 5]]
    return y


def convert_(x):
    return tf.convert_to_tensor([x])


class Recommendation:
    def __init__(self, weight_file = 'mlp_220807.h5'):
        self.d = DataLoader(train=False)
        self.mcls = self.d.item_vector['clac_mcls_nm'].unique()
        self.num_mcls = len(self.mcls)
        self.mcls_to_index = mcls_index()
        self.users = self.d.user_vector['cust'].unique()
        self.num_users = len(self.users)  # 29913
        self.user_to_index = user_index()
        self.idx = pd.DataFrame(sorted(self.mcls_to_index.items()))
        wp = os.path.join(WEIGHTPATH,weight_file)
        self.model = tf.keras.models.load_model(wp)

    def __generate_sample(self, uid_idx, context):
        df = pd.DataFrame(columns=['1', '2', '3', '4', '5', '6', '7'])
        df['2'] = self.idx.loc[:, 1]
        df['1'] = uid_idx
        df.iloc[:, 2:-1] = context
        df['7'] = self.d.item_vector['clac_hlv_nm']
        return df

    def _user_generate_data(self, uid):
        uid_idx = self.user_to_index[uid]
        user_context = self.d.user_vector.loc[(self.d.user_vector['cust'] == uid)].iloc[:, 2:].values.tolist()[0]
        self.user_recommendation_data = self.__generate_sample(uid_idx, user_context)
        return np.array(self.user_recommendation_data)

    def _recommendation(self, uid):
        x = self._user_generate_data(uid)
        self.pr = self.model.predict(convert(x))
        idx = self.idx.iloc[:,1].to_list()
        p_ = np.c_[self.pr, idx]
        df = pd.DataFrame(p_,columns = ['label','idx']).sort_values(by='label',ascending=False)
        return df

    def recommend_items_best3(self,uid):
        ranks = list(self._recommendation(uid).iloc[:3,1])
        lok = list(self.mcls_to_index.keys())
        rec_items = list((map(lambda x : lok[int(x)],ranks)))
        return rec_items


if __name__ == '__main__':
    recommend = Recommendation()
    uid = 'M569085747'
    # recommend.recommendation(uid)
    rec_items = recommend.recommend_items_best5(uid)
    print(rec_items)

    # def predict_one_mcls(self, uid, mclsidx):


        # self.model = MLP(args)
        # self.datapath = './data/'
        #
        # # context vector
        # self.item_vector = pd.read_csv(os.path.join(self.datapath + 'item.csv'), encoding='utf-8')
        # self.user_vector = pd.read_csv(os.path.join(self.datapath + 'user.csv'), encoding='utf-8')
        #
        # self.item_vector['clac_hlv_nm'] = self.minmax_norm(self.item_vector.iloc[:, [2]])
        # for i in range(4):
        #     self.user_vector.iloc[:, [i + 2]] = self.minmax_norm(self.user_vector.iloc[:, [i + 2]])
        #
        #     # user vector, context
        #     self.users = ratings_df["userId"].unique()
        #     self.num_users = len(self.users)
        #     self.user_to_index = {user: idx for idx, user in enumerate(self.users)}
        #     self.user_context = {user: user_context[user_context['cust'] == user].iloc[0, 2:].to_list() for _, user
        #                          in enumerate(self.users)}
        #
        #     # item(mcls)vector, context
        #     self.mcls = ratings_df["mclsId"].unique()
        #     self.num_items = len(self.mcls)
        #     self.mcls_to_index = {mcls: idx for idx, mcls in enumerate(self.mcls)}
        #     self.mcls_context = {mcls: item_context[item_context['clac_mcls_nm'] == mcls]['clac_hlv_nm'].item() for
        #                          _, mcls in enumerate(self.mcls)}
