# basket_hedge

[how to calc return](https://romanorac.github.io/cryptocurrency/analysis/2017/12/29/cryptocurrency-analysis-with-python-part3.html )


## 简单回测

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


![long/short](https://user-images.githubusercontent.com/5565266/128318646-5772fbbf-3934-4d48-95bd-bea6884a0449.png)

###  保存PNL文件

```python pnl_file.py ETH,BTC,MATIC,THETA BCH,XRP,EOS  -t 1d```

把简单回测结果保存到./output 文件夹，默认为pickle格式。(开发此功能初衷是为了跟海龟策略结合，把basket PNL作为海龟策略的输入，后来发现这个想法有问题。)
## 寻找最佳组合

输入 coins 列表，找到表现最好(sharp ratio最高)的 long/short 组合。第一个参数是 coins 列表， 第2/3个参数分别是long/short coins 数量。为了避免回测太慢，这两个数字不应该设置的很大。 

* --sort 输出结果按照什么指标排序: mdd, sharp, cagr, calmar
* -s 输出结果按照sharp ratio 值进行过滤，低于这个值的结果不显示

```python comb.py BTC,ETH,XRP,EOS,LINK,UNI,TRX,IOST 1 1 -t 4h -s 2.0 --sort mdd```



```
result: 
{
   "ETH;BCH":(2.2971850378327128,10.697037681869743,-0.3530622559417854,3.776720255855218,3.539042150808071),
   "ETH;LINK":(2.347284872948933,9.428492438880879,-0.38648287695921546,3.643950883166892,3.4593249749661985),
   "SOL;LINK":(2.352933747100389,23.596596911726394,-0.5170894009038323,12.20155016045382,8.048418673530698),
   "SOL;BCH":(2.357400406263565,23.57270454116125,-0.5244847641365566,12.363524381331697,8.128135849372569),
   ...
}
```


## 滚动回测

每一个月都动态更新当前持仓组合，比如前一段时间(180天)表现最好的是long BTC, short ETH， 则把BTC加入当前long_coins, ETH 加入当前 short_coins。 

* --match or --no-match 是否对齐所有symbols的数据，如果对齐则需要cut一些币种的数据
* -f 30 30天重新评估一次是否更新basket
* -r 180 参考过去180天表现最好的basket来更新当前组合

```python rotate.py BTC,ETH,BNB,XRP,DOT,UNI,BCH,LTC,SOL,LINK,MATIC,XLM,ETC,THETA -t 1d -f 30 -r 180 --no-match```


## 动态调整组合的仓位

检查当前组合多空所占仓位的比例，如果超过最大/最小阈值则重新平衡为初始值(各一半)

* -min 0.3 最小阈值30%
* -max 0.7 最大阈值30%
* -f 30 30天检查一次阈值

```python rebalance.py BTC,ETH BCH,EOS -t 4h -min 0.3 -max 0.7 -f 30```