# basket_hedge

[how to calc return](https://romanorac.github.io/cryptocurrency/analysis/2017/12/29/cryptocurrency-analysis-with-python-part3.html )


## 回测

回测 long/short 组合的收益，第一个参数是 long_coins，第二个参数是 short_coins，用逗号分隔。 


```python hedge.py BTC,ETH XRP,TRX```

## 最佳组合

输入 coins 列表，找到表现最好(sharp ratio最高)的 long/short 组合。为了加快回测速度暂时改为 long/short 列表长度为1，可以很容易改为大于1。


```python comb.py BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST```

<h2>Notebook</h2>
long/short backtest![long/short backtest](https://user-images.githubusercontent.com/5565266/126291402-b9bd2ec3-89db-4ff0-a93d-0fc956528fa1.png)

find_best_combination![find_combination](https://user-images.githubusercontent.com/5565266/126291419-60f09cbd-e85d-4dd0-9686-20edc8d0189e.png)



