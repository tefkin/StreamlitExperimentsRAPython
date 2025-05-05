import streamlit as st

st.title("🎈 My new streamlit app for Richard Updated two")
st.write(
    "Let's start building! For help and inspiration, head over to [docs.streamlit.io](https://docs.streamlit.io/)."
)



import pandas as pd
df = pd.DataFrame({
  'first column': [1, 2, 3, 4],
  'second column': [10, 20, 30, 40]
})

# streamlit assumes the df should be writen to screen so allows you to skip
# the write command - magic
df
