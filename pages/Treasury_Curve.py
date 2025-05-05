# pages/Treasury_Curve.py
import streamlit as st
import pandas as pd
import pandas_datareader.data as web
from datetime import datetime

st.set_page_config(
    page_title="US Treasury Curve",
    layout="wide",
)

st.title("📈 US Treasury Yield Curve")
st.markdown(
    """
    Select a date to see the yield curve across maturities.
    Data source: FRED (Federal Reserve Economic Data).
    """
)

@st.cache_data(show_spinner=False)
def load_yield_data():
    # key maturities & their FRED series codes
    series = {
        "1M": "DGS1MO",
        "3M": "DGS3MO",
        "6M": "DGS6MO",
        "1Y": "DGS1",
        "2Y": "DGS2",
        "3Y": "DGS3",
        "5Y": "DGS5",
        "7Y": "DGS7",
        "10Y": "DGS10",
        "20Y": "DGS20",
        "30Y": "DGS30",
    }
    df = pd.DataFrame()
    for label, code in series.items():
        df[label] = web.DataReader(code, "fred", start="1990-01-01")
    df.dropna(inplace=True)
    return df

# Load data once
df = load_yield_data()

# Slider for date selection
min_date = df.index.min().date()
max_date = df.index.max().date()
selected_date = st.slider(
    "Select date",
    value=max_date,
    min_value=min_date,
    max_value=max_date,
    format="YYYY-MM-DD",
)

# after you get `selected_date` from st.slider (a datetime.date)…
ts = pd.Timestamp(selected_date)

# find the index position of the nearest date ≤ ts
pos = df.index.get_indexer([ts], method="ffill")[0]

# pull that row
yields = df.iloc[pos]


# Extract yields for that date
#yields = df.loc[selected_date]


maturities = [1/12, 3/12, 6/12, 1, 2, 3, 5, 7, 10, 20, 30]
curve_df = pd.DataFrame({
    "Maturity (years)": maturities,
    "Yield (%)": yields.values
})

# Plot
st.line_chart(
    data=curve_df.set_index("Maturity (years)"),
    use_container_width=True
)
