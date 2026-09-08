"""
=================================================================
AI Agent for Automated Data Pipeline & Report Generation
=================================================================
Ye main entry point hai. Ye poori pipeline ko run karta hai:

  Data Source -> Cleaning -> AI Analysis -> Report Generation -> Delivery

Usage:
    python main.py
    python main.py --config config/config.yaml

Config file (config/config.yaml) mein hi sab kuch control hota hai:
data source, output format, AI settings, email delivery, etc.
=================================================================
"""

import os
import sys
import argparse
import yaml

from connectors import get_connector
from processing.cleaner import clean_data
from ai_agent.analyzer import generate_insights
from reports.excel_report import generate_excel_report
from reports.pdf_report import generate_pdf_report
from reports.email_sender import send_report_email


def load_config(path: str) -> dict:
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict):
    print("=" * 60)
    print("AI REPORT AGENT - Pipeline Starting")
    print("=" * 60)

    # Output dir bana lo agar nahi hai
    os.makedirs(config["report"].get("output_dir", "outputs"), exist_ok=True)

    # ---------- STEP 1: Data Ingestion ----------
    print("\n[STEP 1] Data Ingestion...")
    connector = get_connector(config)
    df = connector.fetch()
    print(f"-> {len(df)} rows, {len(df.columns)} columns fetch hui.")

    # ---------- STEP 2: Data Cleaning ----------
    print("\n[STEP 2] Data Cleaning...")
    df = clean_data(df, config.get("cleaning", {}))

    # ---------- STEP 3: AI Analysis ----------
    print("\n[STEP 3] AI Analysis...")
    insights = generate_insights(df, config.get("ai_agent", {}))
    print(f"-> Summary: {insights.get('summary', '')[:150]}...")

    # ---------- STEP 4: Report Generation ----------
    print("\n[STEP 4] Report Generation...")
    generated_files = []
    formats = config["report"].get("formats", ["pdf"])

    if "excel" in formats:
        excel_path = generate_excel_report(df, insights, config["report"])
        generated_files.append(excel_path)

    if "pdf" in formats:
        pdf_path = generate_pdf_report(df, insights, config["report"])
        generated_files.append(pdf_path)

    # ---------- STEP 5: Delivery ----------
    print("\n[STEP 5] Delivery...")
    send_report_email(generated_files, config.get("delivery", {}).get("email", {}))

    print("\n" + "=" * 60)
    print("Pipeline Complete! Generated files:")
    for f in generated_files:
        print(f"  -> {f}")
    print("=" * 60)

    return generated_files


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI Agent for Automated Data Pipeline & Report Generation")
    parser.add_argument("--config", default="config/config.yaml", help="Path to config YAML file")
    args = parser.parse_args()

    cfg = load_config(args.config)
    run_pipeline(cfg)
