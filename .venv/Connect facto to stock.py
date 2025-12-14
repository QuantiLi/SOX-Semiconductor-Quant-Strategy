import pandas as pd
import numpy as np



"""          Connect the factor with the stock data        """
df_close=pd.read_csv('SOX_top20_close_cleaned.csv',index_col=0)
df_revenue_with_growth = pd.read_csv('SOX_top20_revenue_with_growth.csv', parse_dates=['Quarter'])

df_latest_growth = df_revenue_with_growth.groupby('Symbol').last()[['Revenue_QoQ', 'Revenue_YoY']].reset_index()

print(f"Number of new factors：{len(df_latest_growth)}")
print("\nnew factors overview：")
print(df_latest_growth.head())

#connect to teh stock price
#deal with the index date
df_close.index=pd.to_datetime(df_close.index)
#get teh newest close price
latest_price_series=df_close.iloc[-1]
df_latest_price = latest_price_series.reset_index()
df_latest_price.columns = ['Symbol', 'Latest_Price']

df_final = pd.merge(df_latest_growth, df_latest_price, on='Symbol', how='inner')
df_final.to_csv('SOX_top20_final_factor.csv', index=False)
print(f"\n Success,number of data contain {len(df_final)} stocks")
print("\nFianl factor data columns' names：", df_final.columns.tolist())
print("\n Overview：")
print(df_final.head(10))