import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

# Settings
st.set_page_config(page_title="Green Bar Backtest", layout="wide")
st.title("📈 EUR/USD Green Bar Intraday Backtest")

# Sidebar for date selection
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("2025-06-28"))

# Constants
MAX_RISK_EUR = 1000
PIP_SIZE = 0.0001
PIP_VALUE_PER_LOT = 10
TRANSACTION_COST_PIPS = 2

# Fetch EURUSD data
with st.spinner("Downloading EUR/USD data..."):
    data = yf.download("EURUSD=X", start=start_date, end=end_date)
    data = data[["Open", "High", "Low", "Close"]].dropna().copy()
    data.reset_index(inplace=True)
    data[["Open", "High", "Low", "Close"]] = data[["Open", "High", "Low", "Close"]].astype(float)

# Backtest logic
trades = []

for i in range(1, len(data) - 1):
    prev_day = data.iloc[i - 1]
    current_day = data.iloc[i]

    # Only act if previous day was a green bar
    if prev_day["Close"] > prev_day["Open"]:
        high = prev_day["High"]
        low = prev_day["Low"]
        target = high
        stop = low

        # Calculate ideal entry that offers 3:1 reward to risk
        risk = high - low
        entry = high - risk / 3  # Entry price must allow 3:1 RR to target

        # Check if entry was hit on current day
        if current_day["Low"] <= entry:
            # Trade was entered
            if entry - stop == 0:
                continue  # Avoid division by zero

            stop_loss_pips = (entry - stop) / PIP_SIZE
            position_size = MAX_RISK_EUR / (stop_loss_pips * PIP_VALUE_PER_LOT)

            # Exit logic
            if current_day["High"] >= target:
                exit_price = target
                result = "Target"
            elif current_day["Low"] <= stop:
                exit_price = stop
                result = "Stop"
            else:
                exit_price = current_day["Close"]
                result = "Close"

            # PnL calculation
            pnl_pips = (exit_price - entry) / PIP_SIZE
            net_pnl_pips = pnl_pips - TRANSACTION_COST_PIPS
            pnl_eur = net_pnl_pips * position_size * PIP_VALUE_PER_LOT

            trades.append({
                "Date": current_day["Date"],
                "Entry": round(entry, 5),
                "Exit": round(exit_price, 5),
                "Result": result,
                "Position Size (lots)": round(position_size, 2),
                "PnL (EUR)": round(pnl_eur, 2)
            })

# Convert to DataFrame
df = pd.DataFrame(trades)

if not df.empty:
    df["Cumulative PnL"] = df["PnL (EUR)"].cumsum()

    # Summary
    st.subheader("📊 Performance Summary")
    total_pnl = df["PnL (EUR)"].sum()
    win_rate = (df["Result"] == "Target").mean() * 100

    st.markdown(f"""
    - **Total Trades:** {len(df)}  
    - **Win Rate (Target Hit):** {win_rate:.2f}%  
    - **Total PnL:** €{total_pnl:.2f}
    """)

    # Chart
    st.subheader("📈 Cumulative PnL")
    fig, ax = plt.subplots()
    ax.plot(df["Date"], df["Cumulative PnL"], color="green")
    ax.set_xlabel("Date")
    ax.set_ylabel("EUR")
    ax.grid(True)
    st.pyplot(fig)

    # Trade log
    st.subheader("📋 Trade Log")
    st.dataframe(df.set_index("Date"))

    # Excel download
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="Trades")
        writer.save()
        processed_data = output.getvalue()

    st.download_button(
        label="📥 Download Trade Log (Excel)",
        data=processed_data,
        file_name="greenbar_trades.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )
else:
    st.warning("No valid trades in the selected date range.")
