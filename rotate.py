import argparse
from datetime import timedelta
from backtest import backtest
from data.data import get_all_price
from comb import find_best
from collections import deque, OrderedDict
from util import split_data, split_data_rotate

def get_basket(baskets, start, default='BTC;BCH'):
    # 基于当前运行时间段去找basket， basket的结束时间需要和stage2 的start时间在一定范围内
    for end, item in baskets.items():
        if start >= end and start <= end + timedelta(days=10):
            return item
    return default

def stage1(data, coins, freq=30, rotate_days=180):
    print("split data ...")
    batches = split_data_rotate(data, coins, f'{freq}D', rotate_days=rotate_days)
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


def stage2(data, coins, best_basket, freq=30, size=5):
    print("split data ...")
    batches = split_data(data, coins, freq=f'{freq}D')
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


def rotate(data, coins, freq_days=30, rotate_days=180,  size=5):
    best_basket = stage1(data, coins, freq=freq_days, rotate_days=rotate_days)
    stage2(data, coins, best_basket, freq=freq_days, size=size)


def main():
    parser = argparse.ArgumentParser(
        usage='python rotate.py [-h] coins',
        description='backtest rotate strategy',
        epilog='Example: python rotate.py  BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST -t 1d',
    )
    parser.add_argument('coins', help='coin list to work with', default='BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST')
    parser.add_argument('-r', '--rotate', help='num of days to rotate', default=180,type=int)
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    parser.add_argument('-f', '--freq', help='freq days', default=30, type=int)
    flag_parser = parser.add_mutually_exclusive_group(required=False)
    flag_parser.add_argument('--match', dest='match', action='store_true')
    flag_parser.add_argument('--no-match', dest='match', action='store_false')
    parser.set_defaults(flag=False)
    args = parser.parse_args()
    coins = args.coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    new_coins, data = get_all_price(coins, args.timeframe, match=args.match)
    rotate(data, new_coins, args.freq ,args.rotate)


if __name__ == '__main__':
    main()