import pandas as pd
import numpy as np
from datetime import datetime

""" Clean the stock close price data """

df_close=pd.read_csv('.venv/SOX_top20_close.csv', index_col=0)
#(1)transfer the index into the standerd format
df_close.index=pd.to_datetime(df_close.index)
#(2)deal with the missing value:Use previous data to replace
df_close=df_close.fillna(method='ffill').dropna(axis=1)
print("stock close price data cleared")
print("Number of stocks:",len(df_close.columns))

""" Clean the revenue data """
df_revenue=pd.read_csv('.venv/SOX_top20_revenue.csv')
#Filter the non-effect value
df_revenue=df_revenue[df_revenue['Total_Revenue']>0]
#Transfer the data to the standerd format
df_revenue['Quarter']=pd.to_datetime(df_revenue['Quarter'])
#Sort the data as stock and season
df_revenue=df_revenue.sort_values(by=['Symbol','Quarter']).reset_index(drop=True)
#Filter the insufficient data(<2 season)
df_revenue=df_revenue.groupby('Symbol').filter(lambda x:len(x)>=2)
print(f"\nRevenue data cleared:{df_revenue.shape[0]}row*{df_revenue.shape[1]}columns")
print("Number of effective stocks:",df_revenue['Symbol'].nunique())

#Save the after-clearance data
df_close.to_csv('SOX_top20_close_cleaned.csv')
df_revenue.to_csv('SOX_top20_revenue_cleaned.csv')


