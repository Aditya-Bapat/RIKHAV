import yfinance as yf
import pandas as pd
import plotly.graph_objects as go

# Download historical data for the specified ticker
ticker = 'TCS.NS'
start_date = '2023-01-01'
end_date = '2024-01-06'
data = yf.download(ticker, start=start_date, end=end_date)
data = data[['Close']]
data.index.name = 'Date'

# Step 2: Apply the trading strategy with SMA indicators
sma_periods = range(10, 51)
initial_allocation = 100000
results = []

for sma1_period in sma_periods:
    for sma2_period in sma_periods:
        if sma1_period != sma2_period:
            investment = 0
            holding = 'Initial_Investment'
            signal_list1 = []
            buy_price = None
            shares_bought = 0
            remaining_cash = initial_allocation  # Initialize remaining cash
            total_cash = initial_allocation  # Initialize total cash
            data[f'SMA_{sma1_period}'] = data['Close'].rolling(window=sma1_period).mean()
            data[f'SMA_{sma2_period}'] = data['Close'].rolling(window=sma2_period).mean()

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
                    # SMA2 < SMA1 then sell
                    if data[f'SMA_{sma2_period}'].iloc[i] > data[f'SMA_{sma1_period}'].iloc[i] and data[f'SMA_{sma2_period}'].iloc[i - 1] <= data[f'SMA_{sma1_period}'].iloc[i - 1]:
                        if holding == 'buy':
                            sell_price = close_price
                            profit = (sell_price - buy_price) * shares_bought
                            remaining_cash += sell_price * shares_bought  # Update remaining cash with value of sold shares
                            investment = 0  # Reset investment after selling
                            shares_bought = 0  # Reset shares bought after selling
                            total_cash = remaining_cash
                            holding = 'sell'
                            buy_price = None
                            signal_list1.append({
                                'Signal': 'Sell',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Profit/Loss': profit,
                                'Investment': investment,
                                'Shares Bought': shares_bought,
                                'Percentage Change': percentage_change,
                                'Hold Status': 'Profit Hold' if profit > 0 else 'Loss Hold',
                                'Remaining Cash': remaining_cash,
                                'Total Cash': total_cash
                            })
                        else:
                            signal_list1.append({
                                'Signal': 'Sell',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Profit/Loss': 0.0,  # Default value when not holding
                                'Investment': investment,
                                'Shares Bought': round(total_cash/close_price),
                                'Percentage Change': percentage_change,
                                'Hold Status': 'No Hold',
                                'Remaining Cash': remaining_cash,
                                'Total Cash': total_cash
                            })
                    # SMA2 > SMA1 then buy
                    elif data[f'SMA_{sma2_period}'].iloc[i] < data[f'SMA_{sma1_period}'].iloc[i] and data[f'SMA_{sma2_period}'].iloc[i - 1] >= data[f'SMA_{sma1_period}'].iloc[i - 1]:
                        if holding in ['sell', 'Initial_Investment']:
                            buy_price = close_price
                            shares_bought = round(remaining_cash / buy_price)
                            investment = shares_bought * buy_price
                            remaining_cash -= investment  # Update remaining cash
                            profit = None
                            total_cash = remaining_cash + investment
                            signal_list1.append({
                                'Signal': 'Buy',
                                'Date': data.index[i],
                                'Close Price': close_price,
                                'Profit/Loss': 0.0,  # Default value for buy
                                'Investment': investment,
                                'Shares Bought': shares_bought,
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
                            'Profit/Loss': 0.0,  # Default value for hold
                            'Investment': investment,
                            'Shares Bought': shares_bought,
                            'Percentage Change': percentage_change,
                            'Hold Status': hold_status,
                            'Remaining Cash': remaining_cash,
                            'Total Cash': total_cash
                        })

            # Process buy-sell spans
            buy_sell_spans = []
            current_span = []
            for signal in signal_list1:
                if signal['Signal'] == 'Buy':
                    current_span = [signal]
                elif signal['Signal'] == 'Sell' and current_span:
                    current_span.append(signal)
                    buy_sell_spans.append(current_span)
                    current_span = []

            for span in buy_sell_spans:
                if len(span) == 2:  # Only consider valid buy-sell pairs
                    buy_signal = span[0]
                    sell_signal = span[1]
                    profit_loss = sell_signal['Profit/Loss']
                    sell_signal['Profit/Loss'] = profit_loss
                  
            # Process sell-buy spans
            sell_buy_spans = []
            current_span = []
            for signal in signal_list1:
                if signal['Signal'] == 'Sell':
                    current_span = [signal]
                elif signal['Signal'] == 'Buy' and current_span:
                    current_span.append(signal)
                    sell_buy_spans.append(current_span)
                    current_span = []

            for span in sell_buy_spans:
                if len(span) == 2:  # Only consider valid sell-buy pairs
                    sell_signal = span[0]
                    buy_signal = span[1]
                    profit_loss = sell_signal['Profit/Loss']
                    buy_signal['Profit/Loss'] = profit_loss

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

# Save signals of the best combination to CSV
best_signals_df = pd.DataFrame(best_result['Signals'])
best_signals_df['SMA1'] = best_result['SMA1']
best_signals_df['SMA2'] = best_result['SMA2']

csv_path = 'C:/Users/Administrator/Desktop/Aditya_Bapat/TCS_best_signals_sellbuy2.csv'
best_signals_df.to_csv(csv_path, index=False)
print(f"Data saved to {csv_path}")

# Plot the closing prices and SMAs using Plotly
fig = go.Figure()
fig.add_trace(go.Scatter(
    x=data.index,
    y=data['Close'],
    mode='lines',
    name='Close',
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

# Add Buy and Sell signals to the plot
buy_signals = best_signals_df[best_signals_df['Signal'] == 'Buy']
sell_signals = best_signals_df[best_signals_df['Signal'] == 'Sell']

fig.add_trace(go.Scatter(
    x=buy_signals['Date'],
    y=buy_signals['Close Price'],
    mode='markers',
    name='Buy',
    marker=dict(color='green', symbol='triangle-up', size=10)
))

fig.add_trace(go.Scatter(
    x=sell_signals['Date'],
    y=sell_signals['Close Price'],
    mode='markers',
    name='Sell',
    marker=dict(color='red', symbol='triangle-down', size=10)
))

fig.update_layout(
    title=f'TCS Closing Prices and SMAs ({best_result["SMA1"]} Period and {best_result["SMA2"]} Period)',
    xaxis_title='Date',
    yaxis_title='Price',
    legend_title='Legend',
    hovermode='x unified'
)
fig.show()