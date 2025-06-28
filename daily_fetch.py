import yfinance as yf
import pandas as pd
import os
from datetime import datetime
import schedule
import time
import logging

# Set up logging
logging.basicConfig(
    filename='data/daily_fetch.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

tickers_list = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'NVDA']


def compute_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df.sort_values('Date', inplace=True)
    df.reset_index(drop=True, inplace=True)
    df['Pct_Change'] = df['Close'].pct_change() * 100
    df['7D_MA_Close'] = df['Close'].rolling(window=7).mean()
    df['7D_Avg_Volume'] = df['Volume'].rolling(window=7).mean().fillna(0)
    df['Volume_Spike'] = df['Volume'] > (1.5 * df['7D_Avg_Volume'])
    return df


def fetch_and_save():
    logging.info("Starting fetch_and_save...")
    os.makedirs('data', exist_ok=True)
    for ticker in tickers_list:
        try:
            filename = os.path.join('data', f'historical_{ticker}.csv')
            logging.info(f"Fetching {ticker} data...")

            df_new = yf.download(ticker, period='2d')[['Open', 'High', 'Low', 'Close', 'Volume']]
            df_new.reset_index(inplace=True)

            if os.path.exists(filename):
                df_old = pd.read_csv(filename, parse_dates=['Date'])
                df = pd.concat([df_old, df_new]).drop_duplicates('Date')
            else:
                df = df_new

            df = compute_indicators(df)
            df.to_csv(filename, index=False)
            logging.info(f"{ticker}: Saved {len(df)} rows to {filename}")

        except Exception as e:
            logging.error(f"{ticker}: Error occurred - {e}")


if __name__ == '__main__':
    fetch_and_save()
    schedule.every().day.at('18:00').do(fetch_and_save)
    while True:
        schedule.run_pending()
        time.sleep(60)
