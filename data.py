import requests
import pandas as pd
from datetime import datetime
from time import sleep
from multiprocessing import Pool, cpu_count
from itertools import repeat
# use binance as data source

def get_symbols():
    r = requests.get("https://api.binance.com/api/v3/exchangeInfo")
    if not r:
        print("data empty")
        return None
    d = r.json()['symbols']
    return [item['symbol'].replace("USDT","") for item in d if 'USDT' in item['symbol']]

def get_price(coin, period):
    print(f"get_price for {coin} ...")
    symbol = f'{coin.upper()}USDT'
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

def chunks(a, n):
    k, m = divmod(len(a), n)
    return (a[i*k+min(i, m):(i+1)*k+min(i+1, m)] for i in range(n))


def task(coins, period, wait=0.3):
    data = {}
    for i, coin in enumerate(coins):
        data[coin] = get_price(coin, period)
        if i < len(coins) - 1: # not last element
            sleep(wait)
    return data

def get_all_price(coins, period='4h'):  
    data = {}
    batch_symbols = list(chunks(coins, cpu_count()))
    print(f"get_all_prices create batch tasks: {batch_symbols}")
    p = Pool(cpu_count())
    result = p.starmap(task, zip(batch_symbols, repeat(period)))
    [data.update(r) for r in result]
    return data