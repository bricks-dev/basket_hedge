import pandas as pd
from itertools import combinations

    
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


def days(coin_df):
    return (coin_df.iloc[-1].opentime - coin_df.iloc[0].opentime).days + 1

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
