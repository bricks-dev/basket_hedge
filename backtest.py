import pandas as pd
from util import key, percentf, stats, calc_pos
from plot import plot_pnl

    
def parse_alloc(coins, alloc, alloc_list):
    return [alloc/len(coins)] * len(coins) if not alloc_list else [float(a) for a in alloc_list.split(",")]


def backtest(data, long_coins, short_coins, plot=False, allocate=0.5, 
        alloc_long=None, alloc_short=None, init_value=1, timeframe='1d', col='close'):
    all_pos = {}
    # money allocated to each symbol at first
    alloc1 = parse_alloc(long_coins, allocate, alloc_long)
    alloc2 = parse_alloc(short_coins, allocate, alloc_short)
    assert len(alloc1) == len(long_coins)
    assert len(alloc2) == len(short_coins)
    not_used_money = (1 - sum(alloc1) - sum(alloc2)) * init_value
    for coin, alloc in zip(long_coins, alloc1):
        all_pos[coin] = calc_pos(data, coin, init_value * alloc, True, col)
    for coin, alloc in zip(short_coins, alloc2):
        all_pos[coin] = calc_pos(data, coin, init_value * alloc, False, col)
    pnls = pd.DataFrame(all_pos)
    pnls.index = data[long_coins[0]].opentime # time
    pnls['total'] = pnls.sum(axis=1) + not_used_money
    sharpe, mdd, cagr, calmar, first, last = stats(pnls, timeframe)
    k = f"{key(long_coins)};{key(short_coins)}"
    title_key = f"long:[{key(long_coins)}];short:[{key(short_coins)}]"
    title = f"{title_key}, Sharpe: {round(sharpe,2)}, Calmar:{round(calmar,2)}, MDD:{percentf(mdd)}, CAGR:{percentf(cagr)}"
    if plot:
        plot_pnl(pnls, title)
    return k, sharpe, calmar, mdd, cagr, last