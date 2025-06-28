import streamlit as st
import yfinance as yf
import pandas as pd
import matplotlib.pyplot as plt
import io

st.set_page_config(page_title="Green Bar Backtest", layout="wide")
st.title("📈 EUR/USD Green Bar Intraday Backtest with Position Sizing & Analysis")

# Sidebar options
start_date = st.sidebar.date_input("Start date", pd.to_datetime("2022-01-01"))
end_date = st.sidebar.date_input("End date", pd.to_datetime("2025-06-28"))

with st.spinner("Downloading EUR/USD data..."):
    data = yf.download("EURUSD=X", start=start_date, end=end_date)
    data.dropna(inplace=True)

# Constants
MAX_RISK_EUR = 1000
PIP_VALUE_PER_LOT = 10
PIP_SIZE = 0.0001
TRANSACTION_COST_PIPS = 2

# Backtesting logic
trades = []

for i in range(1, len(data) - 1):
    prev_day = data.iloc[i - 1]
    next_day = data.iloc[i + 1]

    if prev_day['Close'] > prev_day['Open']:
        high = prev_day['High']
        low = prev_day['Low']
        entry = high - (high - low) / 3
        target = high
        stop = low

        if next_day['Low'] <= entry:
            stop_loss_pips = (entry - stop) / PIP_SIZE
            if stop_loss_pips == 0:
                continue

            position_size = MAX_RISK_EUR / (stop_loss_pips * PIP_VALUE_PER_LOT)

            if next_day['High'] >= target:
                exit_price = target
                result = 'Win'
            elif next_day['Low'] <= stop:
                exit_price = stop
                result = 'Loss'
            else:
                exit_price = next_day['Close']
                result = 'Close'

            gross_pnl_pips = (exit_price - entry) / PIP_SIZE
            net_pnl_pips = gross_pnl_pips - TRANSACTION_COST_PIPS
            pnl_eur = net_pnl_pips * position_size * PIP_VALUE_PER_LOT

            trades.append({
                'Date': next_day.name,
                'Entry': entry,
                'Exit': exit_price,
                'Result': result,
                'Position Size (lots)': round(position_size, 4),
                'PnL (EUR)': round(pnl_eur, 2)
            })

df = pd.DataFrame(trades)

if not df.empty:
    df['Cumulative PnL'] = df['PnL (EUR)'].cumsum()

    total_trades = len(df)
    wins = df[df['Result'] == 'Win']
    losses = df[df['Result'] == 'Loss']
    closed = df[df['Result'] == 'Close']

    win_rate = len(wins) / total_trades * 100
    avg_win = wins['PnL (EUR)'].mean() if not wins.empty else 0
    avg_loss = losses['PnL (EUR)'].mean() if not losses.empty else 0
    max_win = wins['PnL (EUR)'].max() if not wins.empty else 0
    max_loss = losses['PnL (EUR)'].min() if not losses.empty else 0
    avg_position = df['Position Size (lots)'].mean()
    avg_pnl_per_lot = df['PnL (EUR)'].sum() / df['Position Size (lots)'].sum() if df['Position Size (lots)'].sum() != 0 else 0

    st.subheader("Summary Statistics")
    st.markdown(f"""
    - **Total Trades:** {total_trades}  
    - **Win Rate:** {win_rate:.2f}%  
    - **Average Win (EUR):** {avg_win:.2f}  
    - **Average Loss (EUR):** {avg_loss:.2f}  
    - **Max Win (EUR):** {max_win:.2f}  
    - **Max Loss (EUR):** {max_loss:.2f}  
    - **Average Position Size (lots):** {avg_position:.4f}  
    - **Average PnL per Lot (EUR):** {avg_pnl_per_lot:.2f}  
    - **Total PnL (EUR):** {df['PnL (EUR)'].sum():.2f}  
    """)

    col1, col2, col3 = st.columns(3)
    col1.metric("Total Trades", total_trades)
    col2.metric("Win Rate", f"{win_rate:.2f}%")
    col3.metric("Total PnL (EUR)", round(df['PnL (EUR)'].sum(), 2))

    st.subheader("PnL Over Time")
    fig, ax = plt.subplots(figsize=(10, 4))
    ax.plot(df['Date'], df['Cumulative PnL'], label='Cumulative PnL', color='green')
    ax.set_xlabel("Date")
    ax.set_ylabel("PnL (EUR)")
    ax.set_title("Cumulative Profit & Loss")
    ax.grid(True)
    st.pyplot(fig)

    st.subheader("Trade Log")
    st.dataframe(df.set_index("Date"))

    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, sheet_name='Trades')
        writer.save()
        processed_data = output.getvalue()

    st.download_button(label="Download trade log as Excel",
                       data=processed_data,
                       file_name="trade_log.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
else:
    st.warning("No trades found for the selected date range.")
