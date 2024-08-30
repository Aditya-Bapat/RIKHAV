# import yfinance as yf
# import numpy as np
# import pandas as pd

# # User input
# ticker = input('Enter Ticker: ')

# start_day = int(input('Starting Day: '))
# start_month = int(input('Starting Month: '))
# start_Year = int(input('Starting Year: '))
# start_date = f'{start_Year}-{start_month:02d}-{start_day:02d}'

# end_day = int(input('End Day: '))
# end_month = int(input('End Month: '))
# end_Year = int(input('End Year: '))
# end_date = f'{end_Year}-{end_month:02d}-{end_day:02d}'

# initial_allocation = float(input('Give Investment Amount: '))

# # Download data
# data = yf.download(ticker, start=start_date, end=end_date, interval='1h')

# # Initialize variables
# best_sma1 = None
# best_sma2 = None
# max_return = -np.inf  # Initialize with a very low value
# sma_periods = range(10, 51)

# # Function to calculate returns
# def calculate_returns(data, sma1_period, sma2_period):
#     data['SMA1'] = data['Close'].rolling(window=sma1_period).mean()
#     data['SMA2'] = data['Close'].rolling(window=sma2_period).mean()

#     # Trading signals
#     data['Signal'] = 0
#     data['Signal'][sma1_period:] = np.where(data['SMA1'][sma1_period:] > data['SMA2'][sma1_period:], 1, 0)
#     data['Position'] = data['Signal'].diff()

#     # Calculate returns
#     data['Returns'] = data['Close'].pct_change().shift(-1)
#     data['Strategy'] = data['Returns'] * data['Signal']
    
#     # Total return of strategy
#     total_return = (1 + data['Strategy'].sum()) * initial_allocation
    
#     return total_return

# # Iterate through all combinations of SMA1 and SMA2
# for sma1 in sma_periods:
#     for sma2 in sma_periods:
#         if sma1 != sma2:
#             current_return = calculate_returns(data, sma1, sma2)
#             if current_return > max_return:
#                 max_return = current_return
#                 best_sma1 = sma1
#                 best_sma2 = sma2

# print(f'Best SMA1: {best_sma1}')
# print(f'Best SMA2: {best_sma2}')
# print(f'Maximum Return: INR{max_return}')

# initial_allocation = 100000
# holding = None
# signal_list2 = []

# # Initial state
# signal_list2.append({
#     'Signal': 'Initial',
#     'Date': data.index[0],
#     'Close Price': data['Close'].iloc[0],
#     'Shares Bought': 0,
#     'Profit/Loss': 0,
#     'Investment': 0,
#     'Remaining Cash': initial_allocation,
#     'Hold': "None",
#     'Total Cash': initial_allocation,
#     'SMA1': w1,
#     'SMA2': w2
# })

# for i in range(1, len(data)):
#     close_price = data['Close'].iloc[i]
#     prev_signal = signal_list2[-1]
#     buy_signal = (data[f'SMA_{w2}'].iloc[i] > data[f'SMA_{w1}'].iloc[i]) and \
#                  (data[f'SMA_{w2}'].iloc[i - 1] <= data[f'SMA_{w1}'].iloc[i - 1])
#     sell_signal = (data[f'SMA_{w2}'].iloc[i] < data[f'SMA_{w1}'].iloc[i]) and \
#                   (data[f'SMA_{w2}'].iloc[i - 1] >= data[f'SMA_{w1}'].iloc[i - 1])

#     # Record daily state before any signal
#     if holding is None and not (buy_signal or sell_signal):
#         signal_list2.append({
#             'Signal': 'No Signal',
#             'Date': data.index[i],
#             'Close Price': close_price,
#             'Shares Bought': 0,
#             'Profit/Loss': 0,
#             'Investment': 0,
#             'Remaining Cash': prev_signal['Remaining Cash'],
#             'Hold': "None",
#             'Total Cash': prev_signal['Total Cash'],
#             'SMA1': w1,
#             'SMA2': w2
#         })

#     # Buy Signal
#     if buy_signal:
#       prev_total_cash = signal_list2[-1]['Total Cash']
#       shares_bought = math.floor(prev_total_cash / close_price)
#       investment = shares_bought * close_price
#       remaining_cash = prev_total_cash - investment
#       profit = investment - prev_signal['Investment']
#       if prev_signal['Investment'] == 0:
#         profit = 0
#         total_cash = prev_total_cash
#       else:
#         total_cash = prev_total_cash + profit

#       signal_list2.append({
#             'Signal': 'Buy',
#             'Date': data.index[i],
#             'Close Price': close_price,
#             'Shares Bought': shares_bought,
#             'Profit/Loss': 0,
#             'Investment': investment,
#             'Remaining Cash': remaining_cash,
#             'Hold': "Buy",
#             'Total Cash': total_cash,
#             'SMA1': w1,
#             'SMA2': w2
#         })
#       holding = 'buy'

#     # Buy Hold
#     if holding == 'buy':
#         buy_signal_sb = next((s for s in reversed(signal_list2) if s['Signal'] == 'Buy'), None)
#         if buy_signal_sb:
#             sb = buy_signal_sb['Shares Bought']
#             investment = sb * close_price
#             profit = investment - signal_list2[-1]['Investment']
#             rem = signal_list2[-1]['Remaining Cash']
#             total_cash = signal_list2[-1]['Total Cash'] + profit
#             signal_list2.append({
#                 'Signal': 'Buy Hold',
#                 'Date': data.index[i],
#                 'Close Price': close_price,
#                 'Profit/Loss': profit,
#                 'Investment': investment,
#                 'Shares Bought': sb,
#                 'Remaining Cash': rem,
#                 'Hold': "Buy Hold",
#                 'Total Cash': total_cash,
#                 'SMA1': w1,
#                 'SMA2': w2
#             })

#     # Sell Signal
#     if sell_signal:
#         sb = 0
#         investment = 0
#         profit = 0
#         total_cash = prev_signal['Total Cash']
#         remaining_cash = prev_signal['Remaining Cash']

#         signal_list2.append({
#             'Signal': 'Sell',
#             'Date': data.index[i],
#             'Close Price': close_price,
#             'Profit/Loss': profit,
#             'Investment': investment,
#             'Shares Bought': sb,
#             'Remaining Cash': remaining_cash,
#             'Hold': "Sell Hold",
#             'Total Cash': total_cash,
#             'SMA1': w1,
#             'SMA2': w2
#         })
#         holding = 'sell'

#     # Short Sell
#     if holding == 'sell':
#             shares_bought = math.floor((signal_list2[-1]['Total Cash'])/close_price)
#             investment = shares_bought * close_price
#             prev_investment = signal_list2[-1]['Investment']
#             if prev_investment == 0:
#                 profit = 0
#             else:
#                 profit = investment - prev_investment
#             rem = signal_list2[-1]['Total Cash']-investment
#             total_cash = signal_list2[-1]['Total Cash'] + profit
#             if total_cash < 0:
#                 total_cash = abs(total_cash)
#             signal_list2.append({
#                 'Signal': 'Short Sell',
#                 'Date': data.index[i],
#                 'Close Price': close_price,
#                 'Profit/Loss': profit,
#                 'Investment': investment,
#                 'Shares Bought': shares_bought,
#                 'Remaining Cash': rem,
#                 'Hold': "Sell Hold",
#                 'Total Cash': total_cash,
#                 'SMA1': w1,
#                 'SMA2': w2
#             })

# results_df = pd.DataFrame(signal_list2)

# results_df

# csv_path = input('Save file by unique Name: ')
# csv = csv_path + '.csv'
# results_df.to_csv(csv, index=False)
# print(f"DataFrame saved successfully as {csv}.")

# #Interactive Scatter plot with plotly
# fig = go.Figure()

# fig.add_trace(go.Scatter(
#     x=data.index,
#     y=data['Close'],
#     mode='lines',
#     name='Close Prices',
#     marker=dict(color='blue')
# ))

# fig.add_trace(go.Scatter(
#     x=data.index,
#     y=data[f'SMA_{w1}'],
#     mode='lines',
#     name=f'SMA_{w1}',
#     line=dict(color='red')
# ))

# fig.add_trace(go.Scatter(
#     x=data.index,
#     y=data[f'SMA_{w2}'],
#     mode='lines',
#     name=f'SMA_{w2}',
#     line=dict(color='yellow')
# ))

# fig.update_layout(
#     title=f'{ticker} Closing Prices and SMA_{w1},SMA_{w2}',
#     xaxis_title='Date',
#     yaxis_title='Price',
#     legend_title='Legend',
#     hovermode='x unified'
# )
# fig.show()
import yfinance as yf
import numpy as np
import pandas as pd
import math
import plotly.graph_objects as go

# User input
ticker = input('Enter Ticker: ')

start_day = int(input('Starting Day: '))
start_month = int(input('Starting Month: '))
start_Year = int(input('Starting Year: '))
start_date = f'{start_Year}-{start_month:02d}-{start_day:02d}'

end_day = int(input('End Day: '))
end_month = int(input('End Month: '))
end_Year = int(input('End Year: '))
end_date = f'{end_Year}-{end_month:02d}-{end_day:02d}'

initial_allocation = float(input('Give Investment Amount: '))

# Download data
data = yf.download(ticker, start=start_date, end=end_date, interval='1h')

# Initialize variables
best_sma1 = None
best_sma2 = None
max_return = -np.inf  # Initialize with a very low value
sma_periods = range(10, 51)

# Function to calculate returns
def calculate_returns(data, sma1_period, sma2_period):
    data['SMA1'] = data['Close'].rolling(window=sma1_period).mean()
    data['SMA2'] = data['Close'].rolling(window=sma2_period).mean()

    # Trading signals
    data['Signal'] = 0
    data['Signal'][sma1_period:] = np.where(data['SMA1'][sma1_period:] > data['SMA2'][sma1_period:], 1, 0)
    data['Position'] = data['Signal'].diff()

    # Calculate returns
    data['Returns'] = data['Close'].pct_change().shift(-1)
    data['Strategy'] = data['Returns'] * data['Signal']
    
    # Total return of strategy
    total_return = (1 + data['Strategy'].sum()) * initial_allocation
    
    return total_return

# Iterate through all combinations of SMA1 and SMA2
for sma1 in sma_periods:
    for sma2 in sma_periods:
        if sma1 != sma2:
            current_return = calculate_returns(data, sma1, sma2)
            if current_return > max_return:
                max_return = current_return
                best_sma1 = sma1
                best_sma2 = sma2

print(f'Best SMA1: {best_sma1}')
print(f'Best SMA2: {best_sma2}')
print(f'Maximum Return: INR{max_return}')

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
    'SMA1': best_sma1,
    'SMA2': best_sma2
})

for i in range(1, len(data)):
    close_price = data['Close'].iloc[i]
    prev_signal = signal_list2[-1]
    buy_signal = (data['SMA2'].iloc[i] > data['SMA1'].iloc[i]) and \
                 (data['SMA2'].iloc[i - 1] <= data['SMA1'].iloc[i - 1])
    sell_signal = (data['SMA2'].iloc[i] < data['SMA1'].iloc[i]) and \
                  (data['SMA2'].iloc[i - 1] >= data['SMA1'].iloc[i - 1])

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
            'SMA1': best_sma1,
            'SMA2': best_sma2
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
            'SMA1': best_sma1,
            'SMA2': best_sma2
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
                'SMA1': best_sma1,
                'SMA2': best_sma2
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
            'SMA1': best_sma1,
            'SMA2': best_sma2
        })
        holding = 'sell'

    # Short Sell
    if holding == 'sell':
        shares_bought = math.floor((signal_list2[-1]['Total Cash']) / close_price)
        investment = shares_bought * close_price
        prev_investment = signal_list2[-1]['Investment']
        if prev_investment == 0:
            profit = 0
        else:
            profit = investment - prev_investment
        rem = signal_list2[-1]['Total Cash'] - investment
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
            'SMA1': best_sma1,
            'SMA2': best_sma2
        })

results_df = pd.DataFrame(signal_list2)

# Save results to CSV
csv_path = input('Save file by unique Name: ')
csv = csv_path + '.csv'
results_df.to_csv(csv, index=False)
print(f"DataFrame saved successfully as {csv}.")

# Interactive Scatter plot with Plotly
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
    y=data['SMA1'],
    mode='lines',
    name=f'SMA {best_sma1}',
    line=dict(color='red')
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data['SMA2'],
    mode='lines',
    name=f'SMA {best_sma2}',
    line=dict(color='yellow')
))

fig.update_layout(
    title=f'{ticker} Closing Prices and SMAs {best_sma1}, {best_sma2}',
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Legend',
    hovermode='x unified'
)
fig.show()
