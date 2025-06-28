import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import timedelta

st.title(" Stock Historical Data Fetcher & Viewer")

tickers_list = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'NVDA']
ticker = st.selectbox("Pick a stock ticker:", tickers_list)
filename = f"data/historical_{ticker}.csv"

if os.path.exists(filename):
    if st.button(f" Delete {filename} and reset"):
        os.remove(filename)
        st.success(f"{filename} deleted!")
        st.experimental_rerun()

st.subheader(f" Fetch or Update {ticker} Data")

if st.button(f"Update {ticker} Data"):
    with st.spinner('Fetching data...'):
        if os.path.exists(filename):
            try:
                existing_df = pd.read_csv(filename, index_col=0)
                existing_df.index = pd.to_datetime(existing_df.index, errors='coerce')
                existing_df.dropna(axis=0, inplace=True)
                last_date = existing_df.index.max().date()
                st.write(f" Last date in file: {last_date}")

                next_date = last_date + timedelta(days=1)
                df_new = yf.download(ticker, start=next_date)[['Open','High','Low','Close','Volume']]
                if not df_new.empty:
                    combined_df = pd.concat([existing_df, df_new]).drop_duplicates()
                    combined_df.sort_index(inplace=True)
                    combined_df.to_csv(filename)
                    st.success(f" Updated! Added {len(df_new)} new rows. Total: {len(combined_df)}")
                else:
                    st.info(" No new data to update — you already have the latest prices!")
            except Exception as e:
                st.error(f" Error reading {filename}: {e}. Delete file and try again!")
        else:
            st.write(" No existing file. Fetching last 3 months of data...")
            df_hist = yf.download(ticker, period='3mo')[['Open','High','Low','Close','Volume']]
            df_hist.sort_index(inplace=True)
            df_hist.to_csv(filename)
            st.success(f" Saved {len(df_hist)} total rows to {filename}")

st.subheader(f" View {ticker} Historical CSV")

if os.path.exists(filename):
    try:
        data = pd.read_csv(filename, index_col=0)
        data.index = pd.to_datetime(data.index, errors='coerce')
        data.dropna(axis=0, inplace=True)
        st.write(f"{len(data)} rows loaded:")
        st.dataframe(data.tail(10))
        st.line_chart(data['Close'])

        with open(filename, "rb") as f:
            st.download_button(
                label=" Download CSV",
                data=f,
                file_name=os.path.basename(filename),
                mime="text/csv"
            )
    except Exception as e:
        st.error(f" Error reading CSV file: {e}. Consider resetting the file above!")
else:
    st.warning(f"{filename} not found — click update to create it!")
