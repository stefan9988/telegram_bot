import requests
import json
import pandas as pd
from datetime import datetime, timedelta
from datetime import datetime, timedelta, timezone
import csv
import os


BASE_URL = "https://api.coingecko.com/api/v3"
SAVE_PATH = "/home/stefandragicevic/telegram_bot/data/btc_data.csv"

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
            'current_dominance': current_btc_dominance,
            'usd_market_cap': usd_market_cap,
            'usd_24h_vol': usd_24h_vol,
            'usd_24h_change': usd_24h_change
        }

        return data

    except requests.RequestException as e:
        print(f"Error fetching current data: {e}")
        return None
    
def get_historical_price_data(days=200):
    """Get historical Bitcoin price data for moving average calculation"""
    try:
        url = f"{BASE_URL}/coins/bitcoin/market_chart"
        params = {
            'vs_currency': 'usd',
            'days': days + 10,  # Get a few extra days to ensure we have enough data
            'interval': 'daily'
        }
        
        response = requests.get(url, params=params)
        response.raise_for_status()
        
        data = response.json()
        prices = data['prices']
        
        # Convert to DataFrame
        df = pd.DataFrame(prices, columns=['timestamp', 'price'])
        df['date'] = pd.to_datetime(df['timestamp'], unit='ms')
        df = df.drop('timestamp', axis=1)
        df = df.set_index('date')
        
        return df
        
    except requests.RequestException as e:
        print(f"Error fetching historical price data: {e}")
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
        'current_price': data.get('current_price', 0),
        'dominance_percentage': data.get('current_dominance', 0),
        'market_cap_usd': data.get('usd_market_cap', 0),
        '24h_volume_usd': data.get('usd_24h_vol', 0),
        '24h_change_percentage': data.get('usd_24h_change', 0)
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

if __name__ == "__main__":
    current_data = get_current_price_and_dominance()
    save_data_to_csv(SAVE_PATH, current_data)
    
    # historical_data = get_historical_price_data()

    # if historical_data is not None:
    #     historical_data = calculate_moving_averages(historical_data)
    #     historical_data = calculate_macd(historical_data)
    #     historical_data = calculate_rsi(historical_data)