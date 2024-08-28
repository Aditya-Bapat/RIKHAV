import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import seaborn as sns
import plotly.graph_objects as go
import numpy as np
import math

path = input('Name of the file whose RSI has to be calculated: ')
df = pd.read_csv(f'{path}.csv')
df.info()

close_df = df['Close Price'].diff()

change_up = close_df.copy()
change_down = close_df.copy()

change_up[change_up<0] = 0
change_down[change_down>0]=0

close_df.equals(change_up+change_down)

avg_up = change_up.rolling(14).mean()
avg_down = change_down.rolling(14).mean().abs()

# rsi = 100 - (100/(avg_up+avg_down))
rsi = 100 * avg_up/(avg_up+avg_down)
# rsi.head(10)

plt.style.use('fivethirtyeight')
plt.rcParams['figure.figsize'] = (20,20)
ax1 = plt.subplot2grid((10,1),(0,0),rowspan=4,colspan=1)
ax2 = plt.subplot2grid((10,1),(5,0),rowspan=4,colspan=1)

ax1.set_title(f'{path} Close Price: ')
ax1.plot(df['Close Price'],linewidth = 1)

ax2.set_title('Relative strength Index')
ax2.plot(rsi,color = 'orange',linewidth = 1)

ax2.axhline(30,linestyle = '--',linewidth = 1.5,color='green')
ax2.axhline(70,linestyle = '--',linewidth = 1.5,color = 'red')
plt.show()