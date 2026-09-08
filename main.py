"""
=================================================================
AI Agent for Automated Data Pipeline & Report Generation
=================================================================
This is the main entry point for the application. It runs the
complete data processing pipeline:

  Data Source -> Cleaning -> AI Analysis -> Report Generation -> Delivery

Usage:
    python main.py
    python main.py --config config/config.yaml

The config/config.yaml file controls the complete pipeline,
including the data source, output formats, AI settings,
email delivery, and other application settings.
=================================================================
"""

import os
import sys
import argparse
import yaml

from connectors import get_connector
from cleaner import clean_data
from analyzer import generate_insights
from excel_report import generate_excel_report
from pdf_report import generate_pdf_report
from email_sender import send_report_email


def load_config(path: str) -> dict:
    """Load application configuration from a YAML file."""
    with open(path, "r") as f:
        return yaml.safe_load(f)


def run_pipeline(config: dict):
    print("=" * 60)
    print("AI REPORT AGENT - Pipeline Starting")
    print("=" * 60)

    # Create the output directory if it does not already exist.
    os.makedirs(
        config["report"].get("output_dir", "outputs"),
        exist_ok=True
    )

    # ---------- STEP 1: Data Ingestion ----------
    print("\n[STEP 1] Data Ingestion...")

    connector = get_connector(config)
    df = connector.fetch()

    print(
        f"-> Successfully fetched {len(df)} rows "
        f"and {len(df.columns)} columns."
    )

    # ---------- STEP 2: Data Cleaning ----------
    print("\n[STEP 2] Data Cleaning...")

    df = clean_data(
        df,
        config.get("cleaning", {})
    )

    # ---------- STEP 3: AI Analysis ----------
    print("\n[STEP 3] AI Analysis...")

    insights = generate_insights(
        df,
        config.get("ai_agent", {})
    )

    print(
        f"-> Summary: "
        f"{insights.get('summary', '')[:150]}..."
    )

    # ---------- STEP 4: Report Generation ----------
    print("\n[STEP 4] Report Generation...")

    generated_files = []

    formats = config["report"].get(
        "formats",
        ["pdf"]
    )

    if "excel" in formats:

        excel_path = generate_excel_report(
            df,
            insights,
            config["report"]
        )

        generated_files.append(
            excel_path
        )

    if "pdf" in formats:

        pdf_path = generate_pdf_report(
            df,
            insights,
            config["report"]
        )

        generated_files.append(
            pdf_path
        )

    # ---------- STEP 5: Delivery ----------
    print("\n[STEP 5] Delivery...")

    send_report_email(
        generated_files,
        config.get(
            "delivery",
            {}
        ).get(
            "email",
            {}
        )
    )

    print("\n" + "=" * 60)
    print("Pipeline Complete! Generated files:")

    for file_path in generated_files:
        print(
            f"  -> {file_path}"
        )

    print("=" * 60)

    return generated_files


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description=(
            "AI Agent for Automated Data Pipeline "
            "& Report Generation"
        )
    )

    parser.add_argument(
        "--config",
        default="config/config.yaml",
        help="Path to the configuration YAML file"
    )

    args = parser.parse_args()

    cfg = load_config(
        args.config
    )

    run_pipeline(cfg)
