import pandas as pd
from itertools import combinations

    
def possible(all_shorts):
    return [list(s) for s in combinations(all_shorts, 3)]

def mdd(data : pd.Series):
    roll_max = data.cummax()
    daily_drawdowm = data/roll_max - 1.0
    return daily_drawdowm.cummin().iloc[-1]

def key(symbols):
    return ",".join(symbols)