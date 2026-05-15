import streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime

st.set_page_config(page_title="RAB7A", page_icon="📊", layout="wide")
st.title("📊 RAB7A - Food Distribution Intelligence")
st.markdown("Upload your sales data to get insights")

uploaded_file = st.file_uploader("Upload Excel/CSV", type=['xlsx', 'xls', 'csv'])

if uploaded_file:
    df = pd.read_excel(uploaded_file)
    st.write("Data loaded successfully!")
    st.write(f"Rows: {len(df)}, Columns: {len(df.columns)}")
    st.dataframe(df.head())
    
    # Basic metrics
    if 'Line Sales' in df.columns:
        total_sales = df['Line Sales'].sum()
        st.metric("Total Sales", f"{total_sales:,.0f} QAR")
    
    # Download processed data
    buffer = BytesIO()
    df.to_excel(buffer, index=False)
    st.download_button("Download Excel", buffer.getvalue(), "report.xlsx")
