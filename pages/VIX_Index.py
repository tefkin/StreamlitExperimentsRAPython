# pages/VIX_Index.py

import streamlit as st
import pandas as pd
import pandas_datareader.data as web

st.set_page_config(
    page_title="VIX Index",
    layout="wide",
)

st.title("📈 CBOE Volatility Index (VIX)")
st.markdown(
    """
    The CBOE VIX Index measures the market’s expectation of 30-day 
    volatility as implied by S&P 500 option prices. Data source: FRED.
    """
)

@st.cache_data(show_spinner=False)
def load_vix():
    # FRED series code for the VIX closing level
    df = web.DataReader("VIXCLS", "fred", start="1990-01-01")
    df.dropna(inplace=True)
    return df

# Load time series
df = load_vix()

# Plot the full history: X axis = date, Y axis = VIX level
st.line_chart(
    df,
    use_container_width=True,
    height=400
)

# Show the latest level as a metric
latest_date = df.index.max().date()
latest_value = df.iloc[-1, 0]
st.metric(
    label=f"Latest VIX (as of {latest_date})",
    value=f"{latest_value:.2f}"
)
