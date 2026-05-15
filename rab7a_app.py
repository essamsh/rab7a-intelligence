import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime
from io import BytesIO
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

st.set_page_config(page_title="RAB7A Intelligence", page_icon="📊", layout="wide", initial_sidebar_state="collapsed")

st.markdown("""
<style>
.main-header {font-size: 2.5rem; font-weight: 800; color: #1a1a2e; text-align: center; margin-bottom: 0.5rem;}
.sub-header {font-size: 1.1rem; color: #666; text-align: center; margin-bottom: 2rem;}
.metric-card {background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); padding: 1.5rem; border-radius: 15px; color: white; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.1);}
.metric-value {font-size: 1.8rem; font-weight: 700; margin-bottom: 0.3rem;}
.metric-label {font-size: 0.85rem; opacity: 0.9;}
.section-title {font-size: 1.3rem; font-weight: 700; color: #16213e; margin-top: 2rem; margin-bottom: 1rem; padding-bottom: 0.5rem; border-bottom: 3px solid #e94560;}
.footer {text-align: center; color: #999; font-size: 0.8rem; margin-top: 3rem; padding-top: 1rem; border-top: 1px solid #eee;}
</style>
""", unsafe_allow_html=True)

def generate_pdf(df, metrics, top5_products, top5_customers, channel_analysis):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=1.5*cm, leftMargin=1.5*cm, topMargin=1.5*cm, bottomMargin=1.5*cm)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle('Title', parent=styles['Heading1'], fontSize=22, textColor=colors.HexColor('#1a1a2e'), spaceAfter=15, alignment=TA_CENTER, fontName='Helvetica-Bold')
    section_style = ParagraphStyle('Section', parent=styles['Heading2'], fontSize=13, textColor=colors.HexColor('#16213e'), spaceAfter=10, spaceBefore=18, fontName='Helvetica-Bold')
    story = []
    story.append(Paragraph("RAB7A INTELLIGENCE", title_style))
    story.append(Paragraph("Food Distribution Sales Report", ParagraphStyle('Sub', parent=styles['Normal'], fontSize=10, textColor=colors.HexColor('#666'), alignment=TA_CENTER, spaceAfter=20)))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}", ParagraphStyle('Date', parent=styles['Normal'], fontSize=9, textColor=colors.HexColor('#999'), alignment=TA_CENTER, spaceAfter=25)))
    metric_data = [['TOTAL SALES', 'GROSS PROFIT', 'NET PROFIT', 'GM%'], [f"{metrics['total_sales']:,.0f} QAR", f"{metrics['gross_profit']:,.0f} QAR", f"{metrics['net_profit']:,.0f} QAR", f"{metrics['gm_percent']:.1f}%"]]
    m_table = Table(metric_data, colWidths=[3.5*cm]*4)
    m_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f8f9fa')), ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'), ('FONTSIZE', (0,1), (-1,1), 12), ('BOTTOMPADDING', (0,1), (-1,1), 10), ('TOPPADDING', (0,1), (-1,1), 10), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))]))
    story.append(m_table)
    story.append(Spacer(1, 12))
    sec_data = [['Transactions', 'Customers', 'Products', 'Avg Order'], [f"{metrics['num_transactions']:,}", f"{metrics['num_customers']:,}", f"{metrics['num_products']:,}", f"{metrics['avg_order']:,.0f} QAR"]]
    s_table = Table(sec_data, colWidths=[3.5*cm]*4)
    s_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#e94560')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (-1,-1), 'CENTER'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 5), ('TOPPADDING', (0,0), (-1,0), 5), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#fff5f5')), ('FONTNAME', (0,1), (-1,1), 'Helvetica-Bold'), ('FONTSIZE', (0,1), (-1,1), 11), ('BOTTOMPADDING', (0,1), (-1,1), 8), ('TOPPADDING', (0,1), (-1,1), 8), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))]))
    story.append(s_table)
    story.append(Spacer(1, 20))
    story.append(Paragraph("TOP 5 PRODUCTS", section_style))
    prod_data = [['#', 'Product', 'Sales', 'Qty', 'Profit']]
    for i, (prod, row) in enumerate(top5_products.iterrows(), 1):
        prod_data.append([str(i), str(prod)[:30], f"{row['Line Sales']:,.0f}", f"{row['Qty']:,.0f}", f"{row['Gross Profit']:,.0f}"])
    p_table = Table(prod_data, colWidths=[1*cm, 6*cm, 2.5*cm, 2*cm, 2.5*cm])
    p_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (0,-1), 'CENTER'), ('ALIGN', (2,0), (-1,-1), 'RIGHT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#e8f4f8')), ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#e8f4f8')), ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#e8f4f8')), ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8), ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))]))
    story.append(p_table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("TOP 5 CUSTOMERS", section_style))
    cust_data = [['#', 'Customer', 'Sales', 'Invoices', 'GM%']]
    for i, (cust, row) in enumerate(top5_customers.iterrows(), 1):
        cust_data.append([str(i), str(cust)[:30], f"{row['Total Sales']:,.0f}", f"{row['Invoices']:.0f}", f"{row['GM%']:.1f}%"])
    c_table = Table(cust_data, colWidths=[1*cm, 6*cm, 2.5*cm, 2*cm, 2.5*cm])
    c_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (0,-1), 'CENTER'), ('ALIGN', (2,0), (-1,-1), 'RIGHT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#fff5f5')), ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#fff5f5')), ('BACKGROUND', (0,5), (-1,5), colors.HexColor('#fff5f5')), ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8), ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))]))
    story.append(c_table)
    story.append(Spacer(1, 15))
    story.append(Paragraph("SALES BY CHANNEL", section_style))
    ch_data = [['Channel', 'Sales', 'Gross Profit', 'GM%']]
    for ch, row in channel_analysis.iterrows():
        ch_data.append([str(ch), f"{row['Line Sales']:,.0f}", f"{row['Gross Profit']:,.0f}", f"{row['GM%']:.1f}%"])
    ch_table = Table(ch_data, colWidths=[4.5*cm, 3*cm, 3*cm, 2.5*cm])
    ch_table.setStyle(TableStyle([('BACKGROUND', (0,0), (-1,0), colors.HexColor('#16213e')), ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke), ('ALIGN', (0,0), (0,-1), 'LEFT'), ('ALIGN', (1,0), (-1,-1), 'RIGHT'), ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'), ('FONTSIZE', (0,0), (-1,0), 8), ('BOTTOMPADDING', (0,0), (-1,0), 6), ('TOPPADDING', (0,0), (-1,0), 6), ('BACKGROUND', (0,1), (-1,1), colors.HexColor('#f0f8ff')), ('BACKGROUND', (0,3), (-1,3), colors.HexColor('#f0f8ff')), ('FONTNAME', (0,1), (-1,-1), 'Helvetica'), ('FONTSIZE', (0,1), (-1,-1), 8), ('BOTTOMPADDING', (0,1), (-1,-1), 5), ('TOPPADDING', (0,1), (-1,-1), 5), ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#dee2e6'))]))
    story.append(ch_table)
    story.append(Spacer(1, 25))
    story.append(Paragraph("RAB7A Intelligence — Powered by AI | www.rab7a.com", ParagraphStyle('Foot', parent=styles['Normal'], fontSize=8, textColor=colors.HexColor('#999'), alignment=TA_CENTER)))
    doc.build(story)
    buffer.seek(0)
    return buffer

def analyze_data(df):
    total_sales = df['Line Sales'].sum()
    total_cost = df['Line Cost'].sum()
    gross_profit = df['Gross Profit'].sum()
    net_profit = gross_profit
    gm_percent = (gross_profit / total_sales * 100) if total_sales > 0 else 0
    metrics = {'total_sales': total_sales, 'total_cost': total_cost, 'gross_profit': gross_profit, 'net_profit': net_profit, 'gm_percent': gm_percent, 'num_transactions': len(df), 'num_customers': df['Customer'].nunique(), 'num_products': df['Item'].nunique(), 'avg_order': total_sales / len(df) if len(df) > 0 else 0}
    top5_products = df.groupby('Item').agg({'Line Sales': 'sum', 'Gross Profit': 'sum', 'Qty': 'sum'}).sort_values('Line Sales', ascending=False).head(5)
    top5_customers = df.groupby('Customer').agg({'Line Sales': 'sum', 'Gross Profit': 'sum', 'Invoice No': 'nunique'}).sort_values('Line Sales', ascending=False).head(5)
    top5_customers.columns = ['Total Sales', 'Total GP', 'Invoices']
    top5_customers['GM%'] = (top5_customers['Total GP'] / top5_customers['Total Sales'] * 100).round(2)
    channel_analysis = df.groupby('Channel').agg({'Line Sales': 'sum', 'Gross Profit': 'sum'}).sort_values('Line Sales', ascending=False)
    channel_analysis['GM%'] = (channel_analysis['Gross Profit'] / channel_analysis['Line Sales'] * 100).round(2)
    return metrics, top5_products, top5_customers, channel_analysis

st.markdown('<div class="main-header">📊 RAB7A Intelligence</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-header">Food Distribution Analytics Platform</div>', unsafe_allow_html=True)
st.markdown("---")
uploaded_file = st.file_uploader("📁 Upload your sales Excel file", type=['xlsx', 'xls', 'csv'])

if uploaded_file is not None:
    try:
        if uploaded_file.name.endswith('.csv'):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file)
        with st.expander("📋 Data Preview", expanded=False):
            st.dataframe(df.head(10), use_container_width=True)
            st.info(f"Rows: {len(df):,} | Columns: {len(df.columns)}")
        metrics, top5_products, top5_customers, channel_analysis = analyze_data(df)
        st.markdown("---")
        st.markdown("### 📈 Key Metrics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{metrics["total_sales"]:,.0f}</div><div class="metric-label">Total Sales (QAR)</div></div>', unsafe_allow_html=True)
        with col2:
            st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);"><div class="metric-value">{metrics["gross_profit"]:,.0f}</div><div class="metric-label">Gross Profit (QAR)</div></div>', unsafe_allow_html=True)
        with col3:
            st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #fc4a1a 0%, #f7b733 100%);"><div class="metric-value">{metrics["net_profit"]:,.0f}</div><div class="metric-label">Net Profit (QAR)</div></div>', unsafe_allow_html=True)
        with col4:
            st.markdown(f'<div class="metric-card" style="background: linear-gradient(135deg, #4e54c8 0%, #8f94fb 100%);"><div class="metric-value">{metrics["gm_percent"]:.1f}%</div><div class="metric-label">GM%</div></div>', unsafe_allow_html=True)
        st.markdown("---")
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Transactions", f"{metrics['num_transactions']:,}")
        col2.metric("Customers", f"{metrics['num_customers']:,}")
        col3.metric("Products", f"{metrics['num_products']:,}")
        col4.metric("Avg Order", f"{metrics['avg_order']:,.0f} QAR")
        st.markdown('<div class="section-title">🏆 Top 5 Products by Sales</div>', unsafe_allow_html=True)
        prod_display = top5_products.copy()
        prod_display.columns = ['Sales (QAR)', 'Gross Profit', 'Quantity']
        prod_display['GM%'] = (prod_display['Gross Profit'] / prod_display['Sales (QAR)'] * 100).round(1)
        st.dataframe(prod_display, use_container_width=True)
        st.markdown('<div class="section-title">🏆 Top 5 Customers by Sales</div>', unsafe_allow_html=True)
        st.dataframe(top5_customers, use_container_width=True)
        st.markdown('<div class="section-title">📊 Sales by Channel</div>', unsafe_allow_html=True)
        ch_display = channel_analysis.copy()
        ch_display.columns = ['Sales (QAR)', 'Gross Profit', 'GM%']
        st.dataframe(ch_display, use_container_width=True)
        st.markdown('<div class="section-title">📈 Visual Analytics</div>', unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("Sales by Channel")
            ch_chart = channel_analysis['Line Sales'].reset_index()
            st.bar_chart(ch_chart.set_index('Channel'))
        with col2:
            st.subheader("Top 5 Products")
            prod_chart = top5_products['Line Sales'].reset_index()
            st.bar_chart(prod_chart.set_index('Item'))
        st.markdown("---")
        st.markdown("### 📥 Export Report")
        pdf_buffer = generate_pdf(df, metrics, top5_products, top5_customers, channel_analysis)
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.download_button(label="📄 Download PDF Report", data=pdf_buffer, file_name=f"RAB7A_Report_{datetime.now().strftime('%Y%m%d')}.pdf", mime="application/pdf", use_container_width=True)
        st.markdown('<div class="footer">RAB7A Intelligence — Powered by AI | www.rab7a.com</div>', unsafe_allow_html=True)
    except Exception as e:
        st.error(f"❌ Error: {str(e)}")
        st.info("Required columns: Invoice Date, Invoice No, Customer, Item, Qty, Line Sales, Line Cost, Gross Profit, Channel")
else:
    st.markdown('<div style="text-align: center; padding: 3rem; color: #999;"><div style="font-size: 4rem; margin-bottom: 1rem;">📁</div><div style="font-size: 1.2rem; margin-bottom: 0.5rem;">Upload your sales data to get started</div><div style="font-size: 0.9rem;">Supports Excel (.xlsx, .xls) and CSV files</div></div>', unsafe_allow_html=True)
    with st.expander("📋 Required Data Format"):
        st.markdown("Your Excel file should contain: Invoice Date, Invoice No, Customer, Item, Qty, Line Sales, Line Cost, Gross Profit, Channel")
