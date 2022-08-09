import numpy as np
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori
from ncf.recommendation import Recommendation

tbl_demo = pd.read_csv('./LPOINT_BIG_COMP_01_DEMO.csv') # 고객정보
tbl_pdde = pd.read_csv('./LPOINT_BIG_COMP_02_PDDE.csv') # 상품 구매 정보: 유통사 상품 구매 내역
tbl_cop_u = pd.read_csv('./LPOINT_BIG_COMP_03_COP_U.csv') # 제휴사 이용 정보: 제휴사 서비스 이용 내역
tbl_pd_clac = pd.read_csv('./LPOINT_BIG_COMP_04_PD_CLAC.csv') # 상품 분류 정보: 유통사 상품 카테고리 마스터
tbl_br = pd.read_csv('./LPOINT_BIG_COMP_05_BR.csv') # 점포 정보: 유통사/제휴사 점포 마스터
tbl_lpay = pd.read_csv('./LPOINT_BIG_COMP_06_LPAY.csv') # 엘페이 이용: 엘페이 결제 내역(pdde, cop_u와 중복 가능)
lower_bound = np.percentile(list(tbl_pdde.groupby(['cust']).count()['rct_no']),25)
list_category = ['유통사','숙박업종','엔터테인먼트','F&B','렌탈업종']

class ForUI():
    def __init__(self) -> None:
        # self.cust_id = cust_id
        pass
        
    def if_history(self,cust_id):
        self.pdde_tmp = tbl_pdde[tbl_pdde.cust == cust_id]
        if len(self.pdde_tmp) > 0:
            return True
        else:
            return False

    def personal_info(self,cust_id):
        self.tbl_tmp = tbl_demo[tbl_demo.cust == cust_id]
        if_history = self.if_history(cust_id)
        if len(self.tbl_tmp) != 0: # 고객인 경우
            tbl_tmp = tbl_demo[tbl_demo.cust == cust_id]
            return [tbl_tmp.iloc[0]['ma_fem_dv'],tbl_tmp.iloc[0]['ages'],tbl_tmp.iloc[0]['zon_hlv'],if_history]
        else:
            return None # 고객이 아닌 경우
    
    def por_count(self,cust_id):
        tmp = []
        tmp.append([list_category[0],len(tbl_pdde[tbl_pdde.cust==cust_id])]) # A
        for i in range(4):
            tmp.append([list_category[i+1],len(tbl_cop_u[(tbl_cop_u.cust==cust_id) & (tbl_cop_u['cop_c'].str.contains(str(i+66)))])])
        return tmp

    def por_price(self):
        pass

    def if_lower_bound(self,cust_id):
        return True if len(tbl_pdde[tbl_pdde.cust==cust_id]) >= lower_bound else False
        # 상위 75프로면 True 아니면 False

    def ncf(self,cust_id):
        # NCF recommendation system
        rec = Recommendation()
        return rec.recommend_items_best5(cust_id)

    def most_common(self,cust_id):
        # 구매이력 기반 장바구니 알고리즘(소분류)
        cust_tmp = pd.merge(left=tbl_pdde[tbl_pdde.cust==cust_id], right=tbl_pd_clac, on='pd_c')
        list_pd = cust_tmp.groupby('rct_no')['pd_nm'].apply(list)
        dataset = list(list_pd)
        
        te = TransactionEncoder()
        te_ary = te.fit(dataset).transform(dataset)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df,min_support=0.01,use_colnames=True)
        frequent_itemsets.sort_values(by=['support'],axis=0,ascending=False,inplace=True)
        tmp = frequent_itemsets[:5]['itemsets'].values.tolist()
        return sum([list(x) for x in tmp],[])
        
    def for_no_history(self,cust_id):
        df_1 = tbl_demo[['cust','ma_fem_dv','ages', 'zon_hlv']]
        df_2 = tbl_pdde[['cust', 'pd_c', 'buy_ct', 'chnl_dv']]
        df_4 = tbl_pd_clac

        df_1_2 = pd.merge(df_1, df_2)
        df_orig = pd.merge(df_1_2, df_4)

        input_cust_sex = list(tbl_demo[tbl_demo['cust'] == cust_id]['ma_fem_dv'])[0]
        input_cust_ages = list(tbl_demo[tbl_demo['cust'] ==cust_id]['ages'])[0]
        input_cust_local = list(tbl_demo[tbl_demo['cust'] == cust_id]['zon_hlv'])[0]

        df_orig = df_orig.groupby(['ma_fem_dv', 'ages', 'zon_hlv'])['pd_nm'].apply(', '.join).reset_index()

        condition = (df_orig.ma_fem_dv == input_cust_sex) & (df_orig.ages == input_cust_ages) & (
                    df_orig.zon_hlv == input_cust_local)

        df_personalize = df_orig[condition]

        df_pd_nm_list = list(df_personalize['pd_nm'])[0]

        df_pd_nm_list = pd.DataFrame([df_pd_nm_list.split(',')]).T.value_counts()

        df_recommend = list(pd.DataFrame([df_pd_nm_list]).columns)[:5]

        return [np.array(df_recommend[i])[0].split(' ')[1] for i in range(5)]