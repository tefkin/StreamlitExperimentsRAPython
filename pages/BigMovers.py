import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta

st.title("Financial Trend Deviation Monitor")

# Default tickers shown when the app first loads
DEFAULT_TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "TSLA"]

# Initialize ticker list in the session state
if "tickers" not in st.session_state:
    st.session_state.tickers = DEFAULT_TICKERS.copy()

# Sidebar controls for managing tickers
with st.sidebar:
    st.header("Manage Tickers")

    # Text input to add a new ticker
    new_symbol = st.text_input("Add ticker symbol")
    if st.button("Add") and new_symbol:
        symbol = new_symbol.strip().upper()
        if symbol and symbol not in st.session_state.tickers:
            if len(st.session_state.tickers) < 20:
                st.session_state.tickers.append(symbol)
            else:
                st.warning("Maximum of 20 tickers allowed.")

    # Select box to remove an existing ticker
    if st.session_state.tickers:
        remove_symbol = st.selectbox(
            "Remove ticker",
            options=st.session_state.tickers,
            index=0,
        )
        if st.button("Remove"):
            st.session_state.tickers.remove(remove_symbol)

st.write("**Current tickers:**", ", ".join(st.session_state.tickers))

# Time ranges
END_DATE = datetime.today()
START_DATE = END_DATE - timedelta(days=180)
TWO_WEEKS_AGO = END_DATE - timedelta(days=14)


@st.cache_data(show_spinner=False)
def fetch_history(symbol: str) -> pd.DataFrame:
    """Fetch historical pricing data for a ticker."""
    data = yf.download(symbol, start=START_DATE, end=END_DATE)
    if not data.empty:
        data["Return"] = data["Close"].pct_change()
    return data


off_trend = {}

# Evaluate each ticker for off trend movement
for symbol in st.session_state.tickers:
    df = fetch_history(symbol)
    if df.empty:
        continue

    mean_ret = df["Return"].mean()
    std_ret = df["Return"].std()
    recent = df.loc[df.index >= TWO_WEEKS_AGO]

    if ((recent["Return"] - mean_ret).abs() > 5 * std_ret).any():
        off_trend[symbol] = recent


if off_trend:
    st.header("Tickers Off Trend")
    for symbol, history in off_trend.items():
        st.subheader(symbol)
        st.line_chart(history["Close"], use_container_width=True)
else:
    st.write("No tickers are off trend based on the last two weeks of trading.")
