import numpy as np
import pandas as pd
from mlxtend.preprocessing import TransactionEncoder
from mlxtend.frequent_patterns import apriori

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
        ### TODO: [승건]구매이력이 없는 고객의 경우
        return True

    def personal_info(self,cust_id):
        if self.if_history(cust_id):
            tbl_tmp = tbl_demo[tbl_demo.cust == cust_id]
            return [tbl_tmp.iloc[0]['ma_fem_dv'],tbl_tmp.iloc[0]['ages'],tbl_tmp.iloc[0]['zon_hlv']]
        else:
            return False # 구매 이력이 없는 고객인 경우
    
    def por_count(self,cust_id):
        tmp = []
        tmp.append([list_category[0],len(tbl_pdde[tbl_pdde.cust==cust_id])]) # A
        for i in range(4):
            tmp.append([list_category[i+1],len(tbl_cop_u[(tbl_cop_u.cust==cust_id) & (tbl_cop_u['cop_c'].str.contains(str(i+66)))])])
        return tmp

    def por_price(self):
        pass

    def if_lower_bounde(self,cust_id):
        return True if len(tbl_pdde[tbl_pdde.cust==cust_id]) >= lower_bound else False
        # 상위 75프로면 True 아니면 False

    def most_common(self,cust_id):
        # 구매이력 기반 장바구니 알고리즘(대분류)
        cust_tmp = pd.merge(left=tbl_pdde[tbl_pdde.cust==cust_id], right=tbl_pd_clac, on='pd_c')
        list_pd = cust_tmp.groupby('rct_no')['clac_hlv_nm'].apply(list)
        dataset = list(list_pd)
        
        te = TransactionEncoder()
        te_ary = te.fit(dataset).transform(dataset)
        df = pd.DataFrame(te_ary, columns=te.columns_)

        frequent_itemsets = apriori(df,min_support=0.01,use_colnames=True)
        frequent_itemsets.sort_values(by=['support'],axis=0,ascending=False,inplace=True)
        return frequent_itemsets[:5]
        