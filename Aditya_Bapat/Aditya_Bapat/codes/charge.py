import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math

csv1 = input('file name: ')
df1 = pd.read_csv(f'{csv1}.csv')
csv2 = input('Average Buy- Sell percentage file: ')
df2 = pd.read_csv(f'{csv2}.csv')

average_highest_percentage = df2[df2['Signal'] == 'Average']['Highest Percentage'].values[0]
average_lowest_percentage = df2[df2['Signal'] == 'Average']['Lowest Percentage'].values[0]
new_rows = []
buy_hold_triggered = False
short_sell_triggered = False

locked_shares = None
locked_remaining_cash = None
previous_investment = 0
previous_total_cash = 0

for i in range(len(df1)):
    row = df1.iloc[i].to_dict()
    signal = row['Signal']
    previous_row = df1.iloc[i-1].to_dict() if i > 0 else row
    previous_shares_bought = previous_row.get('Shares Bought', 0)

    if signal in ['Buy Hold', 'Short Sell']:
        # Update the investment from the previous row
        current_investment = previous_row.get('Investment', 0)
    else:
        current_investment = row.get('Investment', 0)

    # Calculate profit and total cash based on previous investment and current investment
    profit = previous_investment - current_investment
    total_cash = previous_total_cash + profit

    if signal == 'Buy Hold':
        percentage_difference = (row['Investment'] - previous_investment) / previous_investment * 100
        row['% Diff'] = percentage_difference

        if not buy_hold_triggered and percentage_difference >= average_highest_percentage:
            # Condition met, trigger Buy Hold and lock shares
            buy_hold_triggered = True
            locked_shares = math.floor(previous_shares_bought / 2)
            row['Shares Bought'] = locked_shares
            row['Investment'] = locked_shares * row['Close Price']
            locked_remaining_cash = row['Remaining Cash']  # Lock remaining cash for subsequent rows
            row['Profit/Loss'] = previous_investment - row['Investment']
            sb_diff = previous_shares_bought - locked_shares
            sb_diff_inv = sb_diff * row['Close Price']
            row['Charge'] = row['Investment'] * (0.7/100)
            row['Remaining Cash'] = (previous_remaining_cash + sb_diff_inv)-row['Charge']
            row['Total Cash'] = row['Investment'] + row['Remaining Cash']
        elif buy_hold_triggered and locked_shares is not None:
            # After Buy Hold is triggered, keep shares and remaining cash constant
            row['Shares Bought'] = locked_shares
            row['Investment'] = locked_shares * row['Close Price']
            row['Remaining Cash'] = locked_remaining_cash  # Keep remaining cash constant
            row['Profit/Loss'] = row['Investment'] - previous_investment
            row['Total Cash'] = previous_total_cash + row['Profit/Loss']
    elif signal == 'Short Sell':
        if previous_investment == 0:
            percentage_difference = 0
        else:
            percentage_difference = (row['Investment'] - previous_investment) / previous_investment * 100
        row['% Diff'] = percentage_difference

        if not short_sell_triggered and percentage_difference >= average_lowest_percentage:
            # Trigger Short Sell and lock shares
            short_sell_triggered = True
            locked_shares = math.floor(previous_shares_bought / 2)
            row['Shares Bought'] = locked_shares
            row['Investment'] = locked_shares * row['Close Price']
            row['Profit/Loss'] = previous_investment - row['Investment']
            sb_diff = previous_shares_bought - locked_shares
            sb_diff_inv = sb_diff * row['Close Price']
            row['Charge'] = row['Investment'] * (0.7/100)
            row['Remaining Cash'] = (previous_remaining_cash + sb_diff_inv) - row['Charge']
            locked_remaining_cash = row['Remaining Cash']  # Lock remaining cash for subsequent rows
            row['Total Cash'] = row['Investment'] + row['Remaining Cash']
        elif short_sell_triggered and locked_shares is not None:
            # After Short Sell is triggered, keep shares and remaining cash constant
            row['Shares Bought'] = locked_shares
            row['Investment'] = locked_shares * row['Close Price']
            row['Remaining Cash'] = locked_remaining_cash  # Keep remaining cash constant
            row['Profit/Loss'] = previous_investment - row['Investment']
            row['Total Cash'] = previous_total_cash + row['Profit/Loss']
    elif signal == 'Sell':
        # Reset for the next cycle
        buy_hold_triggered = False
        short_sell_triggered = False
        row['Charge'] = previous_investment * (0.7/100)
        row['Total Cash'] = previous_total_cash
        row['Remaining Cash'] = previous_total_cash - row['Charge']
        row['Profit/Loss'] = 0
        row['Shares Bought'] = 0
        row['Investment'] = 0


    elif signal == 'Buy':
      row['Charge'] = row['Investment'] * (0.7/100)

    previous_investment = row.get('Investment', 0)
    previous_total_cash = row.get('Total Cash', 0)
    previous_remaining_cash = row.get('Remaining Cash', 0)
    previous_shares_bought = row.get('Shares Bought', 0)
    new_rows.append(row)

# Create a new DataFrame from the modified rows
chargedf = pd.DataFrame(new_rows)

# Add the highest and lowest average percentages for reference
chargedf['High Avg %'] = average_highest_percentage
chargedf['Low Avg %'] = average_lowest_percentage

path = input('Output File Name: ')
csv_charge = path + '.csv'
chargedf.to_csv(csv_charge, index=False)
print(f" DataFrame saved successfully as {csv_charge}.")