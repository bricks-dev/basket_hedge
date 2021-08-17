import os
import pandas as pd
from itertools import combinations
from datetime import timedelta
from typing import Union

def possible(all_shorts):
    return [list(s) for s in combinations(all_shorts, 3)]

def MDD(data : pd.Series):
    roll_max = data.cummax()
    daily_drawdowm = data/roll_max - 1.0
    return daily_drawdowm.cummin().iloc[-1]

def CAGR(first, last, periods):
    rate = last/first
    if rate > 0:
        return rate**(1/periods)-1
    else:
        return -((1-rate)**(1/periods) - 1)

def key(symbols):
    return ",".join(symbols)

def percentf(val, digits=2):
    return f"{round(val * 100, digits)}%"


def days(coin_df: Union[pd.Series, pd.DataFrame]):
    return (coin_df.index[-1] - coin_df.index[0]).days + 1

def get_valid_size(data):
    max_size = 0
    for df in data.values():
        if df.shape[0] > max_size:
            max_size = df.shape[0]
    return max_size

def get_valid_coins(data, coins, valid_size=None):
    if valid_size is None:
        valid_size = get_valid_size(data)
    valid_coins = [s for s in coins if data[s] is not None and data[s].shape[0]>=valid_size]
    invalid_coins = set(coins) - set(valid_coins)
    if invalid_coins:
        print(f"invalid_coins: {invalid_coins}, data size not valid")
    return valid_coins

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
    # rotate_days 整个回看周期是多长时间
    # freq 每次迭代window move 的时间
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

def stats(pnls, timeframe='1d'):
    pnls['daily_return'] = pnls['total'].pct_change(1)
    sharpe_days_multiple = {'1d':1,'4h':6, '1h':24}.get(timeframe, 1)
    sharpe = ((365*sharpe_days_multiple)**0.5)*pnls['daily_return'].mean() / pnls['daily_return'].std()
    mdd = MDD(pnls.total)
    pnl = next(iter(pnls.items()))[1] # select first symbol
    periods = days(pnl)/365 
    first = pnls.iloc[0]['total']
    last = pnls.iloc[-1]['total']
    cagr = CAGR(first, last, periods)
    calmar = abs(cagr/mdd)
    return sharpe, mdd, cagr, calmar, first, last

def calc_pos(data, coin, init_value, is_long=True, col='close'):
    df = data[coin]
    if is_long:
        df = df.assign(norm_return=df[col]/df.at[df.index[0],col])
    else:
        df = df.assign(norm_return=2 - df[col]/df.at[df.index[0], col])
    df['position'] = df['norm_return'] * init_value
    data[coin] = df
    return df['position']

def save_file(df, file_name, format='csv'):
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
    print(f"saving file: {file_name}")