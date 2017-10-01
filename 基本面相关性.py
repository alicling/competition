import pandas as pd
import numpy as np
from scipy.stats.stats import pearsonr
from scipy.stats.stats import spearmanr

## fetch stock list
stocks=get_index_stocks('000300.XSHG')
## fetch close prices of 沪深300
## 每20个工作日取一个值，取121次，即10年的数据
closeprice=history(count=121, unit='20d', field='close', security_list=stocks, df=True, skip_paused=False, fq='pre')
time=closeprice.index #fetch timeline
factors = ['B/M','EPS','PEG','ROE','ROA','GP/R','P/R','L/A','FAP','CMV']

#月初取出因子数值
def get_factors(fdate,factors):
    q = query(
        valuation.code,
        balance.total_owner_equities/valuation.market_cap/100000000,
        income.basic_eps,
        valuation.pe_ratio,
        income.net_profit/balance.total_owner_equities,
        income.net_profit/balance.total_assets,
        income.total_profit/income.operating_revenue,
        income.net_profit/income.operating_revenue,
        balance.total_liability/balance.total_assets,
        balance.fixed_assets/balance.total_assets,
        valuation.circulating_market_cap
        ).filter(
        valuation.code.in_(stocks),
        valuation.circulating_market_cap
    )
    fdf = get_fundamentals(q, date=fdate)
    #print fdf.head(10)
    fdf.index = fdf['code']
    fdf.columns = ['code'] + factors
    return fdf.iloc[:,-10:]

## dataframe of factors
factor={}
for i in range(1,len(time)):
    fdf=get_factors(time[i],factors)
    factor[i]=pd.DataFrame(fdf)

## Calculate Returns--create dataframe
ret={}
for i in range(1,121):
    ret[i]=log(closeprice.iloc[i]/closeprice.iloc[i-1])

## Join Data by Index 
newdf={}
for i in range(1,121):
    newdf[i]=pd.DataFrame.join(pd.Series.to_frame(ret[i]),factor[i]).dropna(axis=0)

## 相关性计算 pearson系数（线性）
cor={}
for i in range(1,11):
    df=[]
    for j in range(1,121):
        df.append(pearsonr(newdf[j].iloc[:,0],newdf[j].iloc[:,i])[0])
    cor[factors[i-1]]=mean(df)
cor

## 相关性检验 spearman系数 （非线性）
cor={}
for i in range(1,11):
    df=[]
    for j in range(1,121):
        df.append(spearmanr(newdf[j].iloc[:,0],newdf[j].iloc[:,i])[0])
    cor[factors[i-1]]=mean(df)
cor
