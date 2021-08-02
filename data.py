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

def get_all_price(coins, period='4h'):  
    # use binance as data source
    data = {}
    batch_symbols = list(chunks(coins, cpu_count()))
    print(f"get_all_prices create batch tasks: {batch_symbols}")
    p = Pool(cpu_count())
    result = p.starmap(task, zip(batch_symbols, repeat(period)))
    [data.update(r) for r in result]
    return data