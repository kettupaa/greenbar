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
    da


