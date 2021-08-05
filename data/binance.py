import requests
import pandas as pd

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
    for col in ['open', 'high','low','close', 'volume']:
        df[col] = df[col].astype(float)
    df.set_index('opentime')
    return df