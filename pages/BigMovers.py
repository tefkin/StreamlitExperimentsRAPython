import streamlit as st
import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import altair as alt


st.title("Financial Trend Deviation Monitor")

# Default tickers shown when the app first loads
DEFAULT_TICKERS = ["BMNR", "GC=F", "CL=F", "NG=F", "CC=F"]




# yahoo finance commodity tickers
# https://finance.yahoo.com/markets/commodities/


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

results = []

# Evaluate each ticker and store the last two weeks of data
for symbol in st.session_state.tickers:
    df = fetch_history(symbol)
    if df.empty:
        continue

    # Split data: exclude last two weeks for full period stats
    mask_full = df.index < TWO_WEEKS_AGO
    full_period = df.loc[mask_full]
    recent = df.loc[df.index >= TWO_WEEKS_AGO]

    # Calculate mean and std for full period (excluding last two weeks)
    mean_ret_full = full_period["Return"].mean()
    std_ret_full = full_period["Return"].std()

    # Calculate mean return for last two weeks
    mean_ret_recent = recent["Return"].mean()

    # Define big move: abs(mean_recent - mean_full) > 5 * std_full
    big_move = abs(mean_ret_recent - mean_ret_full) > 5 * std_ret_full
    results.append((symbol, recent, big_move))

   # st.subheader(f"{symbol}:")
   # st.write(f"Full period mean return (excluding last 2 weeks): {mean_ret_full:.5f}")
   # st.write(f"Full period std dev (excluding last 2 weeks): {std_ret_full:.5f}")
   # st.write(f"Recent (2 weeks) mean return: {mean_ret_recent:.5f}")
   # st.write(f"Big move? {'🚨 Yes' if big_move else 'No'}")


if results:
    for symbol, history, big_move in results:
        status = "🚨 Big mover!" if big_move else "Normal range"
        st.subheader(f"{symbol} - {status}")

        # Prepare data for Altair
        chart_data = history.reset_index()[["Date", "Close"]]
        chart_data = chart_data.rename(columns={"Date": "Date", "Close": "Close"})

        # Create an Altair line chart with tooltips and color
        line = alt.Chart(chart_data).mark_line(
            color="#1f77b4" if not big_move else "#d62728",
            strokeWidth=3
        ).encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Close:Q", title="Close Price"),
            tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip("Close:Q", title="Close Price")]
        )

        points = alt.Chart(chart_data).mark_circle(size=60, color="#ff7f0e").encode(
            x="Date:T",
            y="Close:Q",
            tooltip=[alt.Tooltip("Date:T", title="Date"), alt.Tooltip("Close:Q", title="Close Price")]
        )

        chart = (line + points).interactive().properties(
            width=700,
            height=350,
            title=f"{symbol} Closing Prices (Last 2 Weeks)"
        )

        st.altair_chart(chart, use_container_width=True)
else:
    st.write("No price data available for the selected tickers.")
