import requests
import pandas as pd
from datetime import datetime, timedelta, timezone
import csv
import os

BASE_URL = "https://api.coingecko.com/api/v3"

def get_current_price_and_dominance(id='bitcoin', symbol='btc'):
    """Get current Bitcoin price and market dominance"""
    try:
        # Get Bitcoin price
        price_url = f"{BASE_URL}/simple/price"
        price_params = {
            'ids': id,
            'vs_currencies': 'usd',
            'include_market_cap': 'true',
            'include_24hr_vol': 'true',
            'include_24hr_change': 'true',            
        }
        
        price_response = requests.get(price_url, params=price_params)
        price_response.raise_for_status()
        price_data = price_response.json()[id]
        
        # Get global market data for dominance
        global_url = f"{BASE_URL}/global"
        global_response = requests.get(global_url)
        global_response.raise_for_status()
        global_data = global_response.json()['data']
        
        current_price = price_data.get('usd', 0)
        usd_market_cap = price_data.get('usd_market_cap', 0)
        usd_24h_vol = price_data.get('usd_24h_vol', 0)
        usd_24h_change = price_data.get('usd_24h_change', 0)
        current_btc_dominance = global_data.get('market_cap_percentage', {}).get(symbol, 0)

        data={
            'cryptocurrency': id,
            'symbol': symbol,
            'current_price': current_price,
            'current_dominance': round(current_btc_dominance, 2),
            'usd_market_cap': round(usd_market_cap, 2),
            'usd_24h_vol': round(usd_24h_vol, 2),
            'usd_24h_change': round(usd_24h_change, 2)
        }

        return data

    except requests.RequestException as e:
        print(f"Error fetching current data: {e}")
        return None
    
def get_historical_price_data(days=300):
    """Get historical Bitcoin price and volume data."""
    try:
        url = f"{BASE_URL}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days, # No need to add 10 here, the API handles the range
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status() # Raises an exception for bad status codes (4xx or 5xx)
        
        data = response.json()
        
        # 1. Extract both prices and total_volumes
        prices = data['prices']
        volumes = data['total_volumes']

        # 2. Create separate DataFrames for each
        df_price = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df_volume = pd.DataFrame(volumes, columns=['timestamp', 'volume'])
        
        # 3. Merge them on the timestamp
        df = pd.merge(df_price, df_volume, on='timestamp')
        
        # Convert timestamp to a readable date format
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        
        # Drop the now redundant timestamp column
        df = df.drop('timestamp', axis=1)

        # A small improvement: Use float for price to keep decimal precision
        df['price'] = df['price'].astype(float).round(2)
        df['volume'] = df['volume'].astype(float).round(2)

        return df
        
    except requests.RequestException as e:
        print(f"Error fetching historical data: {e}")
        return None

def get_historical_ohlc_data(coin_id='bitcoin', days=300):
    """
    Get historical Open, High, Low, Close (OHLC) data for a specific coin.
    This function provides the daily high and low prices.
    """
    try:
        url = f"{BASE_URL}/coins/{coin_id}/ohlc"
        params = {
            'vs_currency': 'usd',
            'days': days,
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()  
        
        data = response.json()
        
        df = pd.DataFrame(data, columns=['timestamp', 'open', 'high', 'low', 'close'])
        
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
                
        df = df.drop('timestamp', axis=1)
        
        for col in ['open', 'high', 'low', 'close']:
            df[col] = df[col].astype(float).round(2)

        return df

    except requests.exceptions.RequestException as e:
        print(f"An error occurred with the API request: {e}")
        return None
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        return None

def save_data_to_csv(filename, data):
    """
    Appends a new row of Bitcoin data to a CSV file.
    Creates the file and adds headers if it doesn't exist.

    Args:
        filename (str): The name of the CSV file to save to.
        data (dict): A dictionary containing the data to save.
    """
    # Define the headers for our CSV file
    fieldnames = [
        'date',
        'current_price',
        'dominance_percentage',
        'market_cap_usd',
        '24h_volume_usd',
        '24h_change_percentage'
    ]
    
    # Prepare the data row as a dictionary
    data_row = {
        'date': datetime.now(timezone(timedelta(hours=2))).strftime('%Y-%m-%d %H:%M:%S'),
        'current_price': round(data.get('current_price', 0), 2),
        'dominance_percentage': round(data.get('current_dominance', 0), 2),
        'market_cap_usd': round(data.get('usd_market_cap', 0), 2),
        '24h_volume_usd': round(data.get('usd_24h_vol', 0), 2),
        '24h_change_percentage': round(data.get('usd_24h_change', 0), 2)
    }
    
    try:
        # Check if the file already exists to decide if we need to write headers
        file_exists = os.path.isfile(filename)
        
        # Open the file in 'append' mode. 'newline=""' is important to prevent extra rows.
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            # If the file is new, write the header row
            if not file_exists:
                writer.writeheader()
            
            # Write the data row
            writer.writerow(data_row)
            
        print(f"Data successfully saved to {filename}")
        
    except IOError as e:
        print(f"Error writing to file {filename}: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")