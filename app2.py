
import streamlit as st
import pandas as pd
import yfinance as yf
import os
from datetime import timedelta
import plotly.graph_objects as go

st.set_page_config(page_title="📈 Stock Data Viewer", layout="wide")
st.title("📊 Stock Historical Data Fetcher & Viewer")

tickers_list = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'NVDA']
ticker = st.selectbox("📌 Pick a stock ticker:", tickers_list)
filename = f"historical_{ticker}.csv"

# 💾 Delete file if needed
if os.path.exists(filename):
    if st.button(f"🗑️ Delete {filename} and reset"):
        os.remove(filename)
        st.success(f"{filename} deleted!")
        st.experimental_rerun()

# 📥 Fetch / Update Section
st.subheader(f"🔄 Fetch or Update {ticker} Data")

if st.button(f"📤 Update {ticker} Data"):
    with st.spinner('⏳ Fetching data...'):
        try:
            if os.path.exists(filename):
                existing_df = pd.read_csv(filename, index_col=0)
                existing_df.index = pd.to_datetime(existing_df.index, errors='coerce')
                existing_df.dropna(inplace=True)

                last_date = existing_df.index.max().date()
                st.write(f"📅 Last date in file: {last_date}")

                next_date = last_date + timedelta(days=1)
                df_new = yf.download(ticker, start=next_date)[['Open', 'High', 'Low', 'Close', 'Volume']]

                if not df_new.empty:
                    combined_df = pd.concat([existing_df, df_new])
                    combined_df = combined_df[~combined_df.index.duplicated()]
                    combined_df.sort_index(inplace=True)
                    combined_df.to_csv(filename)
                    st.success(f"✅ Updated! Added {len(df_new)} new rows. Total: {len(combined_df)}")
                else:
                    st.info("ℹ️ No new data to update — you already have the latest prices!")
            else:
                st.write("🔍 No existing file. Fetching last 3 months of data...")
                df_hist = yf.download(ticker, period='3mo')[['Open', 'High', 'Low', 'Close', 'Volume']]
                df_hist.sort_index(inplace=True)
                df_hist.to_csv(filename)
                st.success(f"✅ Saved {len(df_hist)} rows to {filename}")
        except Exception as e:
            st.error(f"❌ Error while updating: {e}")

# 📈 Show Chart and Table
st.subheader(f"📂 View {ticker} Historical Data")

if os.path.exists(filename):
    try:
        data = pd.read_csv(filename, index_col=0)
        data.index = pd.to_datetime(data.index, errors='coerce')
        data.dropna(inplace=True)

        st.write(f"📄 {len(data)} rows loaded:")
        st.dataframe(data.tail(10), height=250)

        # 📊 Interactive Plotly Chart
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=data.index,
            y=data['Close'],
            mode='lines+markers',
            name=f"{ticker} Close",
            line=dict(color='royalblue')
        ))

        fig.update_layout(
            title=f"{ticker} Closing Price Over Time",
            xaxis_title='Date',
            yaxis_title='Close Price (USD)',
            hovermode='x unified',
            template='plotly_white',
            height=500
        )

        st.plotly_chart(fig, use_container_width=True)

        # ⬇️ Download CSV
        with open(filename, "rb") as f:
            st.download_button(
                label="⬇️ Download CSV",
                data=f,
                file_name=filename,
                mime="text/csv"
            )
    except Exception as e:
        st.error(f"⚠️ Error reading CSV file: {e}. Consider resetting above.")
else:
    st.warning(f"⚠️ {filename} not found — click update to create it!")

