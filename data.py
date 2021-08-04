from time import sleep
from multiprocessing import Pool, cpu_count
from itertools import repeat
from binance import get_price

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

def filter_data(data, coins):
    start_dates = [data[coin].iloc[0].opentime for coin in coins]
    min_start =  max(start_dates)
    new_data = {}
    for coin in coins:
        df = data[coin]
        if min_start > df.iloc[0].opentime:
            print(f"cut data for {coin}: {df.iloc[0].opentime} ~ {min_start}")
            new_data[coin] = df[df['opentime'] >= min_start]
            new_data[coin].reset_index(inplace=True, drop=True)
        else:
            new_data[coin] = data[coin]
    return new_data

def get_valid_size(data):
    max_size = 0
    for df in data.values():
        if df.shape[0] > max_size:
            max_size = df.shape[0]
    return max_size

def get_valid_coins(data, coins, valid_size=None):
    if valid_size is None:
        valid_size = get_valid_size(data)
    valid_coins = [s for s in coins if data[s] is not None and data[s].shape[0]>=valid_size]
    invalid_coins = set(coins) - set(valid_coins)
    if invalid_coins:
        print(f"invalid_coins: {invalid_coins}, data size not valid")
    return valid_coins



def get_all_price(coins, period='4h', match=True):  
    # match: 是否对齐所有币种的数据。 如果选择不对齐，则可能会丢弃某些数据较少的币种。
    # use binance as data source
    data = {}
    process_num = min(cpu_count(), len(coins))
    batch_symbols = list(chunks(coins, process_num))
    print(f"get_all_prices create batch tasks: {batch_symbols}")
    p = Pool(cpu_count())
    result = p.starmap(task, zip(batch_symbols, repeat(period)))
    [data.update(r) for r in result]
    if match: 
        new_data = filter_data(data, coins)
        return coins, new_data
    else:
        valid_coins = get_valid_coins(data, coins)
        return valid_coins, data