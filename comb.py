import math
import tqdm
from backtest import backtest
from itertools import combinations, repeat
from multiprocessing import Pool, cpu_count
import argparse
from data import get_all_price
from backtest import backtest


def get_valid_size(data):
    max_size = 0
    for df in data.values():
        if df.shape[0] > max_size:
            max_size = df.shape[0]
    return max_size

def get_valid_coins(data, coins, valid_size):
    valid_coins = [s for s in coins if data[s] is not None and data[s].shape[0]>=valid_size]
    invalid_coins = set(coins) - set(valid_coins)
    print(f"invalid_coins: {invalid_coins}, data size not valid")
    return valid_coins


def find_combinations(data, coins, m=1, n=1, min_sharp=1.5, min_calmar=2.0, drawdown=-1, allocate=0.5):
    # coins 进行long/short的排列组合，选择出 sharp ratio 符合条件的组合
    # m 是 long_coins 数量, n 是 short_coins 数量 
    assert m+n <= len(data), "make sure m+n <= num of coins"
    print("start find_combinations ...")
    p = Pool(cpu_count())
    valid_size = get_valid_size(data)
    coins = get_valid_coins(data, coins, valid_size)
    longs = []
    shorts = []
    for com in combinations(coins, m+n):
        com_list = list(com) 
        for item in combinations(com_list, m): # tuple to list 
            longs.append(list(item))
            shorts.append(list(set(com_list) - set(item)))
    inputs = zip(repeat(data), longs, shorts, repeat(False), repeat(allocate))
    result = p.starmap(backtest, tqdm.tqdm(inputs, total=len(longs)))
    tag = {}
    for (k, sharp, calmar, mdd, cagr) in result:
        if not math.isnan(sharp) and sharp >= min_sharp and mdd >= drawdown and calmar >= min_calmar:
            tag[k] = (sharp, calmar, mdd, cagr)
    sortedtag = {k: v for k, v in sorted(tag.items(), key=lambda item: item[1][1], reverse=True)} # sort by calmar
    print(sortedtag)
    return sortedtag


def main():
    parser = argparse.ArgumentParser(
        usage='python comb.py [-h] coins',
        description='find best combination of long/short in coin list',
        epilog='Example: python comb.py  BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST',
    )
    parser.add_argument('coins', help='coin list to work with', default='BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST')
    parser.add_argument('m', help='num of long coins', default='1',type=int)
    parser.add_argument('n', help='num of short coins', default='1',type=int)
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    parser.add_argument('-s', '--sharp', help='threshold of sharp ratio', default=1.5,type=float)
    parser.add_argument('-c', '--calmar', help='threshold of calmar ratio', default=2,type=float)
    parser.add_argument('-d', '--drawdown', help='threshold of max drawdown', default=-1,type=float)
    parser.add_argument('-a', '--allocate', help='allocate percentage o init money', default=0.5,type=float)
    args = parser.parse_args()
    coins = args.coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    assert args.m + args.n <= len(coins), "make sure m + n <= len of coins list"
    data = get_all_price(coins, args.timeframe)
    find_combinations(data, coins, args.m, args.n, min_sharp=args.sharp, min_calmar=args.calmar, drawdown=args.drawdown, allocate=args.allocate)


if __name__ == '__main__':
    main()