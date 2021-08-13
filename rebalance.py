import argparse
from data.data import get_all_price
import pandas as pd
from math import isclose
from util import key, split_data, calc_pos, percentf, stats
from plot import plot_pnl


def reset_alloc(long_allocs:list, short_allocs:list, min_alloc=0.3,max_alloc=0.7):
    all = sum(long_allocs) + sum(short_allocs)
    assert isclose(all, 1), f"{all} should be close to 1"
    if sum(long_allocs) < min_alloc or sum(long_allocs) > max_alloc:
        print(f"portfolio imbalance, reset allocation: {long_allocs}, {short_allocs}")
        return [0.5/len(long_allocs)] * len(long_allocs), [0.5/len(short_allocs)] * len(short_allocs)
    return long_allocs, short_allocs


def backtest(data, long_coins, short_coins, min_alloc, max_alloc, 
            long_allocs=None, short_allocs=None,  init_value=1):
    all_pos = {}
    index = data[long_coins[0]].opentime # time
    allocs1, allocs2 = reset_alloc(long_allocs, short_allocs, min_alloc=min_alloc, max_alloc=max_alloc)
    for coin, alloc in zip(long_coins, allocs1):
        all_pos[coin] = calc_pos(data, coin, init_value * alloc, True)
    for coin, alloc in zip(short_coins, allocs2):
        all_pos[coin] = calc_pos(data, coin, init_value * alloc, False)
    pnls = pd.DataFrame(all_pos)
    pnls.index = index
    pnls['total'] = pnls.sum(axis=1)
    return pnls

def calc_allocs_and_value(pnls, long_coins, short_coins):
    allocs1 = [pnls.iloc[-1][c] for c in long_coins]
    allocs2 = [pnls.iloc[-1][c] for c in short_coins]
    total = sum(allocs1) + sum(allocs2)
    return [a/total for a in allocs1], [a/total for a in allocs2], total


def rebalance(data, long_coins, short_coins, min_alloc, max_alloc, freq_days=30):
    print("split data ...")
    coins = long_coins + short_coins
    batches = split_data(data, coins, freq=f'{freq_days}D')
    print("============ rebalance backtest ===========")
    value = 1
    allocs1 = [0.5/len(long_coins)] * len(long_coins)
    allocs2 = [0.5/len(short_coins)] * len(short_coins)
    all_pnls = []
    for i, item in enumerate(batches):
        start = item[coins[0]].iloc[0].opentime
        end = item[coins[0]].iloc[-1].opentime
        print(f"batch {i}: {start},{end}")
        print(f"allocations: {allocs1}, {allocs2}")
        pnls = backtest(item, long_coins, short_coins, min_alloc, max_alloc, 
                        long_allocs=allocs1, short_allocs=allocs2, init_value=value)
        all_pnls.append(pnls)
        allocs1, allocs2, value = calc_allocs_and_value(pnls, long_coins, short_coins)
    all_pnls = pd.concat(all_pnls)
    return all_pnls


def run_rebalance(data, long_coins, short_coins, min_alloc,max_alloc, timeframe='1d', freq_days=30):
    pnls = rebalance(data, long_coins, short_coins, min_alloc, max_alloc, freq_days=freq_days)
    sharpe, mdd, cagr, calmar, first, last = stats(pnls, timeframe=timeframe)
    title_key = f"long:[{key(long_coins)}];short:[{key(short_coins)}]"
    title = f"{title_key}, Sharpe: {round(sharpe,2)}, Calmar:{round(calmar,2)}, MDD:{percentf(mdd)}, CAGR:{percentf(cagr)}"
    plot_pnl(pnls, title)


def main():
    parser = argparse.ArgumentParser(
        usage='python rebalance.py [-h] long_coins short_coins',
        description='backtest by long&short a basket of coins',
        epilog='Example: python hedge.py BTC,ETH XRP,EOS',
    )
    parser.add_argument('long_coins', help='coin list to long', default='BTC,ETH')
    parser.add_argument('short_coins', help='coin list to short', default='EOS,XRP')
    parser.add_argument('-t', '--timeframe', help='timeframe of ohlcv, 1d/4h/1h/15m/1m', default='1d')
    parser.add_argument('-min', '--min_alloc', help='min allocation threshold', type=float, default=0.3)
    parser.add_argument('-max', '--max_alloc', help='max allocation threshold', type=float, default=0.7)
    parser.add_argument('-f', '--freq', help='freq days to check', type=int, default=30)
    args = parser.parse_args()
    long_coins = args.long_coins.upper().split(',')
    short_coins = args.short_coins.upper().split(',')
    assert args.timeframe in ['1d','4h','1h','15m','1m']
    coins = long_coins + short_coins
    new_coins, data = get_all_price(coins, args.timeframe)
    run_rebalance(data, long_coins, short_coins, args.min_alloc, args.max_alloc, 
                    timeframe=args.timeframe, freq_days=args.freq)


if __name__ == '__main__':
    main()