// ftx 
def get_symbols():
    r = requests.get("https://ftx.com/api/markets")
    if not r:
        print("data empty")
        return None
    d = r.json()['result']
    return [item['name'] for item in d if 'PERP' in item['name']]
           
def get_price(symbol, period):
    seconds = {'1h': 3600,'2h':7200,'4h': 14400,'1d':86400}[period]
    url = f"https://ftx.com/api/markets/{symbol}/candles?resolution={seconds}"
    r = requests.get(url)
    if not r:
        print("data empty")
        return None
    d = r.json()['result']
    df = pd.DataFrame(d, columns=['close','high','low',
                              'open','startTime','time','volume'])
    df['opentime'] = pd.to_datetime(df['time'], unit='ms')
    df['close'] = df['close'].astype(float)
    df.set_index('opentime')
    return df
def get_all_price(symbols, period):  
    data = {}
    for s in symbols:
        data[s] = get_price(f'{s.upper()}',period)
        print(f"get price for {s}")
        sleep(0.3)
    return data
