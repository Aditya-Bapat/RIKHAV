# Record Buy, Buy Hold, Sell and Sell Hold signals of particular stock

import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math

ticker = input('Enter Ticker: ')

start_day = int(input('Starting Day: '))
start_month = int(input('Starting Month: '))
start_Year = int(input('Starting Year: '))
start_date = f'{start_Year}-{start_month}-{start_day}'

end_day = int(input('End Day: '))
end_month = int(input('End Month: '))
end_Year = int(input('End Year: '))
end_date = f'{end_Year}-{end_month}-{end_day}'
data = yf.download(ticker, start=start_date, end=end_date, interval='1h')

w1=int(input("Enter value for SMA 1 i.e. 10,20: "))
data[f'SMA_{w1}'] = data['Close'].rolling(window=w1).mean()
print(data[['Close', f'SMA_{w1}']].tail())

w2=int(input("Enter value for SMA 2 i.e. 10,20: "))
data[f'SMA_{w2}'] = data['Close'].rolling(window=w2).mean()
print(data[['Close', f'SMA_{w2}']].tail())

initial_allocation = 100000
holding = None
signal_list2 = []

# Initial state
signal_list2.append({
    'Signal': 'Initial',
    'Date': data.index[0],
    'Close Price': data['Close'].iloc[0],
    'Shares Bought': 0,
    'Profit/Loss': 0,
    'Investment': 0,
    'Remaining Cash': initial_allocation,
    'Hold': "None",
    'Total Cash': initial_allocation,
    'SMA1': w1,
    'SMA2': w2
})

for i in range(1, len(data)):
    close_price = data['Close'].iloc[i]
    prev_signal = signal_list2[-1]
    buy_signal = (data[f'SMA_{w2}'].iloc[i] > data[f'SMA_{w1}'].iloc[i]) and \
                 (data[f'SMA_{w2}'].iloc[i - 1] <= data[f'SMA_{w1}'].iloc[i - 1])
    sell_signal = (data[f'SMA_{w2}'].iloc[i] < data[f'SMA_{w1}'].iloc[i]) and \
                  (data[f'SMA_{w2}'].iloc[i - 1] >= data[f'SMA_{w1}'].iloc[i - 1])

    # Record daily state before any signal
    if holding is None and not (buy_signal or sell_signal):
        signal_list2.append({
            'Signal': 'No Signal',
            'Date': data.index[i],
            'Close Price': close_price,
            'Shares Bought': 0,
            'Profit/Loss': 0,
            'Investment': 0,
            'Remaining Cash': prev_signal['Remaining Cash'],
            'Hold': "None",
            'Total Cash': prev_signal['Total Cash'],
            'SMA1': w1,
            'SMA2': w2
        })

    # Buy Signal
    if buy_signal:
      prev_total_cash = signal_list2[-1]['Total Cash']
      shares_bought = math.floor(prev_total_cash / close_price)
      investment = shares_bought * close_price
      remaining_cash = prev_total_cash - investment
      profit = investment - prev_signal['Investment']
      if prev_signal['Investment'] == 0:
        profit = 0
        total_cash = prev_total_cash
      else:
        total_cash = prev_total_cash + profit

      signal_list2.append({
            'Signal': 'Buy',
            'Date': data.index[i],
            'Close Price': close_price,
            'Shares Bought': shares_bought,
            'Profit/Loss': 0,
            'Investment': investment,
            'Remaining Cash': remaining_cash,
            'Hold': "Buy",
            'Total Cash': total_cash,
            'SMA1': w1,
            'SMA2': w2
        })
      holding = 'buy'

    # Buy Hold
    if holding == 'buy':
        buy_signal_sb = next((s for s in reversed(signal_list2) if s['Signal'] == 'Buy'), None)
        if buy_signal_sb:
            sb = buy_signal_sb['Shares Bought']
            investment = sb * close_price
            profit = investment - signal_list2[-1]['Investment']
            rem = signal_list2[-1]['Remaining Cash']
            total_cash = signal_list2[-1]['Total Cash'] + profit
            signal_list2.append({
                'Signal': 'Buy Hold',
                'Date': data.index[i],
                'Close Price': close_price,
                'Profit/Loss': profit,
                'Investment': investment,
                'Shares Bought': sb,
                'Remaining Cash': rem,
                'Hold': "Buy Hold",
                'Total Cash': total_cash,
                'SMA1': w1,
                'SMA2': w2
            })

    # Sell Signal
    if sell_signal:
        sb = 0
        investment = 0
        profit = 0
        total_cash = prev_signal['Total Cash']
        remaining_cash = prev_signal['Remaining Cash']

        signal_list2.append({
            'Signal': 'Sell',
            'Date': data.index[i],
            'Close Price': close_price,
            'Profit/Loss': profit,
            'Investment': investment,
            'Shares Bought': sb,
            'Remaining Cash': remaining_cash,
            'Hold': "Sell Hold",
            'Total Cash': total_cash,
            'SMA1': w1,
            'SMA2': w2
        })
        holding = 'sell'

    # Short Sell
    if holding == 'sell':
            shares_bought = math.floor((signal_list2[-1]['Total Cash'])/close_price)
            investment = shares_bought * close_price
            prev_investment = signal_list2[-1]['Investment']
            if prev_investment == 0:
                profit = 0
            else:
                profit = investment - prev_investment
            rem = signal_list2[-1]['Total Cash']-investment
            total_cash = signal_list2[-1]['Total Cash'] + profit
            if total_cash < 0:
                total_cash = abs(total_cash)
            signal_list2.append({
                'Signal': 'Short Sell',
                'Date': data.index[i],
                'Close Price': close_price,
                'Profit/Loss': profit,
                'Investment': investment,
                'Shares Bought': shares_bought,
                'Remaining Cash': rem,
                'Hold': "Sell Hold",
                'Total Cash': total_cash,
                'SMA1': w1,
                'SMA2': w2
            })

results_df = pd.DataFrame(signal_list2)

results_df

csv_path = input('Save file by unique Name: ')
csv = csv_path + '.csv'
results_df.to_csv(csv, index=False)
print(f"DataFrame saved successfully as {csv}.")

#Interactive Scatter plot with plotly
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    mode='lines',
    name='Close Prices',
    marker=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data[f'SMA_{w1}'],
    mode='lines',
    name=f'SMA_{w1}',
    line=dict(color='red')
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data[f'SMA_{w2}'],
    mode='lines',
    name=f'SMA_{w2}',
    line=dict(color='yellow')
))

fig.update_layout(
    title=f'{ticker} Closing Prices and SMA_{w1},SMA_{w2}',
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Legend',
    hovermode='x unified'
)
fig.show()