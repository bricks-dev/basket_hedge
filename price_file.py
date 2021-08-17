import pandas as pd
from util import key, save_file
import argparse
from data.data import get_all_price
    

def price_df(data, long_coins, short_coins, cols):
    df = pd.DataFrame()
    for col in cols:
        long = data[long_coins[0]][col]
        short = data[short_coins[0]][col]
        for x in long_coins[1:]:
            long = data[x][col].add(long)
        for x in short_coins[1:]:
            short = data[x][col].add(short)
        df[col] = long.divide(short)
    df.index = data[long_coins[0]].opentime # time
    return df

def save_price_file(data, long_coins, short_coins):
    k = f"{key(long_coins)};{key(short_coins)}"
    df = price_df(data, long_coins, short_coins, ['open', 'high', 'low','close'])
    save_file(df, k, 'pkl')
    return df


def main():
    parser = argparse.ArgumentParser(
        usage='python price_file.py [-h] long_coins short_coins',
        description='save price data as csv/pickle file',
        epilog='Example: python price_file.py BTC,ETH XRP,EOS -t 1d',
    )
    parser.add_argument('long_coins', help='coin list to long', default='BTC,ETH')
    parser.add_argument('short_coins', help='coin list to short', default='EOS,XRP')
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    args = parser.parse_args()
    long_coins = args.long_coins.upper().split(',')
    short_coins = args.short_coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    coins = long_coins + short_coins
    new_coins, data = get_all_price(coins, args.timeframe)
    save_price_file(data, long_coins, short_coins)


if __name__ == '__main__':
    main()

