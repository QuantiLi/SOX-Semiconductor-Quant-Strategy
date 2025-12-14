import pandas as pd
import yfinance as yf
import warnings
warnings.filterwarnings('ignore')


df_stocks=pd.read_excel('SOX_top20.xlsx')

stock_list=df_stocks['SYMBOL'].astype(str).tolist()

print('stock_list= ',stock_list)



"""                  Grabe Data                   """
start_date="2020-12-12"
end_date="2025-12-12"



"""             Daily  data                  """
print('Start grabe daily data')

stock_price_dict={}

for stock in stock_list:
    try:
        print('Now grabing:',stock)
        ticker=yf.Ticker(stock)
        #Daily data
        price_data=ticker.history(start=start_date,end=end_date)
        #Retain core columns
        price_data=price_data[["Open","High","Low","Close","Volume"]]
        #store into the dictionary
        stock_price_dict[stock]=price_data
        #save single stock price as CSV
        price_data.to_csv(f"{stock}_price.csv")
    except Exception as e:
        print(f"Failed to grab",{stock},{str(e)})
        continue


close_data = pd.DataFrame()
for stock in stock_price_dict:
    close_data[stock] = stock_price_dict[stock]["Close"]


close_data.to_csv("SOX_top20_close.csv")






"""            Season Revenue data         """# Used for revenue accelerating factor
print('Start grabe season data')
revenue_list=[]
for stock in stock_price_dict:
    try:
        print(f"Now grabing:",{stock})
        ticker=yf.Ticker(stock)
        #Get seasonal income statemnet
        quarterly_income=ticker.quarterly_income_stmt
        #Refine total revenue
        revenue_col = [col for col in quarterly_income.index if "Revenue" in str(col)][0]
        #data format######
        revenue_data=pd.DataFrame({
            "Symbol":stock,
            "Quarter":quarterly_income.columns,
            "Total_Revenue":quarterly_income.loc[revenue_col].values
        })
        revenue_list.append(revenue_data)
    except Exception as e:
        print(f" {stock} revenue grabing failed：{str(e)}")
        continue

    if revenue_list:
        all_revenue=pd.concat(revenue_list,ignore_index=True)
        all_revenue.to_csv(f"SOX_top20_revenue.csv",index=False)
        print("grabing revenue data successfully, SOX_top20_revenue.csv produced")
    else:
        print("no effective revenue data")

    print("All data grabing successfully")





