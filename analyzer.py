"""
AI Analyzer
-----------
Generates a statistical summary of the cleaned dataset and sends it
to the Claude API to generate human-readable insights, trends,
anomalies, and business recommendations.

The ANTHROPIC_API_KEY environment variable must be configured.
"""

import os
import json
import pandas as pd


def _build_data_summary(df: pd.DataFrame) -> str:
    """Build a compact statistical summary of the DataFrame."""

    summary_parts = []

    summary_parts.append(
        f"Total rows: {len(df)}, Total columns: {len(df.columns)}"
    )

    summary_parts.append(
        f"Columns: {list(df.columns)}"
    )

    # Numeric columns
    numeric_cols = df.select_dtypes(include="number").columns.tolist()

    if numeric_cols:
        summary_parts.append("\nNumeric column statistics:")
        summary_parts.append(
            df[numeric_cols].describe().to_string()
        )

    # Categorical columns
    categorical_cols = df.select_dtypes(
        include="object"
    ).columns.tolist()

    for col in categorical_cols[:5]:
        top_values = (
            df[col]
            .value_counts()
            .head(5)
            .to_dict()
        )

        summary_parts.append(
            f"\nTop values in '{col}': {top_values}"
        )

    # Date columns
    date_cols = df.select_dtypes(
        include="datetime"
    ).columns.tolist()

    if date_cols:
        for col in date_cols:
            summary_parts.append(
                f"\nDate range in '{col}': "
                f"{df[col].min()} to {df[col].max()}"
            )

    return "\n".join(summary_parts)


def generate_insights(
    df: pd.DataFrame,
    ai_config: dict
) -> dict:
    """
    Generate AI-powered insights for the dataset.

    Returns:
        {
            "summary": "...",
            "insights": ["...", "..."],
            "recommendations": ["...", "..."]
        }
    """

    # Check whether AI analysis is enabled.
    if not ai_config.get("enabled", True):
        return {
            "summary": "AI analysis is disabled in the configuration.",
            "insights": [],
            "recommendations": []
        }

    # Check for the Anthropic API key.
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print(
            "[AI Analyzer] WARNING: ANTHROPIC_API_KEY was not found. "
            "Using the fallback statistical summary."
        )

        return _fallback_summary(df)

    # Check whether the Anthropic package is installed.
    try:
        import anthropic
    except ImportError:
        print(
            "[AI Analyzer] The 'anthropic' package is not installed."
        )

        return _fallback_summary(df)

    # Build the dataset summary.
    data_summary = _build_data_summary(df)

    domain_hint = ai_config.get(
        "domain_hint",
        "general business data"
    )

    max_insights = ai_config.get(
        "max_insights",
        6
    )

    model = ai_config.get(
        "model",
        "claude-sonnet-4-6"
    )

    # Build the AI prompt.
    prompt = f"""
You are an AI business data analyst.

The statistical summary of the dataset is provided below.

Domain:
{domain_hint}

Dataset Summary:
{data_summary}

Return the response in STRICT JSON format.
Do not include any additional text, only valid JSON.

Format:

{{
    "summary": "2-3 line overall summary",
    "insights": [
        "insight 1",
        "insight 2"
    ],
    "recommendations": [
        "recommendation 1",
        "recommendation 2"
    ]
}}

Provide a maximum of {max_insights} insights.

Insights should:
- Be specific
- Be supported by numerical data
- Be actionable
- Be based on the actual dataset

Do not provide generic statements.
"""

    try:
        # Initialize the Claude client.
        client = anthropic.Anthropic(
            api_key=api_key
        )

        print(
            f"[AI Analyzer] Calling Claude ({model})..."
        )

        response = client.messages.create(
            model=model,
            max_tokens=1500,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
        )

        raw_text = response.content[0].text.strip()

        # Remove Markdown code blocks if present.
        raw_text = (
            raw_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # Parse the JSON response.
        try:
            result = json.loads(raw_text)

        except json.JSONDecodeError:
            print(
                "[AI Analyzer] Failed to parse the AI response as JSON."
            )

            result = {
                "summary": raw_text,
                "insights": [],
                "recommendations": []
            }

        return result

    except Exception as e:
        print(
            f"[AI Analyzer] Claude API error: {e}"
        )

        return _fallback_summary(df)


def _fallback_summary(df: pd.DataFrame) -> dict:
    """
    Provide basic statistical insights when the Claude API
    is unavailable.
    """

    insights = []

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    for col in numeric_cols[:4]:

        # Calculate basic statistics.
        mean_value = df[col].mean()
        max_value = df[col].max()
        min_value = df[col].min()

        insights.append(
            f"'{col}' average = {mean_value:.2f}, "
            f"maximum = {max_value:.2f}, "
            f"minimum = {min_value:.2f}"
        )

    return {
        "summary": (
            f"The dataset contains {len(df)} rows and "
            f"{len(df.columns)} columns. "
            "This is a basic statistical summary."
        ),

        "insights": insights,

        "recommendations": [
            "Configure the ANTHROPIC_API_KEY to generate "
            "deeper AI-powered insights."
        ]
    }
