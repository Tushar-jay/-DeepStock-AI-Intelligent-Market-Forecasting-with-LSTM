import numpy as np
import yfinance as yf
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
import joblib
import os

tickers_list = ['AAPL', 'MSFT', 'GOOG', 'TSLA', 'AMZN', 'NVDA']

lookback = 60
epochs = 20
batch_size = 32

for ticker in tickers_list:
    print(f"Training model for {ticker}...")
    # Fetch last 2 years of data
    df = yf.download(ticker, period="2y")[['Close']]
    data = df.values

    # Scale
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(data)

    # Prepare training data
    X, y = [], []
    for i in range(lookback, len(scaled)):
        X.append(scaled[i-lookback:i, 0])
        y.append(scaled[i, 0])
    X, y = np.array(X), np.array(y)
    X = X.reshape(X.shape[0], X.shape[1], 1)

    # Train/test split
    split = int(len(X) * 0.8)
    X_train, X_test = X[:split], X[split:]
    y_train, y_test = y[:split], y[split:]

    # LSTM model
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(lookback, 1)))
    model.add(LSTM(50))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mse')
    model.fit(X_train, y_train, epochs=epochs, batch_size=batch_size, validation_split=0.1)

    # Save model & scaler
    os.makedirs("models", exist_ok=True)
    model.save(f'models/lstm_model_{ticker}.h5')
    joblib.dump(scaler, f'models/scaler_{ticker}.pkl')
    print(f" Saved lstm_model_{ticker}.h5 and scaler_{ticker}.pkl\n")
