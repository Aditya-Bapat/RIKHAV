import requests
import pandas as pd
from datetime import datetime, timedelta 
import datetime as dt 
import pandas as pd
from datetime import datetime
import os
import schedule
import time

file_path = 'crypto_data.csv'
base_url = "https://min-api.cryptocompare.com/data/v2/histohour"
symbol = "BTC"  
currency = "USD"
limit = 2000 
to_ts = int(datetime.now().timestamp())  # Current timestamp

if os.path.exists(file_path):
    # Load the existing data
    df1 = pd.read_csv(file_path)

    # Convert the 'time' column to datetime
    df1["time"] = pd.to_datetime(df1["time"])
    last_time_in_file = df1["time"].max()

else:
    # Set the API URL and your parameters
    base_url = "https://min-api.cryptocompare.com/data/v2/histohour"
    symbol = "BTC"  # Cryptocurrency symbol (e.g., BTC)
    currency = "USD"  # Currency to compare against (e.g., USD)
    limit = 2000  # Max number of data points returned in one call
    to_ts = int(datetime.now().timestamp())  # Current timestamp

    # Collect data starting from 1st January 2014
    start_date = datetime(2014, 1, 1)
    all_data = []

    while True:
        # Make the API request
        url = f"{base_url}?fsym={symbol}&tsym={currency}&limit={limit}&toTs={to_ts}"
        response = requests.get(url)
        data = response.json()['Data']['Data']

        # Break loop if no more data
        if not data:
            break

        # Convert the timestamps to a human-readable date
        for entry in data:
            entry['time'] = datetime.utcfromtimestamp(entry['time'])

        # Add the data to the list
        all_data.extend(data)

        # Update the timestamp for the next call
        to_ts = data[0]['time'].timestamp()

        # Break if we reach the start date
        if data[0]['time'] < start_date:
            break


    # Assuming 'all_data' is your list of dictionaries or raw data that has been converted into a DataFrame
    df = pd.DataFrame(all_data)

    # Convert the 'time' column to datetime format (assuming 'time' is the column with date information)
    df["time"] = pd.to_datetime(df["time"])

    # Sort the DataFrame by 'time'
    df.sort_values("time", inplace=True)

    # Define your start date (replace with your actual start date)
    start_date = pd.to_datetime("2014-01-01")

    # Filter the DataFrame to only include rows from the start date onward
    df = df[df['time'] >= start_date]

    # Set the 'time' column as the index of the DataFrame
    df.set_index('time', inplace=True)

    # Now df is sorted by date, filtered from the start date, and indexed by the time column
    print(df.head())

    df.to_csv('crypto_data.csv')
    print('Dataset Generated: ')

# Fetch new data if the existing data is outdated or file doesn't exist
if last_time_in_file < datetime.now():
    while True:
        all_data = []
        # Make the API request
        url = f"{base_url}?fsym={symbol}&tsym={currency}&limit={limit}&toTs={to_ts}"
        response = requests.get(url)
        data = response.json()['Data']['Data']

        # Break loop if no more data
        if not data:
            break

        # Convert the timestamps to a human-readable date
        for entry in data:
            entry['time'] = datetime.utcfromtimestamp(entry['time'])

        # Add the data to the list
        all_data.extend(data)

        # Update the timestamp for the next call
        to_ts = data[0]['time'].timestamp()

        # Break if we reach the last time in the CSV file
        if data[0]['time'] <= last_time_in_file:
            break

    # Convert the newly fetched data to a DataFrame
    new_df = pd.DataFrame(all_data)

    # Merge new data with the existing data, remove duplicates
    updated_df = pd.concat([df1, new_df]).drop_duplicates(subset='time').reset_index(drop=True)

    # Save the updated DataFrame back to the CSV file
    updated_df.to_csv(file_path, index=False)
    print(f"Data has been updated and saved to {file_path}.")
else:
    print(f"No update needed, data in {file_path} is up-to-date.")

def fetch_and_update_data():
    # Set API parameters
    base_url = "https://min-api.cryptocompare.com/data/v2/histohour"
    symbol = "BTC"
    currency = "USD"
    limit = 2000

    # Check if the file exists
    file_path = 'crypto.csv'
    if os.path.exists(file_path):
        df1 = pd.read_csv(file_path)
        df1["time"] = pd.to_datetime(df1["time"])
        last_time_in_file = df1["time"].max()
    else:
        last_time_in_file = datetime(2014, 1, 1)
        df1 = pd.DataFrame()
        df1.sort_values("time", inplace=True)

    to_ts = int(datetime.now().timestamp())
    all_data = []

    if last_time_in_file < datetime.now():
        while True:
            url = f"{base_url}?fsym={symbol}&tsym={currency}&limit={limit}&toTs={to_ts}"
            response = requests.get(url)
            data = response.json()['Data']['Data']

            if not data:
                break

            for entry in data:
                entry['time'] = datetime.utcfromtimestamp(entry['time'])

            all_data.extend(data)
            to_ts = data[0]['time'].timestamp()

            if data[0]['time'] <= last_time_in_file:
                break

        new_df = pd.DataFrame(all_data)
        updated_df = pd.concat([df1, new_df]).drop_duplicates(subset='time').reset_index(drop=True)
        updated_df.to_csv(file_path, index=False)
        updated_df.sort_values("time", inplace=True)
        print(f"Data has been updated and saved to {file_path}.")
    else:
        print(f"No update needed, data in {file_path} is up-to-date.")

def job():
    fetch_and_update_data()

# Schedule the job to run every hour, including at midnight
schedule.every().hour.at(":00").do(job)

while True:
    schedule.run_pending()
    time.sleep(1)  # Wait one second between checks

