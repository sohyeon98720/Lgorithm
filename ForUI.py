lower_bound75 = np.percentile(list(tbl_pdde.groupby(['cust']).count()['rct_no']),75)
lower_bound50 = np.percentile(list(tbl_pdde.groupby(['cust']).count()['rct_no']),50)
lower_bound25 = np.percentile(list(tbl_pdde.groupby(['cust']).count()['rct_no']), 25)
list_category = ['유통사','숙박업종','엔터테인먼트','F&B','렌탈업종']

class ForUI():
    def __init__(self) -> None:
        pass

    def if_history(self, cust_id):
        self.pdde_tmp = tbl_pdde[tbl_pdde.cust == cust_id]
        if len(self.pdde_tmp) > 0:
            return True
        else:
            return False

    def personal_info(self, cust_id):
        self.tbl_tmp = tbl_demo[tbl_demo.cust == cust_id]
        if_history = self.if_history(cust_id)
        if len(self.tbl_tmp) != 0:  # 고객인 경우
            tbl_tmp = tbl_demo[tbl_demo.cust == cust_id]
            return [tbl_tmp.iloc[0]['ma_fem_dv'], tbl_tmp.iloc[0]['ages'], tbl_tmp.iloc[0]['zon_hlv'], if_history]
        else:
            return None  # 고객이 아닌 경우

    def por_chnl(self,cust_id):
        tmp = []
        total = len(tbl_pdde[tbl_pdde.cust == cust_id])
        tmp.append(['Online',len(tbl_pdde[(tbl_pdde.cust == cust_id) & (tbl_pdde.chnl_dv == 2)])/total])
        tmp.append(['Offline',len(tbl_pdde[(tbl_pdde.cust == cust_id) & (tbl_pdde.chnl_dv == 1)])/total])
        return tmp

    def _lower_bound_(self, my_history): # 구매 이력 상위 75%, 50%, 25% 구간으로 구분
        if my_history >= lower_bound75:
            return 1
        elif lower_bound75 > my_history >= lower_bound50:
            return 2
        elif lower_bound50 > my_history >= lower_bound25:
            return 3
        else:
            return 4

    def recommendation_model(self, cust_id):
        myhis = self.my_history(cust_id)
        apri = self.most_common(cust_id)
        ncf = self.ncf(cust_id)
        lowerbound = self._lower_bound_(myhis)
        if lowerbound == 1:
            recommended_items = random.sample(apri, 6) + random.sample(ncf, 3)
            return recommended_items
        elif lowerbound == 2:
            recommended_items = random.sample(apri, 5) + random.sample(ncf, 4)
            return recommended_items
        elif lowerbound == 3:
            recommended_items = random.sample(apri, 4) + random.sample(ncf, 5)
            return recommended_items
        elif lowerbound == 4:
            recommended_items = random.sample(apri, 3) + random.sample(ncf, 6)
            return recommended_items
        else:
            recommended_items = ncf
            return recommended_items

    def my_history(self,cust_id):
        return len(tbl_pdde[tbl_pdde.cust == cust_id])

    def ncf(self, cust_id):
        # NCF recommendation system
        rec = Recommendation()
        return rec.recommend_items_best9(cust_id)

    def most_common(self, cust_id):
        # 구매이력 기반 장바구니 알고리즘(소분류)
        cust_tmp = pd.merge(left=tbl_pdde[tbl_pdde.cust == cust_id], right=tbl_pd_clac, on='pd_c')
        list_pd = cust_tmp.groupby('rct_no')['pd_nm'].apply(list)
        dataset = list(list_pd)
        
        te = TransactionEncoder()
        te_ary = te.fit(dataset).transform(dataset)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df, min_support=0.01, use_colnames=True)
        frequent_itemsets.sort_values(by=['support'], axis=0, ascending=False, inplace=True)
        tmp = frequent_itemsets[:9]['itemsets'].values.tolist()
        return sum([list(x) for x in tmp], [])

    def for_no_history(self, cust_id, chnl_dv):
        df_1 = tbl_demo[['cust', 'ma_fem_dv', 'ages', 'zon_hlv']]
        df_2 = tbl_pdde[['cust', 'pd_c', 'buy_ct', 'chnl_dv']]
        df_4 = tbl_pd_clac

        df_1_2 = pd.merge(df_1, df_2)
        df_orig = pd.merge(df_1_2, df_4)

        input_cust_sex = list(tbl_demo[tbl_demo['cust'] == cust_id]['ma_fem_dv'])[0]
        input_cust_ages = list(tbl_demo[tbl_demo['cust'] == cust_id]['ages'])[0]
        input_cust_local = list(tbl_demo[tbl_demo['cust'] == cust_id]['zon_hlv'])[0]
        input_cust_channel = chnl_dv
        
        df_orig = df_orig.groupby(['ma_fem_dv', 'ages', 'zon_hlv', 'chnl_dv'])['pd_nm'].apply(', '.join).reset_index()
        condition = (df_orig.ma_fem_dv == input_cust_sex) & (df_orig.ages == input_cust_ages) & (
                df_orig.zon_hlv == input_cust_local) & (df_orig.chnl_dv == input_cust_channel)
        df_personalize = df_orig[condition]
        df_pd_nm_list = list(df_personalize['pd_nm'])[0]
        df_pd_nm_list = pd.DataFrame([df_pd_nm_list.split(',')]).T.value_counts()
        df_recommend = list(pd.DataFrame([df_pd_nm_list]).columns)[:5]

        return [np.array(df_recommend[i])[0].split(' ')[1] for i in range(5)]

