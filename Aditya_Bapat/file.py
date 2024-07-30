import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np

ticker = 'TCS.NS'
start_date = '2023-01-01'
end_date = '2024-06-30'
data = yf.download(ticker, start=start_date, end=end_date, interval='1h')
# Function to calculate performance for given SMA values
def calculate_performance(sma1_period, sma2_period, data, initial_allocation=100000):
    sma1 = f"SMA_{sma1_period}"
    sma2 = f"SMA_{sma2_period}"

    data[sma1] = data['Close'].rolling(window=sma1_period).mean()
    data[sma2] = data['Close'].rolling(window=sma2_period).mean()

    investment = initial_allocation
    holding = None
    buy_price = None
    shares_bought = 0
    signal_list1 = []

    for i in range(len(data)):
        close_price = data['Close'].iloc[i]
        percentage_change = 0.0

        if i > 0:
            previous_close_price = data['Close'].iloc[i-1]
            percentage_change = ((close_price - previous_close_price) / previous_close_price) * 100

        if i == 0:
            buy_price = close_price
            shares_bought = investment / buy_price
            holding = 'buy'
            signal_list1.append({
                'Signal': 'Buy',
                'Date': data.index[i],
                'Close Price': close_price,
                'Profit/Loss': 0.0,
                'Investment': investment,
                'Shares Bought': shares_bought,
                'Percentage Change': percentage_change,
                'Hold Status': ''
            })
        else:
            if data[sma2].iloc[i] > data[sma1].iloc[i] and data[sma2].iloc[i-1] <= data[sma1].iloc[i-1]:
                if holding == 'buy':
                    sell_price = close_price
                    profit = (sell_price - buy_price) * shares_bought
                    investment += profit
                    signal_list1.append({
                        'Signal': 'Sell',
                        'Date': data.index[i],
                        'Close Price': close_price,
                        'Profit/Loss': profit,
                        'Investment': investment,
                        'Shares Bought': 0,
                        'Percentage Change': percentage_change,
                        'Hold Status': 'Profit Hold' if profit > 0 else 'Loss Hold'
                    })

                    holding = 'sell'
                    shares_bought = 0
                    buy_price = None
                else:
                    signal_list1.append({
                        'Signal': 'Sell',
                        'Date': data.index[i],
                        'Close Price': close_price,
                        'Investment': investment,
                        'Shares Bought': 0,
                        'Percentage Change': percentage_change,
                        'Hold Status': 'No Hold'
                    })

            elif data[sma2].iloc[i] < data[sma1].iloc[i] and data[sma2].iloc[i-1] >= data[sma1].iloc[i-1]:
                if holding in ['sell', None]:
                    buy_price = close_price
                    shares_bought = investment / buy_price
                    profit = 0.0
                    signal_list1.append({
                        'Signal': 'Buy',
                        'Date': data.index[i],
                        'Close Price': close_price,
                        'Profit/Loss': profit,
                        'Investment': investment,
                        'Shares Bought': shares_bought,
                        'Percentage Change': percentage_change,
                        'Hold Status': ''
                    })

                    holding = 'buy'
            else:
                if holding == 'buy':
                    current_value = shares_bought * close_price
                    hold_status = 'Profit Hold' if current_value > initial_allocation else 'Loss Hold'
                    investment = current_value
                else:
                    hold_status = 'No Hold'

                signal_list1.append({
                    'Signal': 'Hold',
                    'Date': data.index[i],
                    'Close Price': close_price,
                    'Investment': investment,
                    'Shares Bought': shares_bought,
                    'Percentage Change': percentage_change,
                    'Hold Status': hold_status
                })

    filtered_signals = [signal for signal in signal_list1 if signal['Signal'] in ['Buy', 'Sell']]
    last_signal = filtered_signals[-1]

    if last_signal['Signal'] == 'Buy':
        final_value = last_signal['Shares Bought'] * data['Close'].iloc[-1]
    else:
        final_value = last_signal['Investment']

    percentage_difference = ((final_value - initial_allocation) / initial_allocation) * 100

    return final_value, percentage_difference, sma1, sma2, signal_list1

# Download data
ticker = 'TCS.NS'
start_date = '2023-05-01'
end_date = '2024-06-30'
data = yf.download(ticker, start=start_date, end=end_date)

# Define SMA periods to test
sma_periods = list(range(10, 51, 10))
results = []

# Test all combinations of SMA periods
for sma1_period in sma_periods:
    for sma2_period in sma_periods:
        if sma1_period < sma2_period:  # Ensure sma1 < sma2 to avoid redundancy
            final_value, percentage_difference, sma1, sma2, signal_list1 = calculate_performance(sma1_period, sma2_period, data)
            results.append({
                'SMA1': sma1_period,
                'SMA2': sma2_period,
                'Final Value': final_value,
                'Percentage Difference': percentage_difference,
                'SMA1 Name': sma1,
                'SMA2 Name': sma2,
                'Signals': signal_list1
            })

# Convert results to DataFrame for better visualization
results_df = pd.DataFrame(results)

# Find the best combination based on the highest final value or percentage difference
best_combination = results_df.loc[results_df['Final Value'].idxmax()]
print("Best SMA Combination based on Final Value:")
print(best_combination)

best_combination_percentage = results_df.loc[results_df['Percentage Difference'].idxmax()]
print("Best SMA Combination based on Percentage Difference:")
print(best_combination_percentage)

# Save signals of the best combination to CSV
best_signals_df = pd.DataFrame(best_combination['Signals'])
best_signals_df['SMA1'] = best_combination['SMA1']
best_signals_df['SMA2'] = best_combination['SMA2']
best_signals_df.to_csv('C:/Users/Administrator/Desktop/Aditya_Bapat/TCS_best_signals.csv', index=False)
print("DataFrame saved successfully as TCS_best_signals.csv.")
