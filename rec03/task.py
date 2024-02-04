import json
from datetime import datetime, timedelta
import requests
import pandas as pd
import ssl
ssl._create_default_https_context = ssl._create_unverified_context

class Task(object):
    def __init__(self):
        self.df = pd.read_csv('bank-data.csv')

    def t1(self):
        mean_income_by_sex = self.df.groupby('sex')['income'].mean()
        return mean_income_by_sex

    def t2(self):
        cross_tab_save_mortgage = pd.crosstab(self.df['save_act'], self.df['mortgage'], margins=True)
        return cross_tab_save_mortgage
        # return None

    def t3(self):
        cross_tab = pd.crosstab(self.df['save_act'], self.df['mortgage'], margins=True)
        mySum = cross_tab.sum().sum()/4
        # temp = cross_tab.apply(lambda r:r/mySum, axis=1)
        # return temp
        return cross_tab/mySum
        # return cross_tab.apply(lambda r: r / r.loc['All'])
        # count the number of the rows

if __name__ == "__main__":
    t = Task()
    print("----T1----" + "\n")
    print(str(t.t1()) + "\n")
    print("----T2----" + "\n")
    print(str(t.t2()) + "\n")
    print("----T3----" + "\n")
    print(str(t.t3()) + "\n")
