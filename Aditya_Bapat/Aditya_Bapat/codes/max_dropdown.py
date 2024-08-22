import pandas as pd
import numpy as np
import plotly.express as px
import scipy.signal

path = input('Enter Name of File: ')
df = pd.read_csv(f'{path}.csv')

df.info()

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Create an interactive line graph
fig = px.line(df, x='Date', y='Total Cash', title='Total Cash Over Time', 
              labels={'Total Cash': 'Total Cash'})

# Update layout for better visual appearance
fig.update_layout(
    xaxis_title='Date',
    yaxis_title='Total Cash',
    xaxis=dict(
        tickformat='%Y-%m-%d',  # Format dates in 'YYYY-MM-DD'
        tickangle=-45           # Rotate date labels for better readability
    ),
    yaxis=dict(
        title='Total Cash',
        zeroline=False
    ),
)

# Add hover data to display the Close Price
fig.update_traces(
    hovertemplate='<b>Date:</b> %{x}<br><b>Total Cash:</b> %{y}<br><b>Close Price:</b> %{customdata[0]}',
    customdata=df[['Close Price']]
)

# Show the interactive graph
fig.show()

max_totalcash = None
min_totalcash = None

# Convert 'Date' column to datetime format
df['Date'] = pd.to_datetime(df['Date'])

# Find local maxima in the 'Total Cash' column
peaks, _ = scipy.signal.find_peaks(df['Total Cash'])
minima, _ = scipy.signal.find_peaks(-df['Total Cash'])

# Extract the peak data
peak_data = df.iloc[peaks][['Date', 'Total Cash', 'Close Price']]
minima_data = df.iloc[minima][['Date', 'Total Cash', 'Close Price']]
paired_data = []
for i in range(len(peaks)):
    # Get the current peak
    peak_index = peaks[i]
    next_peak_index = peaks[i + 1] if i + 1 < len(peaks) else len(df)  # Next peak or end of data
    
    # Filter minima between current peak and next peak
    minima_between = minima[(minima > peak_index) & (minima < next_peak_index)]
    
    # Store data for these minima, paired with the current peak
    for min_index in minima_between:
        paired_data.append({
            'Peak Date': df.iloc[peak_index]['Date'],
            'Peak Total Cash': df.iloc[peak_index]['Total Cash'],
            'Peak Close Price': df.iloc[peak_index]['Close Price'],
            'Minima Date': df.iloc[min_index]['Date'],
            'Minima Total Cash': df.iloc[min_index]['Total Cash'],
            'Minima Close Price': df.iloc[min_index]['Close Price']
        })

# Convert list of paired data to DataFrame
paired_df = pd.DataFrame(paired_data)
# Optionally, save these peaks to a CSV file
maxpath = input('Store Peaks in dataset: ')
maxpath = maxpath + '.csv'
paired_df.to_csv(maxpath, index=False)

