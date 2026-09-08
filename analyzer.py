"""
AI Analyzer
-----------
Cleaned data ka statistical summary banata hai aur Claude API
ko bhejkar human-readable insights, trends/anomalies aur
business recommendations generate karta hai.

ANTHROPIC_API_KEY environment variable mein set hona chahiye.
"""

import os
import json
import pandas as pd


def _build_data_summary(df: pd.DataFrame) -> str:
    """DataFrame ka compact statistical summary banata hai."""

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
    categorical_cols = df.select_dtypes(include="object").columns.tolist()

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
    Dataset ke liye AI insights generate karta hai.

    Returns:
        {
            "summary": "...",
            "insights": ["...", "..."],
            "recommendations": ["...", "..."]
        }
    """

    # AI disabled
    if not ai_config.get("enabled", True):
        return {
            "summary": "AI analysis disabled in config.",
            "insights": [],
            "recommendations": []
        }

    # API key check
    api_key = os.environ.get("ANTHROPIC_API_KEY")

    if not api_key:
        print(
            "[AI Analyzer] WARNING: ANTHROPIC_API_KEY nahi mili. "
            "Fallback statistical summary use ho raha hai."
        )

        return _fallback_summary(df)

    # Anthropic package check
    try:
        import anthropic
    except ImportError:
        print(
            "[AI Analyzer] 'anthropic' package installed nahi hai."
        )

        return _fallback_summary(df)

    # Dataset summary
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

    # Prompt
    prompt = f"""
Tum ek business data analyst AI agent ho.

Neeche dataset ka statistical summary diya gaya hai.

Domain:
{domain_hint}

Dataset Summary:
{data_summary}

Mujhe STRICT JSON format mein jawab do.
Koi extra text nahi, sirf JSON.

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

Maximum {max_insights} insights do.

Insights:
- Specific hone chahiye
- Numbers-based hone chahiye
- Actionable hone chahiye
- Dataset ke actual data par based hone chahiye

Generic baatein mat likho.
"""

    try:
        # Claude client
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

        # Markdown code block remove
        raw_text = (
            raw_text
            .replace("```json", "")
            .replace("```", "")
            .strip()
        )

        # JSON parse
        try:
            result = json.loads(raw_text)

        except json.JSONDecodeError:
            print(
                "[AI Analyzer] JSON parse fail hua."
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
    Agar Claude API available nahi hai to
    basic statistical insights provide karta hai.
    """

    insights = []

    numeric_cols = df.select_dtypes(
        include="number"
    ).columns.tolist()

    for col in numeric_cols[:4]:

        # NaN handling
        mean_value = df[col].mean()
        max_value = df[col].max()
        min_value = df[col].min()

        insights.append(
            f"'{col}' ka average = {mean_value:.2f}, "
            f"max = {max_value:.2f}, "
            f"min = {min_value:.2f}"
        )

    return {
        "summary": (
            f"Dataset mein {len(df)} rows aur "
            f"{len(df.columns)} columns hain. "
            "Ye basic statistical summary hai."
        ),

        "insights": insights,

        "recommendations": [
            "Deeper AI insights ke liye "
            "ANTHROPIC_API_KEY set karein."
        ]
    }
