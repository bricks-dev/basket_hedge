import requests
import pandas as pd
from datetime import datetime
from time import sleep
# use binance as data source

def get_symbols():
    r = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    if not r:
        print("data empty")
        return None
    d = r.json()['symbols']
    return [item['symbol'].replace("USDT","") for item in d if 'USDT' in item['symbol']]

def get_price(symbol, period):
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={period}"
    r = requests.get(url)
    if not r:
        print("data empty")
        return None
    d = r.json()
    df = pd.DataFrame(d, columns=['opentime','open','high','low',
                              'close','volume','closetime',
                              'vcoin','count','buyvolume','buycoin','ignore'])
    df['opentime'] = pd.to_datetime(df['opentime'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('opentime')
    return df

def get_all_price(symbols, period='4h'):  
    data = {}
    for s in symbols:
        data[s] = get_price(f'{s.upper()}USDT', period)
        print(f"get price for {s}")
        sleep(0.3)
    return data