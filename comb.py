import math
from backtest import backtest
from itertools import permutations

def find_combinations(data, coins, m=1, n=1, min_sharp=1.5):
    # coins 进行long/short的排列组合，选择出 sharp ratio 符合条件的组合
    # m 是 long_coins 数量, n 是 short_coins 数量 
    assert m+n <= len(data), "make sure m+n <= num of coins"
    tag = {}
    coins = [s for s in coins if data[s] is not None and data[s].shape[0]>300]
    for item in permutations(coins, m+n):
        item = list(item) # tuple to list 
        # long list -> item[:m], short list -> item[m:]
        k, sharp = backtest(data, item[:m], item[m:])
        if not math.isnan(sharp) and sharp > min_sharp:
            tag[k] = sharp
    sortedtag = {k: v for k, v in sorted(tag.items(), key=lambda item: item[1], reverse=True)}
    print(sortedtag)
    return sortedtag


import argparse
from data import get_all_price
from backtest import backtest


def main():
    parser = argparse.ArgumentParser(
        usage='python comb.py [-h] coins',
        description='find best combination of long/short in coin list',
        epilog='Example: python comb.py  BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST',
    )
    parser.add_argument('coins', help='coin list to work with', default='BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST')
    parser.add_argument('m', help='num of long coins', default='1',type=int)
    parser.add_argument('n', help='num of short coins', default='1',type=int)
    args = parser.parse_args()
    coins = args.coins.upper().split(',')
    assert args.m + args.n <= len(coins), "make sure m + n <= len of coins list"
    data = get_all_price(coins,'1d')
    find_combinations(data, coins, args.m, args.n)


if __name__ == '__main__':
    main()