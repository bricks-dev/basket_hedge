import numpy as np
import math

from plot import plot_line
from util import key, logreturn_df, mdd


def backtest(data, long_coins, short_coins, log=False, draw=False):
    logreturn = logreturn_df(data, long_coins, short_coins)
    logreturn['long'] = logreturn[long_coins].mean(axis=1)
    logreturn['short'] = logreturn[short_coins].mean(axis=1)
    logreturn['return'] = logreturn['long'] - logreturn['short']
    result = logreturn.filter(['return'], axis=1)
    cumresult = result.cumsum()
    return_tmp = cumresult['return'].dropna().to_numpy()
    return_list = list(return_tmp)
    days = len(return_list)
    daily_return = np.array([math.e**(y-x)-1 for x,y in zip(return_list,return_list[1:])])
    maxdrawdown = mdd(return_tmp)
    if not maxdrawdown:
        return 
    final = cumresult['return'].iat[-1]
    minv = cumresult['return'].min()
    maxv = cumresult['return'].max()
    sharp = np.mean(daily_return)/np.std(daily_return)* (days**0.5)
    k = f"long:[{key(long_coins)}],short:[{key(short_coins)}]"
    if log:
        print(f"{k}, min:{minv} max:{maxv}({100*(math.e**maxv-1)}%), mdd:{maxdrawdown}, sharp:{sharp}")
    if draw:
        plot_line(cumresult)
    return k, sharp