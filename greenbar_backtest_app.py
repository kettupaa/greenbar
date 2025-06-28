import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

# App layout
st.set_page_config(page_title="Green Bar Backtest", layout="wide")
st.title("📈 EUR/USD Green Bar Intraday Backtest")

# Sidebar settings
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("2025-06-28"))

# Constants
MAX_RISK_EUR = 1000
PIP_VALUE_PER_LOT = 10
PIP_SIZE = 0.0001
TRANSACTION_COST_PIPS = 2

# Download and clean EUR/USD data
with st.spinner("Fetching EUR/USD data..."):
    data = yf.download("EURUSD=X", start=start_date, end=end_date)
    data = data[["Open", "High", "Low", "Close"]].dropna()
    data.reset_index(inplace=True)
    data[["Open", "High", "Low", "Close"]] = data[["Open", "High", "Low", "Close"]].astype(float)

# Backtesting logic
trades = []

for i in range(1, len(data) - 1):
    prev_day = data.iloc[i - 1]
    next_day = data.iloc[i + 1]

    # Only trade if previous day is a green bar
    if prev_day["Close"] > prev_day["Open"]:
        high = prev_day["High"]
        low = prev_day["Low"]
        entry = high - (high - low) / 3
        target = high
        stop = low

        # Entry condition
        if next_day["Low"] <= entry:
            stop_loss_pips = (entry - stop) / PIP_SIZE
            if stop_loss_pips == 0:
                continue

            position_size = MAX_RISK_EUR / (stop_loss_pips * PIP_VALUE_PER_LOT)

            if next_day["High"] >= target:
                exit_price = target
                result = "Win"
            elif next_day["Low"] <= stop:
                exit_price = stop
                result = "Loss"
            else:
                exit_price = next_day["Clo]()

