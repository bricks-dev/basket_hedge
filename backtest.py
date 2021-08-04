import pandas as pd
from util import key, MDD, CAGR, percentf, days

def calc_pos(data, coin, alloc, is_long=True, init_value=1):
    df = data[coin]
    if is_long:
        df['norm_return'] = df['close']/df.iloc[0]['close']
    else:
        df['norm_return'] = 2 - df['close']/df.iloc[0]['close']
    df['position'] = df['norm_return'] * alloc * init_value
    return df['position']
    
def parse_alloc(coins, alloc, alloc_list):
    return [alloc/len(coins)] * len(coins) if not alloc_list else [float(a) for a in alloc_list.split(",")]


def backtest(data, long_coins, short_coins, plot=False, allocate=0.5, 
        alloc_long=None, alloc_short=None, init_value=1, timeframe='1d'):
    all_pos = {}
    index = data[long_coins[0]].opentime # time
    # money allocated to each symbol at first
    alloc1 = parse_alloc(long_coins, allocate, alloc_long)
    alloc2 = parse_alloc(short_coins, allocate, alloc_short)
    assert len(alloc1) == len(long_coins)
    assert len(alloc2) == len(short_coins)
    not_used_money = (1 - sum(alloc1) - sum(alloc2)) * init_value
    for coin, alloc in zip(long_coins, alloc1):
        all_pos[coin] = calc_pos(data, coin, alloc, True, init_value)
    for coin, alloc in zip(short_coins, alloc2):
        all_pos[coin] = calc_pos(data, coin, alloc, False, init_value)
    value = pd.DataFrame(all_pos)
    value.index = index
    value['total'] = value.sum(axis=1) + not_used_money
    value['daily_return'] = value['total'].pct_change(1)
    sharp_days_multiple = {'1d':1,'4h':6, '1h':24}.get(timeframe, 1)
    sharp = ((365*sharp_days_multiple)**0.5)*value['daily_return'].mean() / value['daily_return'].std()
    mdd = MDD(value.total)
    periods = days(data[long_coins[0]])/365 
    first = value.iloc[0]['total']
    last = value.iloc[-1]['total']
    cagr = CAGR(first, last, periods)
    calmar = abs(cagr/mdd)
    k = f"{key(long_coins)};{key(short_coins)}"
    title_key = f"long:[{key(long_coins)}];short:[{key(short_coins)}]"
    title = f"{title_key}, Sharpe: {round(sharp,2)}, Calmar:{round(calmar,2)}, MDD:{percentf(mdd)}, CAGR:{percentf(cagr)}"
    if plot:
        import matplotlib.pyplot as plt
        plt.style.use('fivethirtyeight')
        value['total'].plot(figsize=(12,8), title=title)
        plt.show()
    return k, sharp, calmar, mdd, cagr, last