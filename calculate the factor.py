from math import factorial

import pandas as pd
import numpy as np
from datetime import datetime


"""              calculate the core factor           """
#1.Year-over-year revenue growth
#2.Revenue Month-over-Month Growth Rate

df_revenue_clean=pd.read_csv('.venv/SOX_top20_revenue_cleaned.csv', parse_dates=['Quarter'])


#Define function:calculate #1#2
def calculate_revenue_growth(df):
    #shift(1)
    df['Revenue_QoQ']=df['Total_Revenue']/df['Total_Revenue'].shift(1)-1
    #shift(4)
    df['Revenue_YoY']=df['Total_Revenue']/df['Total_Revenue'].shift(4)-1
    return df

#Use stock group to calculate growth
df_revenue_with_growth=df_revenue_clean.groupby('Symbol').apply(calculate_revenue_growth)
#Delete the Non
df_revenue_with_growth=df_revenue_with_growth.dropna(subset=['Revenue_QoQ','Revenue_YoY'])

#Retain the data of factor
df_revenue_with_growth.to_csv('SOX_top20_revenue_with_growth.csv',index=False)
print(f"core-factor calculated successfully:{df_revenue_with_growth.shape[0]}")


