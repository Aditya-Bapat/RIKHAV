import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import random

# Define the stock ticker and date range
ticker = 'TCS.NS'
start_date = '2023-01-01'
end_date = '2024-01-06'

# Download the historical data
data = yf.download(ticker, start=start_date, end=end_date)

# Use the 'Close' prices from the data
data = data[['Close']]
data.index.name = 'Date'

# Step 2: Apply the trading strategy with SMA indicators
sma_periods = range(10, 51)
initial_allocation = 100000
results = []

# Calculate SMA columns
for sma_period in sma_periods:
    data[f'SMA_{sma_period}'] = data['Close'].rolling(window=sma_period).mean()

for sma1_period in sma_periods:
    for sma2_period in sma_periods:
        if sma1_period != sma2_period:
            # Initialize variables
            investment = 0
            holding = 'Initial_Investment'
            buy_price = None
            shares_bought = 0
            remaining_cash = initial_allocation
            total_cash = initial_allocation
            purchase_records = []  # List to keep track of each purchase
            signal_list1 = []  # Initialize signal_list1

            # Iterate over data
            for i in range(len(data)):
                close_price = data['Close'].iloc[i]
                percentage_change = 0.0

                if i > 0:
                    previous_close_price = data['Close'].iloc[i - 1]
                    percentage_change = ((close_price - previous_close_price) / previous_close_price) * 100
                    total_cash = remaining_cash + investment

                if i == 0:
                    signal_list1.append({
                        'Signal': 'Initial_Investment',
                        'Date': data.index[i],
                        'Close Price': close_price,
                        'Profit/Loss': 0.0,
                        'Investment': investment,
                        'Shares Bought': shares_bought,
                        'Percentage Change': percentage_change,
                        'Hold Status': 'Initial_Investment',
                        'Remaining Cash': remaining_cash,
                        'Total Cash': total_cash
                    })
                else:
                    # Selling logic
                    if data[f'SMA_{sma2_period}'].iloc[i] > data[f'SMA_{sma1_period}'].iloc[i] and data[f'SMA_{sma2_period}'].iloc[i - 1] <= data[f'SMA_{sma1_period}'].iloc[i - 1]:
                        if holding == 'buy':
                            sell_price = close_price
                            # Sell shares from purchase records
                            shares_to_sell = shares_bought
                            total_profit = 0
                            while shares_to_sell > 0 and purchase_records:
                                purchase = purchase_records.pop(0)
                                if purchase['quantity'] <= shares_to_sell:
                                    total_profit += purchase['quantity'] * (sell_price - purchase['price'])
                                    shares_to_sell -= purchase['quantity']
                                else:
                                    total_profit += shares_to_sell * (sell_price - purchase['price'])
                                    purchase['quantity'] -= shares_to_sell
                                    shares_to_sell = 0
                            remaining_cash += shares_bought * sell_price
                            current_value = remaining_cash + total_profit
                            investment = current_value
                            shares_bought = round(remaining_cash / buy_price)
                            total_cash = remaining_cash
                            signal_list1.append({
                                'Signal': 'Sell',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Profit/Loss': total_profit,
                                'Investment': investment,
                                'Shares Bought': shares_bought,
                                'Percentage Change': percentage_change,
                                'Hold Status': 'Profit Hold' if total_profit > 0 else 'Loss Hold',
                                'Remaining Cash': remaining_cash,
                                'Total Cash': total_cash
                            })
                            holding = 'sell'
                            buy_price = None
                        else:
                            signal_list1.append({
                                'Signal': 'Sell',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Investment': investment,
                                'Shares Bought': shares_bought,
                                'Percentage Change': percentage_change,
                                'Hold Status': 'No Hold',
                                'Remaining Cash': remaining_cash,
                                'Total Cash': total_cash
                            })

                    # Buying logic
                    elif data[f'SMA_{sma2_period}'].iloc[i] < data[f'SMA_{sma1_period}'].iloc[i] and data[f'SMA_{sma2_period}'].iloc[i - 1] >= data[f'SMA_{sma1_period}'].iloc[i - 1]:
                        if holding in ['sell', 'Initial_Investment']:
                            buy_price = close_price
                            shares_to_buy = round(remaining_cash / buy_price)
                            purchase_records.append({'price': buy_price, 'quantity': shares_to_buy})
                            remaining_cash -= shares_to_buy * buy_price
                            investment = sum(purchase['quantity'] * purchase['price'] for purchase in purchase_records)
                            shares_bought = shares_to_buy  # Update shares_bought after buying
                            total_cash = remaining_cash + investment
                            signal_list1.append({
                                'Signal': 'Buy',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Profit/Loss': 0.0,
                                'Investment': investment,
                                'Shares Bought': shares_to_buy,
                                'Percentage Change': percentage_change,
                                'Hold Status': '',
                                'Remaining Cash': remaining_cash,
                                'Total Cash': total_cash
                            })
                            holding = 'buy'
                    else:
                        if holding == 'buy':
                            current_value = shares_bought * close_price
                            hold_status = 'Profit Hold' if current_value > initial_allocation else 'Loss Hold'
                            investment = current_value
                        else:
                            hold_status = 'No Hold'

                        total_cash = remaining_cash + investment
                        signal_list1.append({
                            'Signal': 'Hold',
                            'Date': data.index[i],
                            'Close Price': close_price,
                            'Investment': investment,
                            'Shares Bought': shares_bought,
                            'Percentage Change': percentage_change,
                            'Hold Status': hold_status,
                            'Remaining Cash': remaining_cash,
                            'Total Cash': total_cash
                        })

            # Track Sell-Buy Spans
            sell_buy_spans = []
            current_span = []
            for signal in signal_list1:
                if signal['Signal'] == 'Sell':
                    current_span = [signal]
                elif signal['Signal'] == 'Buy' and current_span:
                    current_span.append(signal)
                    sell_buy_spans.append(current_span)
                    current_span = []

            if current_span:
                current_span.append({
                    'Signal': 'Hold',
                    'Date': data.index[-1],
                    'Close Price': data['Close'].iloc[-1],
                    'Profit/Loss': 0.0,
                    'Investment': total_cash/close_price,
                    'Shares Bought': shares_bought,
                    'Percentage Change': 0.0,
                    'Hold Status': 'No Hold',
                    'Remaining Cash': remaining_cash,
                    'Total Cash': total_cash
                })
                sell_buy_spans.append(current_span)

            # Process sell-buy spans and calculate profit/loss
            for span in sell_buy_spans:
                if len(span) == 2:  # Only consider valid sell-buy pairs
                    sell_signal = span[0]
                    buy_signal = span[-1]
                    span_duration = (buy_signal['Date'] - sell_signal['Date']).days
                    profit_loss = buy_signal['Total Cash'] - sell_signal['Total Cash']
                    span_result = {
                        'Sell Date': sell_signal['Date'],
                        'Buy Date': buy_signal['Date'],
                        'Span Duration (days)': span_duration,
                        'Profit/Loss': profit_loss,
                        'Investment': sell_signal['Investment'],
                        'Final Cash': buy_signal['Total Cash'],
                        'Percentage Change': ((buy_signal['Total Cash'] - sell_signal['Total Cash']) / sell_signal['Total Cash']) * 100
                    }

            results.append({
                'SMA1': sma1_period,
                'SMA2': sma2_period,
                'Final Value': total_cash,
                'Percentage Difference': ((total_cash - initial_allocation) / initial_allocation) * 100,
                'Signals': signal_list1.copy()
            })

best_result = max(results, key=lambda x: x['Final Value'])
print(f"Best SMA Combination:")
print(f"SMA1: {best_result['SMA1']}")
print(f"SMA2: {best_result['SMA2']}")
print(f"Final Value: {best_result['Final Value']:.2f} INR")
print(f"Percentage Difference: {best_result['Percentage Difference']:.2f}%")

best_signals_df = pd.DataFrame(best_result['Signals'])
best_signals_df['SMA1'] = best_result['SMA1']
best_signals_df['SMA2'] = best_result['SMA2']

csv_path = 'C:/Users/Administrator/Desktop/Aditya_Bapat/TCS_best_signals_sellbuy1.csv'
best_signals_df.to_csv(csv_path, index=False)
print(f"Best signals saved to {csv_path}")

# Plotting
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    mode='lines',
    name='Close Prices',
    marker=dict(color='blue')
))

best_sma1 = f'SMA_{best_result["SMA1"]}'
best_sma2 = f'SMA_{best_result["SMA2"]}'

fig.add_trace(go.Scatter(
    x=data.index,
    y=data[best_sma1],
    mode='lines',
    name=f'SMA {best_result["SMA1"]} Period',
    line=dict(color='red', width=2)
))

fig.add_trace(go.Scatter(
    x=data.index,
    y=data[best_sma2],
    mode='lines',
    name=f'SMA {best_result["SMA2"]} Period',
    line=dict(color='yellow', width=2)
))

fig.update_layout(
    title=f'TCS Closing Prices and SMAs ({best_result["SMA1"]} Period and {best_result["SMA2"]} Period)',
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Legend',
    hovermode='x unified'
)
fig.show()