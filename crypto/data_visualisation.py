import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

def plot_crypto_indicators(df, last_n_days=None, savepath="crypto_indicators.png"):
    # Use dark background
    plt.style.use('dark_background')

    # Convert 'date' column to datetime
    df['date'] = pd.to_datetime(df['date'])

    # Sort and slice if needed
    df = df.sort_values('date')
    if last_n_days:
        df = df.tail(last_n_days)

    # MACD Histogram (difference)
    df['MACD_Hist'] = df['MACD'] - df['Signal_Line']

    # Set date as index
    df.set_index('date', inplace=True)

    # Set up subplots
    fig, axs = plt.subplots(4, 1, figsize=(15, 12), sharex=True)
    fig.subplots_adjust(hspace=0.4)
    date_format = mdates.DateFormatter('%Y-%m-%d')

    # Colors
    price_color = 'white'
    band_color = 'yellow'
    ma50_color = 'cyan'
    ma200_color = 'magenta'
    macd_color = 'deepskyblue'
    signal_color = 'orange'
    rsi_color = 'deepskyblue'

    # 1. Price + MAs
    axs[0].plot(df.index, df['price'], label='Price', color=price_color, linewidth=2)
    axs[0].plot(df.index, df['MA50'], label='MA50', color=ma50_color, linestyle='--', linewidth=1.5)
    axs[0].plot(df.index, df['MA200'], label='MA200', color=ma200_color, linestyle='--', linewidth=1.5)
    axs[0].set_title('Price with MA50 & MA200', fontsize=12, fontweight='bold')
    axs[0].legend()
    axs[0].grid(True, color='gray', linestyle='--', alpha=0.3)

    # 2. MACD
    axs[1].plot(df.index, df['MACD'], label='MACD', color=macd_color, linewidth=1.5)
    axs[1].plot(df.index, df['Signal_Line'], label='Signal Line', color=signal_color, linewidth=1.5)
    axs[1].bar(df.index,df['MACD_Hist'],label='Histogram',
               color=['lime' if val >= 0 else 'red' for val in df['MACD_Hist']],alpha=0.7)
    axs[1].set_title('MACD & Histogram', fontsize=12, fontweight='bold')
    axs[1].legend()
    axs[1].grid(True, color='gray', linestyle='--', alpha=0.3)

    # 3. RSI
    axs[2].plot(df.index, df['RSI'], label='RSI', color=rsi_color, linewidth=1.5)
    axs[2].axhline(70, color='red', linestyle='--', linewidth=1, label='Overbought (70)')
    axs[2].axhline(30, color='lime', linestyle='--', linewidth=1, label='Oversold (30)')
    axs[2].set_ylim(0, 100)
    axs[2].set_title(f'RSI - Last {last_n_days} Days', fontsize=12, fontweight='bold')
    axs[2].legend()
    axs[2].grid(True, color='gray', linestyle='--', alpha=0.3)

    # 4. Bollinger Bands
    axs[3].plot(df.index, df['price'], label='Price', color=price_color, linewidth=2)
    axs[3].plot(df.index, df['bollinger_upper'], label='Upper Band', color=band_color, linestyle='--')
    axs[3].plot(df.index, df['bollinger_mid'], label='Mid Band', color=band_color, linestyle=':')
    axs[3].plot(df.index, df['bollinger_lower'], label='Lower Band', color=band_color, linestyle='--')
    axs[3].set_title('Bollinger Bands', fontsize=12, fontweight='bold')
    axs[3].legend()
    axs[3].grid(True, color='gray', linestyle='--', alpha=0.3)

    # Format x-axis
    axs[3].xaxis.set_major_formatter(date_format)
    plt.xticks(rotation=45)

    plt.savefig(savepath, dpi=300, bbox_inches='tight', facecolor='black')

    # plt.tight_layout()
    # plt.show()
