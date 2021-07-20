import math
from backtest import backtest
from itertools import permutations

def find_combinations(data, coins, min_sharp=1.5):
    # coins 进行long/short的排列组合，选择出 sharp ratio 符合条件的组合
    tag = {}
    coins = [s for s in coins if data[s] is not None and data[s].shape[0]>300]
    for (longsymbol, shortsymbol) in permutations(coins,2):
        k, sharp = backtest(data, [longsymbol], [shortsymbol])
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
    args = parser.parse_args()
    coins = args.coins.upper().split(',')
    data = get_all_price(coins,'1d')
    find_combinations(data, coins)


if __name__ == '__main__':
    main()