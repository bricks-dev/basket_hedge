import argparse
from datetime import timedelta
from backtest import backtest
from data import get_all_price
import pandas as pd
from util import get_valid_coins
from comb import find_best
from collections import deque, OrderedDict


def split_data(data, coins, freq='30D'):
    df = data[coins[0]]
    dates = pd.date_range(df.iloc[0].opentime, df.iloc[-1].opentime, freq=freq).to_pydatetime()
    splits = []
    for x, y in zip(dates, dates[1:]):
        split = {}
        for coin in coins:
            df = data[coin]
            split[coin] = df[(df['opentime'] >=x) & (df['opentime']<y)]
        splits.append(split)
    return splits

def split_data_rotate(data, coins, freq='30D', rotate_days=180):
    df = data[coins[0]]
    dates = pd.date_range(df.iloc[0].opentime, df.iloc[-1].opentime, freq=freq).to_pydatetime()
    splits = []
    for x, y in zip(dates, dates[1:]):
        split = {}
        for coin in coins:
            df = data[coin]
            split[coin] = df[(df['opentime'] >=x) & (df['opentime']< x+timedelta(days=rotate_days))]
        splits.append(split)
    return splits


def stage1(data, coins, rotate_days=180):
    print("split data ...")
    batches = split_data_rotate(data, coins, rotate_days=rotate_days)
    best_basket = OrderedDict()
    print("============ stage1: find best basket for each batch =====")
    for i, item in enumerate(batches):
        start = item[coins[0]].iloc[0].opentime
        end = item[coins[0]].iloc[-1].opentime
        result = find_best(item, coins)
        key = list(result.keys())[0]
        best_basket[end] = key
        print(f"batch {i}: {start}, {end}, best:{key}")
    return best_basket

def get_basket(baskets, start):
    # 基于当前运行时间段去找basket， basket的结束时间需要和stage2 的start时间在一定范围内
    for end, item in baskets.items():
        if start >= end and start <= end + timedelta(days=10):
            return item
    return 'BTC;BCH' 

def stage2(data, coins, best_basket, size=5):
    print("split data ...")
    batches = split_data(data, coins)
    print("============ stage2: backtest with best baskets ===========")
    value = 1
    long_queue = deque(maxlen=size)
    short_queue = deque(maxlen=size)
    for i, item in enumerate(batches):
        start = item[coins[0]].iloc[0].opentime
        end = item[coins[0]].iloc[-1].opentime
        basket = get_basket(best_basket, start)
        print(f"batch {i}:{start},{end}, basket:({basket})")
        mcoins = basket.split(";")
        long_coin = mcoins[0]
        short_coin = mcoins[1]
        if long_coin not in set(long_queue):
            long_queue.appendleft(long_coin)
        if short_coin not in set(short_queue):
            short_queue.appendleft(short_coin)
        k, sharp, calmar, mdd, cagr, last = backtest(item, list(long_queue), list(short_queue), init_value=value)
        value = last
        print(f"{list(long_queue)};{list(short_queue)}, value:{value}")
    return 


def rotate(data, coins, rotate_days=180, size=5):
    best_basket = stage1(data, coins, rotate_days)
    stage2(data, coins, best_basket, size=size)


def main():
    parser = argparse.ArgumentParser(
        usage='python rotate.py [-h] coins',
        description='backtest rotate strategy',
        epilog='Example: python rotate.py  BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST -t 1d',
    )
    parser.add_argument('coins', help='coin list to work with', default='BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST')
    parser.add_argument('-r', '--rotate', help='num of days to rotate', default=180,type=int)
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    parser.add_argument('-a', '--allocate', help='allocate percentage o init money', default=0.5,type=float)
    args = parser.parse_args()
    coins = args.coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    data = get_all_price(coins, args.timeframe)
    valid_coins = get_valid_coins(data, coins)
    print(f"valid coins:{valid_coins}")
    rotate(data, valid_coins, args.rotate)


if __name__ == '__main__':
    main()