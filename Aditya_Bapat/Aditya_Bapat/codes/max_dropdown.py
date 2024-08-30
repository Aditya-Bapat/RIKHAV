import pandas as pd
import numpy as np
import plotly.express as px
import scipy.signal

# Load the data
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

# Find local maxima and minima in the 'Total Cash' column
peaks, _ = scipy.signal.find_peaks(df['Total Cash'])
minima, _ = scipy.signal.find_peaks(-df['Total Cash'])

# Extract the peak data
paired_data = []

prev_local_maxima = None
prev_local_minima = None
prev_local_maxima_date = None
prev_local_minima_date = None

i = 0
while i < len(peaks):
    peak_index = peaks[i]
    next_peak_index = peaks[i + 1] if i + 1 < len(peaks) else len(df)  # Next peak or end of data
    
    # Filter minima between current peak and next peak
    minima_between = minima[(minima > peak_index) & (minima < next_peak_index)]
    
    # If no minima found between the peaks, move to the next peak
    if len(minima_between) == 0:
        i += 1
        continue
    
    # Find local minima based on current local maxima
    for min_index in minima_between:
        local_maxima = df.iloc[peak_index]['Total Cash']
        local_minima = df.iloc[min_index]['Total Cash']

        if prev_local_maxima is None or local_maxima > prev_local_maxima:
            # Current local_maxima is greater than previous_local_maxima
            new_local_maxima = local_maxima
            new_local_maxima_date = df.iloc[peak_index]['Date']

            # Find the minimum minima value between the current peak and the next one
            min_minima_value = df.iloc[minima_between]['Total Cash'].min()
            min_minima_index = df[df['Total Cash'] == min_minima_value].index[0]
            min_minima_date = df.iloc[min_minima_index]['Date']
            min_minima_close_price = df.iloc[min_minima_index]['Close Price']

            # Store the peak and corresponding minima
            paired_data.append({
                'Peak Date': new_local_maxima_date,
                'New Local Maxima': new_local_maxima,
                'Peak Close Price': df.iloc[peak_index]['Close Price'],
                'Minima Date': min_minima_date,
                'New Local Minima': min_minima_value,
                'Minima Close Price': min_minima_close_price,
                'Difference': new_local_maxima - min_minima_value
            })
            
        elif local_maxima < prev_local_maxima:
            
            # Current local_maxima is less than previous_local_maxima
            new_local_maxima = prev_local_maxima
            new_local_maxima_date = prev_local_maxima_date

            # Find the minimum minima value between the current peak and the next one
            min_minima_value = df.iloc[minima_between]['Total Cash'].min()
            min_minima_index = df[df['Total Cash'] == min_minima_value].index[0]
            min_minima_date = df.iloc[min_minima_index]['Date']
            min_minima_close_price = df.iloc[min_minima_index]['Close Price']

            total_cash_diff = new_local_maxima - min_minima_value
            paired_data.append({
                'Peak Date': new_local_maxima_date,
                'New Local Maxima': new_local_maxima,
                'Peak Close Price': df.iloc[peak_index]['Close Price'],
                'Minima Date': min_minima_date,
                'New Local Minima': min_minima_value,
                'Minima Close Price': min_minima_close_price,
                'Difference':total_cash_diff,
            })

        # Update previous maxima and minima for the next iteration
        prev_local_maxima = new_local_maxima
        prev_local_minima = local_minima
        prev_local_maxima_date = new_local_maxima_date
        prev_local_minima_date = min_minima_date
    
    i += 1

# Convert list of paired data to DataFrame
paired_df = pd.DataFrame(paired_data)
paired_df = paired_df.drop_duplicates(subset=['Peak Date', 'Minima Date'])

results = []

# Group by 'New Local Maxima'
grouped = paired_df.groupby('New Local Maxima')

# Iterate over each group
for name, group in grouped:
    # Find the minimum 'New Local Minima' within this group
    min_minima_row = group.loc[group['New Local Minima'].idxmin()]
    
    # Extract required information
    peak_date = min(group['Peak Date'])  # Assuming the Peak Date is the same for each Maxima in the group
    peak_close_price = min(group['Peak Close Price'])  # Assuming the Peak Close Price is the same for each Maxima in the group
    minima_date = min_minima_row['Minima Date']
    minima_close_price = min_minima_row['Minima Close Price']
    new_local_maxima = name
    new_local_minima = min_minima_row['New Local Minima']
    difference = (new_local_maxima - new_local_minima)/new_local_minima*100
    
    # Append the results to the list
    results.append({
        'Peak Date': peak_date,
        'Peak Close Price': peak_close_price,
        'Minima Date': minima_date,
        'Minima Close Price': minima_close_price,
        'New Local Maxima': new_local_maxima,
        'New Local Minima': new_local_minima,
        'Difference': difference
    })

# Create a DataFrame from the results
results_df = pd.DataFrame(results)
max_difference = results_df['Difference'].max()

# Add a 'Remark' column with default value 'Normal'
results_df['Remark'] = 'Normal'

# Mark the row with the maximum difference
results_df.loc[results_df['Difference'] == max_difference, 'Remark'] = 'max_difference'


# Store the peaks and minima data into a CSV file
maxpath = input('Store Peaks in dataset: ')
maxpath = maxpath + '.csv'
results_df.to_csv(maxpath, index=False)
