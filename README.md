# basket_hedge

[how to calc return](https://romanorac.github.io/cryptocurrency/analysis/2017/12/29/cryptocurrency-analysis-with-python-part3.html )


## 回测

回测 long/short 组合的收益

* 第一个参数是 long_coins，用逗号分隔
* 第二个参数是 short_coins，用逗号分隔
* -t 4h 获取k线数据的粒度

分配给多/空组合的资金比例, 两种配置方式：
* -a 0.5 ，默认为各50%，小于0.5也就是使用部分资金
* -al 0.1,0.2 ，给做多组合的资金配比，按照逗号分隔，解析后list长度应该等于long coins 个数
* -as 0.2,0.2 ，给做空组合的资金配比，按照逗号分隔，解析后list长度应该等于short coins 个数


```python hedge.py BTC,ETH XRP,TRX -t 4h -a 0.25```


```python hedge.py BTC,ETH XRP,TRX -t 4h -al 0.1,0.1 -as 0.2,0.1```


## 最佳组合

输入 coins 列表，找到表现最好(sharp ratio最高)的 long/short 组合。第一个参数是 coins 列表， 第2/3个参数分别是long/short coins 数量。为了避免回测太慢，这两个数字不应该设置的很大。 


```python comb.py BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST 1 1 -t 4h -s 2.0 ```

<h2>Notebook</h2>

long/short backtest![long/short backtest](https://user-images.githubusercontent.com/5565266/126291402-b9bd2ec3-89db-4ff0-a93d-0fc956528fa1.png)

find_combination![find_combination](https://user-images.githubusercontent.com/5565266/126302906-a3558823-c016-473e-9841-76b6ec5af436.png)




