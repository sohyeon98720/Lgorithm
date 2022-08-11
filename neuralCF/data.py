import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))

import pandas as pd
import os
import numpy as np
from .preprocessing import Preprocessing
from sklearn.preprocessing import LabelEncoder
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
import pickle


class DataLoader:
    def __init__(self, data_path='data/', csv_generate=False, train=True):
        if csv_generate:
            pc = Preprocessing(savepath=data_path)
            pc.data_to_vectors()  # 10분 이상 걸림
        self.datapath = data_path
        self.LE = []
        self.SC = []

        # context vector
        self.item_vector = pd.read_csv(os.path.join(os.path.abspath('.'),'neuralCF', self.datapath + 'item.csv'), encoding='utf-8')
        if train:
            self.user_vector = pd.read_csv(os.path.join(os.path.abspath('.'),'neuralCF', self.datapath + 'user.csv'), encoding='utf-8')
        else:
            self.user_vector = pd.read_csv(os.path.join(os.path.abspath('.'),'neuralCF', self.datapath + 'allusers.csv'), encoding='utf-8')

        item_context, user_context = self.label_encoding()

        self.item_vector['clac_hlv_nm'] = self.minmax_norm(self.item_vector.iloc[:, [2]])
        for i in range(4):
            self.user_vector.iloc[:, [i + 2]] = self.minmax_norm(self.user_vector.iloc[:, [i + 2]])

        if train:
            # user,item,target vector
            ratings_df = pd.read_csv(os.path.join(self.datapath + 'target.csv'), encoding='utf-8').iloc[:, 1:]
            ratings_df.columns = ['userId', 'mclsId', 'num']
            ratings_df['num'] = self.minmax_norm(ratings_df.iloc[:, [2]])

            # user vector, context
            self.users = ratings_df["userId"].unique()
            self.num_users = len(self.users)
            self.user_to_index = {user: idx for idx, user in enumerate(self.users)}
            self.user_context = {user: user_context[user_context['cust'] == user].iloc[0, 2:].to_list() for _, user
                                 in enumerate(self.users)}

            # item(mcls)vector, context
            self.mcls = ratings_df["mclsId"].unique()
            self.num_items = len(self.mcls)
            self.mcls_to_index = {mcls: idx for idx, mcls in enumerate(self.mcls)}
            self.mcls_context = {mcls: item_context[item_context['clac_mcls_nm'] == mcls]['clac_hlv_nm'].item() for
                                 _, mcls in enumerate(self.mcls)}
            with open('mcls_index.p', 'wb') as f:
                pickle.dump(self.mcls_to_index, f)

            # split train,test data
            self.train_df, self.test_df = train_test_split(ratings_df, test_size=0.3, random_state=0, shuffle=True)
        # self.test_df = self.test_df[self.test_df["userId"].isin(self.users) & self.test_df["mclsId"].isin(self.mcls)]

    def save_label_encoder(self, lb):
        self.LE.append(lb)

    def save_scaler(self, s):
        self.SC.append(s)

    def minmax_norm(self, v):
        scaler = MinMaxScaler()
        scaler.fit(v)
        v_scaled = scaler.transform(v)
        self.save_scaler(scaler)
        return v_scaled

    def label_encoding(self):
        iv = self.item_vector

        lb = LabelEncoder()
        iv_ = lb.fit_transform(self.item_vector['clac_hlv_nm'])
        iv['clac_hlv_nm'] = iv_
        self.save_label_encoder(lb)

        uv = self.user_vector
        uv.loc[uv['rct_no'] < 30, 'rct_no'] = 0
        uv.loc[(uv['rct_no'] >= 30) & (uv['rct_no'] < 88), 'rct_no'] = 1
        uv.loc[(uv['rct_no'] >= 88) & (uv['rct_no'] < 214), 'rct_no'] = 2
        uv.loc[uv['rct_no'] >= 214, 'rct_no'] = 3

        lb = LabelEncoder()
        uv['ma_fem_dv'] = lb.fit_transform(uv['ma_fem_dv'])
        self.save_label_encoder(lb)

        lb = LabelEncoder()
        uv['ages'] = lb.fit_transform(uv['ages'])
        self.save_label_encoder(lb)

        lb = LabelEncoder()
        uv['zon_hlv'] = lb.fit_transform(uv['zon_hlv'])
        self.save_label_encoder(lb)

        return iv, uv

    def flatten(self, arg):
        r = []
        for i in arg:
            r.extend(i) if isinstance(i, list) else r.append(i)
        return r

    def generate_train(self):
        x = {'user': self.train_df["userId"].map(self.user_to_index),
             'mcls': self.train_df["mclsId"].map(self.mcls_to_index)}
        x_ = {'user_context': self.train_df['userId'].map(self.user_context),
              'mcls_context': self.train_df['mclsId'].map(self.mcls_context)}

        x.update(x_)

        x_train = np.asarray(pd.DataFrame(x))
        x_train = np.array(list(map(self.flatten, x_train)))
        y_train = self.train_df["num"].astype(np.float32)
        return x_train, np.asarray(y_train)

    def generate_test(self):
        xx = {'user': self.test_df["userId"].map(self.user_to_index),
              'mcls': self.test_df["mclsId"].map(self.mcls_to_index)}
        xx_ = {'user_context': self.test_df['userId'].map(self.user_context),
               'mcls_context': self.test_df['mclsId'].map(self.mcls_context)}

        xx.update(xx_)

        x_test = np.asarray(pd.DataFrame(xx))
        x_test = np.array(list(map(self.flatten, x_test)))
        y_test = self.test_df["num"].astype(np.float32)
        return x_test, np.asarray(y_test)


if __name__ == '__main__':
    data_loader = DataLoader()
    x_train, y_train = data_loader.generate_train()
    x_test, y_test = data_loader.generate_test()
