"""
=================================================================
AI Report Agent - Streamlit Web App
=================================================================
A user-friendly web interface that allows users to upload data
files and automatically generate AI-powered business reports.

Users can upload CSV or Excel files, connect to SQL databases,
or fetch data from REST APIs.

Run locally:
    streamlit run streamlit_app.py
=================================================================
"""

import streamlit as st
import pandas as pd
import os
import tempfile

# ===============================================================
# Local Imports
# ===============================================================
from cleaner import clean_data
from analyzer import generate_insights
from excel_report import generate_excel_report
from pdf_report import generate_pdf_report


# ===============================================================
# Page Configuration
# ===============================================================
st.set_page_config(
    page_title="AI Report Agent",
    page_icon="📊",
    layout="wide"
)


# ===============================================================
# Sidebar - Configuration
# ===============================================================
st.sidebar.title("⚙️ Settings")

api_key_input = st.sidebar.text_input(
    "Anthropic API Key",
    type="password",
    help="Enter your Anthropic API key to enable AI-powered insights.",
    value=os.environ.get("ANTHROPIC_API_KEY", ""),
)

if api_key_input:
    os.environ["ANTHROPIC_API_KEY"] = api_key_input


report_title = st.sidebar.text_input(
    "Report Title",
    value="Automated Business Report"
)


domain_hint = st.sidebar.text_input(
    "Data Domain",
    value="general business data",
    placeholder="e.g. sales data, HR attendance, finance expenses..."
)


output_formats = st.sidebar.multiselect(
    "Report Format",
    ["PDF", "Excel"],
    default=["PDF", "Excel"]
)


st.sidebar.markdown("---")

st.sidebar.caption(
    "💡 Uploaded data is processed only during the current session "
    "and is not permanently stored on the server."
)


# ===============================================================
# Main Area
# ===============================================================
st.title(
    "📊 AI Report Agent — Automated Data Pipeline & Report Generation"
)

st.write(
    "Upload your dataset or connect to a SQL database or REST API. "
    "The system will analyze your data and generate professional "
    "reports with insights and visualizations."
)


# ===============================================================
# Data Source Tabs
# ===============================================================
source_tab, sql_tab, api_tab = st.tabs(
    ["📁 File Upload", "🗄️ Database (SQL)", "🌐 REST API"]
)


df = None


# ===============================================================
# File Upload
# ===============================================================
with source_tab:

    uploaded_file = st.file_uploader(
        "Upload a CSV or Excel file",
        type=["csv", "xlsx", "xls"]
    )

    if uploaded_file is not None:

        try:

            if uploaded_file.name.lower().endswith(".csv"):
                df = pd.read_csv(uploaded_file)
            else:
                df = pd.read_excel(uploaded_file)

            st.success(
                f"✅ Successfully loaded {len(df)} rows "
                f"and {len(df.columns)} columns."
            )

        except Exception as e:

            st.error(
                f"❌ Unable to read the uploaded file: {e}"
            )


# ===============================================================
# SQL Database
# ===============================================================
with sql_tab:

    st.caption(
        "Connect to your database using a connection string "
        "and SQL query."
    )

    conn_str = st.text_input(
        "Connection String",
        placeholder="postgresql://user:password@host:5432/dbname",
        key="sql_conn",
    )

    sql_query = st.text_area(
        "SQL Query",
        placeholder="SELECT * FROM sales",
        key="sql_query"
    )

    if st.button("Load Data from Database"):

        try:

            from sqlalchemy import create_engine

            if not conn_str:
                st.error("❌ Please enter a connection string.")

            elif not sql_query:
                st.error("❌ Please enter a SQL query.")

            else:

                engine = create_engine(conn_str)

                with engine.connect() as conn:

                    df = pd.read_sql(
                        sql_query,
                        conn
                    )

                st.success(
                    f"✅ Successfully retrieved {len(df)} rows "
                    "from the database."
                )

        except Exception as e:

            st.error(
                f"❌ Database connection error: {e}"
            )


# ===============================================================
# REST API
# ===============================================================
with api_tab:

    st.caption(
        "Fetch JSON data from any compatible REST API."
    )

    api_url = st.text_input(
        "API URL",
        key="api_url"
    )

    api_token = st.text_input(
        "Authorization Token (Optional)",
        type="password",
        key="api_token"
    )

    if st.button("Load Data from API"):

        try:

            import requests

            if not api_url:

                st.error(
                    "❌ Please enter an API URL."
                )

            else:

                headers = {}

                if api_token:

                    headers = {
                        "Authorization": f"Bearer {api_token}"
                    }

                resp = requests.get(
                    api_url,
                    headers=headers,
                    timeout=30
                )

                resp.raise_for_status()

                data = resp.json()

                df = pd.json_normalize(data)

                st.success(
                    f"✅ Successfully retrieved {len(df)} rows "
                    "from the API."
                )

        except Exception as e:

            st.error(
                f"❌ API request error: {e}"
            )


# ===============================================================
# Data Preview and Report Pipeline
# ===============================================================
if df is not None and not df.empty:

    st.markdown("### 📋 Data Preview")

    st.dataframe(
        df.head(10),
        use_container_width=True
    )


    # ===========================================================
    # Chart Configuration
    # ===========================================================
    st.markdown(
        "### 📈 Chart Configuration (Optional)"
    )

    col1, col2 = st.columns(2)

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    all_cols = df.columns.tolist()


    with col1:

        chart_x = st.selectbox(
            "X-axis (Category or Date)",
            options=[None] + all_cols
        )


    with col2:

        chart_y = st.selectbox(
            "Y-axis (Numeric Value)",
            options=[None] + numeric_cols
        )


    # ===========================================================
    # Generate Report
    # ===========================================================
    if st.button(
        "🚀 Generate Report",
        type="primary"
    ):

        # -------------------------------------------------------
        # Data Cleaning
        # -------------------------------------------------------
        with st.spinner(
            "Cleaning and preparing your data..."
        ):

            cleaning_config = {
                "drop_duplicates": True,
                "fill_missing_numeric_with": 0,
                "fill_missing_text_with": "Unknown",
                "date_columns": [],
            }

            try:

                cleaned_df = clean_data(
                    df,
                    cleaning_config
                )

            except Exception as e:

                st.error(
                    f"❌ Data cleaning failed: {e}"
                )

                st.stop()


        # -------------------------------------------------------
        # AI Analysis
        # -------------------------------------------------------
        with st.spinner(
            "Generating AI-powered insights..."
        ):

            ai_config = {
                "enabled": True,
                "model": "claude-sonnet-4-6",
                "domain_hint": domain_hint,
                "max_insights": 6,
            }

            try:

                insights = generate_insights(
                    cleaned_df,
                    ai_config
                )

            except Exception as e:

                st.error(
                    f"❌ AI analysis failed: {e}"
                )

                st.stop()


        # -------------------------------------------------------
        # Display Insights
        # -------------------------------------------------------
        st.markdown("### 🧠 AI Insights")

        st.info(
            insights.get(
                "summary",
                "No summary available."
            )
        )


        if insights.get("insights"):

            st.markdown("**Key Insights**")

            for point in insights["insights"]:

                st.markdown(
                    f"- {point}"
                )


        if insights.get("recommendations"):

            st.markdown("**Recommendations**")

            for rec in insights["recommendations"]:

                st.markdown(
                    f"- {rec}"
                )


        # -------------------------------------------------------
        # Generate Reports
        # -------------------------------------------------------
        with tempfile.TemporaryDirectory() as tmp_dir:

            report_config = {
                "title": report_title,
                "output_dir": tmp_dir,
                "charts": (
                    [
                        {
                            "type": "bar",
                            "x": chart_x,
                            "y": chart_y,
                            "title": f"{chart_y} by {chart_x}"
                        }
                    ]
                    if chart_x and chart_y
                    else []
                ),
            }


            st.markdown(
                "### 📥 Download Reports"
            )


            dl_cols = st.columns(2)


            # ---------------------------------------------------
            # PDF Report
            # ---------------------------------------------------
            if "PDF" in output_formats:

                with st.spinner(
                    "Generating PDF report..."
                ):

                    try:

                        pdf_path = generate_pdf_report(
                            cleaned_df,
                            insights,
                            report_config
                        )

                        with open(
                            pdf_path,
                            "rb"
                        ) as f:

                            dl_cols[0].download_button(
                                "⬇️ Download PDF Report",
                                data=f.read(),
                                file_name="report.pdf",
                                mime="application/pdf",
                            )

                    except Exception as e:

                        st.error(
                            f"❌ PDF generation failed: {e}"
                        )


            # ---------------------------------------------------
            # Excel Report
            # ---------------------------------------------------
            if "Excel" in output_formats:

                with st.spinner(
                    "Generating Excel report..."
                ):

                    try:

                        excel_path = generate_excel_report(
                            cleaned_df,
                            insights,
                            report_config
                        )

                        with open(
                            excel_path,
                            "rb"
                        ) as f:

                            dl_cols[1].download_button(
                                "⬇️ Download Excel Report",
                                data=f.read(),
                                file_name="report.xlsx",
                                mime=(
                                    "application/vnd.openxmlformats-"
                                    "officedocument.spreadsheetml.sheet"
                                ),
                            )

                    except Exception as e:

                        st.error(
                            f"❌ Excel generation failed: {e}"
                        )


        st.success(
            "✅ Your report is ready. Download it using the buttons above."
        )


else:

    st.info(
        "📊 Get started by uploading your dataset, or connect a "
        "SQL database or REST API to generate insights and reports."
    )
