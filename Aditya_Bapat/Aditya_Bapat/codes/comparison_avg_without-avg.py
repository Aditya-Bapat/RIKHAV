import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math
csv = input('File name: ')
df1 = pd.read_csv(f'{csv}.csv')
csv1 = input('Average file Name: ')
df2 = pd.read_csv(f'{csv1}.csv')

# Get the last value of 'Total Cash' from df1
last_total_cash_df1 = df1['Total Cash'].iloc[-1]

# Get the last value of 'Total Cash' from df2
last_total_cash_df2 = df2['Total Cash'].iloc[-1]

print("Last Total Cash from df1:", last_total_cash_df1)
print("Last Total Cash from df2:", last_total_cash_df2)


#Total Cash Difference in percentage

# Get the start and end Total Cash for df1
start_total_cash_df1 = df1['Total Cash'].iloc[0]
print(f'Start Total Cash of df1: {start_total_cash_df1}')
end_total_cash_df1 = df1['Total Cash'].iloc[-1]
print(f'End Total Cash of df1: {end_total_cash_df1}')

# Calculate the percentage change for df1
percentage_change_df1 = ((end_total_cash_df1 - start_total_cash_df1) / start_total_cash_df1) * 100

# Get the start and end Total Cash for df2
start_total_cash_df2 = df2['Total Cash'].iloc[0]
print(f'Start Total Cash of df2: {start_total_cash_df2}')
end_total_cash_df2 = df2['Total Cash'].iloc[-1]
print(f'End Total Cash of df2: {end_total_cash_df2}')

# Calculate the percentage change for df2
percentage_change_df2 = ((end_total_cash_df2 - start_total_cash_df2) / start_total_cash_df2) * 100

# Print the results
print(f"Percentage Change in Total Cash for Dataset 1 (Without Average): {percentage_change_df1:.2f}%")
print(f"Percentage Change in Total Cash for Dataset 2 (With Average): {percentage_change_df2:.2f}%")

#Lowest Total Cash of both Datasets
lowest_total_cash_df1 = df1['Total Cash'].min()
lowest_total_cash_df2 = df2['Total Cash'].min()
print(f'Lowest Total Cash of DF1: {lowest_total_cash_df1}')
print(f'Lowset Total Cash of DF2: {lowest_total_cash_df2}')


#Line Graph
# Ensure 'Date' is in datetime format for both datasets
df1['Date'] = pd.to_datetime(df1['Date'])
df2['Date'] = pd.to_datetime(df2['Date'])

# Add a column to each DataFrame to identify the source
df1['Dataset'] = 'Without Average'
df2['Dataset'] = 'Average'

# Combine the datasets, including Close Price
combined_df = pd.concat([df1[['Date', 'Total Cash', 'Close Price', 'Dataset']], 
                         df2[['Date', 'Total Cash', 'Close Price', 'Dataset']]])
# Create a line plot to compare df1 and df2, including Close Price
fig = px.line(combined_df, 
              x='Date', 
              y='Total Cash', 
              color='Dataset', 
              title='Total Cash and Close Price Over Time (Comparison of Dataset 1 and Dataset 2)',
              labels={'Date': 'Date', 'Total Cash': 'Total Cash', 'Close Price': 'Close Price', 'Dataset': 'Dataset'},
              hover_data=['Close Price'])

# Show the plot
fig.show()

