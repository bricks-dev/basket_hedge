import plotly.graph_objects as go
import plotly.express as px

def show_price(df):
    if df is None or df.empty:
        return
    fig = go.Figure(data=[go.Candlestick(x=df['opentime'],
                    open=df['open'], high=df['high'], low=df['low'], close=df['close'])])
    fig.show()

def plot_line(data):
    fig = px.line(data, x=data.index, y='return')
    fig.show()
    #cumresult.plot(figsize=(15, 10)).axhline(color='black', linewidth=2)


