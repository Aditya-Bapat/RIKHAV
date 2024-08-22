import pandas as pd
import numpy as np

path = input('Select file whose annual interest has to be calculated: ')
df = pd.read_csv(f'{path}.csv')

# Convert the 'Date' column to datetime format if it's not already
df['Date'] = pd.to_datetime(df['Date'], utc=True)  # Ensure datetime is timezone-aware

# Extract the year from the Date column
df['Year'] = df['Date'].dt.year

# Initialize an empty list to store results
results = []

# Iterate over each year in the dataset
for year in df['Year'].unique():
    # Define the start and end dates for the current year, ensuring timezone consistency
    start_date = pd.Timestamp(year=year, month=1, day=1, tz='UTC')
    end_date = pd.Timestamp(year=year + 1, month=1, day=1, tz='UTC') - pd.DateOffset(days=1)
    
    # Filter the DataFrame for the current year
    df_year = df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

    if not df_year.empty:
        # Get the closest date to the start date
        start_totalcash_row = df_year.iloc[0]
        start_totalcash = start_totalcash_row['Total Cash'] if not start_totalcash_row.empty else np.nan
        start_date_actual = start_totalcash_row['Date']

        # Get the closest date to the end date
        end_totalcash_row = df_year.iloc[-1]
        end_totalcash = end_totalcash_row['Total Cash'] if not end_totalcash_row.empty else np.nan
        end_date_actual = end_totalcash_row['Date']
        
        # Calculate the total period duration in years
        total_period_years = (end_date_actual - start_date_actual).days / 365.25
        
        # Calculate the return value and annualized return
        return_value = (end_totalcash - start_totalcash) / start_totalcash
        annualized_return = (1 + return_value) ** (1 / total_period_years) - 1
        
        # Store results
        results.append({
            'Year': year,
            'Start Date': start_date_actual,
            'End Date': end_date_actual,
            'Start Total Cash': start_totalcash,
            'End Total Cash': end_totalcash,
            'Annualized Return (%)': annualized_return * 100
        })

# Create a DataFrame from the results
results_df = pd.DataFrame(results)

# Print or save the results DataFrame
print("Yearly Annualized Returns:")
print(results_df)

# Calculate the overall return across the entire time span
start_date_overall = df['Date'].min()
end_date_overall = df['Date'].max()

start_totalcash_overall = df.loc[df['Date'] == start_date_overall, 'Total Cash'].values[0]
end_totalcash_overall = df.loc[df['Date'] == end_date_overall, 'Total Cash'].values[0]

# Calculate the total period duration in years for the overall time span
total_period_years_overall = (end_date_overall - start_date_overall).days / 365.25
# Calculate the overall return value and annualized return
overall_return_value = (end_totalcash_overall - start_totalcash_overall) / start_totalcash_overall
overall_annualized_return = (1 + overall_return_value) ** (1 / total_period_years_overall) - 1

print("\nOverall Annualized Return:")
print(f"Start Date: {start_date_overall}")
print(f"End Date: {end_date_overall}")
print(f"Start Total Cash: {start_totalcash_overall}")
print(f"End Total Cash: {end_totalcash_overall}")
print(f'No Of years: {total_period_years_overall}')
print(f"Annualized Return (%): {overall_annualized_return * 100:.2f}")