import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math
csv = input('Enter Average File name: ')
df = pd.read_csv(f'{csv}.csv')
df.info()
#defining signals
buy_signal = df[df['Signal'] == 'Buy']
sell_signal = df[df['Signal'] == 'Sell']

res = []
processed_short_sells = set()  # To track processed Short Sell signals
last_buy_signal = None  # To keep track of the last Buy signal for Buy - Sell
for i in range(1, len(df)):
    current_signal = df['Signal'].iloc[i]
    previous_totalcash = df.iloc[i - 1]['Total Cash'] if i > 0 else 0

    # Short Sell Signal to Buy Signal (Can be repeated)
    if current_signal == 'Buy':
        short_sell_signal = None
        for j in range(i):  # Iterate up to the current row to find a Short Sell
            if df['Signal'].iloc[j] == 'Sell' and df['Date'].iloc[j] not in processed_short_sells:
                short_sell_signal = df.iloc[j]
                processed_short_sells.add(df['Date'].iloc[j])
                break

        if short_sell_signal is not None:
            # Correcting the end total cash to reflect the current Buy signal execution
            end_total_cash = df['Total Cash'].iloc[i]
            start_total_cash = short_sell_signal['Total Cash']
            total_cash_difference = (end_total_cash - start_total_cash)
            total_cash_difference_percentage = ((end_total_cash - start_total_cash)/start_total_cash)*100
            if total_cash_difference_percentage > 0:
                remark = 'Positive'
            elif total_cash_difference_percentage < 0:
                remark = 'Negative'

            res.append({
                'Signal': 'Sell - Buy',
                'Start Date': short_sell_signal['Date'],
                'Start Close Price': short_sell_signal['Close Price'],
                'End Date': df['Date'].iloc[i],
                'End Close Price': df['Close Price'].iloc[i],
                'Start Total Cash': start_total_cash,
                'End Total Cash': end_total_cash,
                'Total Cash Difference': total_cash_difference,
                '% Difference':total_cash_difference_percentage,
                'Remark':remark
            })

    # Buy Signal to Sell Signal (Can be repeated)
    elif current_signal == 'Sell':
        if last_buy_signal is not None:
            mask = (df['Date'] >= last_buy_signal['Date']) & (df['Date'] < df['Date'].iloc[i])
            investments_in_span = df.loc[mask, 'Investment']

            if not investments_in_span.empty:
                start_total_cash = last_buy_signal['Total Cash']
                end_total_cash = previous_totalcash
                total_cash_difference = (end_total_cash - start_total_cash)
                total_cash_difference_percentage = ((end_total_cash - start_total_cash)/start_total_cash)*100
                if total_cash_difference_percentage > 0:
                    remark = 'Positive'
                elif total_cash_difference_percentage < 0:
                    remark = 'Negative'
                res.append({
                    'Signal': 'Buy - Sell',
                    'Start Date': last_buy_signal['Date'],
                    'Start Close Price': last_buy_signal['Close Price'],
                    'End Date': df['Date'].iloc[i],
                    'End Close Price': df['Close Price'].iloc[i],
                    'Start Total Cash': start_total_cash,
                    'End Total Cash': end_total_cash,
                    'Total Cash Difference': total_cash_difference,
                    '% Difference':total_cash_difference_percentage,
                    'Remark':remark
                })

    # Update the last buy signal
    if current_signal == 'Buy':
        last_buy_signal = df.iloc[i]

# Convert the results to a DataFrame
output = pd.DataFrame(res)

otptdf = input('Enter name of file which has to be store: ')
otpt = otptdf + '.csv'
output.to_csv(otpt, index=False)
print(f" DataFrame saved successfully as {otpt}.")