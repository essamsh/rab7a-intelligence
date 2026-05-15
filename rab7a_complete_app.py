mport streamlit as st
import pandas as pd
import numpy as np
from io import BytesIO
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(page_title="RAB7A - Food Distribution Intelligence", page_icon="📊", layout="wide")

st.markdown("""
<style>
.main-header { font-size: 48px; font-weight: bold; color: #1a1a2e; text-align: center; margin-bottom: 5px; }
.sub-header { font-size: 20px; color: #4a4a4a; text-align: center; margin-bottom: 30px; }
.kpi-card { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 25px; border-radius: 15px; color: white; text-align: center; }
.kpi-value { font-size: 32px; font-weight: bold; margin: 10px 0; }
.kpi-label { font-size: 14px; opacity: 0.9; text-transform: uppercase; }
.section-title { font-size: 24px; font-weight: bold; color: #1a1a2e; margin: 30px 0 15px 0; padding-bottom: 10px; border-bottom: 3px solid #667eea; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-header">📊 RAB7A</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Food Distribution Intelligence Engine</div>', unsafe_allow_html=True)
st.markdown("---")

st.sidebar.markdown("## 🎯 RAB7A Platform")
st.sidebar.markdown("---")
st.sidebar.markdown("### 📋 Reports:")
st.sidebar.markdown("- Executive Summary")
st.sidebar.markdown("- Customer Profitability")
st.sidebar.markdown("- Product Profitability")
st.sidebar.markdown("- Supplier Profitability")
st.sidebar.markdown("- Channel Analysis")
st.sidebar.markdown("- Salesman Performance")
st.sidebar.markdown("- P&L Monthly")

st.markdown("### 📤 Upload Your Sales Transaction Data")
uploaded_file = st.file_uploader("Drop your Excel/CSV file here", type=['xlsx', 'xls', 'csv'])

def process_data(df):
    df.columns = [str(c).strip() for c in df.columns]
    numeric_cols = ['Qty', 'Unit Cost', 'Unit Price', 'Line Sales', 'Line Cost', 'Gross Profit']
    for col in numeric_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    if 'Line Sales' not in df.columns or df['Line Sales'].sum() == 0:
        df['Line Sales'] = df['Qty'] * df['Unit Price']
    if 'Line Cost' not in df.columns or df['Line Cost'].sum() == 0:
        df['Line Cost'] = df['Qty'] * df['Unit Cost']
    if 'Gross Profit' not in df.columns or df['Gross Profit'].sum() == 0:
        df['Gross Profit'] = df['Line Sales'] - df['Line Cost']
    if 'Sale_Sales' not in df.columns:
        df['Sale_Sales'] = df['Line Sales']
        df['Return_Sales'] = 0
    if 'Sale_GP' not in df.columns:
        df['Sale_GP'] = df['Gross Profit']
        df['Return_GP'] = 0
    return df

def generate_executive_summary(df):
    total_sales = df['Line Sales'].sum()
    total_cost = df['Line Cost'].sum()
    total_gp = df['Gross Profit'].sum()
    overall_gm = total_gp / total_sales if total_sales != 0 else 0
    return {
        'Total Sales': total_sales, 'Total GP': total_gp,
        'Overall GM %': overall_gm, 'Cash Used': total_cost,
        'Transactions': len(df), 'Customers': df['Customer'].nunique(),
        'Products': df['Item'].nunique(),
        'Suppliers': df['Supplier'].nunique() if 'Supplier' in df.columns else 0,
        'Channels': df['Channel'].nunique() if 'Channel' in df.columns else 0
    }

def generate_customer_profitability(df):
    cust = df.groupby('Customer').agg({
        'Sale_Sales': 'sum', 'Return_Sales': 'sum', 'Line Cost': 'sum',
        'Line Sales': 'sum', 'Gross Profit': 'sum'
    }).reset_index()
    cust['Net Sales'] = cust['Sale_Sales'] - cust['Return_Sales']
    cust['Net GP'] = cust['Gross Profit']
    cust['Net GM %'] = np.where(cust['Net Sales'] != 0, cust['Net GP'] / cust['Net Sales'], 0)
    cust['Sales Rank'] = cust['Net Sales'].rank(ascending=False, method='min').astype(int)
    cust['GP Rank'] = cust['Net GP'].rank(ascending=False, method='min').astype(int)
    cust = cust.sort_values('Net Sales', ascending=False)
    total_sales = cust['Net Sales'].sum()
    cust['Contribution %'] = cust['Net Sales'] / total_sales
    cust['Cumulative Contribution %'] = cust['Contribution %'].cumsum()
    def get_pareto(row):
        if row['Cumulative Contribution %'] <= 0.20: return 'Top 20%'
        elif row['Cumulative Contribution %'] <= 0.80: return 'Middle 60%'
        else: return 'Bottom 20%'
    cust['Pareto Flag'] = cust.apply(get_pareto, axis=1)
    def get_risk(row):
        if row['Net GM %'] < 0.05 and row['Net Sales'] > total_sales * 0.05:
            return '⚠ Volume Risk'
        elif row['Net GM %'] > 0.30 and row['Pareto Flag'] != 'Top 20%':
            return '⭐ Growth Opportunity'
        else: return 'OK'
    cust['Risk Flag'] = cust.apply(get_risk, axis=1)
    return cust

def generate_product_profitability(df):
    prod = df.groupby('Item').agg({
        'Sale_Sales': 'sum', 'Return_Sales': 'sum', 'Line Cost': 'sum',
        'Line Sales': 'sum', 'Gross Profit': 'sum'
    }).reset_index()
    prod['Net Sales'] = prod['Sale_Sales'] - prod['Return_Sales']
    prod['Net GP'] = prod['Gross Profit']
    prod['Net GM %'] = np.where(prod['Net Sales'] != 0, prod['Net GP'] / prod['Net Sales'], 0)
    prod['Sales Rank'] = prod['Net Sales'].rank(ascending=False, method='min').astype(int)
    prod['GP Rank'] = prod['Net GP'].rank(ascending=False, method='min').astype(int)
    total_gp = prod['Net GP'].sum()
    prod = prod.sort_values('Net Sales', ascending=False)
    prod['Contribution %'] = prod['Net GP'] / total_gp if total_gp != 0 else 0
    prod['Cumulative %'] = prod['Contribution %'].cumsum()
    def get_flag(row):
        if row['Net GM %'] > 0.30 and row['Net Sales'] > 5000: return 'Hidden Gem'
        elif row['Net GM %'] < 0.05 and row['Net Sales'] > 10000: return 'Volume-Low GP'
        elif row['Net Sales'] < 1000: return 'Tail'
        else: return 'Core'
    prod['Flag'] = prod.apply(get_flag, axis=1)
    def get_rec(row):
        if row['Flag'] == 'Hidden Gem': return 'PUSH - HIDDEN GEM'
        elif row['Flag'] == 'Volume-Low GP': return 'REPRICE / CONTROL'
        elif row['Flag'] == 'Tail': return 'STOP / MINIMIZE'
        else: return 'CORE - PROTECT & SCALE'
    prod['Recommendation'] = prod.apply(get_rec, axis=1)
    return prod

def generate_supplier_profitability(df):
    supp = df.groupby('Supplier').agg({
        'Sale_Sales': 'sum', 'Return_Sales': 'sum', 'Line Cost': 'sum',
        'Line Sales': 'sum', 'Gross Profit': 'sum'
    }).reset_index()
    supp['Net Sales'] = supp['Sale_Sales'] - supp['Return_Sales']
    supp['Net GP'] = supp['Gross Profit']
    supp['Net GM %'] = np.where(supp['Net Sales'] != 0, supp['Net GP'] / supp['Net Sales'], 0)
    supp['Sales Rank'] = supp['Net Sales'].rank(ascending=False, method='min').astype(int)
    supp['GP Rank'] = supp['Net GP'].rank(ascending=False, method='min').astype(int)
    total_gp = supp['Net GP'].sum()
    supp = supp.sort_values('Net Sales', ascending=False)
    supp['Contribution %'] = supp['Net GP'] / total_gp if total_gp != 0 else 0
    supp['Cumulative %'] = supp['Contribution %'].cumsum()
    def get_flag(row):
        if row['Net Sales'] > 50000 and row['Net GM %'] > 0.10: return 'Core Supplier'
        elif row['Net Sales'] > 10000 and row['Net GM %'] < 0.05: return 'Volume / Low Margin'
        elif row['Net GM %'] > 0.15 and row['Net Sales'] > 10000: return 'Hidden Value'
        else: return 'Tail Supplier'
    supp['Flag'] = supp.apply(get_flag, axis=1)
    def get_rec(row):
        if row['Flag'] == 'Core Supplier': return 'PROTECT & GROW'
        elif row['Flag'] == 'Volume / Low Margin': return 'RENEGOTIATE / REPRICE'
        elif row['Flag'] == 'Hidden Value': return 'PUSH RANGE / INCREASE SHARE'
        else: return 'REDUCE / EXIT'
    supp['Recommendation'] = supp.apply(get_rec, axis=1)
    return supp

def generate_channel_profitability(df):
    ch = df.groupby('Channel').agg({'Line Sales': 'sum', 'Line Cost': 'sum', 'Gross Profit': 'sum'}).reset_index()
    ch['GM %'] = np.where(ch['Line Sales'] != 0, ch['Gross Profit'] / ch['Line Sales'], 0)
    total_sales = ch['Line Sales'].sum()
    total_gp = ch['Gross Profit'].sum()
    ch['Channel Contribution %'] = ch['Gross Profit'] / total_gp if total_gp != 0 else 0
    ch['Channel Dominance %'] = ch['Line Sales'] / total_sales if total_sales != 0 else 0
    ch['Cost Intensity %'] = ch['Line Cost'] / ch['Line Sales']
    ch['Gross Profit Rank'] = ch['Gross Profit'].rank(ascending=False, method='min').astype(int)
    ch['Profit per 1 QAR'] = ch['GM %']
    ch['Profit Rank'] = ch['Gross Profit'].rank(ascending=False, method='min').astype(int)
    ch['Risk Flag'] = 'OK'
    ch['Action Note'] = 'Maintain'
    return ch.sort_values('Line Sales', ascending=False)

def generate_salesman_performance(df):
    sm = df.groupby('Salesman').agg({'Line Sales': 'sum', 'Line Cost': 'sum', 'Gross Profit': 'sum'}).reset_index()
    sm['GM%'] = np.where(sm['Line Sales'] != 0, sm['Gross Profit'] / sm['Line Sales'], 0)
    sm['Sales Rank'] = sm['Line Sales'].rank(ascending=False, method='min').astype(int)
    sm['GP Rank'] = sm['Gross Profit'].rank(ascending=False, method='min').astype(int)
    return sm.sort_values('Line Sales', ascending=False)

def generate_pl_monthly(df):
    df['Invoice Date'] = pd.to_datetime(df['Invoice Date'])
    df['Month_Name'] = df['Invoice Date'].dt.strftime('%b %Y')
    pl = df.groupby('Month_Name').agg({'Line Sales': 'sum', 'Line Cost': 'sum', 'Gross Profit': 'sum'}).reset_index()
    pl['GM %'] = np.where(pl['Line Sales'] != 0, pl['Gross Profit'] / pl['Line Sales'], 0)
    return pl.sort_values('Line Sales', ascending=False)

if uploaded_file is not None:
    try:
        with st.spinner("RAB7A Engine analyzing your data..."):
            if uploaded_file.name.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            df = process_data(df)
            summary = generate_executive_summary(df)
            customer_df = generate_customer_profitability(df)
            product_df = generate_product_profitability(df)
            supplier_df = generate_supplier_profitability(df)
            channel_df = generate_channel_profitability(df)
            salesman_df = generate_salesman_performance(df)
            pl_monthly = generate_pl_monthly(df)

        st.success("Analysis Complete! All reports generated.")

        st.markdown('<div class="section-title">Executive Summary</div>', unsafe_allow_html=True)
        col1, col2, col3, col4, col5 = st.columns(5)
        with col1:
            st.markdown(f'<div class="kpi-card"><div class="kpi-label">Total Sales</div><div class="kpi-value">{summary["Total Sales"]:,.0f}</div><div style="font-size:12px">QAR</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);"><div class="kpi-label">Gross Profit</div><div class="kpi-value">{summary["Total GP"]:,.0f}</div><div style="font-size:12px">QAR</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);"><div class="kpi-label">GM %</div><div class="kpi-value">{summary["Overall GM %"]*100:.1f}%</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #43e97b 0%, #38f9d7 100%);"><div class="kpi-label">Transactions</div><div class="kpi-value">{summary["Transactions"]:,}</div></div>', unsafe_allow_html=True)
        with col5:
            st.markdown(f'<div class="kpi-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);"><div class="kpi-label">Customers</div><div class="kpi-value">{summary["Customers"]:,}</div></div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">Detailed Reports</div>', unsafe_allow_html=True)
        tabs = st.tabs(["Customers", "Products", "Suppliers", "Channels", "Salesmen", "P&L Monthly"])

        with tabs[0]:
            st.markdown("### Customer Profitability")
            pareto_filter = st.multiselect("Pareto Flag:", options=customer_df['Pareto Flag'].unique(), default=customer_df['Pareto Flag'].unique())
            risk_filter = st.multiselect("Risk Flag:", options=customer_df['Risk Flag'].unique(), default=customer_df['Risk Flag'].unique())
            filtered = customer_df[(customer_df['Pareto Flag'].isin(pareto_filter)) & (customer_df['Risk Flag'].isin(risk_filter))]
            display_cols = ['Customer', 'Net Sales', 'Net GP', 'Net GM %', 'Sales Rank', 'GP Rank', 'Pareto Flag', 'Risk Flag', 'Contribution %']
            st.dataframe(filtered[display_cols].style.format({'Net Sales': '{:,.2f}', 'Net GP': '{:,.2f}', 'Net GM %': '{:.1%}', 'Contribution %': '{:.1%}'}), use_container_width=True, height=500)

        with tabs[1]:
            st.markdown("### Product Profitability")
            flag_filter = st.multiselect("Product Flag:", options=product_df['Flag'].unique(), default=product_df['Flag'].unique(), key="prod")
            filtered = product_df[product_df['Flag'].isin(flag_filter)]
            display_cols = ['Item', 'Net Sales', 'Net GP', 'Net GM %', 'Sales Rank', 'Flag', 'Recommendation']
            st.dataframe(filtered[display_cols].style.format({'Net Sales': '{:,.2f}', 'Net GP': '{:,.2f}', 'Net GM %': '{:.1%}'}), use_container_width=True, height=500)

        with tabs[2]:
            st.markdown("### Supplier Profitability")
            display_cols = ['Supplier', 'Net Sales', 'Net GP', 'Net GM %', 'Flag', 'Recommendation']
            st.dataframe(supplier_df[display_cols].style.format({'Net Sales': '{:,.2f}', 'Net GP': '{:,.2f}', 'Net GM %': '{:.1%}'}), use_container_width=True, height=500)

        with tabs[3]:
            st.markdown("### Channel Analysis")
            display_cols = ['Channel', 'Line Sales', 'Gross Profit', 'GM %', 'Channel Dominance %', 'Profit per 1 QAR', 'Action Note']
            st.dataframe(channel_df[display_cols].style.format({'Line Sales': '{:,.2f}', 'Gross Profit': '{:,.2f}', 'GM %': '{:.1%}', 'Channel Dominance %': '{:.1%}'}), use_container_width=True)

        with tabs[4]:
            st.markdown("### Salesman Performance")
            display_cols = ['Salesman', 'Line Sales', 'Line Cost', 'Gross Profit', 'GM%', 'Sales Rank']
            st.dataframe(salesman_df[display_cols].style.format({'Line Sales': '{:,.2f}', 'Line Cost': '{:,.2f}', 'Gross Profit': '{:,.2f}', 'GM%': '{:.1%}'}), use_container_width=True)

        with tabs[5]:
            st.markdown("### Monthly P&L")
            display_cols = ['Month_Name', 'Line Sales', 'Line Cost', 'Gross Profit', 'GM %']
            st.dataframe(pl_monthly[display_cols].style.format({'Line Sales': '{:,.2f}', 'Line Cost': '{:,.2f}', 'Gross Profit': '{:,.2f}', 'GM %': '{:.1%}'}), use_container_width=True)

        st.markdown('<div class="section-title">Download Reports</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            def gen_excel():
                buffer = BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    pd.DataFrame({'Metric': list(summary.keys()), 'Value': list(summary.values())}).to_excel(writer, sheet_name='Executive Summary', index=False)
                    customer_df.to_excel(writer, sheet_name='Customer Profitability', index=False)
                    product_df.to_excel(writer, sheet_name='Product Profitability', index=False)
                    supplier_df.to_excel(writer, sheet_name='Supplier Profitability', index=False)
                    channel_df.to_excel(writer, sheet_name='Channel Analysis', index=False)
                    salesman_df.to_excel(writer, sheet_name='Salesman Performance', index=False)
                    pl_monthly.to_excel(writer, sheet_name='P&L Monthly', index=False)
                    df.to_excel(writer, sheet_name='Raw Data', index=False)
                buffer.seek(0)
                return buffer
            excel_buffer = gen_excel()
            st.download_button(label="Download Excel Report", data=excel_buffer, file_name=f"RAB7A_Report_{datetime.now().strftime('%Y%m%d')}.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
        with col2:
            csv_buffer = BytesIO()
            df.to_csv(csv_buffer, index=False)
            csv_buffer.seek(0)
            st.download_button(label="Download CSV Data", data=csv_buffer, file_name=f"RAB7A_RawData_{datetime.now().strftime('%Y%m%d')}.csv", mime="text/csv", use_container_width=True)

        st.markdown("---")
        st.markdown("<div style='text-align: center; color: #666;'>Powered by RAB7A Intelligence Engine</div>", unsafe_allow_html=True)

    except Exception as e:
        st.error(f"Error: {str(e)}")
        st.info("Please ensure your file has: Invoice Date, Customer, Item, Qty, Unit Price, Unit Cost, Channel, Supplier, Salesman")

else:
    st.markdown("---")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<div style="background: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 40px;">📤</div><h3>1. Upload</h3><p>Upload your sales transaction data</p></div>', unsafe_allow_html=True)
    with col2:
        st.markdown('<div style="background: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 40px;">🤖</div><h3>2. Analyze</h3><p>AI Engine processes all data</p></div>', unsafe_allow_html=True)
    with col3:
        st.markdown('<div style="background: #f8f9fa; padding: 25px; border-radius: 15px; text-align: center;"><div style="font-size: 40px;">📊</div><h3>3. Download</h3><p>Get Excel & CSV reports</p></div>', unsafe_allow_html=True)
