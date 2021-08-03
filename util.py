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