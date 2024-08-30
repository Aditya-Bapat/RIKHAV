import requests
import pandas as pd
from datetime import datetime, timedelta 
import datetime as dt 
import pandas as pd
from datetime import datetime
import os
import schedule
import time

def cryptocompare_hour_download(coins,api_key):
    base_url = "https://min-api.cryptocompare.com/data/v2/histoday"
    currency = "USD"
    limit = 2000
    for coin in coins:
        
        #Downloading hourly data for each coin
        print(coin)
    
        if os.path.exists("COIN_DATA/"+coin+"_daily.csv"):
            df1 = pd.read_csv("COIN_DATA/"+coin+"_daily.csv")
            df1["DT"] = pd.to_datetime(df1["DT"])
            last_time_in_file = df1["DT"].max()
        else:
            last_time_in_file = datetime.datetime(2014, 1, 1)
            df1 = pd.DataFrame()

        to_ts = int(datetime.datetime.now().timestamp())
        all_data = []

        if last_time_in_file < datetime.datetime.now():
            while True:
                url = f"{base_url}?fsym={coin}&tsym={currency}&limit={limit}&toTs={to_ts}&api_key={api_key}"
                response = requests.get(url)
                data = response.json()['Data']['Data']

                if not data:
                    break

                for entry in data:
                    entry['time'] = datetime.datetime.utcfromtimestamp(entry['time'])

                all_data.extend(data)
                to_ts = data[0]['time'].timestamp()

                if data[0]['time'] <= last_time_in_file:
                    break

            new_df = pd.DataFrame(all_data)
            new_df["DT"]=pd.to_datetime(new_df["time"],unit='s')
            new_df.set_index("DT",inplace=True)
            
            new_df.drop(['conversionType','conversionSymbol'],axis=1,inplace=True)   
            
            new_df.sort_index(inplace=True)
            new_df.rename(columns={'close':'Close','high':'High','low':'Low','open':'Open','volumeto':'Volume'},inplace=True)
            new_df.index = pd.to_datetime(new_df.index, format='%Y-%m-%d %H:%M:%S')
            
            updated_df = pd.concat([df1, new_df]).drop_duplicates(subset='time').reset_index(drop=True)
            updated_df.to_csv("COIN_DATA/"+coin+"_daily.csv", index=False)
            print("Data has been updated and saved to "+"COIN_DATA/"+coin+"_daily.csv")
        else:
            print("No update needed, data in "+"COIN_DATA/"+coin+"_hour.csv"+" is up-to-date.")