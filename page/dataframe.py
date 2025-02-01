import streamlit as st
from app import df

st.title('Dataset de vendas')
st.dataframe(df)