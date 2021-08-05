import os
import pandas as pd
from util import key
import argparse
from data import get_all_price

def calc_pos(data, coin, alloc, is_long=True, col='close'):
    df = data[coin]
    if is_long:
        df['norm_return'] = df[col]/df.iloc[0][col]
    else:
        df['norm_return'] = 2 - df[col]/df.iloc[0][col]
    df['position'] = df['norm_return'] * alloc * 1
    return df['position']
    

def save_pnl_file(df, file_name, format='csv'):
    df['datetime'] = df.index
    df.set_index('datetime', drop=True, inplace=True)
    outdir = './output/'
    if not os.path.exists(outdir):
        os.mkdir(outdir)
    if format == 'csv':
        file_name = f'{outdir}{file_name}.csv'
        df.to_csv(file_name)
    elif format == 'pkl':
        file_name = f'{outdir}{file_name}.pkl'
        df.to_pickle(file_name)
    print(f"saving PNL file: {file_name}")

def backtest(data, long_coins, short_coins, col='close'):
    all_pos = {}
    index = data[long_coins[0]].opentime # time
    # money allocated to each symbol at first
    alloc1 = [0.5 /len(long_coins)] * len(long_coins)
    alloc2 = [0.5 /len(short_coins)] * len(short_coins)
    for coin, alloc in zip(long_coins, alloc1):
        all_pos[coin] = calc_pos(data, coin, alloc, True, col)
    for coin, alloc in zip(short_coins, alloc2):
        all_pos[coin] = calc_pos(data, coin, alloc, False, col)
    value = pd.DataFrame(all_pos)
    value.index = index
    value['total'] = value.sum(axis=1)
    value['daily_return'] = value['total'].pct_change(1)
    return value

def multi_run(data, long_coins, short_coins):
    k = f"{key(long_coins)};{key(short_coins)}"
    df = pd.DataFrame()
    for col in ['open', 'high', 'low','close']:
        pnl = backtest(data, long_coins, short_coins, col)
        df[col] = pnl['total'].copy()
    save_pnl_file(df, k, 'pkl')
    return df


def main():
    parser = argparse.ArgumentParser(
        usage='python hedge.py [-h] long_coins short_coins',
        description='backtest by long&short a basket of coins',
        epilog='Example: python pnl_file.py BTC,ETH XRP,EOS -t 1d',
    )
    parser.add_argument('long_coins', help='coin list to long', default='BTC,ETH')
    parser.add_argument('short_coins', help='coin list to short', default='EOS,XRP')
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    parser.add_argument('-a', '--allocate', help='allocate percentage of init money to long/short, 0.5 as default', default=0.5, type=float)
    parser.add_argument('-al', '--along', help='allocate percents of init money to long')
    parser.add_argument('-as', '--ashort', help='allocate percents of init money to short')
    args = parser.parse_args()
    long_coins = args.long_coins.upper().split(',')
    short_coins = args.short_coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    coins = long_coins + short_coins
    new_coins, data = get_all_price(coins, args.timeframe)
    multi_run(data, long_coins, short_coins)


if __name__ == '__main__':
    main()

