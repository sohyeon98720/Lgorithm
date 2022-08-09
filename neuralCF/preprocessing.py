import pandas as pd
from collections import Counter

class Preprocessing:
    def __init__(self,path = './LPOINT_BIG_COMP/',savepath = './data/'):
        self.datapath = path
        self.savepath = savepath
        self.demo = pd.DataFrame(pd.read_csv(self.datapath+'LPOINT_BIG_COMP_01_DEMO.csv')).sort_values('cust')
        self.pdde = pd.DataFrame(pd.read_csv(self.datapath+'LPOINT_BIG_COMP_02_PDDE.csv')).sort_values('cust') 
        self.pdcl = pd.DataFrame(pd.read_csv(self.datapath+'LPOINT_BIG_COMP_04_PD_CLAC.csv'))
        self.br = pd.DataFrame(pd.read_csv(self.datapath+'LPOINT_BIG_COMP_05_BR.csv'))
        
        self.classes1 = [] # clac_hlv_nm
        self.classes2 = [] # clac_mcls_nm

        self.user_vector = pd.DataFrame()
        self.item_vector = pd.DataFrame()
        self.target_vector = pd.DataFrame()

    def get_classes(self):
        clac_hlv_nm = pd.DataFrame(self.pdcl.groupby('clac_hlv_nm').count().iloc[:,0]) #대분류 60개
        clac_hlv_nm.head()
        self.classes1 = list(clac_hlv_nm.index) #60개의 대분류 class
        clac_mcls_nm = pd.DataFrame(self.pdcl.groupby('clac_mcls_nm').count().iloc[:,0]) #중분류 349개
        self.classes2 = list(clac_mcls_nm.index)

    def get_user_vector(self):
        cnt = pd.DataFrame(self.pdde.groupby('cust').count().iloc[:,0]).sort_values('rct_no',ascending=False)
        self.user_vector = pd.merge(cnt,self.demo, on='cust')

    def get_item_vector(self):
        self.item_vector = self.pdcl[['clac_mcls_nm','clac_hlv_nm']].drop_duplicates().sort_values('clac_mcls_nm')
    
    def generate_lable(self):
        pdlist = {}
        pdde_ = self.pdde.loc[:,['cust','pd_c']]
        pdde_ = pdde_.groupby('cust')['pd_c'].apply(', '.join).reset_index() #고객 별 구매한 물건 리스트
        for i, c in enumerate(self.user_vector.cust):
            product = list(pdde_[pdde_.cust == c]['pd_c'].item().split(', '))
            product_to_class2 = list(map(lambda x:self.pdcl[self.pdcl['pd_c']==x]['clac_mcls_nm'].item(),product))
            pdlist[c] = dict(Counter(product_to_class2))
            # print(i)
        return pdlist

    def generate_rating(self, pdlist):
        rating = []
        for k,v in pdlist.items():
            temp = list(map(lambda x, y:[k,x,y], v.keys(),v.values()))
            rating.extend(temp)
        rating_df = pd.DataFrame(rating)
        return rating_df

    def get_target_vector(self):
        self.target_vector = self.generate_rating(self.generate_lable())
    
    def save_user_vector(self):
        self.get_user_vector()
        self.user_vector.to_csv(self.savepath + 'user.csv')  
    
    def save_item_vector(self):
        self.get_item_vector()
        self.item_vector.to_csv(self.savepath + 'item.csv')

    def save_target_vector(self):
        self.get_target_vector()
        self.target_vector.to_csv(self.savepath + 'target.csv') 
    
    def data_to_vectors(self):
        self.save_item_vector()
        self.save_user_vector()
        self.save_target_vector()


