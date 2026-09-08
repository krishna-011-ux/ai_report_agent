"""
=================================================================
AI Report Agent - Streamlit Web App
=================================================================
Ye ek web interface hai jisse koi bhi (non-technical user bhi)
browser mein file upload karke automatically AI-powered report
bana sakta hai. Deploy karne ke baad ek shareable link mil jayega
jo koi bhi khol sakta hai.

Run locally:
    streamlit run streamlit_app.py

Deploy free (public link ke liye):
    Streamlit Community Cloud - dekho DEPLOY.md
=================================================================
"""

import streamlit as st
import pandas as pd
import os
import tempfile
import io

from processing.cleaner import clean_data
from ai_agent.analyzer import generate_insights
from reports.excel_report import generate_excel_report
from reports.pdf_report import generate_pdf_report

st.set_page_config(page_title="AI Report Agent", page_icon="📊", layout="wide")

# ---------------------------------------------------------------
# Sidebar - Configuration
# ---------------------------------------------------------------
st.sidebar.title("⚙️ Settings")

api_key_input = st.sidebar.text_input(
    "Anthropic API Key (AI insights ke liye)",
    type="password",
    help="Agar khali chhodoge to basic statistical summary milega, AI insights nahi.",
    value=os.environ.get("ANTHROPIC_API_KEY", ""),
)
if api_key_input:
    os.environ["ANTHROPIC_API_KEY"] = api_key_input

report_title = st.sidebar.text_input("Report Title", value="Automated Business Report")
domain_hint = st.sidebar.text_input(
    "Data kis domain ka hai? (AI ko context milega)",
    value="general business data",
    placeholder="e.g. sales data, HR attendance, finance expenses...",
)
output_formats = st.sidebar.multiselect(
    "Report Format", ["PDF", "Excel"], default=["PDF", "Excel"]
)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Data kabhi bhi server pe save nahi hota — sirf is session ke liye process hota hai.")

# ---------------------------------------------------------------
# Main Area
# ---------------------------------------------------------------
st.title("📊 AI Agent — Automated Data Pipeline & Report Generation")
st.write(
    "Apna data upload karo (CSV ya Excel), aur AI khud analyze karke "
    "professional PDF/Excel report bana dega — insights aur charts ke saath."
)

source_tab, sql_tab, api_tab = st.tabs(["📁 File Upload", "🗄️ Database (SQL)", "🌐 API"])

df = None

with source_tab:
    uploaded_file = st.file_uploader("CSV ya Excel file upload karo", type=["csv", "xlsx", "xls"])
    if uploaded_file is not None:
        try:
            if uploaded_file.name.endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)
            st.success(f"✅ {len(df)} rows, {len(df.columns)} columns load hui.")
        except Exception as e:
            st.error(f"File padhne mein error: {e}")

with sql_tab:
    st.caption("Connection string aur query dekar apne database se seedha data lao.")
    conn_str = st.text_input(
        "Connection String",
        placeholder="postgresql://user:password@host:5432/dbname",
        key="sql_conn",
    )
    sql_query = st.text_area("SQL Query", placeholder="SELECT * FROM sales", key="sql_query")
    if st.button("Database se Data Lao"):
        try:
            from sqlalchemy import create_engine
            engine = create_engine(conn_str)
            with engine.connect() as conn:
                df = pd.read_sql(sql_query, conn)
            st.success(f"✅ {len(df)} rows database se aayi.")
        except Exception as e:
            st.error(f"Database connection error: {e}")

with api_tab:
    st.caption("Kisi bhi REST API se JSON data lao.")
    api_url = st.text_input("API URL", key="api_url")
    api_token = st.text_input("Authorization Token (optional)", type="password", key="api_token")
    if st.button("API se Data Lao"):
        try:
            import requests
            headers = {"Authorization": f"Bearer {api_token}"} if api_token else {}
            resp = requests.get(api_url, headers=headers, timeout=30)
            resp.raise_for_status()
            data = resp.json()
            df = pd.json_normalize(data)
            st.success(f"✅ {len(df)} rows API se aayi.")
        except Exception as e:
            st.error(f"API call error: {e}")

# Data preview + pipeline run
if df is not None and not df.empty:
    st.markdown("### 📋 Data Preview")
    st.dataframe(df.head(10), use_container_width=True)

    st.markdown("### 📈 Quick Chart Setup (optional)")
    col1, col2 = st.columns(2)
    numeric_cols = df.select_dtypes(include="number").columns.tolist()
    all_cols = df.columns.tolist()
    with col1:
        chart_x = st.selectbox("Chart X-axis (category/date column)", options=[None] + all_cols)
    with col2:
        chart_y = st.selectbox("Chart Y-axis (numeric column)", options=[None] + numeric_cols)

    if st.button("🚀 Report Generate Karo", type="primary"):
        with st.spinner("Data clean ho raha hai..."):
            cleaning_config = {
                "drop_duplicates": True,
                "fill_missing_numeric_with": 0,
                "fill_missing_text_with": "Unknown",
                "date_columns": [],
            }
            cleaned_df = clean_data(df, cleaning_config)

        with st.spinner("AI insights generate ho rahe hain..."):
            ai_config = {
                "enabled": True,
                "model": "claude-sonnet-4-6",
                "domain_hint": domain_hint,
                "max_insights": 6,
            }
            insights = generate_insights(cleaned_df, ai_config)

        st.markdown("### 🧠 AI Insights")
        st.info(insights.get("summary", ""))
        if insights.get("insights"):
            st.markdown("**Key Insights:**")
            for point in insights["insights"]:
                st.markdown(f"- {point}")
        if insights.get("recommendations"):
            st.markdown("**Recommendations:**")
            for rec in insights["recommendations"]:
                st.markdown(f"- {rec}")

        with tempfile.TemporaryDirectory() as tmp_dir:
            report_config = {
                "title": report_title,
                "output_dir": tmp_dir,
                "charts": [{"type": "bar", "x": chart_x, "y": chart_y, "title": f"{chart_y} by {chart_x}"}]
                if chart_x and chart_y else [],
            }

            st.markdown("### 📥 Download Reports")
            dl_cols = st.columns(2)

            if "PDF" in output_formats:
                with st.spinner("PDF ban raha hai..."):
                    pdf_path = generate_pdf_report(cleaned_df, insights, report_config)
                    with open(pdf_path, "rb") as f:
                        dl_cols[0].download_button(
                            "⬇️ Download PDF Report",
                            data=f.read(),
                            file_name="report.pdf",
                            mime="application/pdf",
                        )

            if "Excel" in output_formats:
                with st.spinner("Excel ban raha hai..."):
                    excel_path = generate_excel_report(cleaned_df, insights, report_config)
                    with open(excel_path, "rb") as f:
                        dl_cols[1].download_button(
                            "⬇️ Download Excel Report",
                            data=f.read(),
                            file_name="report.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                        )

        st.success("✅ Report ready hai! Upar se download karo.")
else:
    st.info("👆 Shuru karne ke liye upar se file upload karo, ya SQL/API tab use karo.")
