import argparse
from data import get_all_price
from backtest import backtest


def main():
    parser = argparse.ArgumentParser(
        usage='python hedge.py [-h] long_coins short_coins',
        description='backtest by long&short a basket of coins',
        epilog='Example: python hedge.py BTC,ETH XRP,EOS',
    )
    parser.add_argument('long_coins', help='coin list to long', default='BTC,ETH')
    parser.add_argument('short_coins', help='coin list to short', default='EOS,XRP')
    args = parser.parse_args()
    long_coins = args.long_coins.upper().split(',')
    short_coins = args.short_coins.upper().split(',')
    coins = long_coins + short_coins
    data = get_all_price(coins,'1d')
    backtest(data, long_coins, short_coins, True, True)


if __name__ == '__main__':
    main()

