import argparse
import pandas as pd
from datetime import timedelta
from backtest import backtest
from data.data import get_all_price
from comb import find_best
from collections import OrderedDict
from util import split_data, split_data_rotate, calc_pos, stats, percentf
from plot import plot_pnl


def get_basket(baskets, start, default='BTC;BCH'):
    # 基于当前运行时间段去找basket， basket的结束时间需要和stage2 的start时间在一定范围内
    for end, item in baskets.items():
        if start >= end and start <= end + timedelta(days=10):
            return item
    return default

def backtest(data, long_coins, short_coins, init_value=1, col='close'):
    all_pos = {}
    # money allocated to each symbol at first
    alloc1 = 0.5/ len(long_coins)
    alloc2 = 0.5/ len(short_coins)
    for coin in long_coins:
        all_pos[coin] = calc_pos(data, coin, init_value * alloc1, True, col)
    for coin in short_coins:
        all_pos[coin] = calc_pos(data, coin, init_value * alloc2, False, col)
    pnls = pd.DataFrame(all_pos)
    pnls.index = data[long_coins[0]].opentime # time
    pnls['total'] = pnls.sum(axis=1)
    return pnls.filter(['total'], axis=1)

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


def stage2(data, coins, best_basket, freq=30):
    batches = split_data(data, coins, freq=f'{freq}D')
    print("============ stage2: backtest with best baskets ===========")
    value = 1
    long_coins = set()
    short_coins = set()
    pnls = []
    for i, item in enumerate(batches):
        start = item[coins[0]].iloc[0].opentime
        end = item[coins[0]].iloc[-1].opentime
        basket = get_basket(best_basket, start)
        print(f"batch {i}:{start},{end}, basket:({basket})")
        mcoins = basket.split(";")
        long_coin = mcoins[0]
        short_coin = mcoins[1]
        long_coins.add(long_coin)
        short_coins.add(short_coin)
        long_coins.discard(short_coin)
        short_coins.discard(long_coin)
        pnl = backtest(item, list(long_coins), list(short_coins), init_value=value)
        pnls.append(pnl)
        value = pnl.iloc[-1]['total']
        print(f"{long_coins};{short_coins}, value={value}")
    pnls = pd.concat(pnls)
    return pnls



def rotate(data, coins, timeframe='1d', freq_days=30, rotate_days=180):
    best_basket = stage1(data, coins, freq=freq_days, rotate_days=rotate_days)
    pnls = stage2(data, coins, best_basket, freq=freq_days)
    sharpe, mdd, cagr, calmar, first, last = stats(pnls, timeframe=timeframe)
    title = f"Rotate Basket, Sharpe: {round(sharpe,2)}, Calmar:{round(calmar,2)}, MDD:{percentf(mdd)}, CAGR:{percentf(cagr)}"
    plot_pnl(pnls, title)


def main():
    pd.set_option('mode.chained_assignment','raise')
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
    rotate(data, new_coins, args.timeframe, args.freq ,args.rotate)


if __name__ == '__main__':
    main()