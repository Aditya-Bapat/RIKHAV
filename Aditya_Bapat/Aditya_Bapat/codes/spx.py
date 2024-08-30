import yfinance as yf
import pandas as pd
import numpy as np
import datetime
import plotly.graph_objects as go
import matplotlib.pyplot as plt

ticker = '^SPX'

start_day = 16
start_month = 5
start_Year = 2022
start_date = f'{start_Year}-{start_month}-{start_day}'

end_day = 1
end_month = 8
end_Year = 2024
end_date = f'{end_Year}-{end_month}-{end_day}'

data = yf.download(ticker, start=start_date, end=end_date, interval='1D')
print(data.head(5))
data1 = data['Close']
print(data1.head())
path = 'curves.csv'
curves = pd.read_csv(path, usecols=["Datetime","Portfolio_Value"],index_col=0,parse_dates=True)
df = curves.groupby(pd.Grouper(freq='1D',closed='left',label='left')).agg({"Portfolio_Value": "last"})
print(df.head(5))

df2 =pd.concat([df,data1],axis=1)
df2 = df2[df2['Portfolio_Value'].notna()]

df2['Close_pct'] = df2['Close'].pct_change()
df2['SPX'] = 0.0
for i in range(len(df2)):
    if i == 0:
        df2['SPX'][i] = df2['Portfolio_Value'][i]
    else:
        df2['SPX'][i] = df2['SPX'][i-1] + (df2['SPX'][i-1] * df2['Close_pct'][i])

print(df2.head(5))
df2.to_csv('curves_merdged.csv')
print(f"DataFrame saved successfully.")

#Interactive Scatter plot with plotly
fig = go.Figure()

fig.add_trace(go.Scatter(
    x=df2.index,
    y=df2['Portfolio_Value'],
    mode='lines',
    name='Portfolio_Value',
    marker=dict(color='blue')
))

fig.add_trace(go.Scatter(
    x=df2.index,
    y=df2['SPX'],
    mode='lines',
    name='SPX',
    line=dict(color='red')
))

fig.update_layout(
    title='Portfolio_Value and SPX',
    xaxis_title='Date',
    yaxis_title='Price',
    yaxis_type='log',
    legend_title='Legend',
    hovermode='x unified'
)
fig.show()

# # Create a figure
# plt.figure(figsize=(12, 6))

# # Set the width of the bars and the positions
# bar_width = 0.4
# index = np.arange(len(df2.index))

# # Plot Portfolio_Value bars
# plt.bar(index - bar_width/2, df2['Portfolio_Value'], bar_width, color='blue', label='Portfolio_Value')

# # Plot Close (SPX) bars
# plt.bar(index + bar_width/2, df2['Close'], bar_width, color='red', label='SPX')

# # Add labels and title
# # plt.xlabel('Date')
# plt.ylabel('Value')
# plt.title('Portfolio_Value and SPX Close Prices Over Time')
# # plt.xticks(index, df2.index.date, rotation=45)  # Use the date part for x-ticks
# plt.legend()

# # Adjust layout
# plt.tight_layout()
# # Show the plot
# plt.show()
