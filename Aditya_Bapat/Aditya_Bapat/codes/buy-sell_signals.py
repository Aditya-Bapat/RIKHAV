#Record Buy-Sell, Sell-Buy signal pairs with highest and lowest average percentage 
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math

csv_file = input('Enter Name of CSV file: ')
df = pd.read_csv(f'{csv_file}.csv')
#defining signals
buy_signal = df[df['Signal'] == 'Buy']
sell_signal = df[df['Signal'] == 'Sell']

res = []
processed_short_sells = set()  # To track processed Short Sell signals
last_buy_signal = None  # To keep track of the last Buy signal for Buy - Sell

for i in range(1, len(df)):
    current_signal = df['Signal'].iloc[i]
    previous_investment = df.iloc[i - 1]['Investment'] if i > 0 else 0
    # Short Sell Signal to Buy Signal (Can be repeated)
    if current_signal == 'Buy':
        short_sell_signal = None
        for j in range(i):  # Iterate up to the current row to find a Short Sell
            if df['Signal'].iloc[j] == 'Short Sell' and df['Date'].iloc[j] not in processed_short_sells:
                short_sell_signal = df.iloc[j]
                processed_short_sells.add(df['Date'].iloc[j])
                break

        if short_sell_signal is not None:
            mask = (df['Date'] > short_sell_signal['Date']) & (df['Date'] <= df['Date'].iloc[i])
            investments_in_span = df.loc[mask, 'Investment']

            if not investments_in_span.empty:
                max_investment = investments_in_span.max()

                # Filter out zero values before determining the minimum investment
                filtered_investments = investments_in_span[investments_in_span > 0].sort_values().reset_index(drop=True)
                if not filtered_investments.empty:
                    min_investment = filtered_investments[0]
                else:
                    min_investment = investments_in_span.min()  # Fallback to the original min if no non-zero values

                profit = short_sell_signal['Investment'] - previous_investment
                lowest_percentage = ((min_investment - short_sell_signal['Investment']) / short_sell_signal['Investment']) * 100 * -1

                res.append({
                    'Signal': 'Short Sell - Buy',
                    'Start Close Price': short_sell_signal['Close Price'],
                    'Start Date': short_sell_signal['Date'],
                    'End Close Price': df['Close Price'].iloc[i],
                    'End Date': df['Date'].iloc[i],
                    'Start Investment': short_sell_signal['Investment'],
                    'End Investment': previous_investment,
                    'Profit/Loss': profit,
                    'Highest Investment': max_investment,
                    'Lowest Investment': min_investment,
                    'Highest Percentage': 0,
                    'Lowest Percentage': lowest_percentage
                })

    # Buy Signal to Sell Signal (Can be repeated)
    elif current_signal == 'Sell':
        if last_buy_signal is not None:
            mask = (df['Date'] >= last_buy_signal['Date']) & (df['Date'] < df['Date'].iloc[i])
            investments_in_span = df.loc[mask, 'Investment']

            if not investments_in_span.empty:
                max_investment = investments_in_span.max()

                # Filter out zero values before determining the minimum investment
                filtered_investments = investments_in_span[investments_in_span > 0].sort_values().reset_index(drop=True)
                if not filtered_investments.empty:
                    min_investment = filtered_investments[0]
                else:
                    min_investment = investments_in_span.min()  # Fallback to the original min if no non-zero values

                profit = previous_investment - last_buy_signal['Investment']
                highest_percentage = ((max_investment - last_buy_signal['Investment']) / last_buy_signal['Investment']) * 100
                lowest_percentage = ((min_investment - last_buy_signal['Investment']) / last_buy_signal['Investment']) * 100 * -1

                res.append({
                    'Signal': 'Buy - Sell',
                    'Start Close Price': last_buy_signal['Close Price'],
                    'Start Date': last_buy_signal['Date'],
                    'End Close Price': df['Close Price'].iloc[i],
                    'End Date': df['Date'].iloc[i],
                    'Start Investment': last_buy_signal['Investment'],
                    'End Investment': previous_investment,
                    'Profit/Loss': profit,
                    'Highest Investment': max_investment,
                    'Lowest Investment': min_investment,
                    'Highest Percentage': highest_percentage,
                    'Lowest Percentage': 0
                })

    # Update the last buy signal
    if current_signal == 'Buy':
        last_buy_signal = df.iloc[i]

# Convert the results to a DataFrame
output = pd.DataFrame(res)

# Calculate the average percentages
average_highest_percentage = output['Highest Percentage'].mean() if not output.empty else 0
average_lowest_percentage = output['Lowest Percentage'].mean() if not output.empty else 0

# Append the averages to the DataFrame
averages_df = pd.DataFrame([{
    'Signal': 'Average',
    'Start Close Price': '',
    'Start Date': '',
    'End Close Price': '',
    'End Date': '',
    'Start Investment': '',
    'End Investment': '',
    'Profit/Loss': '',
    'Highest Investment': '',
    'Lowest Investment': '',
    'Highest Percentage': average_highest_percentage,
    'Lowest Percentage': average_lowest_percentage
}])

# Append to the original DataFrame
output = pd.concat([output, averages_df], ignore_index=True)

# Specify the correct path to save in Google Drive
cp = input('Enter File name which has to be stored: ')
csv = cp + '.csv'
output.to_csv(csv, index=False)
print(f"DataFrame saved successfully as {csv}.")