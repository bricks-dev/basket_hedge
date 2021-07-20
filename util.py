import pandas as pd
import numpy as np
from itertools import combinations


def logreturn_df(all, longsymbols,shortsymbols):
    allsymbols = longsymbols + shortsymbols
    mydict = {}
    for s in allsymbols:
        mydict[s] = all[s].close
    mydict['datetime'] = all[longsymbols[0]].opentime
    df = pd.DataFrame(mydict)
    df.set_index('datetime', inplace=True)
    return df.apply(lambda x: np.log(x) - np.log(x.shift(1))) 
    
def possible(all_shorts):
    return [list(s) for s in combinations(all_shorts, 3)]

def mdd(xs):
    temp = np.maximum.accumulate(xs) - xs
    if 0 in [np.array(temp).size, np.array(xs).size]:
        return -1
    i = np.argmax(temp) # end of the period
    if np.array(xs[:i]).size == 0:
        return -1
    j = np.argmax(xs[:i]) # start of period
    return xs[i] - xs[j]

def key(symbols):
    return ",".join(symbols)