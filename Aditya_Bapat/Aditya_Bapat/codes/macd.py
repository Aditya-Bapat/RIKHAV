import pandas as pd
import matplotlib.pyplot as plt
import plotly.graph_objects as go
import math 
import yfinance as yf

ticker = input('Enter Ticker: ')

start_day = int(input('Starting Day: '))
start_month = int(input('Starting Month: '))
start_Year = int(input('Starting Year: '))
start_date = f'{start_Year}-{start_month}-{start_day}'

end_day = int(input('End Day: '))
end_month = int(input('End Month: '))
end_Year = int(input('End Year: '))

end_date = f'{end_Year}-{end_month}-{end_day}'
df = yf.download(ticker, start=start_date, end=end_date, interval='1h')

# path = input('Enter File whose MACD has to be found out: ')
# df = pd.read_csv(f'{path}.csv')

df.info()

df['Short_Term_Avg'] = df['Close'].ewm(span = 12, adjust=False).mean()
df['Long_Term_Avg'] = df['Close'].ewm(span=26,adjust=False).mean()

df['MACD_Line'] = df['Short_Term_Avg'] - df['Long_Term_Avg']

df['Signal_Line'] = df['MACD_Line'].ewm(span=9, adjust=False).mean()

df['MACD_Histogram'] = df['MACD_Line'] - df['Signal_Line']

fig = go.Figure()

# MACD Line
fig.add_trace(go.Scatter(x=df.index, y=df['MACD_Line'], mode='lines', name='MACD Line', line=dict(color='blue')))

# Signal Line
fig.add_trace(go.Scatter(x=df.index, y=df['Signal_Line'], mode='lines', name='Signal Line', line=dict(color='red')))

# MACD Histogram
fig.add_trace(go.Bar(x=df.index, y=df['MACD_Histogram'], name='MACD Histogram', marker_color='grey'))

# Update layout for better interactivity
fig.update_layout(
    title='MACD Chart',
    xaxis_title='Date',
    yaxis_title='Value',
    barmode='overlay',
)

# Show plot
fig.show()

macd_line = df['MACD_Line']
signal_line = df['Signal_Line']

initial_allocation = 100000
holding = None
signal_list2 = []

# Initial state
signal_list2.append({
    'Signal': 'Initial',
    'Date': df.index[0],
    'Close Price': df['Close'].iloc[0],
    'Shares Bought': 0,
    'Profit/Loss': 0,
    'Investment': 0,
    'Remaining Cash': initial_allocation,
    'Hold': "None",
    'Total Cash': initial_allocation,
})

for i in range(1, len(df)):
    close_price = df['Close'].iloc[i]
    prev_signal = signal_list2[-1]
    buy_signal = (macd_line.iloc[i] > signal_line.iloc[i]) and \
                 (macd_line.iloc[i - 1] <= signal_line.iloc[i - 1])
    sell_signal = (macd_line.iloc[i] < signal_line.iloc[i]) and \
                  (macd_line.iloc[i - 1] >= signal_line.iloc[i - 1])

    # Record daily state before any signal
    if holding is None and not (buy_signal or sell_signal):
        signal_list2.append({
            'Signal': 'No Signal',
            'Date': df.index[i],
            'Close Price': close_price,
            'Shares Bought': 0,
            'Profit/Loss': 0,
            'Investment': 0,
            'Remaining Cash': prev_signal['Remaining Cash'],
            'Hold': "None",
            'Total Cash': prev_signal['Total Cash']
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
            'Date': df.index[i],
            'Close Price': close_price,
            'Shares Bought': shares_bought,
            'Profit/Loss': 0,
            'Investment': investment,
            'Remaining Cash': remaining_cash,
            'Hold': "Buy",
            'Total Cash': total_cash
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
                'Date': df.index[i],
                'Close Price': close_price,
                'Profit/Loss': profit,
                'Investment': investment,
                'Shares Bought': sb,
                'Remaining Cash': rem,
                'Hold': "Buy Hold",
                'Total Cash': total_cash,
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
            'Date': df.index[i],
            'Close Price': close_price,
            'Profit/Loss': profit,
            'Investment': investment,
            'Shares Bought': sb,
            'Remaining Cash': remaining_cash,
            'Hold': "Sell Hold",
            'Total Cash': total_cash,
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
                'Date': df.index[i],
                'Close Price': close_price,
                'Profit/Loss': profit,
                'Investment': investment,
                'Shares Bought': shares_bought,
                'Remaining Cash': rem,
                'Hold': "Sell Hold",
                'Total Cash': total_cash
            })

results_df = pd.DataFrame(signal_list2)

results_df

csv_path = input('Save file by unique Name: ')
csv = csv_path + '.csv'
results_df.to_csv(csv, index=False)
print(f"DataFrame saved successfully as {csv}.")